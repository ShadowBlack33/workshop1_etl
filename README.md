
# Workshop-1 — ETL y Data Warehouse (Star Schema)

Proyecto con **un solo entrypoint** (`main.py`) que ejecuta: **ETL → KPIs → gráficas**.

## Ejecutar
```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux/Mac
# source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

## Regla HIRED
Se considera **contratado** si: `Code Challenge Score ≥ 7` **y** `Technical Interview Score ≥ 7`.

## Esquema Estrella (Dimensiones y Hechos)
- **DimCandidate** (candidate_id, first_name, last_name, email, seniority, yoe)
- **DimTechnology** (technology_id, technology)
- **DimCountry** (country_id, country)
- **DimDate** (date_id, full_date, year, month, day)
- **FactHires** (scores, hired, FKs a dims)

KPIs y consultas en `sql/queries.sql`. Salidas gráficas en `visuals/`.
