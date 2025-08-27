
import sqlite3, pandas as pd

DDL=[
"""CREATE TABLE IF NOT EXISTS DimDate(date_id INTEGER PRIMARY KEY, full_date TEXT UNIQUE, year INT, month INT, day INT);""",
"""CREATE TABLE IF NOT EXISTS DimTechnology(technology_id INTEGER PRIMARY KEY, technology TEXT UNIQUE);""",
"""CREATE TABLE IF NOT EXISTS DimCountry(country_id INTEGER PRIMARY KEY, country TEXT UNIQUE);""",
"""CREATE TABLE IF NOT EXISTS DimCandidate(candidate_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT UNIQUE, seniority TEXT, yoe INT);""",
"""CREATE TABLE IF NOT EXISTS FactHires(fact_id INTEGER PRIMARY KEY, candidate_id INT, technology_id INT, country_id INT, date_id INT, code_challenge_score REAL, technical_interview_score REAL, hired INT);"""
]

def ensure_schema(conn):
    c=conn.cursor()
    for ddl in DDL: c.execute(ddl)
    conn.commit()

def _map(conn, table, key, idc):
    return {r[1]: r[0] for r in conn.execute(f"SELECT {idc},{key} FROM {table}")}

def load_star(conn, df: pd.DataFrame):
    ensure_schema(conn)
    c=conn.cursor()
    # Dims
    for t in pd.Series(df['technology']).dropna().unique():
        c.execute("INSERT OR IGNORE INTO DimTechnology(technology) VALUES(?)", (str(t),))
    for co in pd.Series(df['country']).dropna().unique():
        c.execute("INSERT OR IGNORE INTO DimCountry(country) VALUES(?)", (str(co),))
    for d in pd.to_datetime(df['application_date']).dt.strftime('%Y-%m-%d').unique():
        y,m,day=map(int,d.split('-'))
        c.execute("INSERT OR IGNORE INTO DimDate(full_date,year,month,day) VALUES(?,?,?,?)", (d,y,m,day))
    for _, r in df[['first_name','last_name','email','seniority','yoe']].drop_duplicates('email').iterrows():
        c.execute("INSERT OR IGNORE INTO DimCandidate(first_name,last_name,email,seniority,yoe) VALUES(?,?,?,?,?)",
                  (r['first_name'], r['last_name'], r['email'], r['seniority'], int(r['yoe'])))
    conn.commit()
    # Maps
    tech=_map(conn,'DimTechnology','technology','technology_id')
    country=_map(conn,'DimCountry','country','country_id')
    date=_map(conn,'DimDate','full_date','date_id')
    cand=_map(conn,'DimCandidate','email','candidate_id')
    # Facts
    rows=[(cand.get(r['email']), tech.get(r['technology']), country.get(r['country']),
           date.get(pd.to_datetime(r['application_date']).strftime('%Y-%m-%d')),
           float(r['code_challenge_score']), float(r['technical_interview_score']), int(r['hired']))
          for _, r in df.iterrows()]
    c.executemany("""INSERT INTO FactHires(candidate_id,technology_id,country_id,date_id,
                     code_challenge_score,technical_interview_score,hired)
                     VALUES(?,?,?,?,?,?,?)""", rows)
    conn.commit()
