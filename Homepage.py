import streamlit as st
import pandas as pd
from src.Data import Data
import chainladder as cl

st.set_page_config(layout="wide")
st.title("Presentation - Profitability Analysis - MRH")

st.write("Profitability analysis of MRH product launch in 2022.")

st.write("* Porfolio : Current status of the portfolio composition")
st.write("* Historical profitability : How the book is performing from 2022")
st.write("* Ultimate 2024 : How 2024 will perform at ultimate ?")
st.write("* Pricing evolution : stategy and adjustment")


