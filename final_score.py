import pandas as pd

def put_final_result(filename):
    df = pd.read_excel(filename)

    for i in range(len(df)):
        # Calculate the score
        uid_score = df.loc[i, 'UID Match Score']
        address_score1 = df.loc[i, 'Final Address Match Score']
        name_score = df.loc[i, 'Name match percentage']
        
        score = (float(uid_score) + float(address_score1) + float(name_score)) / 3
        
        # Determine Overall Match
        if score > 90:
            df.loc[i, 'Overall Match'] = True
        else:
            df.loc[i, 'Overall Match'] = False
        
        # Determine Final Remarks
        if float(uid_score) == 100 and float(address_score1) > 80 and float(name_score) >= 90:
            df.loc[i, 'Final Remarks'] = "Aadhar Card Verified Successfully."
        elif float(uid_score) < 100 or float(address_score1) < 80 or float(name_score) < 85:
            df.loc[i, 'Final Remarks'] = "Fields missing. Couldn't Verify Your aadhar card."
        
        # Check for missing fields
        missing_fields = []
        if pd.isna(uid_score) or float(uid_score) == 0:
            missing_fields.append('UID')
        if pd.isna(address_score1) or float(address_score1) == 0:
            missing_fields.append('Address')
        if pd.isna(name_score) or float(name_score) == 0:
            missing_fields.append('Name')
        
        if missing_fields:
            if len(missing_fields) == 3:
                df.loc[i, 'Final Remarks'] = "The Image is not aadhar card."
            else:
                df.loc[i, 'Final Remarks'] = f"Couldn't Verify Your aadhar card.Couldn't Verify : {', '.join(missing_fields)}."
    
    df.to_excel(filename, index=False)

# Example usage
#put_final_result('output_data.xlsx')