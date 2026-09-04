import pandas as pd
import numpy as np
from io import StringIO
from src.Data import Data

def get_data_claims():
    try:
        D = Data(
            db='postgres',
            user='postgres', 
            password='HelloWorld4000!',
            host='db.vxpmkphdzdnccwyzsnzp.supabase.co',
            port=5432
        )
        df = D.fetch_data("SELECT * FROM public.claims_mrh;")
        df['accidentDate'] = pd.to_datetime(df['accidentDate'])
        df['accidentYear'] = df['accidentDate'].dt.year
        df = df.drop_duplicates(subset=['claimId', 'contractId', 'claimType', 'accidentDate', 'accidentYear', 'paidAmount', 'caseReserve', 'incurredAmount', 'claimStatus'], keep='first')
        return df
    except Exception as e:
        print(f"Error: {e}")

df = get_data_claims()

print(df)

print("=" * 80)
print("DATA DICTIONARY CONFIRMATION")
print("=" * 80)

# 1. Verify the data structure matches the description
print("\n1. Verification that each row is a monthly snapshot:")
claim_sample = df[df['claimId'] == 'CLM_2022_00001'].sort_values('developmentMonth')
print(claim_sample[['developmentMonth', 'paidAmount', 'caseReserve', 'incurredAmount']].head(10))

# 2. Verify paidAmount is incremental (as expected)
print("\n2. PaidAmount is incremental (payments during the month):")
for month in range(5):
    paid = claim_sample[claim_sample['developmentMonth'] == month]['paidAmount'].values[0]
    print(f"  Month {month}: Paid = {paid:.2f}")

# 3. Show how to create cumulative views
print("\n" + "=" * 80)
print("CREATING CUMULATIVE VIEWS")
print("=" * 80)

# Option A: Cumulative paid per claim
df['cumulativePaid'] = df.groupby('claimId')['paidAmount'].cumsum()
claim_sample['cumulativePaid'] = claim_sample.groupby('claimId')['paidAmount'].cumsum()
print("\nA. Cumulative paid per claim (first claim sample):")
print(claim_sample[['developmentMonth', 'paidAmount', 'cumulativePaid']].head(10))

# Option B: Cumulative paid triangle
paid_triangle = df.groupby(['accidentYear', 'developmentMonth'])['paidAmount'].sum().unstack().fillna(0)
cumulative_paid_triangle = paid_triangle.cumsum(axis=1)

print("\nB. Cumulative Paid Triangle (first 6 months):")
print(cumulative_paid_triangle.iloc[:, :6].round(2))

# Option C: Incurred triangle (already cumulative)
incurred_triangle = df.groupby(['accidentYear', 'developmentMonth'])['incurredAmount'].sum().unstack().fillna(0)

print("\nC. Incurred Triangle (already cumulative by definition):")
print(incurred_triangle.iloc[:, :6].round(2))

# 4. Compare approaches
print("\n" + "=" * 80)
print("IBNR ESTIMATION - BEST APPROACHES")
print("=" * 80)

print("""
Based on the data dictionary, you have two valid approaches for IBNR:

APPROACH 1: Use Incurred Amounts (Recommended)
- Data: incurredAmount (already cumulative)
- Method: Standard Chain Ladder
- What it estimates: Total IBNR (case reserves + IBNR)

APPROACH 2: Use Paid Amounts (Alternative)
- Data: cumulative paid (cumsum of paidAmount)
- Method: Chain Ladder on paid losses
- What it estimates: IBNR for paid losses only

APPROACH 3: Paid + Reserve (Most Comprehensive)
- Data: cumulative paid + case reserves separately
- Method: Chain Ladder on both
- What it estimates: Separates IBNR into:
  1. IBNR on paid losses
  2. IBNR on outstanding reserves
""")

# 5. Implementation
print("\n" + "=" * 80)
print("IMPLEMENTATION")
print("=" * 80)

