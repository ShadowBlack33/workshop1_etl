# TODO sale del DW; el CSV solo se usa para poblar el DW en run_etl()

import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import plotly.express as px

from src.extract import extract_candidates
from src.transform import transform
from src.load import load_star

# Rutas
DATASET_PATH = os.environ.get("INPUT_CSV", "data/candidates.csv")
SQLITE_PATH  = os.environ.get("SQLITE_PATH", "dw/workshop1_dw.sqlite")

console = Console()

# Consultas KPI (todas contra el DW)
SQLS = {
    "kpi_hires_by_technology": """
        SELECT t.technology, SUM(f.hired) AS hires, COUNT(*) AS total,
               ROUND(100.0*SUM(f.hired)/COUNT(*),2) AS hire_rate_pct
        FROM FactHires f
        JOIN DimTechnology t ON f.technology_id = t.technology_id
        GROUP BY t.technology ORDER BY hires DESC;
    """,
    "kpi_hires_by_year": """
        SELECT d.year, SUM(f.hired) AS hires, COUNT(*) AS total,
               ROUND(100.0*SUM(f.hired)/COUNT(*),2) AS hire_rate_pct
        FROM FactHires f
        JOIN DimDate d ON f.date_id = d.date_id
        GROUP BY d.year ORDER BY d.year;
    """,
    "kpi_hires_by_seniority": """
        SELECT c.seniority, SUM(f.hired) AS hires, COUNT(*) AS total,
               ROUND(100.0*SUM(f.hired)/COUNT(*),2) AS hire_rate_pct
        FROM FactHires f
        JOIN DimCandidate c ON f.candidate_id = c.candidate_id
        GROUP BY c.seniority ORDER BY hires DESC;
    """,
    "kpi_hires_country_year": """
        SELECT d.year, co.country, SUM(f.hired) AS hires
        FROM FactHires f
        JOIN DimDate d ON f.date_id = d.date_id
        JOIN DimCountry co ON f.country_id = co.country_id
        WHERE co.country IN ('United States','Brazil','Colombia','Ecuador')
        GROUP BY d.year, co.country ORDER BY d.year, hires DESC;
    """,
    "extra_hire_rate_by_country": """
        SELECT co.country, SUM(f.hired) AS hires, COUNT(*) AS total,
               ROUND(100.0*SUM(f.hired)/COUNT(*),2) AS hire_rate_pct
        FROM FactHires f JOIN DimCountry co ON f.country_id = co.country_id
        GROUP BY co.country ORDER BY hire_rate_pct DESC;
    """,
    "extra_avg_scores_by_hired": """
        SELECT hired,
               ROUND(AVG(code_challenge_score),2) AS avg_code_challenge,
               ROUND(AVG(technical_interview_score),2) AS avg_tech_interview
        FROM FactHires GROUP BY hired ORDER BY hired DESC;
    """
}

# Títulos cortos (ES)
TITULOS_ES = {
    "kpi_hires_by_technology": "Contrataciones por tecnología",
    "kpi_hires_by_year": "Contrataciones por año",
    "kpi_hires_by_seniority": "Contrataciones por seniority",
    "kpi_hires_country_year": "Contrataciones por país (por año)",
    "extra_hire_rate_by_country": "Tasa por país (%)",
    "extra_avg_scores_by_hired": "Promedios de puntajes (Sí vs No)",
}

# ---------- Utilidades ----------
def query_df(sql_key: str) -> pd.DataFrame:
    conn = sqlite3.connect(SQLITE_PATH)
    try:
        return pd.read_sql(SQLS[sql_key], conn)
    finally:
        conn.close()

def rich_print_df(df: pd.DataFrame, title: str, max_rows: int | None = None):
    """Imprime DataFrame como tabla Rich con formateo básico."""
    if max_rows:
        df = df.head(max_rows)
    table = Table(title=title, show_lines=False, header_style="bold")
    for col in df.columns:
        table.add_column(str(col))
    for _, row in df.iterrows():
        vals = []
        for v in row:
            if isinstance(v, float):
                # redondeo suave
                vals.append(f"{v:,.2f}")
            else:
                vals.append(str(v))
        table.add_row(*vals)
    console.print(table)

