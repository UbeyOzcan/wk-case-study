SELECT sum("caseReserve") 
from public.claims_mrh 
where "developmentMonth" = 11 and "claimType" = 'Dégâts des eaux' and "accidentDate" >= '2024-01-01' and "accidentDate" < '2025-01-01'; 


SELECT *
from public.claims_mrh 
where "developmentMonth" = 32 and "accidentDate" >= '2022-01-01' and "accidentDate" < '2023-01-01';

SELECT * FROM public.claims_mrh where "claimId" = 'CLM_2022_00007'; 


