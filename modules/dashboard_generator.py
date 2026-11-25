"""Question-driven dashboard planning and rendering for AI Data Analyst Assistant."""
import json
import re

import pandas as pd
import plotly.express as px
import streamlit as st

ALLOWED_AGGREGATIONS = {"count", "sum", "mean", "median", "min", "max", "nunique"}
ALLOWED_CHARTS = {"bar", "line", "pie", "histogram", "scatter", "box"}
NUMERIC_AGGS = {"sum", "mean", "median", "min", "max"}


def _column_profile(df):
    profile = []
    for col in df.columns:
        series = df[col]
        profile.append({
            "name": str(col),
            "dtype": str(series.dtype),
            "numeric": bool(pd.api.types.is_numeric_dtype(series)),
            "datetime": bool(pd.api.types.is_datetime64_any_dtype(series)),
            "unique_values": int(series.nunique(dropna=True)),
            "sample_values": [str(v)[:80] for v in series.dropna().head(4).tolist()],
        })
    return profile


def _extract_business_questions(requirements):
    """Extract numbered/bulleted questions from the saved questionnaire text."""
    match = re.search(
        r"BUSINESS QUESTIONS:\s*(.*?)(?=\n\s*(?:REQUESTED KPI COLUMNS|COMPARISON DIMENSIONS|TIME COLUMN|PREFERRED CHARTS|ADDITIONAL REQUIREMENTS|[A-Z ]{4,}:)|\Z)",
        requirements, flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        # Also support a plain list pasted directly into Build My Dashboard.
        raw = requirements
    else:
        raw = match.group(1)
    questions = []
    for line in raw.splitlines():
        line = line.strip()
        line = re.sub(r"^(?:[-*•]+\s*|\d+[.)]\s*)", "", line).strip()
        if not line or line.lower() in {"not specified", "none"}:
            continue
        # If multiple complete questions were pasted on one line, split them.
        parts = re.split(r"(?<=\?)\s+(?=[A-Z0-9])", line)
        questions.extend(part.strip() for part in parts if part.strip())
    return questions


def _clean_json_response(response):
    cleaned = (response or "").strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Gemini did not return a valid JSON dashboard plan. Please try again.")
    return json.loads(cleaned[start:end + 1])


def _validate_metric(item, df):
    if not isinstance(item, dict):
        return None
    col = str(item.get("column", "*"))
    agg = str(item.get("aggregation", "count")).lower()
    if agg not in ALLOWED_AGGREGATIONS:
        return None
    if col != "*" and col not in df.columns:
        return None
    if col != "*" and agg in NUMERIC_AGGS and not pd.api.types.is_numeric_dtype(df[col]):
        return None
    return {"label": str(item.get("label", f"{agg.title()} {col}"))[:90], "column": col, "aggregation": agg}


def _validate_chart(item, df):
    if not isinstance(item, dict):
        return None
    kind = str(item.get("type", "")).lower()
    x, y, group = item.get("x"), item.get("y"), item.get("group_by")
    if kind not in ALLOWED_CHARTS:
        return None
    if x is not None and x not in df.columns:
        return None
    if y is not None and y not in df.columns:
        return None
    if group is not None and group not in df.columns:
        group = None
    if kind in {"histogram", "box"}:
        target = y or x
        if not target or not pd.api.types.is_numeric_dtype(df[target]):
            return None
        x, y = None, target
    elif kind == "scatter":
        if not x or not y:
            return None
        if not (pd.api.types.is_numeric_dtype(df[x]) and pd.api.types.is_numeric_dtype(df[y])):
            return None
    else:
        if not x:
            return None
        if y and not pd.api.types.is_numeric_dtype(df[y]):
            y = None
    agg = str(item.get("aggregation", "mean")).lower()
    if agg not in {"sum", "mean", "count"}:
        agg = "mean"
    return {
        "title": str(item.get("title", f"{kind.title()} chart"))[:120],
        "type": kind, "x": x, "y": y, "aggregation": agg, "group_by": group,
    }


def _auto_chart_type(question, chart, df):
    """Choose a chart from the meaning of the business question and valid columns."""
    q = str(question).lower()
    numeric = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])
                   and not pd.api.types.is_datetime64_any_dtype(df[c])
                   and 1 < df[c].nunique(dropna=True) <= 30]
    dates = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]

    # Keep Gemini's selected columns when valid; infer only missing fields.
    x = chart.get("x") if chart else None
    y = chart.get("y") if chart else None
    if not x:
        x = dates[0] if dates and any(w in q for w in ("trend", "over time", "monthly", "daily", "weekly")) else (categorical[0] if categorical else None)
    if not y and numeric:
        y = numeric[0]

    if any(w in q for w in ("relationship", "correlation", "related", "versus", " vs ", "against")):
        nums = [c for c in numeric if c != x]
        if len(numeric) >= 2:
            x, y = numeric[0], numeric[1]
            kind = "scatter"
        else:
            kind = chart.get("type", "bar") if chart else "bar"
    elif any(w in q for w in ("distribution", "spread", "frequency", "range of")):
        if y and pd.api.types.is_numeric_dtype(df[y]):
            kind = "histogram"
        else:
            kind = "bar"
    elif any(w in q for w in ("share", "proportion", "percentage", "composition", "breakdown")):
        kind = "pie" if x else "bar"
    elif any(w in q for w in ("trend", "over time", "monthly", "daily", "weekly", "yearly")):
        kind = "line" if (x and (x in dates or pd.api.types.is_datetime64_any_dtype(df[x]))) else "bar"
    elif any(w in q for w in ("variation", "variability", "spread across", "distribution by")) and x and y:
        kind = "box"
    else:
        kind = chart.get("type", "bar") if chart else "bar"

    # Ensure chart specs are valid for the chosen type.
    if kind == "scatter":
        if len(numeric) < 2:
            return None
        x, y = numeric[0], numeric[1]
    elif kind in {"histogram", "box"}:
        if not numeric:
            return None
        y = y if y in numeric else numeric[0]
        if kind == "box":
            x = x if x in categorical else (categorical[0] if categorical else None)
            if not x:
                kind = "histogram"
        x = None if kind == "histogram" else x
    else:
        if not x:
            x = categorical[0] if categorical else (dates[0] if dates else None)
        if not x:
            return None
        if y not in numeric:
            y = numeric[0] if numeric else None

    base = chart or {"title": question, "aggregation": "mean", "group_by": None}
    return {"title": question, "type": kind, "x": x, "y": y,
            "aggregation": base.get("aggregation", "mean"),
            "group_by": base.get("group_by") if base.get("group_by") in df.columns else None}


