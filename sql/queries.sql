
-- KPI 1: Hires por tecnología
SELECT t.technology, SUM(f.hired) AS hires, COUNT(*) AS total,
       ROUND(100.0*SUM(f.hired)/COUNT(*),2) AS hire_rate_pct
FROM FactHires f
JOIN DimTechnology t ON f.technology_id = t.technology_id
GROUP BY t.technology
ORDER BY hires DESC;

-- KPI 2: Hires por año
SELECT d.year, SUM(f.hired) AS hires, COUNT(*) AS total,
       ROUND(100.0*SUM(f.hired)/COUNT(*),2) AS hire_rate_pct
FROM FactHires f
JOIN DimDate d ON f.date_id = d.date_id
GROUP BY d.year
ORDER BY d.year;

-- KPI 3: Hires por seniority
SELECT c.seniority, SUM(f.hired) AS hires, COUNT(*) AS total,
       ROUND(100.0*SUM(f.hired)/COUNT(*),2) AS hire_rate_pct
FROM FactHires f
JOIN DimCandidate c ON f.candidate_id = c.candidate_id
GROUP BY c.seniority
ORDER BY hires DESC;

-- KPI 4: Hires por país a lo largo de los años (USA, Brazil, Colombia, Ecuador)
SELECT d.year, co.country, SUM(f.hired) AS hires
FROM FactHires f
JOIN DimDate d ON f.date_id = d.date_id
JOIN DimCountry co ON f.country_id = co.country_id
WHERE co.country IN ('United States','Brazil','Colombia','Ecuador')
GROUP BY d.year, co.country
ORDER BY d.year, hires DESC;

-- Extra A: Hire rate por país
SELECT co.country, SUM(f.hired) AS hires, COUNT(*) AS total,
       ROUND(100.0*SUM(f.hired)/COUNT(*),2) AS hire_rate_pct
FROM FactHires f
JOIN DimCountry co ON f.country_id = co.country_id
GROUP BY co.country
ORDER BY hire_rate_pct DESC;

-- Extra B: Promedios de puntajes por contratado vs no
SELECT hired,
       ROUND(AVG(code_challenge_score),2) AS avg_code_challenge,
       ROUND(AVG(technical_interview_score),2) AS avg_tech_interview
FROM FactHires
GROUP BY hired
ORDER BY hired DESC;
