import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta

EXCLUDED_MISDEMEANORS = {
    "CR.3.203": "Second-degree assault",
    "27.342": "Second-degree assault",
}
NON_CONVICTION_TERMS = ["DISMISSED",
                        "ACQUITTED", "NOLLE PROSEQUI", "NOT GUILTY"]
WAIT_PERIODS = {"misdemeanor": 7 * 365, "non_conviction": 3 * 365}


if "file_processed" not in st.session_state:
    st.session_state.file_processed = False
if "case_data" not in st.session_state:
    st.session_state.case_data = None
if "df" not in st.session_state:
    st.session_state.df = None
if "selected_case" not in st.session_state:
    st.session_state.selected_case = None


def clean_dataframe(df):
    df.columns = df.columns.str.strip()
    df["Disposition Date"] = pd.to_datetime(
        df["Disposition Date"].astype(str).str.strip(), errors="coerce")
    df["Case Number"] = df["Case Number"].astype(str).str.strip()
    df["Charge Class"] = df["Charge Class"].astype(str).str.strip().str.upper()
    df["Statute Code"] = df["Statute Code"].astype(str).str.strip()
    df["Case Type"] = df["Case Type"].astype(str).str.upper()
    return df


def categorize_charges(df):
    df["Is Misdemeanor"] = df["Charge Class"].str.startswith(
        "MISDEMEANOR", na=False)
    df["Is Felony"] = df["Charge Class"].str.startswith("FELONY", na=False)
    df["Is Non-Conviction"] = df["Disposition"].astype(
        str).str.upper().str.contains('|'.join(NON_CONVICTION_TERMS), na=False)
    df["Is Excluded Misdemeanor"] = df["Statute Code"].isin(
        EXCLUDED_MISDEMEANORS.keys())
    df["Is Domestic Violence"] = df["Case Type"].str.contains(
        "DOMESTIC VIOLENCE", na=False)
    return df


def determine_eligibility(df):
    today = datetime.today()
    eligibility_status = {}

    for case_number, case_df in df.groupby("Case Number"):
        latest_disposition_date = case_df["Disposition Date"].max()

        if pd.isnull(latest_disposition_date):
            eligibility_status[case_number] = "No valid disposition date"
            continue

        case_df["Statute Code"] = case_df["Statute Code"].astype(
            str).str.strip()

        # Excluded misdemeanors must be checked first for any charge
        excluded_charges = case_df[case_df["Statute Code"].isin(
            EXCLUDED_MISDEMEANORS.keys())]

        if not excluded_charges.empty:
            reasons = "; ".join(
                f"{row['Charge Description']} ({row['Statute Code']})" for _, row in excluded_charges.iterrows()
            )
            eligibility_status[
                case_number] = f"❌ Not Eligible - Excluded Misdemeanor(s): {reasons}"
            continue

        # Non-conviction cases take precedence
        if case_df["Is Non-Conviction"].any():
            latest_non_conviction_disposition = case_df[case_df["Is Non-Conviction"]
                                                        ]["Disposition Date"].max()
            final_wait_date = latest_non_conviction_disposition + \
                timedelta(days=3*365)

            eligibility_status[case_number] = (
                "✅ Eligible - Non-Conviction"
                if today >= final_wait_date
                else f"⏳ Wait until {final_wait_date.strftime('%Y-%m-%d')} (Non-Conviction)"
            )
            continue

        # Felonies are not eligible
        if case_df["Is Felony"].any():
            eligibility_status[case_number] = "❌ Not Eligible - Felony Disposition"
            continue

        # Domestic violence cases are not eligible
        if case_df["Is Domestic Violence"].any():
            eligibility_status[case_number] = "❌ Not Eligible - Domestic Violence Case"
            continue

        # ✅ Apply 7-year waiting period for misdemeanors
        final_wait_date = latest_disposition_date + timedelta(days=7*365)

        eligibility_status[case_number] = (
            "✅ Eligible"
            if today >= final_wait_date
            else f"⏳ Wait until {final_wait_date.strftime('%Y-%m-%d')}"
        )

    df["Eligibility"] = df["Case Number"].map(eligibility_status)
    return df


def process_csv(file):
    """Processes the uploaded CSV file and returns case data and raw charge data."""
    try:
        file.seek(0)
        raw_data = file.getvalue().decode("utf-8")

        if not raw_data.strip():
            st.error("Error: The uploaded CSV file is empty.")
            return None, None

        df = pd.read_csv(io.StringIO(raw_data), delimiter=",",
                         skip_blank_lines=True, header=0)

        if df.empty:
            st.error("Error: No data found in the CSV file.")
            return None, None

        df = clean_dataframe(df)
        df = categorize_charges(df)
        df = determine_eligibility(df)

        # Turn into case-level view
        case_data = df.groupby("Case Number").agg({
            "Defendant Name": "first",
            "Case Type": "first",
            "Disposition Date": "max",
            "Eligibility": "first"
        }).reset_index()

        case_data["Disposition Date"] = case_data["Disposition Date"].dt.strftime(
            "%Y-%m-%d")

        return case_data, df

    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None, None


# Streamlit UI
st.set_page_config(page_title="Maryland Eligibility Checker", layout="wide")
st.title("Maryland Eligibility Checker")

# File Upload
if not st.session_state.file_processed:
    uploaded_file = st.file_uploader("📂 Upload CSV", type=["csv"])

    if uploaded_file:
        if st.button("📩 Submit and Process File"):
            st.session_state.file_processed = True
            st.session_state.case_data, st.session_state.df = process_csv(
                uploaded_file)
            st.rerun()

