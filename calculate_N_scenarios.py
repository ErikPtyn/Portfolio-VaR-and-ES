import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent
candidates = list(base.glob("prices_2024-07-19_to_today.*"))
if not candidates:
    raise FileNotFoundError("Fichier 'prices_2024-07-19_to_today.(xlsx/xls/csv)' introuvable dans ce dossier.")
file = candidates[0]

if file.suffix.lower() in [".xlsx", ".xls"]:
    df = pd.read_excel(file)
elif file.suffix.lower() == ".csv":
    df = pd.read_csv(file)
else:
    raise ValueError("Extension non prise en charge.")

non_asset_cols = {"Date"}
tickers = [c for c in df.columns if c not in non_asset_cols]

gross_returns = df[tickers].div(df[tickers].shift(1)).dropna()
last_prices = df.loc[df.index.max(), tickers]

scenario_prices = gross_returns.mul(last_prices, axis=1)
scenario_prices.index = range(1, len(scenario_prices) + 1)
scenario_prices.index.name = "Scenario"
