import streamlit as st
from input import get_result
from uid_match import uid_matching
from address_matching import process_and_match_addresses
from model import process_folder, process_file
from name_matching import process_names
from final_score import put_final_result

# Streamlit UI for selecting mode and input path
st.title("UID AAdhar Fraud Detection")

# Ask user to select mode (file/folder)
mode = st.selectbox("Select Mode", ["file", "folder"])

# Ask user to input the path
path = st.text_input("Enter the Path", "")

if path:
    if mode == "folder":
        result = process_folder(path)
    elif mode == "file":
        result = process_file(path)
    else:
        st.error("Invalid mode selected. Please choose either 'file' or 'folder'.")
        result = None

    # Process and output results
    if result:
        output_file_path = get_result(result)
        
        # Call the processing functions
        uid_matching(output_file_path)
        process_and_match_addresses(output_file_path, output_file_path)
        process_names(output_file_path, output_file_path)
        put_final_result(output_file_path)

        # Indicate completion
        st.success("Processing complete. Final results have been saved.")
else:
    st.warning("Please enter a valid path.")
