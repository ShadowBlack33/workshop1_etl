import pandas as pd
import unicodedata, re

def _slug(s: str) -> str:
    if s is None:
        return s
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def _canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    norm = {c: _slug(c) for c in df.columns}

    syn = [
        ({"first_name","firstname","first"}, "first_name"),
        ({"last_name","lastname","last"}, "last_name"),
        ({"email","e_mail","mail","correo"}, "email"),
        ({"seniority","seniority_level","nivel","level"}, "seniority"),
        ({"yoe","years_of_experience","years_experience","experience_years","years","anios_experiencia","anos_experiencia"}, "yoe"),
        ({"technology","tech","stack","tecnologia","tecnologia"}, "technology"),
        ({"country","pais"}, "country"),
        ({"application_date","applied_at","date","fecha","fecha_aplicacion"}, "application_date"),
        ({"code_challenge_score","coding_challenge_score","challenge_score","code_score","prueba_codigo","prueba_de_codigo"}, "code_challenge_score"),
        ({"technical_interview_score","interview_score","technical_score","tech_interview","tech_score","prueba_tecnica"}, "technical_interview_score"),
    ]

    def canon(n: str) -> str:
        for names, target in syn:
            if n in names:
                return target
        return n

    new_cols = [canon(norm[c]) for c in df.columns]
    df = df.copy()
    df.columns = new_cols
    return df

def _clean_str(x):
    if pd.isna(x):
        return x
    return str(x).strip()

def transform(df_raw_from_dw: pd.DataFrame) -> pd.DataFrame:
    df = _canonicalize_columns(df_raw_from_dw)

    for col in ["first_name","last_name","email","seniority","technology","country","application_date"]:
        if col in df.columns:
            df[col] = df[col].apply(_clean_str)

    df["yoe"] = pd.to_numeric(df.get("yoe"), errors="coerce").fillna(0).astype(int)
    df["code_challenge_score"] = pd.to_numeric(df.get("code_challenge_score"), errors="coerce")
    df["technical_interview_score"] = pd.to_numeric(df.get("technical_interview_score"), errors="coerce")

    if "application_date" in df.columns:
        df["application_date"] = pd.to_datetime(df["application_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    df["hired"] = (
        (df.get("code_challenge_score", pd.Series(dtype=float)) >= 7) &
        (df.get("technical_interview_score", pd.Series(dtype=float)) >= 7)
    ).astype(int)

    cols = [
        "first_name","last_name","email","seniority","yoe",
        "technology","country","application_date",
        "code_challenge_score","technical_interview_score","hired"
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df[cols]
