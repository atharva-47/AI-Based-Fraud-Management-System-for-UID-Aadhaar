import pandas as pd
from difflib import SequenceMatcher

def uid_matching(filename):
    df = pd.read_excel(filename)
        
    for i in range(len(df)):
        
        if (df.loc[i,'UID'] == df.loc[i,'UID Extracted From OVD']):
            #print(True)
            df.loc[i,'UID Match Score'] = 100
        else:
            #print(False)
            df.loc[i,'UID Match Score'] = SequenceMatcher(None,str(df.loc[i,'UID']), str(df.loc[i,'UID Extracted From OVD'])).ratio() * 100

    df.to_excel(filename)