
import pandas as pd
import numpy as np


def build_dataset_context(df):

    # 1. Basic dataset information
    total_rows = len(df)
    total_columns = len(df.columns)

    # 2. Missing values
    missing_values = df.isnull().sum()

    # 3. Duplicate records
    duplicate_count = int(df.duplicated().sum())

    # 4. Numerical analysis
    numeric_df = df.select_dtypes(include="number")

    if not numeric_df.empty:

        numerical_summary = numeric_df.describe().round(2).to_string()

        mean_values = numeric_df.mean().round(2).to_string()

        median_values = numeric_df.median().round(2).to_string()

    else:
        numerical_summary = "No numerical columns found."
        mean_values = "No numerical columns found."
        median_values = "No numerical columns found."

    # 5. Categorical analysis
    categorical_df = df.select_dtypes(
        exclude="number"
    )

    categorical_summary = []

    for column in categorical_df.columns:

        top_values = (
            categorical_df[column]
            .value_counts()
            .head(10)
            .to_string()
        )

        categorical_summary.append(
            f"\nColumn: {column}\n{top_values}"
        )

    # 6. Correlation analysis
    if numeric_df.shape[1] >= 2:
        correlation = numeric_df.corr().round(2).to_string()
    else:
        correlation = "Not enough numerical columns."

    # 7. Missing-value report
    missing_report = missing_values.to_string()

    # 8. Create complete context
    dataset_context = f"""
    DATASET ANALYSIS REPORT

    Total Rows: {total_rows}

    Total Columns: {total_columns}

    Column Names:
    {df.columns.tolist()}

    Data Types:
    {df.dtypes.to_string()}

    Missing Values:
    {missing_report}

    Duplicate Rows:
    {duplicate_count}

    Numerical Descriptive Statistics:
    {numerical_summary}

    Mean Values:
    {mean_values}

    Median Values:
    {median_values}

    Categorical Column Analysis:
    {' '.join(categorical_summary)}

    Correlation Analysis:
    {correlation}

    First 10 Records:
    {df.head(10).to_string(index=False)}
    """

    return dataset_context
