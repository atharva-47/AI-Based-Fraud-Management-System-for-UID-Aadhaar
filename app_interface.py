import streamlit as st
import pandas as pd
import zipfile
import os
from input import get_result
from uid_match import uid_matching
from address_matching import process_and_match_addresses
from model import process_folder, process_file
from name_matching import process_names
from final_score import put_final_result

# Streamlit UI
st.title("UID Aadhaar Fraud Detection")

# File uploader for ZIP files
uploaded_file = st.file_uploader("Upload a ZIP File", type="zip")

# Temporary directory for extracted files
temp_dir = "temp_extracted_files"

if uploaded_file:
    # Extract ZIP file
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
        extracted_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
        st.success("ZIP file extracted successfully.")
        st.write("Extracted Files:", [os.path.basename(f) for f in extracted_files])  # Show extracted files

    # Automatically decide how to process
    if len(extracted_files) == 1:
        # Single file - process as file
        st.info("Single file detected. Processing as a file...")
        result = process_file(extracted_files[0])
    elif len(extracted_files) > 1:
        # Multiple files - process as folder
        st.info("Multiple files detected. Processing as a folder...")
        result = process_folder(temp_dir)
    else:
        st.error("No valid files found in the ZIP.")
        result = None

    # Process results if available
    if result:
        output_file_path = get_result(result)

        # Run additional processing steps
        uid_matching(output_file_path)
        process_and_match_addresses(output_file_path, output_file_path)
        process_names(output_file_path, output_file_path)
        put_final_result(output_file_path)

        # Display final results in table format
        try:
            df = pd.read_excel(output_file_path, usecols=["SrNo", "Final Remarks", "Document Type"])
            st.write("Processed Results:")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error displaying results: {e}")

        st.success("Processing complete. Final results have been saved.")
    else:
        st.warning("Processing not completed. Please check your input.")
else:
    st.warning("Please upload a ZIP file.")

# Clean up temporary directory
import shutil
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
