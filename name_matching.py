from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd

# Function to remove stop words from a name
def remove_stop_words(name, stop_words):
    return ' '.join([word for word in name.split() if word.lower() not in stop_words])

# Function to match names with rules and fuzzy logic
def name_match(input_name, extracted_name, stop_words):
    input_name_clean = remove_stop_words(input_name, stop_words).strip().lower()
    extracted_name_clean = remove_stop_words(extracted_name, stop_words).strip().lower()

    if input_name_clean == extracted_name_clean:
        return 100.0, True

    input_parts = input_name_clean.split()
    extracted_parts = extracted_name_clean.split()

    if len(input_parts) <= len(extracted_parts) and all(part in extracted_parts for part in input_parts):
        return 100.0, True

    if set(input_parts) == set(extracted_parts):
        return 100.0, True

    match_ratio = fuzz.ratio(input_name_clean, extracted_name_clean)
    match_partial_ratio = fuzz.partial_ratio(input_name_clean, extracted_name_clean)
    match_token_sort_ratio = fuzz.token_sort_ratio(input_name_clean, extracted_name_clean)
    match_token_set_ratio = fuzz.token_set_ratio(input_name_clean, extracted_name_clean)

    match_percentage = (match_ratio + match_partial_ratio + match_token_sort_ratio + match_token_set_ratio) / 4.0
    return match_percentage, match_percentage >= 75.0

# Main function to process the Excel file
def process_names(input_file, output_file, stop_words=None):
    if stop_words is None:
        stop_words = [
            "dr", "mr.", "mrs.", "smt.", "ms.", "col.", "professor",
            "jt1", "jt", "prof.", "huf", "minor", "bhai",
        ]

    try:
        df = pd.read_excel(input_file)

        name_match_percentages = []
        name_match_scores = []

        for index, row in df.iterrows():
            input_name = row.get('Name')
            extracted_name = row.get('Name extracted from OVD')

            if pd.isna(input_name) or pd.isna(extracted_name):
                name_match_percentages.append(0.0)
                name_match_scores.append(False)
            else:
                match_percentage, match_score = name_match(input_name, extracted_name, stop_words)
                name_match_percentages.append(match_percentage)
                name_match_scores.append(match_score if match_percentage >= 75 else False)

        df['Name match percentage'] = name_match_percentages
        df['Name Match Score'] = name_match_scores

        df.to_excel(output_file, index=False)
        print(f"Output saved to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
#process_names("output_data.xlsx", "output_data.xlsx")