def create_dashboard_plan(df, requirements, ask_gemini):
    """Ask Gemini to create one answer section for every entered business question."""
    profile = _column_profile(df)
    questions = _extract_business_questions(requirements)
    question_count = len(questions)
    prompt = f"""
You are an expert data analyst creating a dashboard directly from the user's business questions.
Return ONLY valid JSON. Do not return markdown fences or extra text.

USER REQUIREMENTS:
{requirements}

BUSINESS QUESTIONS EXTRACTED BY THE APPLICATION (preserve every question exactly):
{json.dumps(questions, ensure_ascii=False)}

DATASET PROFILE (use exact column names only):
{json.dumps(profile, ensure_ascii=False)}

Return this JSON structure:
{{
  "dashboard_title": "short title",
  "summary": "short summary",
  "question_sections": [
    {{
      "question": "exact original business question",
      "status": "supported or unsupported",
      "answer_type": "chart or metric or table or unsupported",
      "answer_text": "brief explanation of how this question is answered or why it is unsupported",
      "metric": {{"label": "KPI label", "column": "exact column or *", "aggregation": "count|sum|mean|median|min|max|nunique"}},
      "chart": {{"title": "question-specific chart title", "type": "bar|line|pie|histogram|scatter|box", "x": "exact column or null", "y": "exact numeric column or null", "aggregation": "sum|mean|count", "group_by": "exact column or null"}}
    }}
  ],
  "filters": ["exact column name"]
}}

STRICT RULES:
- Return exactly {question_count} question_sections, one for EACH extracted question, in the same order.
- Copy each question into its section's question field without changing its meaning.
- Do NOT replace the user's questions with generic or standard dashboard topics.
- Every supported question must have its own answer section.
- A section may contain a KPI, a chart, or BOTH when both add useful information. Do not force a KPI or chart when it does not answer the question.
- For a single-number question, provide a KPI. For comparison/distribution/relationship questions, provide a chart. For questions asking highest/lowest/top/bottom, provide a ranked chart or table AND a KPI only if a useful single value can be calculated.
- Do not use generic or predefined chart headings. The application will use the exact original business question as the section and chart heading.
- Use unsupported only if the dataset cannot answer the question; explain the missing field.
- For chart, provide a valid chart object using exact dataset columns. Scatter needs two numeric columns; histogram/box needs a numeric column; bar/line/pie needs a category/date x column.
- For metric, provide a valid metric object. Use column '*' for row count.
- Never invent columns, values, dates, sales, revenue, profit or business meanings.
- If estimated profit is requested and both target_price and unit_cost exist, use target_price minus unit_cost only if the chart can be derived; do not claim it is actual realized profit.
- Use only columns in the dataset profile. Filters should be relevant and use exact column names.
- Do not impose a maximum number of questions or charts. The output count must match the question count.
"""
    response = ask_gemini(prompt)
    if not response or response.startswith("Gemini API Error") or response.startswith("Gemini models could not"):
        raise RuntimeError(response or "Gemini returned an empty response.")
    plan = _clean_json_response(response)
    return validate_dashboard_plan(plan, df, questions)