def calculate_ibnr_approaches(df):
    """
    Calculate IBNR using different approaches
    """
    # Filter to complete years (2022-2023)
    df_filtered = df[df['accidentYear'].isin([2022, 2023])].copy()
    
    # ---- Approach 1: Incurred Amounts ----
    inc_triangle = df_filtered.groupby(['accidentYear', 'developmentMonth'])['incurredAmount'].sum().unstack().fillna(0)
    
    # Ensure all months present
    max_month = int(inc_triangle.columns.max())
    for month in range(max_month + 1):
        if month not in inc_triangle.columns:
            inc_triangle[month] = 0
    inc_triangle = inc_triangle[sorted(inc_triangle.columns)]
    
    # Chain Ladder on incurred
    factors_inc = {}
    for i in range(len(inc_triangle.columns) - 1):
        current = inc_triangle.columns[i]
        next_col = inc_triangle.columns[i + 1]
        if inc_triangle[current].sum() > 0:
            factors_inc[next_col] = inc_triangle[next_col].sum() / inc_triangle[current].sum()
        else:
            factors_inc[next_col] = 1.0
    
    # Project incurred
    projected_inc = inc_triangle.copy()
    for i in range(len(projected_inc.columns) - 1):
        current = projected_inc.columns[i]
        next_col = projected_inc.columns[i + 1]
        factor = factors_inc[next_col]
        for year in projected_inc.index:
            if projected_inc.loc[year, current] > 0 and projected_inc.loc[year, next_col] == 0:
                projected_inc.loc[year, next_col] = projected_inc.loc[year, current] * factor
    
    # Calculate IBNR from incurred
    ibnr_inc = {}
    total_ibnr_inc = 0
    for year in projected_inc.index:
        latest = projected_inc.loc[year, projected_inc.loc[year] > 0].iloc[-1]
        ultimate = projected_inc.loc[year, projected_inc.columns[-1]]
        ibnr = max(0, ultimate - latest)
        ibnr_inc[year] = ibnr
        total_ibnr_inc += ibnr
    
    # ---- Approach 2: Cumulative Paid ----
    paid_triangle = df_filtered.groupby(['accidentYear', 'developmentMonth'])['paidAmount'].sum().unstack().fillna(0)
    cum_paid_triangle = paid_triangle.cumsum(axis=1)
    
    # Ensure all months present
    for month in range(max_month + 1):
        if month not in cum_paid_triangle.columns:
            cum_paid_triangle[month] = 0
    cum_paid_triangle = cum_paid_triangle[sorted(cum_paid_triangle.columns)]
    
    # Chain Ladder on cumulative paid
    factors_paid = {}
    for i in range(len(cum_paid_triangle.columns) - 1):
        current = cum_paid_triangle.columns[i]
        next_col = cum_paid_triangle.columns[i + 1]
        if cum_paid_triangle[current].sum() > 0:
            factors_paid[next_col] = cum_paid_triangle[next_col].sum() / cum_paid_triangle[current].sum()
        else:
            factors_paid[next_col] = 1.0
    
    # Project paid
    projected_paid = cum_paid_triangle.copy()
    for i in range(len(projected_paid.columns) - 1):
        current = projected_paid.columns[i]
        next_col = projected_paid.columns[i + 1]
        factor = factors_paid[next_col]
        for year in projected_paid.index:
            if projected_paid.loc[year, current] > 0 and projected_paid.loc[year, next_col] == 0:
                projected_paid.loc[year, next_col] = projected_paid.loc[year, current] * factor
    
    # Calculate IBNR from paid
    ibnr_paid = {}
    total_ibnr_paid = 0
    for year in projected_paid.index:
        latest = projected_paid.loc[year, projected_paid.loc[year] > 0].iloc[-1]
        ultimate = projected_paid.loc[year, projected_paid.columns[-1]]
        ibnr = max(0, ultimate - latest)
        ibnr_paid[year] = ibnr
        total_ibnr_paid += ibnr
    
    return {
        'incurred': (ibnr_inc, total_ibnr_inc),
        'paid': (ibnr_paid, total_ibnr_paid)
    }

# Run the analysis
results = calculate_ibnr_approaches(df)

print("\nIBNR Results Comparison:")
print(f"Approach 1 (Incurred Amounts): {results['incurred'][1]:,.2f}")
print(f"Approach 2 (Cumulative Paid): {results['paid'][1]:,.2f}")
print(f"\nDifference: {results['incurred'][1] - results['paid'][1]:,.2f}")
print("This difference represents the IBNR on outstanding case reserves")