


SELECT  
    a."accident_year",
    count(distinct a."contractId") as n_contracts, 
    count(distinct b."claimId") as n_claims, 
    sum(a."exposure") as exposure,
    sum(a.allocated_premium) as Premium,  
    sum(b."paidAmount") as Paid, 
    sum(b."incurredAmount") as "incurredAmount", 
    (sum(a.allocated_broker_commission) + sum(b."incurredAmount"))/sum(a.allocated_premium) as Composite_ratio
FROM contrats_mrh_new a 
LEFT JOIN claim_new b on 
    a."contractId" = b."contractId" and 
    a."split_coverage_start" < b."accidentDate" and 
    a."split_coverage_end" > b."accidentDate" 
GROUP BY a."accident_year"; 

