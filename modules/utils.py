import pandas as pd

def to_csv(df):
    return df.to_csv(index=False, sep=';', decimal=',', encoding='utf-8-sig')