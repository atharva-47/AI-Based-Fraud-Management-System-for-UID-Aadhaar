from input import get_result
from uid_match import uid_matching
from address_matching import process_and_match_addresses
from model import process_folder
from model import process_file
from name_matching import process_names
from final_score import put_final_result   
    # Test with a folder or a single file
mode = input("Enter mode (file/folder): ").strip().lower()
path = input("Enter the path: ").strip()

if mode == "folder":
    result = process_folder(path)
elif mode == "file":
    result = process_file(path)
else:
    print("Invalid mode. Please enter 'file' or 'folder'.")
    exit()

    
for serial_number, details in result.items():
    print(f"\nSerial Number: {serial_number}")
    print(f"Result: {details}")


output_file_path = get_result(result)

uid_matching(output_file_path)
process_and_match_addresses(output_file_path, output_file_path)
process_names(output_file_path,output_file_path)
put_final_result(output_file_path)