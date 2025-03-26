import streamlit as st
from utils.constants import REQUIRED_COLUMNS


def initialize_session():
    """Initialize Streamlit session state variables if not set."""
    if "data_source" not in st.session_state:
        st.session_state["data_source"] = "Use example data"

    if "file_processed" not in st.session_state:
        st.session_state["file_processed"] = False

    if "case_data" not in st.session_state:
        st.session_state["case_data"] = None

    if "df" not in st.session_state:
        st.session_state["df"] = None

    if "selected_case" not in st.session_state:
        st.session_state["selected_case"] = None

    if "show_schema" not in st.session_state:
        st.session_state["show_schema"] = False

    if "use_example_data" not in st.session_state:
        st.session_state["use_example_data"] = False

    if "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = {
            file: None for file in REQUIRED_COLUMNS}
    if "mysql_conn_info" not in st.session_state:
        st.session_state["mysql_conn_info"] = None
    if "pending_mysql_load" not in st.session_state:
        st.session_state["pending_mysql_load"] = False


def reset_session_state():
    """Resets session state and prevents duplicate rerun triggers."""
    st.session_state.file_processed = False
    st.session_state.case_data = None
    st.session_state.df = None
    st.session_state.selected_case = None
    st.session_state.uploaded_files = {file: None for file in REQUIRED_COLUMNS}
    st.session_state.show_schema = False
    st.session_state.use_example_data = st.session_state.data_source == "Use example data"
    st.session_state.eligibility_determined = False
    st.session_state.mysql_conn = None

    # Ensure rerun is only called once to avoid duplicate reruns
    if not st.session_state.get("rerun_triggered", False):
        st.session_state.rerun_triggered = True
        st.rerun()
