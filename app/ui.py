import streamlit as st
import pandas as pd
from datetime import timedelta
from utils.constants import NON_CONVICTION_TERMS, WAIT_PERIODS


def render_summary():
    """Displays a summary of total cases and eligibility."""
    case_data = st.session_state.case_data

    if case_data is None or case_data.empty:
        st.warning("⚠️ No cases to display. Please check your data.")
        return

    total_cases = len(case_data)
    eligible_cases = case_data[case_data["Eligibility"].str.startswith(
        "✅ Eligible", na=False)]
    ineligible_cases = case_data[~case_data["Eligibility"].str.startswith(
        "✅ Eligible", na=False)]

    if not eligible_cases.empty:
        st.download_button(
            label="📥 Download Eligible Cases (CSV)",
            data=eligible_cases.to_csv(index=False),
            file_name="eligible_cases.csv",
            mime="text/csv"
        )
    st.subheader("📊 Eligibility Summary")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="📂 Total Cases", value=total_cases)

    with col2:
        st.metric(label="✅ Eligible Cases", value=len(eligible_cases))

    with col3:
        st.metric(label="❌ Ineligible Cases", value=len(ineligible_cases))


def render_case_list():
    """Displays a list of cases and case details when selected."""
    case_data = st.session_state.case_data

    if case_data is None or case_data.empty:
        st.warning("⚠️ No case data available.")
        return

    if st.session_state.selected_case is None:
        st.subheader("📊 Case List")

        def render_case_table(cases, title, key_prefix):
            """Renders case list table."""
            st.subheader(title)
            col1, col2, col3, col4, col5, col6 = st.columns(
                [0.15, 0.3, 0.2, 0.15, 0.15, 0.1])
            col1.write("**Case Number**")
            col2.write("**Name**")
            col3.write("**Case Type**")
            col4.write("**Disposition Date**")
            col5.write("**Eligibility**")
            col6.write("**View Details**")

            if cases.empty:
                st.info(f"No {title.lower()} found.")
            else:
                for index, row in cases.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns(
                        [0.15, 0.3, 0.2, 0.15, 0.15, 0.1])
                    col1.write(f"**{row['Case Number']}**")
                    col2.write(row['Name'])
                    col3.write(row['Case Type'])

                    # Show disposition date and eligibility in green if waiting period has passed
                    if row['Eligibility'].startswith("✅"):
                        col4.write(f":green[{row['Disposition Date']}]")
                        col5.write(f":green[{row['Eligibility']}]")
                    else:
                        col4.write(f":red[{row['Disposition Date']}]")
                        col5.write(row['Eligibility'])

                    if col6.button("🔍", key=f"{key_prefix}_{index}"):
                        st.session_state.selected_case = row["Case Number"]
                        st.rerun()

        eligible_cases = case_data[case_data["Eligibility"].str.startswith(
            "✅ Eligible", na=False)]
        ineligible_cases = case_data[~case_data["Eligibility"].str.startswith(
            "✅ Eligible", na=False)]

        render_case_table(eligible_cases, "✅ Eligible Cases", "eligible_case")
        render_case_table(ineligible_cases,
                          "❌ Ineligible Cases", "ineligible_case")

    else:
        render_case_details()


