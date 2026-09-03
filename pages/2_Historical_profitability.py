import streamlit as st
import pandas as pd
from src.Data import Data
import numpy as np
import plotly.express as px
import chainladder as cl

@st.cache_data
def get_data_contract():
    try:
        D = Data(
            db='postgres',
            user='postgres', 
            password='HelloWorld4000!',
            host='db.vxpmkphdzdnccwyzsnzp.supabase.co',
            port=5432
        )
        df = D.fetch_data("SELECT * FROM public.contrats_mrh_new;")
        df.insert(loc = 0, column='Year', value=pd.DatetimeIndex(df['coverageStartDate']).year)
        df.insert(loc=len(df.columns), column='is_cancelled', value=np.where(df['cancellationDate'].notnull(), 'Yes', 'No'))

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
        df.insert(loc = 0, column='Dev Year', value=pd.DatetimeIndex(df['viewDate']).year)
        df = df.drop_duplicates(subset=['claimId', 'contractId', 'claimType', 'accidentDate', 'Accident Year', 'paidAmount', 'caseReserve', 'incurredAmount', 'claimStatus'], keep='first')
        df = df.sort_values(by=['claimId', 'viewDate'])
        df = df.drop_duplicates(subset=['claimId'], keep='last')
        return df
    except Exception as e:
        print(f"Error: {e}")


claims = get_data_claims()
contracts = get_data_contract()

risk = pd.merge(contracts, claims, left_on=['contractId', 'Year'], right_on=['contractId', 'Accident Year'],  how='left')
st.dataframe(claims, hide_index=True)
st.dataframe(risk, hide_index=True)
st.write(f"Number of contracts before join: {contracts['contractId'].nunique()}")
st.write(f"Number of contracts after join: {risk['contractId'].nunique()}")

st.write(f"Premium before join: {contracts['allocated_premium'].sum()}")
st.write(f"Premium after join: {risk['allocated_premium'].sum()}")


st.write(f"Paid before join: {claims['paidAmount'].sum()}")
st.write(f"Paid after join: {risk['paidAmount'].sum()}")