import pandas as pd

def extract_candidates(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path, sep=";", encoding="utf-8")
