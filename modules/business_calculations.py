
import pandas as pd


def calculate_product_metrics(df):

    required_columns = [
        "product_name",
        "unit_cost",
        "target_price"
    ]

    # Check required columns
    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        return "Required columns are missing: " + ", ".join(missing)

    # Convert values to numeric
    data = df.copy()

    data["unit_cost"] = pd.to_numeric(
        data["unit_cost"], errors="coerce"
    )

    data["target_price"] = pd.to_numeric(
        data["target_price"], errors="coerce"
    )

    data = data.dropna(
        subset=["unit_cost", "target_price"]
    )

    if data.empty:
        return "No valid product price data found."

    # Calculate potential profit
    data["potential_profit"] = (
        data["target_price"] - data["unit_cost"]
    )

    # Calculate potential profit margin
    data["profit_margin"] = (
        data["potential_profit"]
        / data["target_price"].replace(0, float("nan"))
    ) * 100

    # Highest target price
    highest = data.loc[data["target_price"].idxmax()]

    # Lowest target price
    lowest = data.loc[data["target_price"].idxmin()]

    # Average values
    average_price = data["target_price"].mean()
    average_cost = data["unit_cost"].mean()
    average_profit = data["potential_profit"].mean()

    # Create report
    report = f"""
EXACT BUSINESS CALCULATION REPORT

HIGHEST PRICED PRODUCT

Product: {highest['product_name']}
Target Price: ${highest['target_price']:,.2f}
Unit Cost: ${highest['unit_cost']:,.2f}
Potential Profit: ${highest['potential_profit']:,.2f}
Potential Profit Margin: {highest['profit_margin']:.2f}%

LOWEST PRICED PRODUCT

Product: {lowest['product_name']}
Target Price: ${lowest['target_price']:,.2f}
Unit Cost: ${lowest['unit_cost']:,.2f}

AVERAGE BUSINESS METRICS

Average Target Price: ${average_price:,.2f}
Average Unit Cost: ${average_cost:,.2f}
Average Potential Profit: ${average_profit:,.2f}

NOTE:
These are potential figures based on target_price
and unit_cost, not confirmed actual profits.
"""

    return report
