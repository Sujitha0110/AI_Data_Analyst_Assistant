
import pandas as pd


def analyze_categories(df):

    required_columns = [
        "product_category",
        "unit_cost",
        "target_price"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        return f"Missing columns: {missing}"

    data = df.copy()

    data["unit_cost"] = pd.to_numeric(
        data["unit_cost"], errors="coerce"
    )

    data["target_price"] = pd.to_numeric(
        data["target_price"], errors="coerce"
    )

    data = data.dropna(
        subset=required_columns
    )

    if data.empty:
        return "No valid category data available."

    data["potential_profit"] = (
        data["target_price"] - data["unit_cost"]
    )

    category_report = data.groupby(
        "product_category"
    ).agg(
        product_count=("product_category", "count"),
        average_target_price=("target_price", "mean"),
        average_unit_cost=("unit_cost", "mean"),
        average_profit=("potential_profit", "mean")
    ).round(2)

    category_report = category_report.sort_values(
        by="average_target_price",
        ascending=False
    )

    return category_report.to_string()
