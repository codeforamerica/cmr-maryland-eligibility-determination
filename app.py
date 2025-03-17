import streamlit as st
from app.session import initialize_session, reset_session_state
from app.file_uploads import handle_file_uploads
from app.processing import process_csv
from app.ui import render_summary, render_case_list, render_synthetic_data_notice
from utils.constants import REQUIRED_COLUMNS
from utils.helpers import EXAMPLE_DATA, show_csv_schema

# Initialize session state
initialize_session()

st.set_page_config(page_title="Maryland Eligibility Checker", layout="wide")
st.title("Maryland Eligibility Checker")

# Handle user selection for data source
if st.session_state.case_data is None:
    data_source = st.radio(
        "Select data source:", ["Use example data", "Upload your own data"],
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
else:
    all_files_uploaded = all(
        st.session_state.uploaded_files[file] is not None for file in REQUIRED_COLUMNS
    )

# Show Determine Eligibility button only when all files are uploaded
if all_files_uploaded and not st.session_state.get("file_processed", False):
    if st.button("Determine Eligibility", key="determine_eligibility"):
        if st.session_state["data_source"] == "Upload your own data":
            st.session_state.case_data, st.session_state.df = process_csv(
                st.session_state.uploaded_files["parties"],
                st.session_state.uploaded_files["cases"],
                st.session_state.uploaded_files["charges"]
            )
        else:
            # Process example data
            st.session_state.case_data, st.session_state.df = process_csv(
                EXAMPLE_DATA["parties"], EXAMPLE_DATA["cases"], EXAMPLE_DATA["charges"]
            )

        st.session_state.uploaded_files = {
            file: None for file in REQUIRED_COLUMNS}
        st.session_state.file_processed = True
        st.rerun()

# Show case summary and case details
if st.session_state.get("file_processed", False) and st.session_state.case_data is not None:
    if st.button("🔄 Upload a New File", key="upload_new_file"):
        reset_session_state()

    if st.session_state.selected_case is None:
        render_summary()

    render_case_list()
