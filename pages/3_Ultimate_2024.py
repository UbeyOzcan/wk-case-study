import streamlit as st
import pandas as pd
from src.Data import Data
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")

st.title("2024 Ultimate composite Ratio estimation")

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

triangle_df = get_data_claims()['df_triangle']
triangle_df = triangle_df.groupby(['Accident Year', 'developmentMonth']).agg({"incurredAmount" : "sum"}).reset_index()
triangle_df = triangle_df[(triangle_df["developmentMonth"] == 1) | (triangle_df["developmentMonth"] == 12) | (triangle_df["developmentMonth"] == 24)]
tri_pivot = triangle_df.pivot(index=['Accident Year'], columns = 'developmentMonth', values = "incurredAmount").reset_index()


st.dataframe(tri_pivot)

st.write(f'To estimate the ultimate composite ratio for 2024, we need to calcule a development pattern. In this situation, looking at 2023, one year of development double de Incurred. Remaining looks not significant as MRH line of business is a short tail business')
st.write(f'For 2024, Incurred + IBNR, we are expecting 408.505 of incurred claims')
st.write(f'In term of composite ratio, this will bring 2024 at 73.6% which is higher the target')