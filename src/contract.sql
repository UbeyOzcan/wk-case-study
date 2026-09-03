select * from public.claims_mrh; 

select sum("premiumHT" ) from public.contrats_mrh; 

CREATE TABLE public.contrats_mrh_new AS 
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
), 
final_tab as (
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
    accident_year,
    split_start AS split_coverage_start,
    split_end AS split_coverage_end,
    --(split_end - split_start) + 1 AS days_in_year,
    ("premiumHT" * ((split_end - split_start) + 1)) / NULLIF(("coverageEndDate"::date - "coverageStartDate"::date) + 1, 0)::numeric AS allocated_premium,
    ("brokerCommission" * ((split_end - split_start) + 1)) / NULLIF(("coverageEndDate"::date - "coverageStartDate"::date) + 1, 0)::numeric AS allocated_broker_commission,
    round(((split_end - split_start) + 1)/365.0, 2) AS exposure
FROM yearly_splits
WHERE split_start <= split_end)
SELECT * FROM final_tab ; 


-- CONTROLS
SELECT count(DISTINCT "contractId")  FROM public.contrats_mrh 

union all 

SELECT COUNT(DISTINCT "contractId") FROM public.contrats_mrh_new ;

SELECT SUM("premiumHT") FROM public.contrats_mrh

union all

select SUM(allocated_premium) FROM public.contrats_mrh_new ;


select "propertyType", count(distinct "contractId") from public.contrats_mrh GROUP BY "propertyType"

union all

select "propertyType", count(distinct "contractId") from public.contrats_mrh_new GROUP BY "propertyType"    ;