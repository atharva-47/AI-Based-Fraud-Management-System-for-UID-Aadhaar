import pandas as pd
def put_final_result(filename):
    df = pd.read_excel(filename)

    for i in range(len(df)):
        score = (float(df.loc[i,'UID Match Score']) + float(df.loc[i,'Final Address Match Score']) + float(df.loc[i,'Final Address Match Score'])) / 3
        if score > 90 :
            df.loc[i,'Overall Match'] = True
        else:
            df.loc[i,'Overall Match'] = False
        if float(df.loc[i,'UID Match Score']) == 100 and float(df.loc[i,'Final Address Match Score']) > 80 and float(df.loc[i,'Final Address Match Score']) >= 90:
            df.loc[i,'Final Remarks'] = "Aadhar Card Verified Successfully ."
        if float(df.loc[i,'UID Match Score']) < 100 or float(df.loc[i,'Final Address Match Score']) < 80 or float(df.loc[i,'Final Address Match Score']) < 85:
            df.loc[i,'Final Remarks'] = "Fields missing .Couldn't Verify Your aadhar card."
        if float(df.loc[i,'UID Match Score']) == 0 and float(df.loc[i,'Final Address Match Score']) == 0 and float(df.loc[i,'Final Address Match Score']) == 0:
            df.loc[i,'Final Remarks'] = "The Image is not aadhar card."
    df.to_excel(filename, index=False)