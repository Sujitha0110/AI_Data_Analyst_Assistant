
import pandas as pd


def analyze_categories(df):
    """
    Generate category-wise analysis for a dataset.
    Returns a text report for the AI assistant.
    """

    if df is None or df.empty:
        return "No dataset available for category analysis."

    report = []

    # Identify categorical and numerical columns
    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    numerical_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    report.append("CATEGORY-WISE BUSINESS ANALYSIS")
    report.append(f"Total records: {len(df)}")

    if not categorical_columns:
        return (
            "No categorical columns were found. "
            "Category-wise analysis is not applicable."
        )

    # Analyze each categorical column
    for column in categorical_columns:

        report.append(f"\nCategory Column: {column}")

        category_counts = (
            df[column]
            .fillna("Missing")
            .value_counts()
            .head(10)
        )

        report.append("\nCategory Counts:")
        report.append(category_counts.to_string())

        # Calculate numerical metrics for each category
        for numeric_column in numerical_columns:

            grouped = df.groupby(
                column,
                dropna=False
            )[numeric_column].agg(
                ["count", "mean", "sum", "min", "max"]
            ).round(2)

            report.append(
                f"\n{numeric_column} by {column}:"
            )

            report.append(
                grouped.head(10).to_string()
            )

    return "\n".join(report)
