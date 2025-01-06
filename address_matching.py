import re
from difflib import SequenceMatcher
import pandas as pd
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Define the filename and ignore terms
filename = "output_data.xlsx"
ignore_terms = [
    "PO-", "PO", "Marg", "Peeth", "Veedhi", "Rd", "Lane", "NR", 
    "Beside", "Opposite", "OPP", "Behind", "near", "Enclave", 
    "Township", "Society", "Soc", "Towers", "Block", "S/o", "C/o", 
    "D/o", "W/o",
]

# Define a dictionary of common synonyms and abbreviations
synonyms = {
    "St": "Street",
    "Rd": "Road",
    "Ave": "Avenue",
    "Blvd": "Boulevard",
    "Ln": "Lane",
    "Dr": "Drive",
    "Pl": "Place",
    "Ct": "Court",
    "Ter": "Terrace",
    "Wy": "Way",
    "Cir": "Circle",
    "Pkwy": "Parkway",
    "Hwy": "Highway",
}

def normalize_text(text):
    """Normalize the text by removing ignore terms, lemmatizing, and handling synonyms."""
    if not isinstance(text, str) or not text.strip():
        return ""
    # Remove ignore terms (case-insensitive)
    for term in ignore_terms:
        text = re.sub(r'\b' + re.escape(term) + r'\b', '', text, flags=re.IGNORECASE)
    # Replace synonyms
    for short, full in synonyms.items():
        text = re.sub(r'\b' + re.escape(short) + r'\b', full, text, flags=re.IGNORECASE)
    # Tokenize and lemmatize
    tokens = word_tokenize(text.lower())
    normalized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    # Remove non-alphanumeric characters and extra spaces
    normalized_text = ' '.join(normalized_tokens)
    normalized_text = re.sub(r'[^a-zA-Z0-9\s]', '', normalized_text)
    normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
    return normalized_text

def calculate_similarity(str1, str2):
    """Calculate the similarity score between two strings using SequenceMatcher."""
    if not str1 or not str2:
        return 0.0
    return SequenceMatcher(None, str1, str2).ratio()

def address_matching(input_fields, extracted_address):
    # Clean both the input fields and the extracted address
    normalized_extracted_address = normalize_text(extracted_address)
    
    # Normalize input fields by cleaning each value
    normalized_input_fields = {field: normalize_text(value) for field, value in input_fields.items()}
    
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
    
    # Define weights for different fields
    weights = {
        'House Flat Number': 1.0,
        'Street Road Name': 1.0,
        'City': 1.0,
        'Floor Number': 0.5,
        'PINCODE': 1.0,
        'Premise Building Name': 0.8,
        'Landmark': 0.5,
        'State': 1.0,
    }
    
    # Compare each part of the extracted address to the corresponding input field
    for field, input_value in normalized_input_fields.items():
        if field not in weights:
            print(f"Warning: Field '{field}' not found in weights dictionary. Using default weight of 1.0.")
            weights[field] = 1.0
        
        field_score = 0
        if input_value:  # Only proceed if the input value is not empty
            # Check similarity for each part of the extracted address
            for part in extracted_parts:
                part_score = calculate_similarity(part, input_value)
                if part_score > field_score:
                    field_score = part_score
        
        # Apply weight to the field score
        field_score *= weights[field]
        
        # Store the field score regardless of threshold
        field_scores[field] = round(field_score * 100, 2)
    
    # Calculate the overall match score (weighted average of field scores above the threshold)
    included_field_scores = [score for score in field_scores.values() if score >= 70]
    if included_field_scores:
        total_score = sum(included_field_scores)
        average_score = total_score / len(included_field_scores)
    else:
        average_score = 0

    # Check final match: If pincode matches and overall score is above 70, it's a match
    final_match = average_score >= 70 and pincode_score == 100
    
    return field_scores, average_score, final_match

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
            house_flat_number_matches.append(field_scores_1.get('House Flat Number', 0))
            street_road_name_matches.append(field_scores_1.get('Street Road Name', 0))
            city_matches.append(field_scores_1.get('City', 0))
            floor_number_matches.append(field_scores_1.get('Floor Number', 0))
            pincode_matches.append(field_scores_1.get('PINCODE', 0))
            premise_building_name_matches.append(field_scores_1.get('Premise Building Name', 0))
            landmark_matches.append(field_scores_1.get('Landmark', 0))
            state_matches.append(field_scores_1.get('State', 0))
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
# if __name__ == "__main__":
#     process_and_match_addresses("test_data.xlsx", "output_data.xlsx")