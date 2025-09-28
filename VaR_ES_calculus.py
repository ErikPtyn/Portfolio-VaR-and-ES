import math, numpy as np, pandas as pd

VAL=7639.48
ALPHA=0.99
POS_CSV="positions_user_semicolon.csv"
PRICES_CSV="prices_2024-07-19_to_today.csv"

pos=pd.read_csv(POS_CSV,sep=";")
pos["Ticker"]=pos["Ticker"].str.upper()
pos["Weight"]=pos["Weight"]/pos["Weight"].sum()

P=pd.read_csv(PRICES_CSV,sep=";",index_col=0,parse_dates=True)
cols=[c for c in pos["Ticker"].tolist() if c in P.columns]
P=P[cols]

R=np.log(P/P.shift(1))
R=R.replace([np.inf,-np.inf],np.nan)

w=pos.set_index("Ticker").loc[cols,"Weight"]
wv=w.values
W=np.tile(wv,(len(R),1))
mask=~np.isnan(R.values)
W=W*mask
rowsum=W.sum(axis=1).reshape(-1,1)
rowsum[rowsum==0]=np.nan
W=W/rowsum
rp=np.nansum(R.values*W,axis=1)
rp=pd.Series(rp,index=R.index).dropna()
r1=np.exp(rp)-1.0

n=len(r1)
if n==0:
    raise SystemExit("Aucun rendement exploitable.")

q=np.quantile(r1,1-ALPHA)
var_pct=-q
es_pct=-(r1[r1<=q]).mean()

k=max(1,int(np.ceil((1-ALPHA)*n)))  
sorted_losses=np.sort(-r1.values)   
var_os_pct=sorted_losses[k-1] if k-1<len(sorted_losses) else np.nan

out=pd.DataFrame([
    {"alpha":ALPHA,"horizon":"1D","method":"Empirical quantile","VaR_pct":var_pct,"ES_pct":es_pct,"VaR_eur":VAL*var_pct,"ES_eur":VAL*es_pct},
    {"alpha":ALPHA,"horizon":"1D","method":f"Order-stat k={k} of n={n}","VaR_pct":var_os_pct,"ES_pct":np.nan,"VaR_eur":VAL*var_os_pct,"ES_eur":np.nan},
])
out.to_csv("var_es_99_from_prices.csv",index=False)
print(out.to_string(index=False))

worst=r1.nsmallest(min(10,n)).to_frame("return_1d")
worst["loss_%"]=-worst["return_1d"]*100
print(worst.round(4).to_string())
