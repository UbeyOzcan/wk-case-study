import streamlit as st

st.title("Pricing evolution proposal for 2025")

st.write('Based on the observation we have made through this report, here are some recommendation we are making.')

st.markdown(f'In terms of good profile, we can definitely point out the contract with : ')
st.markdown(f'* Premium Formula')
st.markdown(f'* Living on Appartement')
st.markdown(f'* The building in risk zone out of risk zone 1 and 5')
st.markdown(f'* With a Franchise of 150 ou 300')
st.markdown(f'For those profile, the average premium that we are offering can be increased by the household market index.')

st.markdown(f'To get the 70% of composite Ratio, on total level the Premium from 2024 to 2025 should be increased by aroud 5%')
st.markdown(f"To achieve that, on total level the 2025 Premium should be increased by 5%. Let's define 3 buckets of increase which are 5%, 7% and 10% on top of the household market index.")

st.markdown(f'* The worst profitable profile can be defined as contract with House with franchise of 500 ==> + 10%')
st.markdown(f'* The following bad profitable profile can be defined as contract with House with franchise of 300 ==> + 7%')
st.markdown(f'* The remaining profile ==> + 5%')


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

df = get_risk()
df = df[df['accident_year'] == 2024]
total_exposure = df['exposure'].sum()

good_profile = df[(df['propertyType'] == 'Appartement') &  (df['franchise'] == 150)]
exp_good = good_profile['exposure'].sum()

worst_profile = df[(df['propertyType'] == 'Maison') & (df['riskZone'] != 2 ) & (df['riskZone'] != 3 ) & (df['riskZone'] != 4 )]
exp_worst = worst_profile['exposure'].sum()

mid_profile = df[(df['propertyType'] == 'Maison')  & (df['formula'] != "Premium")]
exp_mid = mid_profile['exposure'].sum()

st.write(f"Total Exposure on 2024 is : {total_exposure} ")
st.write(f"Total Exposure on 2024 for good profile is : {round(exp_good, 2)}")
st.write(f"Total Exposure on 2024 for worst profile is :{exp_worst}")
st.write(f"Total Exposure on 2024 for Mid profile is : {exp_mid}")
st.write(f"Total Exposure on 2024 for the remaining profile is : {round(total_exposure - exp_good - exp_worst - exp_mid, 2)}")

st.write("This strategy will lead us to a global increase of 5.4%")