def validate_dashboard_plan(plan, df, questions=None):
    if not isinstance(plan, dict):
        raise ValueError("Dashboard plan must be a JSON object.")
    questions = questions or []
    raw_sections = plan.get("question_sections", [])
    sections = []
    for index, question in enumerate(questions):
        raw = raw_sections[index] if index < len(raw_sections) and isinstance(raw_sections[index], dict) else {}
        # The original user question is authoritative; never use an AI-generated generic title.
        metric = _validate_metric(raw.get("kpi") or raw.get("metric"), df)
        chart = _validate_chart(raw.get("chart"), df)
        if chart:
            chart = _auto_chart_type(question, chart, df)
        else:
            chart = None
        status = str(raw.get("status", "supported")).lower()
        if metric or chart:
            status = "supported"
        else:
            status = "unsupported"
        if chart:
            chart["title"] = question
        sections.append({
            "question": question,
            "status": status,
            "answer_text": str(raw.get("answer_text", ""))[:500],
            "metric": metric,
            "chart": chart,
            "table": str(raw.get("table", ""))[:300],
        })

    # Backward-compatible fallback for a plain-text request without extracted questions.
    metrics = []
    for item in plan.get("metrics", [])[:8]:
        metric = _validate_metric(item, df)
        if metric:
            metrics.append(metric)
    charts = []
    for item in plan.get("charts", []):
        chart = _validate_chart(item, df)
        if chart:
            charts.append(chart)

    if not sections and not metrics and not charts:
        raise ValueError("No business questions could be mapped to the dataset. Check your questions and column names.")
    return {
        "dashboard_title": str(plan.get("dashboard_title", "Your Custom Dashboard"))[:100],
        "summary": str(plan.get("summary", ""))[:500],
        "question_sections": sections,
        "metrics": metrics,
        "charts": charts,
        "filters": [c for c in plan.get("filters", []) if c in df.columns][:6],
    }


def _metric_value(df, metric):
    col, agg = metric["column"], metric["aggregation"]
    if agg == "count":
        return len(df) if col == "*" else int(df[col].count())
    series = df[col].dropna()
    if series.empty:
        return "N/A"
    value = {
        "sum": series.sum, "mean": series.mean, "median": series.median,
        "min": series.min, "max": series.max, "nunique": lambda: series.nunique(),
    }[agg]()
    return f"{value:,.2f}" if isinstance(value, (int, float)) and agg != "nunique" else f"{value:,}" if isinstance(value, (int, float)) else str(value)


def _render_chart(data, spec, index):
    kind, x, y, title = spec["type"], spec["x"], spec["y"], spec["title"]
    if data.empty:
        st.info(f"No data available for {title}.")
        return
    if kind in {"bar", "line", "pie"}:
        if y and spec["aggregation"] != "count":
            grouped = data.groupby(x, dropna=False)[y]
            plot_df = getattr(grouped, spec["aggregation"])().reset_index()
            value_col = y
        else:
            plot_df = data.groupby(x, dropna=False).size().reset_index(name="Record Count")
            value_col = "Record Count"
        if kind == "bar":
            fig = px.bar(plot_df, x=x, y=value_col, title=title)
        elif kind == "line":
            fig = px.line(plot_df, x=x, y=value_col, markers=True, title=title)
        else:
            fig = px.pie(plot_df, names=x, values=value_col, title=title, hole=0.35)
    elif kind == "histogram":
        fig = px.histogram(data, x=y, title=title, marginal="box")
    elif kind == "scatter":
        fig = px.scatter(data, x=x, y=y, color=spec["group_by"], title=title)
    else:
        fig = px.box(data, x=spec["group_by"], y=y, title=title, points="outliers")
    st.plotly_chart(fig, use_container_width=True, key=f"req_dashboard_chart_{index}")