if st.session_state.file_processed and st.session_state.case_data is not None:

    case_data = st.session_state.case_data
    eligible_cases = case_data[case_data["Eligibility"].str.contains(
        "Eligible", na=False)]
    ineligible_cases = case_data[~case_data["Eligibility"].str.contains(
        "Eligible", na=False)]
    st.session_state.file_processed = True
    df = st.session_state.df

    if st.button("🔄 Upload a New File"):
        st.session_state.file_processed = False
        st.session_state.case_data = None
        st.session_state.df = None
        st.session_state.selected_case = None
        st.rerun()

    if case_data is not None:
        if "selected_case" not in st.session_state:
            st.session_state.selected_case = None

        # Main View
        if st.session_state.selected_case is None:
            st.subheader("📊 Case List")

            # Separate eligible and ineligible cases
            eligible_cases = case_data[
                case_data["Eligibility"].str.startswith("✅ Eligible", na=False)
            ]

            ineligible_cases = case_data[
                ~case_data["Eligibility"].str.startswith(
                    "✅ Eligible", na=False)
            ]

            def render_table_header():
                col1, col2, col3, col4, col5, col6 = st.columns(
                    [0.15, 0.3, 0.2, 0.15, 0.15, 0.1])
                col1.write("**Case Number**")
                col2.write("**Defendant Name**")
                col3.write("**Case Type**")
                col4.write("**Most Relevant Disposition Date**")
                col5.write("**Eligibility**")
                col6.write("**View Details**")

            # Eligible Cases
            st.subheader("✅ Eligible Cases")
            render_table_header()

            if not eligible_cases.empty:
                for index, row in eligible_cases.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns(
                        [0.15, 0.3, 0.2, 0.15, 0.15, 0.1])

                    col1.write(f"**{row['Case Number']}**")
                    col2.write(row['Defendant Name'])
                    col3.write(row['Case Type'])
                    col4.write(f":red[{row['Disposition Date']}]")
                    col5.write(f" {row['Eligibility']}")

                    if col6.button("🔍", key=f"eligible_case_{index}"):
                        st.session_state.selected_case = row["Case Number"]
                        st.rerun()
            else:
                st.info("No eligible cases found.")

            # Ineligible Cases
            st.subheader("❌ Ineligible Cases")
            render_table_header()

            if not ineligible_cases.empty:
                for index, row in ineligible_cases.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns(
                        [0.15, 0.3, 0.2, 0.15, 0.15, 0.1])

                    col1.write(f"**{row['Case Number']}**")
                    col2.write(row['Defendant Name'])
                    col3.write(row['Case Type'])
                    col4.write(f":red[{row['Disposition Date']}]")
                    col5.write(f"{row['Eligibility']}")

                    if col6.button("🔍", key=f"ineligible_case_{index}"):
                        st.session_state.selected_case = row["Case Number"]
                        st.rerun()
            else:
                st.info("No ineligible cases found.")
            st.subheader("📥 Download Processed Case Data")
            csv_data = st.session_state.case_data.to_csv(
                index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Processed Cases CSV",
                data=csv_data,
                file_name="processed_cases.csv",
                mime="text/csv"
            )
        # Case Details View
        else:
            case_details = case_data[case_data["Case Number"]
                                     == st.session_state.selected_case]

            if not case_details.empty:
                row = case_details.iloc[0]
                st.subheader(
                    f"📜 Case Details - {st.session_state.selected_case} ({row['Eligibility']})")

                col1, col2 = st.columns([0.5, 0.5])
                with col1:
                    st.write(f"**Defendant Name:** {row['Defendant Name']}")
                    st.write(f"**Case Type:** {row['Case Type']}")
                with col2:
                    st.write(
                        f"**Disposition Date:** :red[{row['Disposition Date']}]")
                    st.write(f"**Eligibility:** {row['Eligibility']}")

                case_charges = df[df["Case Number"]
                                  == st.session_state.selected_case]

                if not case_charges.empty:
                    st.subheader("⚖️ Charges for this Case")

                    most_relevant_disposition_date = case_charges["Disposition Date"].max(
                    )
                    all_same_disposition = case_charges["Disposition Date"].nunique(
                    ) == 1

                    for _, charge_row in case_charges.iterrows():
                        is_most_relevant = charge_row["Disposition Date"] == most_relevant_disposition_date

                        disposition_label = f"({charge_row['Disposition Date'].strftime('%Y-%m-%d')})"
                        if all_same_disposition:
                            disposition_label += " 👈  **Same Date for All Charge Disposition**"
                        elif is_most_relevant:
                            disposition_label += " 👈 **Most Relevant Date for Case**"

                        with st.expander(
                            f"🔹 {charge_row['Charge Description']} ({charge_row['Charge Class']}) {disposition_label}"
                        ):
                            col1, col2 = st.columns([0.5, 0.5])
                            with col1:
                                st.write(
                                    f"**Statute Code:** {charge_row['Statute Code']}")
                                st.write(
                                    f"**Charge Class:** {charge_row['Charge Class']}")
                            with col2:
                                st.write(
                                    f"**Disposition:** {charge_row['Disposition']}")
                                st.write(
                                    f"**Disposition Date:** {charge_row['Disposition Date'].strftime('%Y-%m-%d')}")

            # Back button to return to the case list
            if st.button("🔙 Back to Case List"):
                st.session_state.selected_case = None
                st.rerun()
