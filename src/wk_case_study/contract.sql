WITH yearly_splits AS (
    SELECT 
        "contractId",
        "subscriptionYear",
        "policyYear",
        "propertyType",
        "surface",
        "riskZone",
        "formula",
        "franchise",
        "premiumHT",
        "brokerCommission",
        "coverageStartDate",
        "coverageEndDate",
        "cancellationDate",
        "cancellationReason",
        "coverageStartDate"::date AS start_date,
        "coverageEndDate"::date AS end_date,
        EXTRACT(YEAR FROM d) AS accident_year,
        GREATEST("coverageStartDate"::date, d::date) AS split_start,
        LEAST("coverageEndDate"::date, (d + INTERVAL '1 year' - INTERVAL '1 day')::date) AS split_end
    FROM public.contrats_mrh c
    CROSS JOIN LATERAL generate_series(
        DATE_TRUNC('year', "coverageStartDate"::date),
        DATE_TRUNC('year', "coverageEndDate"::date),
        INTERVAL '1 year'
    ) AS d
    WHERE "coverageStartDate" IS NOT NULL 
      AND "coverageEndDate" IS NOT NULL
      AND "coverageStartDate"::date <= "coverageEndDate"::date
)
CREATE TABLE public.contrats_mrh_split (
SELECT 
    "contractId",
    "subscriptionYear",
    "policyYear",
    "propertyType",
    "surface",
    "riskZone",
    "formula",
    "franchise",
    "brokerCommission",
    "coverageStartDate",
    "coverageEndDate",
    "cancellationDate",
    "cancellationReason",
    ("premiumHT" * ((split_end - split_start) + 1)) / NULLIF(("coverageEndDate"::date - "coverageStartDate"::date) + 1, 0)::numeric AS allocated_premium,
    round(((split_end - split_start) + 1)/365.0, 2) AS exposure
FROM yearly_splits
WHERE split_start <= split_end
ORDER BY "contractId", accident_year ) ; 
