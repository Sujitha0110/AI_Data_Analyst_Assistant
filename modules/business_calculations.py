
import pandas as pd


def calculate_product_metrics(df):
    """
    Calculate product-level business metrics.

    Returns a copy of the dataset with additional
    calculated columns wherever the required fields exist.
    """

    if df is None or df.empty:
        return df.copy() if df is not None else pd.DataFrame()

    result = df.copy()

    # Normalize column names for matching
    column_map = {
        str(col).strip().lower().replace(" ", "_"): col
        for col in result.columns
    }

    # Identify product cost and target price columns
    cost_col = next(
        (column_map[c] for c in
         ["unit_cost", "cost_price", "product_cost"]
         if c in column_map),
        None
    )

    price_col = next(
        (column_map[c] for c in
         ["target_price", "selling_price", "unit_price"]
         if c in column_map),
        None
    )

    # Convert identified columns to numeric values
    if cost_col:
        result[cost_col] = pd.to_numeric(
            result[cost_col], errors="coerce"
        )

    if price_col:
        result[price_col] = pd.to_numeric(
            result[price_col], errors="coerce"
        )

    # Calculate estimated profit per product
    if cost_col and price_col:
        result["estimated_profit"] = (
            result[price_col] - result[cost_col]
        )

        # Calculate estimated profit margin
        result["estimated_profit_margin"] = (
            result["estimated_profit"]
            .div(result[price_col].where(result[price_col] != 0))
            * 100
        ).round(2)

        # Identify profitable and loss-making products
        result["profit_status"] = result[
            "estimated_profit"
        ].apply(
            lambda x: (
                "Profitable" if x > 0
                else "Loss" if x < 0
                else "Break-even" if pd.notna(x)
                else "Unknown"
            )
        )

    return result
