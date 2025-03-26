import streamlit as st


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
    col2.write(f"**Disposition Date:** :red[{row['Disposition Date']}]")
    col2.write(f"**Eligibility:** {row['Eligibility']}")

    # Retrieve charge details for this case
    case_charges = st.session_state.df[st.session_state.df["Case Number"]
                                       == st.session_state.selected_case]

    if not case_charges.empty:
        st.subheader("⚖️ Charges for this Case")
        most_relevant_disposition_date = case_charges["Disposition Date"].max()
        all_same_disposition = case_charges["Disposition Date"].nunique() == 1

        for _, charge_row in case_charges.iterrows():
            is_most_relevant = charge_row["Disposition Date"] == most_relevant_disposition_date

            disposition_label = f"({charge_row['Disposition Date'].strftime('%Y-%m-%d')})"
            if all_same_disposition:
                disposition_label += " 👈  **Same Date for All Charges**"
            elif is_most_relevant:
                disposition_label += " 👈 **Most Relevant Date for Case**"

            with st.expander(
                f"🔹 {charge_row['Charge Description']} ({charge_row['Charge Class']}) {disposition_label}"
            ):
                col1, col2 = st.columns([0.5, 0.5])
                col1.write(f"**Statute Code:** {charge_row['Statute Code']}")
                col1.write(f"**Charge Class:** {charge_row['Charge Class']}")
                col2.write(f"**Disposition:** {charge_row['Disposition']}")
                col2.write(
                    f"**Disposition Date:** {charge_row['Disposition Date'].strftime('%Y-%m-%d')}")

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
