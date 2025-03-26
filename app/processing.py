from datetime import datetime, timedelta
import pandas as pd
from utils.constants import WAIT_PERIODS, EXCLUDED_MISDEMEANORS, REQUIRED_COLUMNS
from utils.helpers import categorize_charges, clean_dataframe, validate_schema
import streamlit as st


def clean_dataframe(df):
    """Cleans and standardizes DataFrame columns."""
    df.columns = df.columns.str.strip()
    return df


def determine_eligibility(df):
    """
    Determines eligibility for record clearance based on charge type, disposition,
    and waiting periods. Applies exclusion rules for felonies, domestic violence,
    and specific misdemeanor statutes.
    """
    today = datetime.today()
    eligibility_status = {}

    for case_number, case_df in df.groupby("Case Number"):
        latest_disposition_date = case_df["Disposition Date"].max()

        if pd.isnull(latest_disposition_date):
            eligibility_status[case_number] = "❌ Not Eligible - No valid disposition date"
            continue

        case_df["Statute Code"] = case_df["Statute Code"].astype(
            str).str.strip()

        def check_condition(condition, message):
            """Helper function to apply eligibility checks."""
            if condition.any() if hasattr(condition, 'any') else condition:
                eligibility_status[case_number] = message
                return True
            return False

        # Check for excluded misdemeanors
        excluded_charges = case_df[case_df["Statute Code"].isin(
            EXCLUDED_MISDEMEANORS)]
        if not excluded_charges.empty:
            reasons = "; ".join(
                f"{row['Charge Description']} ({row['Statute Code']})"
                for _, row in excluded_charges.iterrows()
            )
            if check_condition(True, f"❌ Not Eligible - Excluded Misdemeanor(s): {reasons}"):
                continue

        # Prioritize non-convictions
        if case_df["Is Non-Conviction"].any():
            latest_non_conviction_date = case_df.loc[case_df["Is Non-Conviction"],
                                                     "Disposition Date"].max()
            final_wait_date = latest_non_conviction_date + \
                timedelta(days=WAIT_PERIODS["non_conviction"])
            if check_condition(today >= final_wait_date, "✅ Eligible - Non-Conviction"):
                continue
            eligibility_status[
                case_number] = f"⏳ Wait until {final_wait_date.strftime('%Y-%m-%d')} (Non-Conviction)"
            continue

        # Domestic violence cases must be ineligible
        if check_condition(case_df["Is Domestic Violence"], "❌ Not Eligible - Domestic Violence Case"):
            continue

        # Felonies must be ineligible
        if check_condition(case_df["Is Felony"], "❌ Not Eligible - Felony Disposition"):
            continue

        # Apply waiting period for misdemeanors
        final_wait_date = latest_disposition_date + \
            timedelta(days=WAIT_PERIODS["misdemeanor"])
        if check_condition(today >= final_wait_date, "✅ Eligible"):
            continue
        eligibility_status[
            case_number] = f"⏳ Wait until {final_wait_date.strftime('%Y-%m-%d')}"

    # Assign final eligibility status
    df["Eligibility"] = df["Case Number"].map(eligibility_status)
    return df


def process_case_data(parties_df, cases_df, charges_df, show_errors=True):
    """
    Processes and merges case-related data from any source, then determines eligibility.
    """
    try:
        if not all([
            validate_schema(
                parties_df, REQUIRED_COLUMNS["parties"], "Parties"),
            validate_schema(cases_df, REQUIRED_COLUMNS["cases"], "Cases"),
            validate_schema(charges_df, REQUIRED_COLUMNS["charges"], "Charges")
        ]):
            return pd.DataFrame(), pd.DataFrame()

        # Merge dataframes on relevant keys
        merged_df = charges_df.merge(
            cases_df, on="CaseID", how="left"
        ).merge(parties_df, on="PartyID", how="left")

        # Ensure Disposition Date is properly formatted
        if "Disposition Date" in merged_df.columns:
            merged_df["Disposition Date"] = pd.to_datetime(
                merged_df["Disposition Date"], errors="coerce")

        # Check if merged data is empty
        if merged_df.empty:
            if show_errors:
                st.error(
                    "❌ Merged data is empty! Check if input files contain valid data.")
            return pd.DataFrame(), pd.DataFrame()

        # Categorize and determine eligibility
        merged_df = determine_eligibility(
            categorize_charges(clean_dataframe(merged_df))
        )

        # Aggregate case-level summary
        case_data = (
            merged_df.groupby("Case Number")
            .agg({"Name": "first", "Case Type": "first", "Disposition Date": "max", "Eligibility": "first"})
            .reset_index()
        )

        # Format disposition date
        if "Disposition Date" in case_data.columns:
            case_data["Disposition Date"] = pd.to_datetime(
                case_data["Disposition Date"], errors="coerce")
            case_data["Disposition Date"] = case_data["Disposition Date"].dt.strftime(
                "%Y-%m-%d")

        # Return case data
        return case_data, merged_df

    except Exception as e:
        if show_errors:
            st.error(f"❌ Error in processing case data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()
