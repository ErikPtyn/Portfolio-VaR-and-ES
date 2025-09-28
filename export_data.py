import numpy as np, pandas as pd, yfinance as yf

START_DATE="2024-07-19"
POS_CSV="positions_user_semicolon.csv"

dfp=pd.read_csv(POS_CSV,sep=";")
tickers=dfp["Ticker"].astype(str).str.upper().tolist()

d=yf.download(tickers,start=START_DATE,auto_adjust=True,progress=False,group_by="ticker")
cols=[]
for tk in tickers:
    try: cols.append(d[tk]["Close"].rename(tk))
    except: pass
P=pd.concat(cols,axis=1).dropna(how="all")
P.to_csv("prices_2024-07-19_to_today.csv",sep=";")
print("OK prices_2024-07-19_to_today.csv",P.shape)
