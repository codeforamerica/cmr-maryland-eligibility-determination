import streamlit as st
import pandas as pd
from app.db import ensure_schema_exists, fetch_all_tables, update_eligible_cases
from app.session import initialize_session, reset_session_state
from app.file_uploads import handle_file_uploads
from app.processing import process_case_data
from app.ui import render_summary, render_case_list, render_synthetic_data_notice
from utils.constants import REQUIRED_COLUMNS
from utils.helpers import EXAMPLE_DATA, show_csv_schema

# Initialize session state
initialize_session()

st.set_page_config(page_title="Eligibility Checker", layout="wide")
st.title("Eligibility Checker")
MD_DATA_SOURCE_OPTIONS = ["Use example data",
                          "Upload your own data", "Load from MySQL"]
HI_DATA_SOURCE_OPTIONS = ["Use example data"]

# Handle user selection for data source
if st.session_state.case_data is None:
    selected_state = st.selectbox(
        "Select state:", options=["Maryland", "Hawaii"],
        index=0, key="selected_state"
    )
    if st.session_state["selected_state"] == "Hawaii":
        data_source_options = HI_DATA_SOURCE_OPTIONS
    else:
        data_source_options = MD_DATA_SOURCE_OPTIONS
    data_source = st.radio(
        "Select data source:", data_source_options,
        index=0, key="data_source"
    )

    if data_source != st.session_state["data_source"]:
        st.session_state["data_source"] = data_source
        reset_session_state()

# Reset uploaded files when switching to "Upload your own data"
if st.session_state["data_source"] == "Upload your own data" and not st.session_state.get("file_processed", False):
    st.session_state.uploaded_files = {file: None for file in REQUIRED_COLUMNS}
    if st.button("📋 View/Hide Expected CSV Format"):
        st.session_state["show_schema"] = not st.session_state["show_schema"]

    if st.session_state["show_schema"]:
        show_csv_schema()
    # Handle file uploads if user chooses "Upload your own data"
    if not st.session_state.get("file_processed", False):
        if st.session_state["data_source"] == "Upload your own data":
            handle_file_uploads()
            st.session_state.use_example_data = False


# Show synthetic data disclaimer
if st.session_state["data_source"] == "Use example data" and not st.session_state.get("file_processed", False):
    render_synthetic_data_notice()

# Load example data if selected
if st.session_state["data_source"] == "Use example data":
    st.session_state.uploaded_files = EXAMPLE_DATA
    st.session_state.use_example_data = True
    all_files_uploaded = True
elif st.session_state["data_source"] == "Load from MySQL":
    conn_string = st.session_state.get("mysql_conn_string")

    if not conn_string:
        with st.form("mysql_connection_form"):
            st.subheader("🔐 Connect to Your MySQL Database")
            connection_string = st.text_input(
                "MySQL Connection String",
                value="mysql://user:password@host:port/database",
                help="Format: mysql://user:password@host:port/database"
            )
            connect = st.form_submit_button("Connect and Load Data")

            if connect:
                st.session_state["mysql_conn_string"] = connection_string
                st.session_state["pending_mysql_load"] = True
                st.rerun()

    else:
        if st.session_state.get("pending_mysql_load"):
            with st.spinner("🔄 Connecting to MySQL and loading tables..."):
                ensure_schema_exists(conn_string)
                parties_df, cases_df, charges_df = fetch_all_tables(conn_string)

                st.session_state.df = charges_df.merge(
                    cases_df, on="CaseID", how="left"
                ).merge(parties_df, on="PartyID", how="left")

                st.session_state["raw_parties"] = parties_df
                st.session_state["raw_cases"] = cases_df
                st.session_state["raw_charges"] = charges_df

                st.success("✅ Connected and all tables loaded!")
            st.session_state["pending_mysql_load"] = False

    df = st.session_state.get("df")
    all_files_uploaded = isinstance(df, pd.DataFrame) and not df.empty
else:
    all_files_uploaded = all(
        st.session_state.uploaded_files[file] is not None for file in REQUIRED_COLUMNS
    )

# Show Determine Eligibility button only when all files are uploaded
if all_files_uploaded and not st.session_state.get("file_processed", False):
    if st.button("Determine Eligibility", key="determine_eligibility"):

        data_source = st.session_state["data_source"]

        if data_source == "Upload your own data":
            st.session_state.case_data, st.session_state.df = process_case_data(

                st.session_state.uploaded_files["parties"],
                st.session_state.uploaded_files["cases"],
                st.session_state.uploaded_files["charges"]
            )

        elif data_source == "Load from MySQL":
            conn_string = st.session_state.get("mysql_conn_string")
            if conn_string:
                try:
                    with st.spinner("⏳ Processing data and determining eligibility..."):
                        parties_df, cases_df, charges_df = fetch_all_tables(
                            conn_string)
                        st.session_state.case_data, st.session_state.df = process_case_data(
                            parties_df, cases_df, charges_df
                        )

                        # Update eligible column for qualifying cases
                        update_eligible_cases(
                            conn_string, st.session_state.case_data)
                        st.success("✅ Eligibility determination complete.")
                except Exception as e:
                    st.error(f"❌ Failed to fetch/process MySQL data: {e}")
            else:
                st.error("❌ MySQL connection string is missing.")

        elif data_source == "Use example data":
            print("Using example data")
            st.session_state.case_data, st.session_state.df = process_case_data(
                EXAMPLE_DATA["parties"],
                EXAMPLE_DATA["cases"],
                EXAMPLE_DATA["charges"]
            )
            print(st.session_state.case_data.head())

        st.session_state.uploaded_files = {
            file: None for file in REQUIRED_COLUMNS
        }
        st.session_state.file_processed = True

        st.rerun()

# Show case summary and case details
if st.session_state.get("file_processed", False) and st.session_state.case_data is not None:
    if st.button("🔄 Upload a New File", key="upload_new_file"):
        reset_session_state()

    if st.session_state.selected_case is None:
        render_summary()

    render_case_list()