def render_requirement_dashboard(df, requirements, ask_gemini):
    st.header("Build My Dashboard")
    st.write("Charts are selected automatically from the meaning of each saved business question and the available dataset columns.")
    request = requirements or ""
    with st.form("dashboard_requirement_form"):
        request = st.text_area(
            "Business requirements received from the previous page",
            value=request,
            height=150,
            help="Each saved business question receives an automatically selected KPI, chart or explanation.",
        )
        submitted = st.form_submit_button("Generate My Dashboard", type="primary", use_container_width=True)

    if submitted:
        if not request.strip():
            st.warning("Please save your business questions first.")
        else:
            with st.spinner("Analyzing questions and selecting suitable visualizations..."):
                try:
                    plan = create_dashboard_plan(df, request.strip(), ask_gemini)
                    st.session_state["requirement_dashboard_plan"] = plan
                    st.session_state["requirement_dashboard_request"] = request.strip()
                except Exception as exc:
                    st.error(f"Could not generate the dashboard: {exc}")
                    st.session_state.pop("requirement_dashboard_plan", None)

    plan = st.session_state.get("requirement_dashboard_plan")
    if not plan:
        st.info("Save your business questions, then select Generate My Dashboard.")
        return

    st.subheader(plan["dashboard_title"])
    if plan["summary"]:
        st.caption(plan["summary"])

    # Filters are rendered before the question cards and affect every result.
    filtered = df.copy()
    filters = plan.get("filters", [])
    if filters:
        st.subheader("Dashboard Filters")
        filter_cols = st.columns(min(len(filters), 3))
        for i, col_name in enumerate(filters):
            values = filtered[col_name].dropna().astype(str).unique().tolist()
            if len(values) <= 100:
                with filter_cols[i % len(filter_cols)]:
                    selected = st.multiselect(f"{col_name}", values, default=values, key=f"req_dashboard_filter_{col_name}")
                filtered = filtered[filtered[col_name].astype(str).isin(selected)] if selected else filtered.iloc[0:0]

    # Divider 1: separates filters from the analysis area.
    st.divider()
    if filtered.empty:
        st.warning("No rows match the selected filters.")
        return

    sections = plan.get("question_sections", [])
    if sections:
        supported = sum(section["status"] == "supported" for section in sections)
        st.caption(f"Question coverage: {supported} of {len(sections)} questions mapped to dataset-backed answers.")
        for start_idx in range(0, len(sections), 2):
            cols = st.columns(2, gap="large")
            for offset, col in enumerate(cols):
                idx = start_idx + offset
                if idx >= len(sections):
                    continue
                section = sections[idx]
                with col:
                    with st.container(border=True):
                        st.markdown(f"#### {idx + 1}. {section['question']}")
                        if section["status"] != "supported":
                            st.warning(section["answer_text"] or "This question cannot be answered using the available dataset columns.")
                        else:
                            if section.get("metric"):
                                st.metric(section["metric"]["label"], _metric_value(filtered, section["metric"]))
                            if section.get("answer_text"):
                                st.caption(section["answer_text"])
                            if section.get("chart"):
                                _render_chart(filtered, section["chart"], idx + 1)
                            if section.get("table"):
                                st.info(section["table"])
                            if not section.get("metric") and not section.get("chart") and not section.get("table"):
                                st.info("No suitable KPI or chart could be inferred. Please clarify the question or required dataset field.")

    # Divider 2: separates the question-led dashboard from the supporting data.
    st.divider()
    with st.expander("View data used in this dashboard"):
        st.caption(f"{len(filtered):,} rows × {filtered.shape[1]} columns")
        st.dataframe(filtered.head(100), use_container_width=True)
    plan_json = json.dumps(plan, indent=2, ensure_ascii=False)
    st.download_button("Download Dashboard Configuration (JSON)", data=plan_json,
                       file_name="dashboard_configuration.json", mime="application/json")
