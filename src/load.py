import pandas as pd
import sqlite3

DDL = [
    """
    CREATE TABLE IF NOT EXISTS CleanCandidates (
        first_name TEXT,
        last_name  TEXT,
        email      TEXT,
        seniority  TEXT,
        yoe        INTEGER,
        technology TEXT,
        country    TEXT,
        application_date TEXT,
        code_challenge_score REAL,
        technical_interview_score REAL,
        hired INTEGER
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DimCandidate (
        candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name  TEXT,
        email      TEXT UNIQUE,
        seniority  TEXT,
        yoe        INTEGER
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DimTechnology (
        technology_id INTEGER PRIMARY KEY AUTOINCREMENT,
        technology    TEXT UNIQUE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DimCountry (
        country_id INTEGER PRIMARY KEY AUTOINCREMENT,
        country    TEXT UNIQUE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DimDate (
        date_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        full_date TEXT UNIQUE,
        year      INTEGER,
        month     INTEGER,
        day       INTEGER
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS FactHires (
        fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,
        technology_id INTEGER,
        country_id INTEGER,
        date_id INTEGER,
        code_challenge_score REAL,
        technical_interview_score REAL,
        hired INTEGER,
        FOREIGN KEY(candidate_id) REFERENCES DimCandidate(candidate_id),
        FOREIGN KEY(technology_id) REFERENCES DimTechnology(technology_id),
        FOREIGN KEY(country_id) REFERENCES DimCountry(country_id),
        FOREIGN KEY(date_id) REFERENCES DimDate(date_id)
    );
    """,
]

DROP_ALL = """
DROP TABLE IF EXISTS FactHires;
DROP TABLE IF EXISTS DimCandidate;
DROP TABLE IF EXISTS DimTechnology;
DROP TABLE IF EXISTS DimCountry;
DROP TABLE IF EXISTS DimDate;
DROP TABLE IF EXISTS CleanCandidates;
DROP TABLE IF EXISTS RawCandidates;
"""

INDEXES = """
CREATE INDEX IF NOT EXISTS idx_fact_cand   ON FactHires(candidate_id);
CREATE INDEX IF NOT EXISTS idx_fact_tech   ON FactHires(technology_id);
CREATE INDEX IF NOT EXISTS idx_fact_ctry   ON FactHires(country_id);
CREATE INDEX IF NOT EXISTS idx_fact_date   ON FactHires(date_id);
"""

def reset_warehouse(conn: sqlite3.Connection) -> None:
    conn.executescript(DROP_ALL)
    cur = conn.cursor()
    for ddl in DDL:
        cur.execute(ddl)
    conn.commit()

def load_raw_candidates(conn: sqlite3.Connection, df_raw: pd.DataFrame) -> None:
    # Crea/actualiza la tabla RAW con las columnas EXACTAS del CSV
    df_raw.to_sql("RawCandidates", conn, if_exists="replace", index=False)

def load_clean_candidates(conn: sqlite3.Connection, df_clean: pd.DataFrame) -> None:
    df_clean.to_sql("CleanCandidates", conn, if_exists="replace", index=False)

def build_star_from_clean(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript("""
        DELETE FROM FactHires;
        DELETE FROM DimCandidate;
        DELETE FROM DimTechnology;
        DELETE FROM DimCountry;
        DELETE FROM DimDate;
    """)
    conn.commit()

    cur.executescript("""
        INSERT INTO DimCandidate (first_name,last_name,email,seniority,yoe)
        SELECT first_name,last_name,email,seniority,yoe
        FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY email ORDER BY email) AS rn
            FROM CleanCandidates
        ) WHERE rn=1 AND email IS NOT NULL;

        INSERT INTO DimTechnology(technology)
        SELECT DISTINCT technology FROM CleanCandidates WHERE technology IS NOT NULL;

        INSERT INTO DimCountry(country)
        SELECT DISTINCT country FROM CleanCandidates WHERE country IS NOT NULL;

        INSERT INTO DimDate(full_date, year, month, day)
        SELECT DISTINCT
            application_date,
            CAST(substr(application_date,1,4) AS INTEGER),
            CAST(substr(application_date,6,2) AS INTEGER),
            CAST(substr(application_date,9,2) AS INTEGER)
        FROM CleanCandidates
        WHERE application_date IS NOT NULL AND length(application_date)=10;
    """)

    cand_map = dict(conn.execute("SELECT email, candidate_id FROM DimCandidate;").fetchall())
    tech_map = dict(conn.execute("SELECT technology, technology_id FROM DimTechnology;").fetchall())
    country_map = dict(conn.execute("SELECT country, country_id FROM DimCountry;").fetchall())
    date_map = dict(conn.execute("SELECT full_date, date_id FROM DimDate;").fetchall())

    df = pd.read_sql("SELECT * FROM CleanCandidates;", conn)

    fact = pd.DataFrame({
        "candidate_id": df["email"].map(cand_map),
        "technology_id": df["technology"].map(tech_map),
        "country_id": df["country"].map(country_map),
        "date_id": df["application_date"].map(date_map),
        "code_challenge_score": pd.to_numeric(df["code_challenge_score"], errors="coerce"),
        "technical_interview_score": pd.to_numeric(df["technical_interview_score"], errors="coerce"),
        "hired": pd.to_numeric(df["hired"], errors="coerce").fillna(0).astype(int),
    }).dropna(subset=["candidate_id","technology_id","country_id","date_id"])

    fact.to_sql("FactHires", conn, if_exists="append", index=False)
    cur.executescript(INDEXES)
    conn.commit()
