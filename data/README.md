# data/

This folder holds your **local dataset**. The real CSV is **not committed** to Git (see `.gitignore`).  
The ETL reads from here, populates the SQLite **Data Warehouse**, and **all KPIs/charts** are computed **from the DW** (not from the CSV).

---

## Expected file
- **Path:** `data/candidates.csv`
- **Encoding:** UTF-8
- **Delimiter:** semicolon `;`
- **Header row:** required (see schema below)

### Required columns (exact names)
| Column                      | Type    | Example            | Notes                                                         |
|----------------------------|---------|--------------------|---------------------------------------------------------------|
| `first_name`               | string  | `Ana`              |                                                               |
| `last_name`                | string  | `Pérez`            |                                                               |
| `email`                    | string  | `ana@corp.com`     | Ideally unique                                                |
| `seniority`                | string  | `Junior`           | Free text; normalized downstream                              |
| `yoe`                      | int     | `3`                | Years of experience ≥ 0                                       |
| `technology`               | string  | `Python`           | Used for **DimTechnology**                                    |
| `country`                  | string  | `Colombia`         | Cleaned/standardized for **DimCountry**                       |
| `application_date`         | date    | `2021-07-15`       | ISO `YYYY-MM-DD` → used for **DimDate**                       |
| `code_challenge_score`     | float   | `8.5`              | Range **0–10**                                                |
| `technical_interview_score`| float   | `7.0`              | Range **0–10**                                                |

> In `transform`, `hired` is **derived** (not read from CSV) with the rule:  
> **hired = 1** if `code_challenge_score ≥ 7` **and** `technical_interview_score ≥ 7`; else **0**.

### Optional / ignored columns
Any extra columns are safely ignored by the pipeline.

---

## Minimal sample (semicolon-separated)
> Use this only for local testing; don’t commit real data.

```csv
first_name;last_name;email;seniority;yoe;technology;country;application_date;code_challenge_score;technical_interview_score
Ana;Pérez;ana.perez@example.com;Junior;2;Python;Colombia;2021-07-15;8.2;7.1
Bruno;Silva;bruno.silva@example.com;Mid;5;Java;Brazil;2020-03-10;6.5;7.8
Camila;Rojas;camila.rojas@example.com;Senior;7;Python;Colombia;2019-11-22;9.0;8.6
Diego;Luna;diego.luna@example.com;Mid;4;JavaScript;Mexico;2022-01-05;7.0;6.9
Elena;García;elena.garcia@example.com;Junior;1;Go;Ecuador;2020-08-30;7.2;7.3
