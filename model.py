from ultralytics import YOLO
import easyocr
import cv2
import os
import re
import pandas as pd

def classify_document(image_path):
    # Load the trained YOLO classification model
    model = YOLO('classification.pt')
    
    # Predict the class of the document
    results = model.predict(source=image_path)
    for result in results:
        # Get the predicted class index with the highest probability
        predicted_class_index = result.probs.top1
        # Get the class name using the index
        predicted_class = result.names[predicted_class_index]
        #print(f"The image {os.path.basename(image_path)} is classified as: {predicted_class}")
        
        # Check if the classification is Aadhaar
        return predicted_class.lower() == "aadhar"  # Correct spelling and match expected class
    
    return False

def detect_and_extract_text(image_path):
    # Load the YOLO detection model
    model = YOLO("detection.pt")
    # Initialize the OCR reader
    reader = easyocr.Reader(['en'])

    # Read the input image
    image = cv2.imread(image_path)

    # Perform object detection
    results = model(image_path)

    # Dictionary to store extracted fields
    extracted_data = {}

    # Process each detection result (bounding boxes)
    for result in results[0].boxes.data.tolist():
        x1, y1, x2, y2, confidence, class_id = map(int, result[:6])
        field_class = model.names[class_id]  # Get class name (e.g., 'Name', 'UID', 'Address')

        # Crop the detected region
        cropped_roi = image[y1:y2, x1:x2]

        # Convert cropped ROI to grayscale for OCR
        gray_roi = cv2.cvtColor(cropped_roi, cv2.COLOR_BGR2GRAY)

        # Use EasyOCR to extract text
        text = reader.readtext(gray_roi, detail=0)  # detail=0 returns only the text

        # Save the text to the extracted_data dictionary
        extracted_data[field_class] = ' '.join(text)

    return extracted_data

def process_folder(folder_path):
    results = {}
    # Dictionary to store aggregated results
    aggregated_results = {}

    # Iterate through all images in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg')):  # Only process image files
            image_path = os.path.join(folder_path, filename)

            #print(f"Processing image: {filename}")

            # Extract the base serial number
            base_serial_number = re.sub(r'(_\d+)?\.\w+$', '', filename)

            # Step 1: Classification
            if classify_document(image_path):
                #print(f"{filename} classified as Aadhaar card.")

                # Step 2: Detection and OCR
                extracted_data = detect_and_extract_text(image_path)

                if extracted_data:
                    if base_serial_number not in aggregated_results:
                        aggregated_results[base_serial_number] = {
                            "status": "Aadhar",
                            "data": extracted_data
                        }
                    else:
                        # Merge the extracted data, excluding duplicates
                        for key, value in extracted_data.items():
                            if key not in aggregated_results[base_serial_number]["data"]:
                                aggregated_results[base_serial_number]["data"][key] = value
                else:
                    if base_serial_number not in aggregated_results:
                        aggregated_results[base_serial_number] = {
                            "status": "Non Aadhar",
                            "message": "Failed to extract text.",
                            "data": {}  # Ensure the 'data' key is present
                        }
                    else:
                        aggregated_results[base_serial_number]["status"] = "Non Aadhar"
                        aggregated_results[base_serial_number]["message"] = "Failed to extract text."
                        aggregated_results[base_serial_number]["data"] = {}  # Ensure the 'data' key is present
            else:
                #print(f"WARNING: {filename} is not an Aadhaar card.")
                if base_serial_number not in aggregated_results:
                    aggregated_results[base_serial_number] = {
                        "status": "Non Aadhar",
                        "message": "Not an Aadhaar card.",
                        "data": {}  # Ensure the 'data' key is present
                    }
                else:
                    aggregated_results[base_serial_number]["status"] = "Non Aadhar"
                    aggregated_results[base_serial_number]["message"] = "Not an Aadhaar card."
                    aggregated_results[base_serial_number]["data"] = {}  # Ensure the 'data' key is present

    return aggregated_results

def process_file(file_path):
    #print(f"Processing file: {file_path}")

    # Extract the base serial number
    base_serial_number = re.sub(r'(_\d+)?\.\w+$', '', os.path.basename(file_path))

    # Step 1: Classification
    if classify_document(file_path):
        #print(f"{file_path} classified as Aadhaar card.")

        # Step 2: Detection and OCR
        extracted_data = detect_and_extract_text(file_path)

        if extracted_data:
            result = {
                "status": "Aadhar",
                "data": extracted_data
            }
        else:
            result = {
                "status": "Non Aadhar",
                "message": "Failed to extract text.",
                "data": {}
            }
    else:
        #print(f"WARNING: {file_path} is not an Aadhaar card.")
        result = {
            "status": "Non Aadhar",
            "message": "Not an Aadhaar card.",
            "data": {}
        }

    return {base_serial_number: result}

# if __name__ == "__main__":
#     # Test with a folder or a single file
#     mode = input("Enter mode (file/folder): ").strip().lower()
#     path = input("Enter the path: ").strip()

#     if mode == "folder":
#         result = process_folder(path)
#     elif mode == "file":
#         result = process_file(path)
#     else:
#         #print("Invalid mode. Please enter 'file' or 'folder'.")
#         exit()

#     # #print results
#     #print(result)
#     for serial_number, details in result.items():
#         #print(f"\nSerial Number: {serial_number}")
#         #print(f"Result: {details}")
