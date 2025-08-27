
import pandas as pd
HIRED_THRESHOLD = 7

def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['country'] = df['country'].replace({'USA':'United States','U.S.A.':'United States','US':'United States','Brasil':'Brazil'})
    df['hired'] = ((df['code_challenge_score']>=HIRED_THRESHOLD) & (df['technical_interview_score']>=HIRED_THRESHOLD)).astype(int)
    bins = [-1, 2, 5, 10, 1000]; labels = ['0-2','3-5','6-10','11+']
    df['yoe_band'] = pd.cut(df['yoe'], bins=bins, labels=labels)
    return df
