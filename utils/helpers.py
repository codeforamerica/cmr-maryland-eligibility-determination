import streamlit as st
from datetime import timedelta
import pandas as pd
from utils.constants import REQUIRED_COLUMNS, WAIT_PERIODS, EXCLUDED_MISDEMEANORS, NON_CONVICTION_TERMS


def load_example_data():
    """
    Loads example data from CSV files into Pandas DataFrames and returns them as a dictionary.
    """
    try:
        return {name: pd.read_csv(f"data/{name}.csv") for name in ["parties", "cases", "charges"]}
    except Exception as e:
        print(f"Error loading example data: {e}")
        return {}


# Load example data
EXAMPLE_DATA = load_example_data()


def categorize_charges(df):
    """
    Categorizes charges based on class, disposition, statute code, and case type.
    - Identifies misdemeanors and felonies.
    - Flags non-convictions based on predefined terms.
    - Marks excluded misdemeanors based on statute codes.
    - Identifies domestic violence cases.
    """
    conditions = {
        "Charge Class": {
            "Is Misdemeanor": lambda x: x.str.contains("MISDEMEANOR", case=False, na=False),
            "Is Felony": lambda x: x.str.contains("FELONY", case=False, na=False),
        },
        "Disposition": {
            "Is Non-Conviction": lambda x: x.astype(str).str.upper().str.contains('|'.join(NON_CONVICTION_TERMS), na=False),
        },
        "Statute Code": {
            "Is Excluded Misdemeanor": lambda x: x.isin(EXCLUDED_MISDEMEANORS.keys()),
        },
        "Case Type": {
            "Is Domestic Violence": lambda x: x.str.contains("DOMESTIC VIOLENCE", case=False, na=False),
        }
    }

    for col, mappings in conditions.items():
        if col in df.columns:
            for new_col, func in mappings.items():
                df[new_col] = func(df[col])

    return df


def clean_dataframe(df):
    """Cleans column values in the DataFrame."""
    df.columns = df.columns.str.strip()

    transformations = {
        "Disposition Date": lambda x: pd.to_datetime(x.astype(str).str.strip(), errors="coerce"),
        "Case Number": lambda x: x.astype(str).str.strip(),
        "Charge Class": lambda x: x.astype(str).str.strip().str.upper(),
        "Statute Code": lambda x: x.astype(str).str.strip(),
        "Case Type": lambda x: x.astype(str).str.upper(),
    }

    for col, func in transformations.items():
        if col in df.columns:
            df[col] = func(df[col])

    return df


def check_eligibility_conditions(case_df, today):
    """
    Evaluates different eligibility conditions and determines eligibility status for a case.
    """
    latest_disposition_date = case_df["Disposition Date"].max()

    if pd.isnull(latest_disposition_date):
        return "No valid disposition date"

    # Check for excluded misdemeanors
    excluded_charges = case_df[case_df["Statute Code"].isin(
        EXCLUDED_MISDEMEANORS)]
    if not excluded_charges.empty:
        reasons = "; ".join(
            f"{row['Charge Description']} ({row['Statute Code']})"
            for _, row in excluded_charges.iterrows()
        )
        return f"❌ Not Eligible - Excluded Misdemeanor(s): {reasons}"

    # Check for non-convictions
    if case_df["Disposition"].astype(str).str.upper().str.contains('|'.join(NON_CONVICTION_TERMS), na=False).any():
        latest_non_conviction_date = case_df["Disposition Date"].max()
        final_wait_date = latest_non_conviction_date + \
            timedelta(days=WAIT_PERIODS["non_conviction"])
        return f"✅ Eligible - Non-Conviction" if today >= final_wait_date else f"⏳ Wait until {final_wait_date.strftime('%Y-%m-%d')} (Non-Conviction)"

    # Apply waiting period for misdemeanors
    final_wait_date = latest_disposition_date + \
        timedelta(days=WAIT_PERIODS["misdemeanor"])
    return f"✅ Eligible" if today >= final_wait_date else f"⏳ Wait until {final_wait_date.strftime('%Y-%m-%d')}"


def show_csv_schema(source_type="csv"):
    """Displays expected schema format for CSV or SQL sources."""
    st.subheader("📄 Expected Schema Format")

    for section in ["parties", "cases", "charges"]:
        title = section.capitalize()
        with st.expander(f"ℹ️ Expected {title} Format"):
            st.write("**Required Columns:**")
            st.code(", ".join(REQUIRED_COLUMNS[section]), language="csv")

            if source_type == "csv":
                # Show a sample row if it's a CSV source
                if section == "parties":
                    st.code(
                        """1,"DOE, JOHN",White,Male,01/01/1980,"123 MAIN ST",ANYTOWN,MD,12345,N/A""", language="csv")
                elif section == "cases":
                    st.code(
                        """1,1,"State vs DOE, JOHN",123456,District Court,"456 ELM ST",Criminal,01/01/2020,Closed,Judge Smith""", language="csv")
                elif section == "charges":
                    st.code(
                        """1,1,1,1-2345,12.345,"SAMPLE CHARGE",Misdemeanor,01/01/2020,"CITY POLICE",Guilty,02/01/2020,"Guilty",03/01/2020""", language="csv")
            else:
                st.info("Data from SQL must include the same required columns.")


def validate_schema(df: pd.DataFrame, required_cols: list, name: str) -> bool:
    """Checks if the given DataFrame has all required columns."""
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(
            f"❌ {name} data is missing required columns: {', '.join(missing)}")
        return False
    return True


def get_schema_label(data_source: str) -> str:
    return "📋 View/Hide Expected Schema Format" if data_source == "Load from MySQL" else "📋 View/Hide Expected CSV Format"


def get_source_type(data_source: str) -> str:
    return "sql" if data_source == "Load from MySQL" else "csv"
