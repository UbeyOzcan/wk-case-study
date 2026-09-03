import streamlit as st
import pandas as pd
from src.Data import Data
import chainladder as cl

st.set_page_config(layout="wide")
st.title("My Streamlit App")
st.write("Welcome to my Streamlit application! This is a simple app to demonstrate the capabilities of Streamlit.")

selected_peril = st.selectbox("Choose a peril to display:", ["Dégâts des eaux", "Incendie", "Vol", "Tempête"])
selected_claim = st.selectbox("Choose a claim type to display:", ["paidAmount", "caseReserve", "incurredAmount"])

def get_data():
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

        return df
    except Exception as e:
        print(f"Error: {e}")

df_dict = get_data()
st.dataframe(df_dict)
df_filt = df_dict[df_dict['claimType'] == selected_peril]
raa = cl.Triangle(
    df_filt,
    origin="Accident Year",
    development="viewDate",
    columns=selected_claim,
    cumulative=True,
)

