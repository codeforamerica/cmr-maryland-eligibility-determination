import streamlit as st
import pandas as pd
from utils.constants import REQUIRED_COLUMNS
from utils.data_loader import EXAMPLE_DATA


def handle_file_uploads():
    """Handles user file uploads and manages example data selection."""

    # Reset uploaded files if switching from example data to manual upload
    if st.session_state.get("use_example_data", False):
        st.session_state.uploaded_files = {
            file: None for file in REQUIRED_COLUMNS}
        st.session_state.use_example_data = False

    # Handle manual file uploads
    for file_key in REQUIRED_COLUMNS:
        uploaded_file = st.file_uploader(
            f"📂 Upload your `{file_key}` CSV file", type=["csv"], key=file_key
        )

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            df.columns = df.columns.str.strip()

            # Validate required columns
            missing_columns = [
                col for col in REQUIRED_COLUMNS[file_key] if col not in df.columns]

            if missing_columns:
                st.error(
                    f"❌ `{uploaded_file.name}` is missing required columns: {', '.join(missing_columns)}"
                )
                continue
            else:
                st.session_state.uploaded_files[file_key] = df
                st.success(f"✅ `{uploaded_file.name}` uploaded successfully!")

    # If using example data, auto load data
    if st.session_state["data_source"] == "Use example data":
        st.session_state.uploaded_files = EXAMPLE_DATA
        st.session_state.use_example_data = True
        st.success("✅ Using example data. File uploads are disabled.")

    # Ensure all required files are uploaded before processing
    all_uploaded = all(
        st.session_state.uploaded_files[file] is not None for file in REQUIRED_COLUMNS)
    st.session_state["all_files_uploaded"] = all_uploaded