def ensure_dirs():
    os.makedirs("visuals", exist_ok=True)
    os.makedirs("docs", exist_ok=True)  # para GitHub Pages (HTML)

# ---------- Flujo ----------
def run_etl():
    console.rule("[bold]ETL (poblar DW desde CSV)")
    df = extract_candidates(DATASET_PATH)
    df_t = transform(df)
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    try:
        load_star(conn, df_t)
    finally:
        conn.close()
    console.print(Panel.fit(f"DW listo en: [bold]{SQLITE_PATH}[/bold]"))

def print_kpis():
    console.rule("[bold]KPIs (desde el DW)")
    orden = [
        "kpi_hires_by_technology",
        "kpi_hires_by_year",
        "kpi_hires_by_seniority",
        "kpi_hires_country_year",
        "extra_hire_rate_by_country",
        "extra_avg_scores_by_hired",
    ]
    for key in orden:
        titulo = TITULOS_ES.get(key, key)
        df = query_df(key)

        # Renombrar/ordenar para que luzca mejor (sin cambiar la consulta)
        if key == "kpi_hires_by_technology":
            df = df.rename(columns={
                "technology":"Tecnología","hires":"Contrataciones",
                "total":"Total","hire_rate_pct":"Tasa_%"
            })
            df["Tasa_%"] = pd.to_numeric(df["Tasa_%"], errors="coerce").round(1)
            rich_print_df(df, f"{titulo} (Top 15)", max_rows=15)

        elif key == "kpi_hires_by_year":
            df = df.rename(columns={"year":"Año","hires":"Contrataciones","total":"Total","hire_rate_pct":"Tasa_%"})
            df["Tasa_%"] = pd.to_numeric(df["Tasa_%"], errors="coerce").round(1)
            df = df.sort_values("Año")
            rich_print_df(df, titulo)

        elif key == "kpi_hires_by_seniority":
            df = df.rename(columns={"seniority":"Seniority","hires":"Contrataciones","total":"Total","hire_rate_pct":"Tasa_%"})
            df["Seniority"] = df["Seniority"].fillna("Desconocido")
            df["Tasa_%"] = pd.to_numeric(df["Tasa_%"], errors="coerce").round(1)
            rich_print_df(df, titulo)

        elif key == "kpi_hires_country_year":
            if not df.empty:
                piv = df.pivot(index="year", columns="country", values="hires").fillna(0).astype(int)
                piv = piv.rename_axis(None, axis=1).rename_axis("Año", axis=0).sort_index().reset_index()
                rich_print_df(piv, titulo)
            else:
                console.print(Panel.fit("Sin datos para (United States, Brazil, Colombia, Ecuador)."))

        elif key == "extra_hire_rate_by_country":
            df = df.rename(columns={"country":"País","hires":"Contrataciones","total":"Total","hire_rate_pct":"Tasa_%"})
            df["Tasa_%"] = pd.to_numeric(df["Tasa_%"], errors="coerce").round(1)
            df = df.sort_values("Tasa_%", ascending=False).reset_index(drop=True)
            rich_print_df(df, f"{titulo} (Top 10)", max_rows=10)

        elif key == "extra_avg_scores_by_hired":
            df = df.replace({"hired": {1:"Sí", 0:"No"}})
            df = df.rename(columns={"hired":"Contratado","avg_code_challenge":"Prom_CC","avg_tech_interview":"Prom_Ent_Téc"})
            df["Prom_CC"] = pd.to_numeric(df["Prom_CC"], errors="coerce").round(2)
            df["Prom_Ent_Téc"] = pd.to_numeric(df["Prom_Ent_Téc"], errors="coerce").round(2)
            rich_print_df(df, titulo)

