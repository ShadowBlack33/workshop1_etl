# Workshop-1 · ETL → Data Warehouse (Star Schema) → KPIs & Charts

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](https://www.python.org/)
[![pandas](https://img.shields.io/badge/pandas-2.x-150458)](https://pandas.pydata.org/)
[![matplotlib](https://img.shields.io/badge/matplotlib-3.x-11557c)](https://matplotlib.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.x-3e4ba9)](https://plotly.com/python/)
[![Rich](https://img.shields.io/badge/Rich-Console_Formatting-3fb950)](https://github.com/Textualize/rich)

Individual **ETL project in Python** that builds a **Data Warehouse (SQLite)** with a **star schema** from a candidates dataset, then computes **KPIs** and generates **charts** (PNG & interactive HTML).  
> **Important:** *All metrics and charts are computed from the DW only.* The CSV is **only** used to populate the DW during the ETL.

---

## 🧭 Table of Contents
- [Goal](#goal)
- [Live Demo / Interactive Charts](#live-demo--interactive-charts)
- [Features](#features)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Requirements](#requirements)
- [Install & Run](#install--run)
- [KPIs](#kpis)
- [GitHub Pages](#github-pages)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 🎯 Goal
- Implement an **ETL pipeline** (Extract → Transform → Load).
- Model a **star schema** in **SQLite**.
- Compute **hiring KPIs** and **visualize** results.
- Publish **interactive charts** via **GitHub Pages**.

---

## 🌐 Live Demo / Interactive Charts
If GitHub Pages is enabled (see below), the site will be available at:

- **Site:** https://shadowblack33.github.io/workshop1_etl/

**Interactive HTML (Plotly) in `docs/`:**
- `contrataciones_tecnologia.html`
- `contrataciones_anio.html`
- `contrataciones_seniority.html`
- `contrataciones_pais_anio.html`

> Static **PNGs** are in `visuals/` for quick sharing.

---

## ✨ Features
- **ETL** with `pandas`.
- **DW in SQLite** with `Dim*` tables + `FactHires`.
- Centralized **SQL KPI queries** in `main.py`.
- **Pretty console KPIs** using **Rich**.
- **Charts**:
  - **PNG** (Matplotlib) → `visuals/`
  - **Interactive HTML** (Plotly) → `docs/` (for **GitHub Pages**)
- **DW-driven**: nothing is computed from the CSV directly.

---

## 🏗️ Architecture

### Star Schema (Mermaid)
```mermaid
erDiagram
    DimCandidate ||--o{ FactHires : candidate_id
    DimTechnology ||--o{ FactHires : technology_id
    DimCountry   ||--o{ FactHires : country_id
    DimDate      ||--o{ FactHires : date_id

    DimCandidate {
      int candidate_id PK
      string first_name
      string last_name
      string email
      string seniority
      int yoe
    }

    DimTechnology {
      int technology_id PK
      string technology
    }

    DimCountry {
      int country_id PK
      string country
    }

    DimDate {
      int date_id PK
      string full_date
      int year
      int month
      int day
    }

    FactHires {
      int fact_id PK
      int candidate_id FK
      int technology_id FK
      int country_id FK
      int date_id FK
      float code_challenge_score
      float technical_interview_score
      int hired
    }
````

---

## 📁 Repository Structure

```
workshop1_etl/
├─ data/
│  └─ candidates.csv          # (NOT committed) — only used to populate the DW
├─ dw/
│  └─ workshop1_dw.sqlite     # (generated) — the SQLite DW
├─ docs/                      # Interactive HTML (Plotly) → published via GitHub Pages
├─ sql/
│  └─ queries.sql
├─ src/
│  ├─ __init__.py
│  ├─ extract.py
│  ├─ transform.py
│  └─ load.py
├─ visuals/                   # PNG (Matplotlib)
├─ main.py                    # Orchestrates: ETL → KPIs (Rich) → charts (PNG/HTML)
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## ✅ Requirements

* **Python 3.10+**
* `pip install -r requirements.txt` (pandas, matplotlib, rich, plotly)

---

## ⚙️ Install & Run

```bash
# (optional) virtual environment
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt

# place data/candidates.csv (semicolon-separated)
python main.py
```

* Populates the **DW** (`dw/workshop1_dw.sqlite`).
* Prints **KPIs** in the console (nicely formatted with **Rich**).
* Generates **PNGs** in `visuals/` and **HTML** in `docs/`.

---

## 📊 KPIs (DW only)

1. **Hires by technology** — Hires, Total, Rate %
2. **Hires by year** — Hires, Total, Rate %
3. **Hires by seniority** — Hires, Total, Rate %
4. **Hires by country (per year)** — Trend for US/Brazil/Colombia/Ecuador
5. **Hiring rate by country (%)** — Country ranking
6. **Average scores (Hired vs Not)** — Code Challenge & Interview

---

## 🚀 GitHub Pages

This repo includes a **GitHub Actions workflow** that:

1. Runs `main.py` (if `data/candidates.csv` exists).
2. Publishes the `docs/` folder as a **GitHub Pages** site.

* Enable Pages: **Settings → Pages → Source: GitHub Actions**.
* Every push to `main` builds and publishes the site.

---

## 🛠️ Troubleshooting

**`git` not found on Windows**

* Install Git (`winget install --id Git.Git -e`) and ensure `C:\Program Files\Git\cmd` is in **PATH**.

**Permission error activating `.venv` on Windows**

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**`sqlite3.OperationalError: database is locked`**

* Close any process using the `.sqlite` and run again.

**CI without CSV**

* The workflow still publishes a minimal index; once you add `data/candidates.csv` and run `main.py`, it will produce HTML into `docs/` on your machine. Commit & push to update Pages.

---

## 📜 License

MIT © 2025 — ShadowBlack33

````

---

# File: `docs/index.html`
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Workshop-1 · KPIs & Charts</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root { --fg:#0d1117; --bg:#ffffff; --muted:#6b7280; --card:#f8fafc; }
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, "Noto Sans", "Helvetica Neue", Arial, "Apple Color Emoji", "Segoe UI Emoji"; margin:0; color:var(--fg); background:var(--bg); }
    .wrap { max-width: 980px; margin: 40px auto; padding: 0 16px; }
    header { margin-bottom: 24px; }
    h1 { margin: 0 0 8px; }
    p.lead { color:var(--muted); margin: 0 0 24px; }
    .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
    .card { background: var(--card); border:1px solid #e5e7eb; border-radius: 12px; padding: 16px; }
    .card h3 { margin: 8px 0 12px; }
    .card a { text-decoration: none; color: #2563eb; }
    footer { margin-top: 32px; color: var(--muted); }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Workshop-1 · KPIs & Charts</h1>
      <p class="lead">ETL → Data Warehouse (SQLite) → KPIs and visualizations. Interactive charts built with Plotly.</p>
    </header>

    <section class="grid">
      <div class="card">
        <h3>Hires by technology</h3>
        <a href="./contrataciones_tecnologia.html">Open chart</a>
      </div>
      <div class="card">
        <h3>Hires by year</h3>
        <a href="./contrataciones_anio.html">Open chart</a>
      </div>
      <div class="card">
        <h3>Hires by seniority</h3>
        <a href="./contrataciones_seniority.html">Open chart</a>
      </div>
      <div class="card">
        <h3>Hires by country (per year)</h3>
        <a href="./contrataciones_pais_anio.html">Open chart</a>
      </div>
    </section>

    <footer>
      <p>Made by <strong>@ShadowBlack33</strong> · Served from <code>/docs</code> via GitHub Pages</p>
    </footer>
  </div>
</body>
</html>
````

---


```yaml
name: Build & Publish Pages

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Ensure docs/index.html exists
        run: |
          mkdir -p docs
          if [ ! -f "docs/index.html" ]; then
            cat > docs/index.html <<'HTML'
            <!doctype html><meta charset="utf-8"><title>Workshop-1</title>
            <p>GitHub Pages is ready. Add <code>data/candidates.csv</code> and run <code>main.py</code> locally to generate Plotly HTML files under <code>docs/</code>, then commit & push.</p>
            HTML
          fi

      - name: Run ETL + KPIs + Charts (only if CSV exists)
        run: |
          if [ -f "data/candidates.csv" ]; then
            python main.py
          else
            echo "No data/candidates.csv → skipping main.py"
          fi

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./docs

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

---

# .editorconfig

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 2

[*.py]
indent_size = 4

[*.md]
trim_trailing_whitespace = false
```

---

# .gitattributes

```gitattributes
* text=auto
*.py  text eol=lf
*.md  text eol=lf
*.sql text eol=lf
*.yml text eol=lf
```

---

## Final step (commit & push)

```powershell
git add -A
git commit -m "docs: polished English README, Pages index, workflow, editorconfig, gitattributes"
git push
```

After pushing, in your repo go to **Settings → Pages → Source: GitHub Actions** to finalize publication.
