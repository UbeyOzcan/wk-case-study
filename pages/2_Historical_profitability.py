import streamlit as st
import pandas as pd
from src.Data import Data
import numpy as np
import plotly.express as px

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
        df = D.fetch_data("SELECT * FROM public.contrats_mrh;")
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
        return df
    except Exception as e:
        print(f"Error: {e}")

st.dataframe(get_data_contract(), hide_index=True)
st.dataframe(get_data_claims(), hide_index=True)
