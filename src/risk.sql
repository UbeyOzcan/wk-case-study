CREATE TABLE public.risk as 
SELECT  a.*, b."claimId", b."claimType", b."accidentDate", b."paidAmount", b."caseReserve", b."incurredAmount",  b."claimStatus"
FROM contrats_mrh_new a 
LEFT JOIN claim_new b on 
    a."contractId" = b."contractId" and 
    a."split_coverage_start" < b."accidentDate" and 
    a."split_coverage_end" > b."accidentDate" ; 



SELECT distinct formula, "claimType"
from risk 
order by 1, 2; 

SELECT  
    a."accident_year",
    count(distinct a."contractId") as n_contracts, 
    count(distinct b."claimId") as n_claims, 
    sum(a."exposure") as exposure,
    sum(a.allocated_premium) as Premium,  
    sum(a.allocated_broker_commission) as commission,
    sum(b."paidAmount") as Paid, 
    sum(b."caseReserve") as Reserve,
    sum(b."incurredAmount") as "incurredAmount", 
    round(count(distinct b."claimId")/sum(a."exposure"), 2) as Frequency,
    sum(b."incurredAmount")/count(distinct b."claimId") as Severity,
    round(count(distinct b."claimId")/sum(a."exposure"), 2) * sum(b."incurredAmount")/count(distinct b."claimId") as RP,
    (sum(a.allocated_broker_commission) + sum(b."incurredAmount"))/sum(a.allocated_premium) as Composite_ratio
FROM contrats_mrh_new a 
LEFT JOIN claim_new b on 
    a."contractId" = b."contractId" and 
    a."split_coverage_start" < b."accidentDate" and 
    a."split_coverage_end" > b."accidentDate" 
GROUP BY a."accident_year"; 

