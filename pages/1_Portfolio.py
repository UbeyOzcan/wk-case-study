import streamlit as st
import pandas as pd
from src.Data import Data
import numpy as np
import plotly.express as px


st.set_page_config(layout="wide")

st.title("Portfolio")

@st.cache_data
def get_data():
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

def evolution(df:pd.DataFrame) -> pd.DataFrame:

    premium = df.groupby('Year').agg({'premiumHT': ['sum', 'mean'], 'brokerCommission': ['sum', 'mean'], 'contractId' : 'nunique'}).reset_index()

    return premium


data = get_data()

data['surface bins'] = pd.cut(
    data['surface'], 
    bins=[20, 35, 45, 60, 75, 90, 110, 130, 145, 160, 175, 190, 205, 220, 235, 250], 
    labels=['20-35', '35-45', '45-60', '60-75', '75-90', '90-110', '110-130', '130-145', '145-160', '160-175', '175-190', '190-205', '205-220', '220-235', '235-250'])

data['Premium bins'] = pd.cut(
    data['premiumHT'],
    bins=[0, 130, 190, 250, 310, 370, 430, 490, 700],
    labels=['0-130', '130-190', '190-250', '250-310', '310-370', '370-430', '430-490', '490-700'])



def composition(df:pd.DataFrame, rfs:str):

    df_sorted = df.sort_values(by=rfs)

    df_agg = df_sorted.groupby(['Year', rfs]).agg({'premiumHT': 'sum'}).reset_index()
    df_agg_year = df_agg.groupby('Year').agg({'premiumHT': 'sum'}).reset_index().rename(columns={'premiumHT': 'total_premium'})
    df_agg = pd.merge(df_agg, df_agg_year, on='Year')


    df_agg['percentage of grand total'] = round((df_agg['premiumHT'] / df_agg['total_premium']) * 100, 2)
    df_agg = df_agg[['Year', rfs, 'percentage of grand total']]

    df_agg_pivot = df_agg.pivot(index='Year', columns=rfs, values='percentage of grand total').reset_index()

    fig = px.histogram(df_sorted, x="Year", y="premiumHT",
                color=rfs, barmode='group',
                histfunc='sum',
                height=400, text_auto=True)


    return {"df": df_agg_pivot, "fig": fig}

def pichart(df:pd.DataFrame):

    df_agg = df.groupby(['Year', 'formula']).agg({'premiumHT': 'sum'}).reset_index()
    fig_dict = {}
    for i in [2022, 2023, 2024]:
        df_agg_year = df_agg[df_agg['Year'] == i]
        df_agg_year['percentage of grand total'] = round((df_agg_year['premiumHT'] / df_agg_year['premiumHT'].sum()) * 100, 2)
        fig = px.pie(df_agg_year, values='percentage of grand total', names='formula', title=f'Distribution of Premium by Formula for {i}', hole=0.3)
        fig_dict[i] = fig

    return fig_dict

with st.expander("Yearly Evolution of Premiums and Commissions"):
    st.dataframe(evolution(data), hide_index=True)
    fig_dict = pichart(data)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(fig_dict[2022], use_container_width=True)
    with col2:
        st.plotly_chart(fig_dict[2023], use_container_width=True)
    with col3:
        st.plotly_chart(fig_dict[2024], use_container_width=True)

with st.expander("Portfolio composition"):
    rfs = st.selectbox("Choose a variable to display:", ["policyYear", "propertyType", "surface bins", "riskZone", "franchise", "Year", "is_cancelled"])
    st.write(f"Distribution by year of Premium for {rfs}")
    st.plotly_chart(composition(data, rfs)["fig"], use_container_width=True)
    st.write(f"Evolution of percentage of grand total of premiums by year and for {rfs}")
    st.dataframe(composition(data, rfs)["df"], hide_index=True)


with st.expander("Portfolio composition by Formula"):
    formula = st.selectbox("Choose a formula to display:", ["Confort", "Essentielle", "Premium"])
    rfs_formula = st.selectbox("Choose a variable to display:", ["policyYear", "propertyType", "surface bins", "riskZone", "franchise", "Year", "is_cancelled"], key="rfs_formula")
    data_formula = data[data['formula'] == formula]
    st.write(f"Distribution by year of Premium for {rfs_formula}")
    st.plotly_chart(composition(data_formula, rfs_formula)["fig"], use_container_width=True)
    st.write(f"Evolution of percentage of grand total of premiums by year and for {rfs_formula}")
    st.dataframe(composition(data_formula, rfs_formula)["df"], hide_index=True)


with st.expander("Premium Distribution analysis"):
    df_formula_mean = data.groupby(['Year', 'formula']).agg({'premiumHT': 'mean'}).reset_index().sort_values(by=['formula'])
    df_formula_mean_pivot = df_formula_mean.pivot(index='Year', columns='formula', values='premiumHT').reset_index()
    st.write("Mean Premium by Year and Formula")
    st.dataframe(df_formula_mean_pivot, hide_index=True)
    st.plotly_chart(composition(data_formula, 'Premium bins')["fig"], use_container_width=True)