def save_charts():
    console.rule("[bold]Gráficas (desde el DW)")
    ensure_dirs()

    # 1) Tecnología (Top 10) — PNG + HTML
    df_tech = query_df("kpi_hires_by_technology")
    if not df_tech.empty:
        top = df_tech.nlargest(10, "hires")

        # PNG (Matplotlib)
        plt.figure(figsize=(9,5))
        plt.bar(top["technology"], top["hires"])
        plt.xticks(rotation=45, ha="right")
        plt.title("Contrataciones por tecnología (Top 10)")
        plt.ylabel("Contrataciones")
        plt.grid(True, axis="y", linestyle="--", alpha=0.4)
        plt.tight_layout()
        plt.savefig("visuals/contrataciones_tecnologia.png")
        plt.close()

        # HTML (Plotly)
        fig = px.bar(top, x="technology", y="hires", title="Contrataciones por tecnología (Top 10)")
        fig.write_html("docs/contrataciones_tecnologia.html", include_plotlyjs="cdn")

    # 2) Año — PNG + HTML
    df_year = query_df("kpi_hires_by_year")
    if not df_year.empty:
        df_year = df_year.sort_values("year")

        plt.figure(figsize=(9,5))
        plt.plot(df_year["year"], df_year["hires"], marker="o")
        plt.title("Contrataciones por año")
        plt.xlabel("Año"); plt.ylabel("Contrataciones")
        plt.grid(True, axis="y", linestyle="--", alpha=0.4)
        plt.tight_layout()
        plt.savefig("visuals/contrataciones_anio.png")
        plt.close()

        fig = px.line(df_year, x="year", y="hires", markers=True, title="Contrataciones por año")
        fig.write_html("docs/contrataciones_anio.html", include_plotlyjs="cdn")

    # 3) Seniority — PNG + HTML
    df_sen = query_df("kpi_hires_by_seniority")
    if not df_sen.empty:
        df_sen["seniority"] = df_sen["seniority"].fillna("Desconocido")
        df_sen = df_sen.sort_values("hires", ascending=False)

        plt.figure(figsize=(9,5))
        plt.bar(df_sen["seniority"], df_sen["hires"])
        plt.xticks(rotation=45, ha="right")
        plt.title("Contrataciones por seniority")
        plt.ylabel("Contrataciones")
        plt.grid(True, axis="y", linestyle="--", alpha=0.4)
        plt.tight_layout()
        plt.savefig("visuals/contrataciones_seniority.png")
        plt.close()

        fig = px.bar(df_sen, x="seniority", y="hires", title="Contrataciones por seniority")
        fig.write_html("docs/contrataciones_seniority.html", include_plotlyjs="cdn")

    # 4) País × Año — PNG + HTML
    df_cy = query_df("kpi_hires_country_year")
    if not df_cy.empty:
        piv = df_cy.pivot(index="year", columns="country", values="hires").sort_index()

        plt.figure(figsize=(9,5))
        for col in piv.columns:
            plt.plot(piv.index, piv[col], marker="o", label=col)
        plt.title("Contrataciones por país a lo largo de los años")
        plt.xlabel("Año"); plt.ylabel("Contrataciones")
        plt.legend(title="País", ncol=2, frameon=False)
        plt.grid(True, axis="y", linestyle="--", alpha=0.4)
        plt.tight_layout()
        plt.savefig("visuals/contrataciones_pais_anio.png")
        plt.close()

        fig = px.line(df_cy, x="year", y="hires", color="country", markers=True,
                      title="Contrataciones por país a lo largo de los años")
        fig.write_html("docs/contrataciones_pais_anio.html", include_plotlyjs="cdn")

    console.print(Panel.fit("PNG en [bold]visuals/[/bold] • HTML en [bold]docs/[/bold] (sirve para GitHub Pages)"))

if __name__ == "__main__":
    run_etl()
    print_kpis()
    save_charts()
    console.rule("[bold green]Listo[/bold green]")