def render_case_details():
    """Displays details for a selected case."""
    case_data = st.session_state.case_data
    case_details = case_data[case_data["Case Number"]
                             == st.session_state.selected_case]

    if case_details.empty:
        st.error("❌ No case details found.")
        return

    row = case_details.iloc[0]
    st.subheader(
        f"📜 Case Details - {st.session_state.selected_case} ({row['Eligibility']})")

    col1, col2 = st.columns([0.5, 0.5])
    col1.write(f"**Name:** {row['Name']}")
    col1.write(f"**Case Type:** {row['Case Type']}")

    # Show disposition date and eligibility in green if waiting period has passed
    if row['Eligibility'].startswith("✅"):
        col2.write(f"**Disposition Date:** :green[{row['Disposition Date']}]")
        col2.write(f"**Eligibility:** :green[{row['Eligibility']}]")
    else:
        col2.write(f"**Disposition Date:** :red[{row['Disposition Date']}]")
        col2.write(f"**Eligibility:** {row['Eligibility']}")

    # Retrieve charge details for this case
    case_charges = st.session_state.df[st.session_state.df["Case Number"]
                                       == st.session_state.selected_case]

    if not case_charges.empty:
        st.subheader("⚖️ Charges for this Case")

        # Add custom CSS for hover effect on eligible charges
        st.markdown("""
            <style>
            /* Target all expanders in the charge section */
            div[data-testid="stExpander"] details summary {
                transition: color 0.2s ease;
            }
            /* Change arrow color to green for eligible charges */
            div[data-testid="stExpander"]:has(.eligible-marker) details summary svg {
                color: #00cc00 !important;
                stroke: #00cc00 !important;
            }
            /* Hover effect for eligible charges */
            div[data-testid="stExpander"]:has(.eligible-marker) details summary:hover,
            div[data-testid="stExpander"]:has(.eligible-marker) details summary:hover p,
            div[data-testid="stExpander"]:has(.eligible-marker) details summary:hover div,
            div[data-testid="stExpander"]:has(.eligible-marker) details summary:hover span {
                color: #00cc00 !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Determine the most relevant disposition date based on eligibility calculation
        # The most relevant date is the one that determines when the case becomes eligible
        # This is calculated as: disposition_date + applicable_wait_period
        def is_non_conviction(disposition):
            """Check if a disposition is a non-conviction."""
            if not disposition or str(disposition).strip() == "":
                return False
            return any(term in str(disposition).upper() for term in NON_CONVICTION_TERMS)

        def calculate_eligibility_date(row):
            """Calculate when a charge becomes eligible based on disposition and wait period."""
            if not row["Disposition Date"] or str(row["Disposition Date"]).strip() == "":
                return None

            # Determine if this is a non-conviction
            if is_non_conviction(row["Disposition"]):
                wait_days = WAIT_PERIODS["non_conviction"]
            else:
                wait_days = WAIT_PERIODS["misdemeanor"]

            return row["Disposition Date"] + timedelta(days=wait_days)

        # Filter charges with valid disposition dates and calculate eligibility dates
        valid_charges = case_charges[case_charges["Disposition Date"].notna()].copy()
        valid_charges["eligibility_date"] = valid_charges.apply(calculate_eligibility_date, axis=1)

        # The most relevant date is the one with the LATEST eligibility date (determines case eligibility)
        most_relevant_eligibility_date = valid_charges["eligibility_date"].max() if not valid_charges.empty else None

        # Find the disposition date that corresponds to the most relevant eligibility date
        if most_relevant_eligibility_date:
            most_relevant_row = valid_charges[valid_charges["eligibility_date"] == most_relevant_eligibility_date].iloc[0]
            most_relevant_disposition_date = most_relevant_row["Disposition Date"]
        else:
            most_relevant_disposition_date = None

        all_same_disposition = valid_charges["Disposition Date"].nunique() == 1 if not valid_charges.empty else True

        from datetime import datetime
        today = datetime.today()

        # Check if the overall case is eligible
        case_is_eligible = row['Eligibility'].startswith("✅")

        for _, charge_row in case_charges.iterrows():
            is_most_relevant = charge_row["Disposition Date"] == most_relevant_disposition_date

            # Determine charge type label
            is_charge_non_conviction = is_non_conviction(charge_row["Disposition"])
            if is_charge_non_conviction:
                charge_type_label = f"Non-Conviction - {charge_row['Charge Class']}"
            else:
                charge_type_label = charge_row['Charge Class']

            # Calculate if this individual charge is eligible
            # A charge is only eligible if both the charge's waiting period has passed AND the case is eligible
            charge_eligibility_date = calculate_eligibility_date(charge_row)
            charge_waiting_period_passed = charge_eligibility_date and today >= charge_eligibility_date
            is_charge_eligible = case_is_eligible and charge_waiting_period_passed

            # Handle missing or NaT disposition dates
            if pd.isna(charge_row['Disposition Date']):
                disposition_label = "(No Date)"
            else:
                disposition_label = f"({charge_row['Disposition Date'].strftime('%Y-%m-%d')})"

            if all_same_disposition:
                disposition_label += " 👈  **Same Date for All Charges**"
            elif is_most_relevant:
                disposition_label += " 👈 **Most Relevant Date for Case**"

            # Use a different emoji/marker for eligible charges in the title
            charge_emoji = "✅" if is_charge_eligible else "🔹"

            with st.expander(
                f"{charge_emoji} {charge_row['Charge Description']} ({charge_type_label}) {disposition_label}"
            ):
                # Add marker inside the expander for eligible charges
                if is_charge_eligible:
                    st.markdown('<div class="eligible-marker" style="display:none;"></div>', unsafe_allow_html=True)

                col1, col2 = st.columns([0.5, 0.5])
                col1.write(f"**Statute Code:** {charge_row['Statute Code']}")
                col1.write(f"**Charge Class:** {charge_row['Charge Class']}")
                col2.write(f"**Disposition:** {charge_row['Disposition']}")

                # Show disposition date in green if charge is eligible
                if pd.isna(charge_row['Disposition Date']):
                    col2.write(f"**Disposition Date:** No Date")
                elif is_charge_eligible:
                    col2.write(f"**Disposition Date:** :green[{charge_row['Disposition Date'].strftime('%Y-%m-%d')}]")
                else:
                    col2.write(f"**Disposition Date:** {charge_row['Disposition Date'].strftime('%Y-%m-%d')}")

    if st.button("🔙 Back to Case List"):
        st.session_state.selected_case = None
        st.rerun()


def render_synthetic_data_notice():
    """Displays a notice about the synthetic example data usage."""
    st.warning(
        "⚠️ This tool uses **synthetic example data** designed specifically "
        "for **Maryland** cases. However, the methodology can be applied to other state datasets. "
        "This data is **for demonstration purposes only** and does **not** contain real case records. "
        "\n\n🔒 We do **not** collect, store, or track any personally identifiable information (PII)."
    )
