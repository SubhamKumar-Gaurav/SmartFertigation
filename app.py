import streamlit as st
import pandas as pd
import pickle
from fertilizer import recommend_fertilizer


# Load Model
model = pickle.load(open("model.pkl", "rb"))


# UI Title
st.title("🌾 Smart Fertigation System")
st.write("Predict rainfall and get irrigation + fertilizer recommendations.")


# Daily Water Requirement Table (litres per plant)
water_table = {
    "Jan": {1:0.6, 2:0.5, 3:2,   4:2.9, 5:7.5},
    "Feb": {1:0.8, 2:1.5, 3:3.8, 4:5.9, 5:13.6},
    "Mar": {1:1.7, 2:2.2, 3:6.3, 4:10.2, 5:22.5},
    "Apr": {1:3.3, 2:5.4, 3:13.6,4:33.1, 5:40.9},
    "May": {1:4.1, 2:9.6, 3:16.3,4:39.2, 5:53.3},
    "Jun": {1:4.4, 2:8.4, 3:15.8,4:38.1, 5:54.3},
    "Jul": {1:3.2, 2:6.5, 3:10.1,4:27.8, 5:35.8},
    "Aug": {1:2.6, 2:4.4, 3:9.8, 4:21.4, 5:29.3},
    "Sep": {1:1.9, 2:4.9, 3:7.8, 4:19.6, 5:26.1},
    "Oct": {1:1.7, 2:3.5, 3:6.4, 4:15.2, 5:18.8},
    "Nov": {1:1.1, 2:1.9, 3:4,   4:5.7, 5:12.5},
    "Dec": {1:0.6, 2:1.4, 3:0.5, 4:7,   5:7.5}
}

month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


# Weather Inputs
st.header("🌧️ Weather Inputs (Yesterday)")
cloudcover = st.slider("Cloud Cover (%)", 0, 100, 50)
dew = st.number_input("Dew Point (°C)", value=15.0)
tempmin = st.number_input("Minimum Temperature (°C)", value=20.0)
pressure = st.number_input("Pressure (mb)", value=1010.0)
windgust = st.number_input("Wind Gust (km/h)", value=20.0)
humidity = st.number_input("Humidity (%)", value=60.0)
windspeed = st.number_input("Wind Speed (km/h)", value=10.0)
month_name = st.selectbox("Month", month_names)

# Convert to numeric for model
month = month_names.index(month_name) + 1


# FERTILIZER INPUTS 
st.header("🌱 Fertilizer Inputs")

age_year = st.number_input("Plant Age (Years)", min_value=1, max_value=50, value=1)
age_month = st.number_input("Plant Age (Months)", 0, 11, 0)

N_avail = st.number_input("Available Nitrogen (g)", value=0.0)
P_avail = st.number_input("Available Phosphorous (g)", value=0.0)
K_avail = st.number_input("Available Potassium (g)", value=0.0)


# Prepare Input Data
input_dict = {
    'cloudcover_lag1': cloudcover,
    'dew_lag1': dew,
    'tempmin_lag1': tempmin,
    'pressure_lag1': pressure,
    'windgust_lag1': windgust,
    'humidity_lag1': humidity,
    'windspeed_lag1': windspeed,
    'month_lag1': month
}

# Convert to DataFrame
input_df = pd.DataFrame([input_dict])

# Get correct feature order from model
feature_order = list(model.feature_names_in_)

# Reorder columns to match training
input_df = input_df[feature_order]


# Prediction
if st.button("🔍 Get Recommendation"):

    # 🌧️ Rain Prediction
    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]

    st.subheader("🌤️ Rainfall Prediction")

    if prediction == 1:
        st.success(f"🌧️ Rain Expected Today\n\nProbability: {probability:.2f}")
    else:
        st.info(f"☀️ No Rain Expected Today\n\nProbability: {probability:.2f}")

    
    # Irrigation Recommendation 
    st.subheader("🌱 Irrigation Advice")

    if probability > 0.7:
        st.warning("⚠️ High chance of rain → Avoid irrigation")
    elif probability > 0.4:
        st.warning("🌤️ Moderate chance → Irrigate cautiously")
    else:
        st.success("✅ Low chance of rain → Safe to irrigate")


    # 💧 Irrigation Calculation
    irrigation_age = min(age_year, 5)

    water_required = water_table[month_name][irrigation_age]

    st.subheader("💧 Daily Water Requirement")
    st.write(f"Base requirement: {water_required} litres/plant/day")


    # 🌱 Smart Irrigation Decision
    st.subheader("🌱 Irrigation Advice")

    if probability > 0.7:
        st.warning("🌧️ Rain expected → Skip irrigation")
        st.write("Recommended: 0 litres")
    elif probability > 0.4:
        reduced = water_required * 0.5
        st.warning("🌤️ Moderate rain chance → Reduce irrigation")
        st.write(f"Recommended: {round(reduced,2)} litres")
    else:
        st.success("☀️ No rain → Full irrigation")
        st.write(f"Recommended: {water_required} litres")

  
    # 🌿 Fertilizer Recommendation 
    fert = recommend_fertilizer(age_year, age_month, N_avail, P_avail, K_avail)

    st.subheader("🌿 Fertilizer Recommendation")

    st.write("### Monthly Nutrient Requirement")
    st.write(f"Nitrogen: {fert['monthly_required_N']} g")
    st.write(f"Phosphorous: {fert['monthly_required_P']} g")
    st.write(f"Potassium: {fert['monthly_required_K']} g")

    st.write("### Additional Requirement (Deficit)")
    st.write(f"Nitrogen deficit: {fert['deficit_N']} g")
    st.write(f"Phosphorous deficit: {fert['deficit_P']} g")
    st.write(f"Potassium deficit: {fert['deficit_K']} g")

    st.write("### Fertilizer to Apply")
    st.success(f"Urea: {fert['urea']} g")
    st.success(f"SSP: {fert['ssp']} g")
    st.success(f"MOP: {fert['mop']} g")


    # 🌧️ Smart Integration Logic 
    st.subheader("⚠️ Final Advisory")

    if probability > 0.7:
        st.warning("Rain expected → Delay fertilizer application to avoid nutrient loss")
    else:
        st.success("No heavy rain expected → Safe to apply fertilizers")


# Debug Section (If anything goes wrong)
with st.expander("🔍 Debug Info"):
    st.write("Model expects feature order:", feature_order)
    st.write("Input Data Passed to Model:")
    st.write(input_df) 