# address_matching.py

import re
from difflib import SequenceMatcher
filename = "output_data.xlsx"
ignore_terms = [
    "PO-", "PO", "Marg", "Peeth", "Veedhi", "Rd", "Lane", "NR", 
    "Beside", "Opposite", "OPP", "Behind", "near", "Enclave", 
    "Township", "Society", "Soc", "Towers", "Block", "S/o", "C/o", 
    "D/o", "W/o",
]

def remove_ignore_terms(address):
    """Remove stopwords and non-alphanumeric characters from the address."""
    if not isinstance(address, str):
        return ""
    # Remove ignore terms (case-insensitive)
    for term in ignore_terms:
        address = re.sub(r'\b' + re.escape(term) + r'\b', '', address, flags=re.IGNORECASE)
    # Remove non-alphanumeric characters and extra spaces
    address = re.sub(r'[^a-zA-Z0-9\s]', '', address)
    address = re.sub(r'\s+', ' ', address).strip()
    return address

def calculate_similarity(str1, str2):
    """Calculate the similarity score between two strings using SequenceMatcher."""
    return SequenceMatcher(None, str1, str2).ratio()

def address_matching(input_fields, extracted_address):
    # Clean both the input fields and the extracted address
    normalized_extracted_address = remove_ignore_terms(extracted_address)
    
    # Normalize input fields by cleaning each value
    normalized_input_fields = {field: remove_ignore_terms(value) for field, value in input_fields.items()}
    
    # Extract pincode
    input_pincode = input_fields.get('PINCODE', '').replace(' ', '')
    extracted_pincode = re.search(r'\d{6}', normalized_extracted_address)
    extracted_pincode = extracted_pincode.group(0) if extracted_pincode else ''
    
    # Pincode Matching
    pincode_score = 100 if input_pincode == extracted_pincode else 0
    
    # Split the extracted address into a list of words/parts
    extracted_parts = normalized_extracted_address.split()
    
    # Initialize a dictionary to store the scores for each field
    field_scores = {}
    
    # Compare each part of the extracted address to the corresponding input field
    for field, input_value in normalized_input_fields.items():
        field_score = 0
        # Check similarity for each part of the extracted address
        for part in extracted_parts:
            part_score = calculate_similarity(part, input_value)
            if part_score > field_score:
                field_score = part_score
        
        # Store the field score regardless of threshold
        field_scores[field] = round(field_score * 100, 2)
    
    # Calculate the overall match score (average of field scores above the threshold)
    included_field_scores = [score for score in field_scores.values() if score >= 70]
    if included_field_scores:
        total_score = sum(included_field_scores)
        average_score = total_score / len(included_field_scores)
    else:
        average_score = 0

    # Check final match: If pincode matches and overall score is above 70, it's a match
    final_match = average_score >= 70 and pincode_score == 100
    
    return field_scores, average_score, final_match


import pandas as pd

def process_and_match_addresses(input_file, output_file):
    # Step 1: Read the Excel file
    df = pd.read_excel(input_file)

    # Step 2: Select relevant columns
    selected_columns = df[["SrNo", "House Flat Number", "Street Road Name", "Town", "City", "Floor Number", "Country", "PINCODE", "Premise Building Name", "Landmark", "State", "Address Extracted From OVD"]]

    # Step 3: Create input data dictionary
    excel_data = {}
    for index, row in selected_columns.iterrows():
        input_fields_1 = {
            'House Flat Number': str(row['House Flat Number']),
            'Town': str(row['Town']),
            'Street Road Name': str(row['Street Road Name']),
            'City': str(row['City']),
            'Floor Number': str(row['Floor Number']),
            'PINCODE': str(row['PINCODE']),
            'Premise Building Name': str(row['Premise Building Name']),
            'Landmark': str(row['Landmark']),
            'State': str(row['State'])
        }
        excel_data[row["SrNo"]] = input_fields_1

    # Step 4: Initialize lists to store results
    house_flat_number_matches = []
    street_road_name_matches = []
    city_matches = []
    floor_number_matches = []
    pincode_matches = []
    premise_building_name_matches = []
    landmark_matches = []
    state_matches = []
    final_address_matches = []
    final_address_match_scores = []

    # Step 5: Iterate over excel_data and use the "Address Extracted From OVD" column
    for sr_no, input_addr in excel_data.items():
        extracted_addr = selected_columns[selected_columns["SrNo"] == sr_no]["Address Extracted From OVD"].values[0]
        if extracted_addr:
            field_scores_1, average_score_1, final_match_1 = address_matching(input_addr, extracted_addr)
            house_flat_number_matches.append(field_scores_1['House Flat Number'])
            street_road_name_matches.append(field_scores_1['Street Road Name'])
            city_matches.append(field_scores_1['City'])
            floor_number_matches.append(field_scores_1['Floor Number'])
            pincode_matches.append(field_scores_1['PINCODE'])
            premise_building_name_matches.append(field_scores_1['Premise Building Name'])
            landmark_matches.append(field_scores_1['Landmark'])
            state_matches.append(field_scores_1['State'])
            final_address_matches.append(final_match_1)
            final_address_match_scores.append(round(average_score_1, 2))
        else:
            house_flat_number_matches.append('0')
            street_road_name_matches.append('0')
            city_matches.append('0')
            floor_number_matches.append('0')
            pincode_matches.append('0')
            premise_building_name_matches.append('0')
            landmark_matches.append('0')
            state_matches.append('0')
            final_address_matches.append(False)
            final_address_match_scores.append('0')

    # Step 6: Update the original DataFrame with the new columns
    df['House Flat Number Match Score'] = house_flat_number_matches
    df['Street Road Name Match Score'] = street_road_name_matches
    df['City Match Score'] = city_matches
    df['Floor Number Match Score'] = floor_number_matches
    df['PINCODE Match Score'] = pincode_matches
    df['Premise Building Name Match Score'] = premise_building_name_matches
    df['Landmark Match Score'] = landmark_matches
    df['State Match Score'] = state_matches
    df['Final Address Match'] = final_address_matches
    df['Final Address Match Score'] = final_address_match_scores

    # Step 7: Save the updated DataFrame to output.xlsx
    df.to_excel(output_file, index=False)

    print("Output saved to output_data.xlsx")

# Example usage

