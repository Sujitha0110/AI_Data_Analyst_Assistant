
import streamlit as st
import pandas as pd


def render_data_cleaning(df):
    st.title("Data Cleaning")
    st.write("Identify and handle missing values and duplicate records.")

    if df is None or df.empty:
        st.warning("Please upload a dataset first.")
        return df

    # Keep the original dataset unchanged
    if "original_df" not in st.session_state:
        st.session_state["original_df"] = df.copy()

    if "cleaned_df" not in st.session_state:
        st.session_state["cleaned_df"] = df.copy()

    current_df = st.session_state["cleaned_df"].copy()

    st.subheader("1. Data Quality Before Cleaning")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Rows", len(current_df))

    with col2:
        st.metric("Missing Values", int(current_df.isnull().sum().sum()))

    with col3:
        st.metric("Duplicate Rows", int(current_df.duplicated().sum()))

    missing_summary = pd.DataFrame({
        "Column": current_df.columns,
        "Missing Values": current_df.isnull().sum().values,
        "Missing Percentage": (
            current_df.isnull().mean().values * 100
        ).round(2)
    })

    st.subheader("Missing Value Summary")
    st.dataframe(missing_summary, use_container_width=True)

    # Cleaning options
    st.subheader("2. Choose Cleaning Methods")

    missing_method = st.selectbox(
        "How do you want to handle missing values?",
        [
            "Keep missing values",
            "Remove rows with missing values",
            "Fill numerical values with Mean",
            "Fill numerical values with Median",
            "Fill values with Mode"
        ]
    )

    remove_duplicates = st.checkbox(
        "Remove duplicate rows",
        value=False
    )

    if st.button("Apply Data Cleaning", type="primary"):

        cleaned = current_df.copy()

        # Handle missing values
        if missing_method == "Remove rows with missing values":
            cleaned = cleaned.dropna()

        elif missing_method == "Fill numerical values with Mean":
            numeric_columns = cleaned.select_dtypes(
                include="number"
            ).columns

            for column in numeric_columns:
                if cleaned[column].isnull().any():
                    cleaned[column] = cleaned[column].fillna(
                        cleaned[column].mean()
                    )

        elif missing_method == "Fill numerical values with Median":
            numeric_columns = cleaned.select_dtypes(
                include="number"
            ).columns

            for column in numeric_columns:
                if cleaned[column].isnull().any():
                    cleaned[column] = cleaned[column].fillna(
                        cleaned[column].median()
                    )

        elif missing_method == "Fill values with Mode":
            for column in cleaned.columns:
                if cleaned[column].isnull().any():
                    modes = cleaned[column].mode(dropna=True)

                    if not modes.empty:
                        cleaned[column] = cleaned[column].fillna(
                            modes.iloc[0]
                        )

        # Remove duplicates
        if remove_duplicates:
            cleaned = cleaned.drop_duplicates()

        st.session_state["cleaned_df"] = cleaned

        # Update the active dataset used by the other pages
        st.session_state["df"] = cleaned.copy()

        st.success("Data cleaning completed successfully!")

        st.rerun()

    # Show cleaned dataset
    cleaned_df = st.session_state["cleaned_df"]

    st.divider()
    st.subheader("3. Data Quality After Cleaning")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Remaining Rows",
            len(cleaned_df),
            delta=len(cleaned_df) - len(current_df)
        )

    with col2:
        st.metric(
            "Remaining Missing Values",
            int(cleaned_df.isnull().sum().sum())
        )

    with col3:
        st.metric(
            "Remaining Duplicate Rows",
            int(cleaned_df.duplicated().sum())
        )

    st.subheader("Cleaned Dataset")
    st.dataframe(cleaned_df, use_container_width=True)

    # Download cleaned dataset
    csv_data = cleaned_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Cleaned CSV",
        data=csv_data,
        file_name="cleaned_dataset.csv",
        mime="text/csv"
    )

    if st.button("Reset to Original Dataset"):
        original = st.session_state["original_df"].copy()
        st.session_state["cleaned_df"] = original
        st.session_state["df"] = original.copy()
        st.rerun()

    return cleaned_df
