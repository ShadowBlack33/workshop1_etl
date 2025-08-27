
import pandas as pd

def extract_candidates(path_csv: str) -> pd.DataFrame:
    df = pd.read_csv(path_csv, sep=';')
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    df['application_date'] = pd.to_datetime(df['application_date'], errors='coerce')
    for col in ['first_name','last_name','email','country','seniority','technology']:
        df[col] = df[col].astype(str).str.strip()
    df['yoe'] = pd.to_numeric(df['yoe'], errors='coerce').fillna(0).astype(int)
    df['code_challenge_score'] = pd.to_numeric(df['code_challenge_score'], errors='coerce')
    df['technical_interview_score'] = pd.to_numeric(df['technical_interview_score'], errors='coerce')
    return df
