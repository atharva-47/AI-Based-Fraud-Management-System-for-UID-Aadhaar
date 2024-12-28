import pandas as pd

def get_result(results):
    df = pd.read_excel("input.xlsx")

    
    rows = []
    for key, value in results.items():
        row = {
            'SrNO': key,
            'status': value.get('status', None),
            'uid': value.get('data', {}).get('uid', None),
            'name': value.get('data', {}).get('name', None),
            'address': value.get('data', {}).get("address'", None)
        }
        rows.append(row)

    df2 = pd.DataFrame(rows)

    for i in range(len(df2)):
        
        if df2.loc[i,'uid'] is not None:
            df.loc[i,'UID Extracted From OVD'] = float(str(df2.loc[i,'uid']).replace(" ",""))
        
        if df2.loc[i,'address'] is not None:
            df.loc[i,'Address Extracted From OVD'] = df2.loc[i,'address']

        df.loc[i,'Name extracted from OVD'] = df2.loc[i,'name']

        df['Document Type'][i] = df2['status'][i]

    # Save the DataFrame to an Excel file
    output_file = 'output_data.xlsx'
    df.to_excel(output_file, index=False)

    #print(f"Data saved to {output_file}")

    return output_file
