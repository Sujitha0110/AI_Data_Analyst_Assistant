# ============================================================
# AI DATA ANALYST ASSISTANT
# Main Streamlit Application
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

from modules.gemini_assistant import ask_gemini
from modules.data_analyzer import build_dataset_context
from modules.business_calculations import calculate_product_metrics
from modules.category_analysis import analyze_categories
from modules.dashboard_generator import render_requirement_dashboard

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Data Analyst Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. SESSION STATE INITIALIZATION
# ============================================================

if "df" not in st.session_state:
    st.session_state["df"] = None

if "filename" not in st.session_state:
    st.session_state["filename"] = None

# ============================================================
# 3. CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --app-bg: #f4f7fb;
        --surface: #ffffff;
        --ink: #172033;
        --muted: #68758a;
        --line: #e5eaf2;
        --accent: #5b5ce2;
        --accent-soft: #eeefff;
    }

    .stApp { background: var(--app-bg); color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(244,247,251,.88); }
    [data-testid="stSidebar"] {
        background: #111a2e;
        border-right: 1px solid #26334b;
    }
    [data-testid="stSidebar"] * { color: #e8edfa; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label { color: #d5def0; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { color: #ffffff; }
    [data-testid="stSidebar"] hr { border-color: #34415a; }

    .main-title {
        font-size: 30px;
        line-height: 1.2;
        font-weight: 800;
        letter-spacing: -0.8px;
        color: #172033;
        margin: 0 0 4px 0;
    }
    .sub-title { font-size: 14px; color: #68758a; margin-bottom: 12px; }
    .page-eyebrow {
        color: var(--accent); font-size: 11px; font-weight: 800;
        letter-spacing: 1.4px; text-transform: uppercase;
    }
    .hero-panel {
        background: linear-gradient(120deg, #222c55 0%, #5556c9 58%, #7775ec 100%);
        border-radius: 18px; padding: 26px 28px; color: #fff;
        box-shadow: 0 10px 28px rgba(42,49,110,.14); margin: 8px 0 22px 0;
    }
    .hero-panel h2 { color: #fff; margin: 0 0 8px 0; font-size: 27px; }
    .hero-panel p { color: #e4e7ff; margin: 0; font-size: 14px; }
    div[data-testid="stMetric"] {
        background: var(--surface); border: 1px solid var(--line);
        padding: 16px 18px; border-radius: 14px;
        box-shadow: 0 3px 12px rgba(25,40,75,.035);
    }
    div[data-testid="stMetricLabel"] { color: var(--muted); font-weight: 600; }
    div[data-testid="stMetricValue"] { color: var(--ink); font-weight: 800; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--line); border-radius: 14px;
    }
    div.stButton > button, div.stDownloadButton > button,
    [data-testid="stFormSubmitButton"] > button {
        border-radius: 10px; font-weight: 650; min-height: 42px;
    }
    div.stButton > button[kind="primary"],
    [data-testid="stFormSubmitButton"] > button[kind="primary"] {
        background: var(--accent); border-color: var(--accent);
    }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid var(--line); border-radius: 12px; overflow: hidden;
    }
    [data-testid="stExpander"] { background: #fff; border: 1px solid var(--line); border-radius: 12px; }
    h1, h2, h3 { letter-spacing: -.35px; color: #172033; }
    hr { border-color: var(--line); }
    .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 4. APPLICATION HEADER
# ============================================================

st.markdown(
    """
    <div class="page-eyebrow">ANALYTICS WORKSPACE</div>
    <div class="main-title">📊 AI Data Analyst Assistant</div>
    <div class="sub-title">Turn your dataset and business questions into clear, interactive insights.</div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 5. SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("🧭 Navigation")

page = st.sidebar.radio(
    "Choose a section",
    [
        "Home",
        "Dataset Upload",
        "Data Analysis",
        "Business Requirement Questions",
        "Build My Dashboard",
        "AI Business Insights"
    ]
)

st.sidebar.divider()

if st.session_state["df"] is not None:

    st.sidebar.success("Dataset Loaded")

    st.sidebar.write(
        f"**File:** {st.session_state['filename']}"
    )

    st.sidebar.write(
        f"**Rows:** {st.session_state['df'].shape[0]}"
    )

    st.sidebar.write(
        f"**Columns:** {st.session_state['df'].shape[1]}"
    )

else:

    st.sidebar.info("No dataset uploaded yet")

# ============================================================
# 6. HOME PAGE
# ============================================================

if page == "Home":

    st.markdown(
        """
        <div class="hero-panel">
            <div class="page-eyebrow" style="color:#c9cbff">WELCOME BACK</div>
            <h2>Your data. Your questions. Clear answers.</h2>
            <p>Upload a dataset, prepare the data, explore patterns and build a dashboard around the questions your business needs answered.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Data Processing",
            "Pandas"
        )

    with col2:
        st.metric(
            "Numerical Analysis",
            "NumPy"
        )

    with col3:
        st.metric(
            "Visualization",
            "Plotly"
        )

    st.divider()

    st.subheader("🚀 Application Features")

    feature_col1, feature_col2 = st.columns(2)

    with feature_col1:

        st.markdown(
            """
            **📁 Dataset Management**

            - CSV and Excel upload
            - Dataset preview
            - Dataset information
            - Data validation

            **📊 Data Analysis**

            - Descriptive statistics
            - Missing-value analysis
            - Duplicate detection
            - Correlation analysis
            """
        )

    with feature_col2:

        st.markdown(
            """
            **📈 Interactive Visualizations**

            - Bar charts
            - Line charts
            - Pie charts
            - Histograms
            - Scatter plots
            - Box plots

            **📥 Export**

            - Download analyzed dataset
            """
        )

    st.divider()

    if st.session_state["df"] is not None:

        st.success(
            f"Your dataset {st.session_state['filename']} is ready for analysis."
        )

    else:

        st.info(
            "Start by opening Dataset Upload from the sidebar."
        )

# ============================================================
# 7. DATASET UPLOAD PAGE
# ============================================================

elif page == "Dataset Upload":

    st.header("📁 Upload Your Dataset")

    st.write(
        "Upload a CSV or Excel file to begin your analysis."
    )

    uploaded_file = st.file_uploader(
        "Choose your dataset",
        type=["csv", "xlsx", "xls"],
        key="dataset_uploader"
    )

    if uploaded_file is not None:

        try:

            file_bytes = uploaded_file.getvalue()

            if uploaded_file.name.lower().endswith(".csv"):

                df = pd.read_csv(
                    BytesIO(file_bytes)
                )

            else:

                df = pd.read_excel(
                    BytesIO(file_bytes)
                )

            if df.empty:

                st.error("The uploaded dataset is empty.")

            else:

                st.session_state["df"] = df
                st.session_state["filename"] = uploaded_file.name

                st.success(
                    f"Successfully uploaded: {uploaded_file.name}"
                )

        except Exception as e:

            st.error(
                f"Unable to read the uploaded dataset: {e}"
            )

    # Retrieve the saved dataset

    if st.session_state["df"] is not None:

        df = st.session_state["df"]

        st.divider()

        st.subheader("📋 Dataset Preview")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

        st.subheader("📊 Dataset Overview")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Rows",
                df.shape[0]
            )

        with col2:

            st.metric(
                "Total Columns",
                df.shape[1]
            )

        with col3:

            st.metric(
                "Missing Values",
                int(df.isnull().sum().sum())
            )

        st.subheader("📌 Column Information")

        column_info = pd.DataFrame({

            "Column Name": df.columns,

            "Data Type": df.dtypes.astype(str).values,

            "Missing Values": df.isnull().sum().values,

            "Unique Values": df.nunique().values

        })

        st.dataframe(
            column_info,
            use_container_width=True
        )

        st.divider()

        # Download dataset

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Dataset as CSV",
            data=csv_data,
            file_name="uploaded_dataset.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "Please upload a dataset to see its preview."
        )

# ============================================================
# 8. DATA ANALYSIS PAGE
# ============================================================

elif page == "Data Analysis":

    st.header("📊 Data Analysis Dashboard")

    if st.session_state["df"] is None:

        st.warning(
            "Please upload a dataset first using Dataset Upload."
        )

    else:

        df = st.session_state["df"]

        st.success(
            f"Analyzing: {st.session_state['filename']}"
        )

        # ----------------------------------------------------
        # KPI CARDS
        # ----------------------------------------------------

        numeric_df = df.select_dtypes(include="number")

        categorical_df = df.select_dtypes(
            exclude="number"
        )

        total_rows = df.shape[0]

        total_columns = df.shape[1]

        missing_values = int(
            df.isnull().sum().sum()
        )

        duplicate_rows = int(
            df.duplicated().sum()
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Records",
            total_rows
        )

        col2.metric(
            "Total Columns",
            total_columns
        )

        col3.metric(
            "Missing Values",
            missing_values
        )

        col4.metric(
            "Duplicate Rows",
            duplicate_rows
        )

        st.divider()

        col5, col6 = st.columns(2)

        col5.metric(
            "Numerical Columns",
            numeric_df.shape[1]
        )

        col6.metric(
            "Other Columns",
            categorical_df.shape[1]
        )

        st.divider()

        # ----------------------------------------------------
        # DATASET PREVIEW
        # ----------------------------------------------------

        st.subheader("📋 Dataset Preview")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

        # ----------------------------------------------------
        # DATASET INFORMATION
        # ----------------------------------------------------

        st.subheader("🔍 Dataset Information")

        info_df = pd.DataFrame({

            "Column Name": df.columns,

            "Data Type": df.dtypes.astype(str).values,

            "Missing Values": df.isnull().sum().values,

            "Missing Percentage": (
                df.isnull().mean().values * 100
            ).round(2),

            "Unique Values": df.nunique().values

        })

        st.dataframe(
            info_df,
            use_container_width=True
        )

        # ----------------------------------------------------
        # DESCRIPTIVE STATISTICS
        # ----------------------------------------------------

        st.subheader("📈 Descriptive Statistics")

        if not numeric_df.empty:

            st.dataframe(
                numeric_df.describe().T,
                use_container_width=True
            )

        else:

            st.info(
                "No numerical columns are available."
            )

        # ----------------------------------------------------
        # MEAN, MEDIAN AND MODE
        # ----------------------------------------------------

        st.subheader("📊 Statistical Measures")

        if not numeric_df.empty:

            statistics_df = pd.DataFrame({

                "Mean": numeric_df.mean(),

                "Median": numeric_df.median(),

                "Mode": numeric_df.mode().iloc[0],

                "Minimum": numeric_df.min(),

                "Maximum": numeric_df.max(),

                "Standard Deviation": numeric_df.std()

            })

            st.dataframe(
                statistics_df,
                use_container_width=True
            )

        else:

            st.info(
                "Statistical measures require numerical columns."
            )

        # ----------------------------------------------------
        # MISSING VALUE ANALYSIS
        # ----------------------------------------------------

        st.subheader("⚠️ Missing Value Analysis")

        missing_df = pd.DataFrame({

            "Column": df.columns,

            "Missing Count": df.isnull().sum().values,

            "Missing Percentage": (
                df.isnull().mean().values * 100
            ).round(2)

        })

        st.dataframe(
            missing_df,
            use_container_width=True
        )

        # Missing value chart

        missing_chart_df = missing_df[
            missing_df["Missing Count"] > 0
        ]

        if not missing_chart_df.empty:

            fig_missing = px.bar(
                missing_chart_df,
                x="Column",
                y="Missing Count",
                title="Missing Values by Column",
                text="Missing Count"
            )

            st.plotly_chart(
                fig_missing,
                use_container_width=True
            )

        else:

            st.success(
                "No missing values found in the dataset."
            )

        # ----------------------------------------------------
        # DUPLICATE ANALYSIS
        # ----------------------------------------------------

        st.subheader("🔁 Duplicate Record Analysis")

        if duplicate_rows > 0:

            st.warning(
                f"{duplicate_rows} duplicate rows detected."
            )

            st.dataframe(
                df[df.duplicated(keep=False)],
                use_container_width=True
            )

        else:

            st.success(
                "No duplicate rows found."
            )

        # ----------------------------------------------------
        # CORRELATION ANALYSIS
        # ----------------------------------------------------

        st.subheader("🔥 Correlation Analysis")

        if numeric_df.shape[1] >= 2:

            correlation = numeric_df.corr()

            fig_corr = px.imshow(
                correlation,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                title="Numerical Column Correlation"
            )

            st.plotly_chart(
                fig_corr,
                use_container_width=True
            )

            st.dataframe(
                correlation,
                use_container_width=True
            )

        else:

            st.info(
                "At least two numerical columns are required for correlation analysis."
            )

# ============================================================
# 9. INTERACTIVE VISUALIZATIONS PAGE
# ============================================================

elif page == "Visualizations":

    st.header("📈 Interactive Data Visualizations")

    if st.session_state["df"] is None:

        st.warning(
            "Please upload a dataset first."
        )

    else:

        df = st.session_state["df"].copy()

        st.success(
            f"Dataset: {st.session_state['filename']}"
        )

        # ----------------------------------------------------
        # DATA FILTER
        # ----------------------------------------------------

        st.subheader("🔎 Filter Your Dataset")

        categorical_columns = df.select_dtypes(
            exclude="number"
        ).columns.tolist()

        filtered_df = df.copy()

        if categorical_columns:

            filter_column = st.selectbox(
                "Choose a column to filter",
                ["No Filter"] + categorical_columns
            )

            if filter_column != "No Filter":

                unique_values = (
                    df[filter_column]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

                selected_values = st.multiselect(
                    "Select values",
                    unique_values
                )

                if selected_values:

                    filtered_df = df[
                        df[filter_column]
                        .astype(str)
                        .isin(selected_values)
                    ]

        st.write(
            f"Filtered records: {len(filtered_df)}"
        )

        st.divider()

        # ----------------------------------------------------
        # CHART SELECTION
        # ----------------------------------------------------

        st.subheader("🎨 Create Your Chart")

        chart_type = st.selectbox(
            "Select Chart Type",
            [
                "Bar Chart",
                "Line Chart",
                "Pie Chart",
                "Histogram",
                "Scatter Plot",
                "Box Plot"
            ]
        )

        all_columns = filtered_df.columns.tolist()

        numeric_columns = filtered_df.select_dtypes(
            include="number"
        ).columns.tolist()

        if not all_columns:

            st.warning(
                "No columns available after filtering."
            )

        elif chart_type == "Histogram":

            if numeric_columns:

                x_col = st.selectbox(
                    "Select Numerical Column",
                    numeric_columns
                )

                fig = px.histogram(
                    filtered_df,
                    x=x_col,
                    title=f"Distribution of {x_col}",
                    marginal="box"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:

                st.warning(
                    "Histogram requires a numerical column."
                )

        elif chart_type == "Scatter Plot":

            if len(numeric_columns) >= 2:

                col1, col2 = st.columns(2)

                with col1:

                    x_col = st.selectbox(
                        "Select X Axis",
                        numeric_columns
                    )

                with col2:

                    y_options = [
                        col for col in numeric_columns
                        if col != x_col
                    ]

                    y_col = st.selectbox(
                        "Select Y Axis",
                        y_options
                    )

                fig = px.scatter(
                    filtered_df,
                    x=x_col,
                    y=y_col,
                    title=f"{y_col} vs {x_col}"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:

                st.warning(
                    "Scatter plot requires at least two numerical columns."
                )

        elif chart_type == "Pie Chart":

            if all_columns:

                name_options = [
                    col for col in all_columns
                    if col not in numeric_columns
                ]

                if name_options:

                    names_col = st.selectbox(
                        "Select Category Column",
                        name_options
                    )

                    value_options = [
                        "Count"
                    ] + numeric_columns

                    values_col = st.selectbox(
                        "Select Values",
                        value_options
                    )

                    if values_col == "Count":

                        pie_df = (
                            filtered_df[names_col]
                            .fillna("Missing")
                            .value_counts()
                            .reset_index()
                        )

                        pie_df.columns = [
                            names_col,
                            "Count"
                        ]

                        fig = px.pie(
                            pie_df,
                            names=names_col,
                            values="Count",
                            title=f"Distribution of {names_col}"
                        )

                    else:

                        fig = px.pie(
                            filtered_df,
                            names=names_col,
                            values=values_col,
                            title=f"{values_col} by {names_col}"
                        )

                    st.plotly_chart(
                        fig,
                    )    
                
        # ----------------------------------------------------
        # BAR CHART
        # ----------------------------------------------------

        elif chart_type == "Bar Chart":

            if all_columns:

                x_col = st.selectbox(
                    "Select X Axis Column",
                    all_columns,
                    key="bar_x"
                )

                y_options = ["Count"] + numeric_columns

                y_col = st.selectbox(
                    "Select Y Axis Column",
                    y_options,
                    key="bar_y"
                )

                if y_col == "Count":

                    chart_df = (
                        filtered_df.groupby(x_col, dropna=False)
                        .size()
                        .reset_index(name="Count")
                    )

                    fig = px.bar(
                        chart_df,
                        x=x_col,
                        y="Count",
                        title=f"Count by {x_col}",
                        color=x_col
                    )

                else:

                    chart_df = (
                        filtered_df.groupby(x_col, dropna=False)[y_col]
                        .mean()
                        .reset_index()
                    )

                    fig = px.bar(
                        chart_df,
                        x=x_col,
                        y=y_col,
                        title=f"Average {y_col} by {x_col}",
                        color=x_col
                    )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        # ----------------------------------------------------
        # LINE CHART
        # ----------------------------------------------------

        elif chart_type == "Line Chart":

            if numeric_columns and all_columns:

                x_col = st.selectbox(
                    "Select X Axis Column",
                    all_columns,
                    key="line_x"
                )

                y_col = st.selectbox(
                    "Select Y Axis Column",
                    numeric_columns,
                    key="line_y"
                )

                line_df = filtered_df.copy()

                if pd.api.types.is_datetime64_any_dtype(
                    line_df[x_col]
                ):
                    line_df = line_df.sort_values(x_col)

                fig = px.line(
                    line_df,
                    x=x_col,
                    y=y_col,
                    markers=True,
                    title=f"{y_col} Trend by {x_col}"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:

                st.warning(
                    "Line Chart requires at least one numerical column."
                )

        # ----------------------------------------------------
        # BOX PLOT
        # ----------------------------------------------------

        elif chart_type == "Box Plot":

            if numeric_columns:

                y_col = st.selectbox(
                    "Select Numerical Column",
                    numeric_columns,
                    key="box_y"
                )

                category_options = [
                    col for col in all_columns
                    if col != y_col
                    and not pd.api.types.is_numeric_dtype(
                        filtered_df[col]
                    )
                ]

                x_col = st.selectbox(
                    "Group By Category (Optional)",
                    ["No Grouping"] + category_options,
                    key="box_x"
                )

                if x_col == "No Grouping":

                    fig = px.box(
                        filtered_df,
                        y=y_col,
                        title=f"Distribution of {y_col}",
                        points="all"
                    )

                else:

                    fig = px.box(
                        filtered_df,
                        x=x_col,
                        y=y_col,
                        color=x_col,
                        title=f"{y_col} Distribution by {x_col}",
                        points="all"
                    )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:

                st.warning(
                    "Box Plot requires at least one numerical column."
                )




# ============================================================
# 10. ASK YOUR DATA - GEMINI AI CHATBOT
# ============================================================

elif page == "Ask Your Data":

    st.header("🤖 Ask Your Data")

    st.write(
        "Ask questions about your uploaded dataset "
        "and receive AI-powered insights."
    )

    if st.session_state["df"] is None:

        st.warning(
            "Please upload a CSV or Excel dataset first."
        )

    else:

        df = st.session_state["df"]

        st.success(
            f"Connected Dataset: {st.session_state['filename']}"
        )

        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        # Generate complete dataset analysis
        business_report = calculate_product_metrics(df)
        category_report = analyze_categories(df)

        st.divider()

        st.subheader("💬 Chat with Your Dataset")

        # Clear conversation
        if st.button("🗑️ Clear Chat"):

            st.session_state["chat_history"] = []
            st.rerun()

        # Display previous messages
        for message in st.session_state["chat_history"]:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User input
        user_question = st.chat_input(
            "Ask something about your dataset..."
        )

        if user_question:

            # Save user message
            st.session_state["chat_history"].append({
                "role": "user",
                "content": user_question
            })

            with st.chat_message("user"):
                st.markdown(user_question)

            # Prepare conversation history
            conversation = ""

            for message in st.session_state["chat_history"][-8:]:

                conversation += (
                    f"\n{message['role'].upper()}: "
                    f"{message['content']}"
                )

            # Prepare Gemini prompt
            # Generate dataset analysis
            dataset_info = build_dataset_context(df)

            # Generate business calculations
            business_report = calculate_product_metrics(df)
            
            # Generate category-wise business analysis
            category_report = analyze_categories(df)

            # Prepare the prompt
            prompt = f"""
You are an expert AI Data Analyst Assistant.

Answer questions using the uploaded dataset.

IMPORTANT RULES:
1. Use the actual dataset analysis.
2. Never invent statistics.
3. Explain results in simple English.
4. Clearly distinguish observations from assumptions.

DATASET INFORMATION:

{dataset_info}

BUSINESS CALCULATION REPORT:

{business_report}

CATEGORY-WISE BUSINESS ANALYSIS:
{category_report}

USER QUESTION:

{user_question}

Provide an accurate and useful answer.
"""


            # Generate Gemini response

            with st.chat_message("assistant"):

                with st.spinner(
                    "🤖 Gemini is analyzing your dataset..."
                ):

                    try:

                        answer = ask_gemini(prompt)

                        if answer:

                            st.markdown(answer)

                            st.session_state["chat_history"].append({
                                "role": "assistant",
                                "content": answer
                            })

                        else:

                            st.warning(
                                "Gemini returned an empty response. "
                                "Please try again."
                            )

                    except Exception as e:

                        st.error(
                            f"Unable to generate response: {e}"
                        )


# ============================================================
# 11. AUTOMATIC VISUAL INSIGHTS DASHBOARD
# ============================================================

elif page == "Visual Insights":

    st.header("📊 Automatic Business Insights")

    st.write(
        "Explore your product data through six interactive "
        "business visualizations."
    )

    if st.session_state["df"] is None:

        st.warning("Please upload a dataset first.")

    else:

        df = st.session_state["df"].copy()

        # ----------------------------------------------------
        # 1. CHECK REQUIRED COLUMNS
        # ----------------------------------------------------

        required_columns = [
            "product_name",
            "product_category",
            "unit_cost",
            "target_price"
        ]

        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            st.error(
                f"Missing required columns: {missing_columns}"
            )

        else:

            # ------------------------------------------------
            # 2. DATA PREPARATION
            # ------------------------------------------------

            df["unit_cost"] = pd.to_numeric(
                df["unit_cost"], errors="coerce"
            )

            df["target_price"] = pd.to_numeric(
                df["target_price"], errors="coerce"
            )

            if "weight_kg" in df.columns:
                df["weight_kg"] = pd.to_numeric(
                    df["weight_kg"], errors="coerce"
                )

            df = df.dropna(
                subset=[
                    "product_name",
                    "product_category",
                    "unit_cost",
                    "target_price"
                ]
            ).copy()

            if df.empty:

                st.warning(
                    "No valid product data is available."
                )

            else:

                # ------------------------------------------------
                # 3. BUSINESS CALCULATIONS
                # ------------------------------------------------

                df["potential_profit"] = (
                    df["target_price"] - df["unit_cost"]
                )

                df["potential_profit_margin"] = np.where(
                    df["target_price"] != 0,
                    (
                        df["potential_profit"]
                        / df["target_price"]
                    ) * 100,
                    np.nan
                )

                st.success(
                    f"Successfully analyzed {len(df)} products."
                )

                # ------------------------------------------------
                # 4. INTERACTIVE CATEGORY FILTER
                # ------------------------------------------------

                st.subheader("🔎 Interactive Filters")

                categories = [
                    "All Categories"
                ] + sorted(
                    df["product_category"].unique().tolist()
                )

                selected_category = st.selectbox(
                    "Select Product Category",
                    categories,
                    key="visual_insights_category"
                )

                if selected_category != "All Categories":

                    df = df[
                        df["product_category"] == selected_category
                    ].copy()

                st.info(f"Showing {len(df)} products")

                # ------------------------------------------------
                # 5. KPI CARDS
                # ------------------------------------------------

                st.subheader(
                    "📌 Business Performance Overview"
                )

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Total Products", len(df))

                col2.metric(
                    "Average Target Price",
                    f"${df['target_price'].mean():,.2f}"
                )

                col3.metric(
                    "Average Unit Cost",
                    f"${df['unit_cost'].mean():,.2f}"
                )

                col4.metric(
                    "Average Potential Profit",
                    f"${df['potential_profit'].mean():,.2f}"
                )

                st.divider()

                # ------------------------------------------------
                # 6. CREATE ALL SIX CHARTS FIRST
                # ------------------------------------------------

                # BAR CHART

                category_profit = (
                    df.groupby("product_category")
                    ["potential_profit"]
                    .mean()
                    .reset_index()
                )

                fig1 = px.bar(
                    category_profit,
                    x="product_category",
                    y="potential_profit",
                    color="product_category",
                    text_auto=".2f",
                    title="Average Potential Profit by Category",
                    labels={
                        "product_category": "Product Category",
                        "potential_profit": "Average Potential Profit ($)"
                    }
                )

                # PIE CHART

                category_count = (
                    df["product_category"]
                    .value_counts()
                    .reset_index()
                )

                category_count.columns = [
                    "product_category",
                    "product_count"
                ]

                fig2 = px.pie(
                    category_count,
                    names="product_category",
                    values="product_count",
                    hole=0.4,
                    title="Product Distribution by Category"
                )

                # LINE CHART

                line_df = df.sort_values("target_price")

                fig3 = px.line(
                    line_df,
                    x="product_name",
                    y="target_price",
                    markers=True,
                    color="product_category",
                    title="Product Target Price Comparison"
                )

                # SCATTER PLOT

                size_col = None

                if "weight_kg" in df.columns:
                    if (
                        df["weight_kg"].notna().all()
                        and (df["weight_kg"] > 0).all()
                    ):
                        size_col = "weight_kg"

                scatter_args = {}

                if size_col is not None:
                    scatter_args["size"] = size_col

                fig4 = px.scatter(
                    df,
                    x="unit_cost",
                    y="target_price",
                    color="product_category",
                    hover_name="product_name",
                    title="Unit Cost vs Target Price",
                    labels={
                        "unit_cost": "Unit Cost ($)",
                        "target_price": "Target Price ($)"
                    },
                    **scatter_args
                )

                # BOX PLOT

                fig5 = px.box(
                    df,
                    x="product_category",
                    y="unit_cost",
                    color="product_category",
                    points="all",
                    title="Unit Cost Distribution by Category",
                    labels={
                        "product_category": "Product Category",
                        "unit_cost": "Unit Cost ($)"
                    }
                )

                # HISTOGRAM

                fig6 = px.histogram(
                    df,
                    x="target_price",
                    nbins=10,
                    marginal="box",
                    title="Distribution of Product Target Prices",
                    labels={
                        "target_price": "Target Price ($)"
                    }
                )

                # ------------------------------------------------
                # 7. DISPLAY SIX CHARTS WITH INDIVIDUAL HEADINGS
                # ------------------------------------------------

                st.subheader("📊 Business Visualizations")

                # ROW 1: BAR + PIE

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader(
                        "1️⃣ Category-wise Potential Profit"
                    )
                    st.plotly_chart(
                        fig1,
                        use_container_width=True,
                        key="insights_bar"
                    )

                with col2:
                    st.subheader(
                        "2️⃣ Product Category Distribution"
                    )
                    st.plotly_chart(
                        fig2,
                        use_container_width=True,
                        key="insights_pie"
                    )

                st.divider()

                # ROW 2: LINE + SCATTER

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader(
                        "3️⃣ Product-wise Target Price"
                    )
                    st.plotly_chart(
                        fig3,
                        use_container_width=True,
                        key="insights_line"
                    )

                with col2:
                    st.subheader(
                        "4️⃣ Unit Cost vs Target Price"
                    )
                    st.plotly_chart(
                        fig4,
                        use_container_width=True,
                        key="insights_scatter"
                    )

                st.divider()

                # ROW 3: BOX + HISTOGRAM

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader(
                        "5️⃣ Product Cost Distribution"
                    )
                    st.plotly_chart(
                        fig5,
                        use_container_width=True,
                        key="insights_box"
                    )

                with col2:
                    st.subheader(
                        "6️⃣ Target Price Distribution"
                    )
                    st.plotly_chart(
                        fig6,
                        use_container_width=True,
                        key="insights_histogram"
                    )

                st.divider()

                # ------------------------------------------------
                # 8. HIGHEST AND LOWEST PRICED PRODUCTS
                # ------------------------------------------------

                st.subheader("🏆 Product Price Highlights")

                highest = df.loc[df["target_price"].idxmax()]
                lowest = df.loc[df["target_price"].idxmin()]

                col1, col2 = st.columns(2)

                col1.metric(
                    "Highest Priced Product",
                    highest["product_name"],
                    f"${highest['target_price']:,.2f}"
                )

                col2.metric(
                    "Lowest Priced Product",
                    lowest["product_name"],
                    f"${lowest['target_price']:,.2f}"
                )

                st.divider()

                # ------------------------------------------------
                # 9. PROFITABILITY TABLE
                # ------------------------------------------------

                st.subheader("📋 Product Profitability Details")

                display_columns = [
                    "product_name",
                    "product_category",
                    "unit_cost",
                    "target_price",
                    "potential_profit",
                    "potential_profit_margin"
                ]

                st.dataframe(
                    df[display_columns].round(2),
                    use_container_width=True
                )

                st.divider()

                # ------------------------------------------------
                # 10. DOWNLOAD BUSINESS ANALYSIS
                # ------------------------------------------------

                st.subheader("📥 Download Business Analysis")

                csv_data = df.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    label="Download Business Insights CSV",
                    data=csv_data,
                    file_name="business_visual_insights.csv",
                    mime="text/csv"
                )


# ============================================================
# 12. AI-POWERED BUSINESS INSIGHTS
# ============================================================

elif page == "AI Business Insights":

    st.header("🤖 AI-Powered Business Insights")

    st.write(
        "Generate an intelligent business analysis report "
        "using Gemini AI and your uploaded dataset."
    )

    if st.session_state["df"] is None:

        st.warning("Please upload a dataset first.")

    else:

        df = st.session_state["df"].copy()

        st.subheader("📊 Dataset Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Rows", df.shape[0])
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Missing Values", int(df.isnull().sum().sum()))

        st.write("**Dataset Columns:**")
        st.write(", ".join(df.columns.astype(str)))

        st.divider()

        st.subheader("🧠 Generate AI Business Report")

        st.write(
            "Click the button below to let Gemini analyze "
            "your dataset and generate business insights."
        )

        if "ai_business_report" not in st.session_state:
            st.session_state["ai_business_report"] = ""

        if st.button(
            "✨ Generate AI Business Insights",
            type="primary",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Gemini AI is analyzing your dataset..."
                ):

                    # Dataset information
                    dataset_info = build_dataset_context(df)

                    # Business calculations
                    business_report = calculate_product_metrics(df)

                    # Category analysis
                    category_report = analyze_categories(df)

                    # AI prompt
                    prompt = f"""
You are an expert Business Intelligence Analyst
and AI Data Analyst.

Analyze the uploaded dataset carefully.

DATASET INFORMATION:
{dataset_info}

BUSINESS CALCULATION REPORT:
{business_report}

CATEGORY-WISE BUSINESS ANALYSIS:
{category_report}

YOUR TASK:

Generate a professional AI Business Insights Report
with the following sections:

1. EXECUTIVE SUMMARY
- Summarize the dataset.
- Explain the most important findings.

2. KEY BUSINESS OBSERVATIONS
- Identify important patterns and trends.
- Explain relationships between numerical columns.
- Highlight important category-level differences.

3. POTENTIAL RISKS
- Identify possible business risks.
- Mention unusual values or potential outliers
  only when supported by the available data.
- Explain missing data or data quality concerns.

4. BUSINESS RECOMMENDATIONS
- Provide practical recommendations.
- Suggest ways to improve business performance.
- Explain which areas need further investigation.

5. CONCLUSION
- Summarize the overall business findings.

IMPORTANT RULES:
- Use only the supplied dataset and reports.
- Never invent statistics, values, or business facts.
- Do not assume that potential profit is actual profit.
- Clearly mention when information is unavailable.
- Distinguish observations from assumptions.
- Write in clear, professional English.
- Use headings and bullet points.
"""

                    # Call existing Gemini function
                    answer = ask_gemini(prompt)

                    st.session_state["ai_business_report"] = answer

            except Exception as e:

                st.error(
                    f"Unable to generate AI insights: {e}"
                )

        # ------------------------------------------------
        # DISPLAY AI REPORT
        # ------------------------------------------------

        if st.session_state["ai_business_report"]:

            st.divider()

            st.subheader("📋 AI Business Analysis Report")

            st.markdown(
                st.session_state["ai_business_report"]
            )

            st.divider()

            # ------------------------------------------------
            # DOWNLOAD AI REPORT
            # ------------------------------------------------

            st.subheader("📥 Download AI Report")

            st.download_button(
                label="Download AI Business Report",
                data=st.session_state["ai_business_report"],
                file_name="AI_Business_Insights_Report.txt",
                mime="text/plain",
                use_container_width=True
            )

# ============================================================
# 13. BUSINESS REQUIREMENT QUESTIONS
# ============================================================

elif page == "Business Requirement Questions":

    st.header("Business Requirement Questions")
    st.write(
        "Tell us what decision you want to make with this dataset. "
        "Your answers will guide the dashboard generated in the next step."
    )

    if st.session_state["df"] is None:
        st.warning("Please upload a CSV or Excel dataset first.")
        st.info("After uploading, return here to answer the business questions.")
    else:
        df = st.session_state["df"].copy()
        all_columns = df.columns.astype(str).tolist()
        numeric_columns = df.select_dtypes(include="number").columns.astype(str).tolist()
        categorical_columns = [
            str(c) for c in df.columns
            if not pd.api.types.is_numeric_dtype(df[c])
        ]
        date_like_columns = [
            str(c) for c in df.columns
            if pd.api.types.is_datetime64_any_dtype(df[c])
            or any(word in str(c).lower() for word in ["date", "time", "month", "year"])
        ]

        st.caption(
            f"Dataset: {st.session_state.get('filename', 'Uploaded dataset')} · "
            f"{len(df):,} rows · {len(all_columns)} columns"
        )

        with st.form("business_requirement_questions_form"):
            st.subheader("1. Business objective")
            business_objective = st.text_input(
                "What is the main goal of this analysis?",
                placeholder="Example: Understand sales performance and improve revenue"
            )

            st.subheader("2. Questions you want the dashboard to answer")
            business_questions = st.text_area(
                "Enter your business questions",
                height=120,
                placeholder=(
                    "Example:\nWhich products generate the highest revenue?\n"
                    "How are sales changing each month?\nWhich categories perform best?"
                )
            )

            st.subheader("3. Metrics and KPIs")
            selected_kpis = st.multiselect(
                "Which numerical columns should be considered for KPIs?",
                options=numeric_columns,
                help="Select columns such as Revenue, Sales, Profit, Quantity or Amount."
            )

            st.subheader("4. Breakdown and comparison")
            selected_dimensions = st.multiselect(
                "Which categories should be compared or grouped?",
                options=categorical_columns,
                help="Examples: Product, Region, Department, Customer Segment or Category."
            )

            date_options = ["Not applicable"] + date_like_columns
            selected_date = st.selectbox(
                "Which column should be used for time-based trends?",
                options=date_options
            )

            st.subheader("5. Preferred visualizations")
            preferred_charts = st.multiselect(
                "Choose chart types (optional)",
                options=["Bar chart", "Line chart", "Pie chart", "Histogram", "Scatter plot", "Box plot"]
            )

            st.subheader("6. Additional requirements")
            additional_requirements = st.text_area(
                "Any filters, comparisons, audience, or other instructions?",
                height=90,
                placeholder="Example: Focus on 2026 data and prepare the dashboard for senior management."
            )

            requirements_submitted = st.form_submit_button(
                "Save Requirements and Continue",
                type="primary",
                use_container_width=True
            )

        if requirements_submitted:
            if not business_objective.strip() and not business_questions.strip():
                st.warning("Please enter a business objective or at least one business question.")
            else:
                requirement_parts = [
                    "BUSINESS OBJECTIVE:", business_objective.strip() or "Not specified",
                    "BUSINESS QUESTIONS:", business_questions.strip() or "Not specified",
                    "REQUESTED KPI COLUMNS:", ", ".join(selected_kpis) or "Let the AI choose suitable metrics",
                    "COMPARISON DIMENSIONS:", ", ".join(selected_dimensions) or "Let the AI choose suitable dimensions",
                    "TIME COLUMN:", selected_date if selected_date != "Not applicable" else "Not specified",
                    "PREFERRED CHARTS:", ", ".join(preferred_charts) or "Choose suitable chart types",
                    "ADDITIONAL REQUIREMENTS:", additional_requirements.strip() or "None"
                ]
                st.session_state["requirement_dashboard_request"] = "\n".join(requirement_parts)
                st.session_state.pop("requirement_dashboard_plan", None)
                st.success("Your business requirements have been saved.")
                st.info("Next, open Build My Dashboard to generate your customized dashboard.")

        saved_requirements = st.session_state.get("requirement_dashboard_request", "")
        if saved_requirements:
            with st.expander("Review saved business requirements", expanded=False):
                st.text(saved_requirements)

# ============================================================
# 14. REQUIREMENT-DRIVEN DYNAMIC DASHBOARD
# ============================================================

elif page == "Build My Dashboard":

    if st.session_state["df"] is None:
        st.header("Build My Dashboard")
        st.warning("Please upload a CSV or Excel dataset first.")
    else:
        render_requirement_dashboard(
            st.session_state["df"].copy(),
            st.session_state.get("requirement_dashboard_request", ""),
            ask_gemini
        )

