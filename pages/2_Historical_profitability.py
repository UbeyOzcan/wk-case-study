import streamlit as st
import pandas as pd
from src.Data import Data
import numpy as np
import plotly.express as px

st.title("Historical Profitability")

st.set_page_config(layout="wide")
@st.cache_data
def get_risk():
    try:
        D = Data(
            db='postgres',
            user='postgres', 
            password='HelloWorld4000!',
            host='db.vxpmkphdzdnccwyzsnzp.supabase.co',
            port=5432
        )
        df = D.fetch_data("SELECT * FROM public.risk;")
        return df
    except Exception as e:
        print(f"Error: {e}")

@st.cache_data
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
        df.insert(loc = 0, column='Accident Year', value=pd.DatetimeIndex(df['accidentDate']).year)
        #df = df.drop_duplicates(subset=['claimId', 'contractId', 'claimType', 'accidentDate', 'Accident Year', 'paidAmount', 'caseReserve', 'incurredAmount', 'claimStatus'], keep='first')
        df_last = df.sort_values(by=['claimId', 'viewDate'])
        df_last = df_last.drop_duplicates(subset=['claimId'], keep='last')
        return {'df_triangle': df, 'df_last': df_last}
    except Exception as e:
        print(f"Error: {e}")


risk_df = get_risk()
risk_df['surface bins'] = pd.cut(
    risk_df['surface'], 
    bins=[20, 35, 45, 60, 75, 90, 110, 130, 145, 160, 175, 190, 205, 220, 235, 250], 
    labels=['20-35', '35-45', '45-60', '60-75', '75-90', '90-110', '110-130', '130-145', '145-160', '160-175', '175-190', '190-205', '205-220', '220-235', '235-250'])
with st.expander("General observed profitability analysis"):
    profit_tab = risk_df.groupby('accident_year').agg({'contractId': 'nunique', 
                                                        'claimId': 'nunique', 
                                                        'exposure': 'sum', 
                                                        'allocated_premium': 'sum',
                                                        'allocated_broker_commission': 'sum',
                                                        'paidAmount': 'sum',
                                                        'caseReserve': 'sum',
                                                        'incurredAmount': 'sum'}).reset_index()


    profit_tab.insert(loc=len(profit_tab.columns), 
                    column='composite_ratio (Incurred)', value=round(((profit_tab['incurredAmount'] + profit_tab['allocated_broker_commission']) / profit_tab['allocated_premium']) * 100, 2))

    st.dataframe(profit_tab, hide_index=True)

with st.expander("Profitability analysis by profile"):
    rfs = st.selectbox("Choose a variable to display:", ["policyYear", "formula", "propertyType", "surface bins", "riskZone", "franchise", "Year"])

    profit_tab_peril = risk_df.groupby([rfs, 'accident_year']).agg({'contractId': 'nunique', 
                                                                            'claimId': 'nunique', 
                                                                            'exposure': 'sum', 
                                                                            'allocated_premium': 'sum',
                                                                            'allocated_broker_commission': 'sum',
                                                                            'paidAmount': 'sum',
                                                                            'caseReserve': 'sum',
                                                                            'incurredAmount': 'sum'}).reset_index()

    profit_tab_peril.insert(loc=len(profit_tab_peril.columns), column='composite_ratio (Incurred)', value=round(((profit_tab_peril['incurredAmount'] + profit_tab_peril['allocated_broker_commission']) / profit_tab_peril['allocated_premium']) * 100, 2))
    
    profit_tab_peril_ratio = profit_tab_peril[[rfs, 'accident_year', 'composite_ratio (Incurred)']]
    profit_tab_peril_ratio = profit_tab_peril_ratio[profit_tab_peril_ratio['accident_year'] < 2025]
    profit_tab_peril_ratio_pivot = profit_tab_peril_ratio.pivot(index = rfs, columns = 'accident_year', values = 'composite_ratio (Incurred)').reset_index()
    st.dataframe(profit_tab_peril_ratio_pivot, hide_index=True)

    premium_tab_peril_ratio = profit_tab_peril[[rfs, 'accident_year', 'allocated_premium', 'exposure']]
    premium_tab_peril_ratio.insert(loc=len(premium_tab_peril_ratio.columns), column = 'average Premium', value = premium_tab_peril_ratio['allocated_premium']/premium_tab_peril_ratio['exposure'])
    premium_tab_peril_ratio = premium_tab_peril_ratio[[rfs, 'accident_year', 'average Premium']]
    premium_tab_peril_ratio_pivot = premium_tab_peril_ratio.pivot(index = rfs, columns = 'accident_year', values = 'average Premium').reset_index()

    st.dataframe(premium_tab_peril_ratio_pivot, hide_index=True)


    exposure_tab_peril_ratio = profit_tab_peril[[rfs, 'accident_year', 'exposure']]
    exposure_tab_peril_ratio_pivot = exposure_tab_peril_ratio.pivot(index = rfs, columns = 'accident_year', values = 'exposure').reset_index()
    st.dataframe(exposure_tab_peril_ratio_pivot, hide_index=True)