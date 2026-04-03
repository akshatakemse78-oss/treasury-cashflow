
import streamlit as st
import pandas as pd
import pickle

st.set_page_config(page_title="Treasury Dashboard", layout="wide")

st.title("💰 Treasury Cash Flow Dashboard")

# ------------------ LOAD DATA ------------------
df = pd.read_csv("cleaned_cashflow.csv")

# Convert Date if exists
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"])
    df["Day"] = df["Date"].dt.day
    df["Month"] = df["Date"].dt.month

# Load model
model = pickle.load(open("model.pkl", "rb"))

# ------------------ SIDEBAR ------------------
st.sidebar.title("Navigation")
option = st.sidebar.selectbox("Choose Option", ["Dashboard", "Prediction"])

# ================== DASHBOARD ==================
if option == "Dashboard":

    st.subheader("📊 Data Preview")
    st.dataframe(df.head())

    # Prediction on full dataset
    features = ["Cash_Inflow", "Cash_Outflow", "Currency_Rate", "Month", "Day"]
    X = df[features]
    df["Predicted_Cash"] = model.predict(X)

    # ✅ Download Report
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Report",
        data=csv,
        file_name="treasury_cashflow_report.csv",
        mime="text/csv"
    )

    # Charts
    if "Date" in df.columns:
        df_chart = df.set_index("Date")
    else:
        df_chart = df

    st.subheader("📈 Net Cash Trend")
    st.line_chart(df_chart["Net_Cash"])

    st.subheader("🔮 Predicted Cash Flow")
    st.line_chart(df_chart["Predicted_Cash"])

    # KPI Section
    st.subheader("📌 Key Metrics")
    col1, col2, col3 = st.columns(3)

    col1.metric("Average Cash", f"{df['Net_Cash'].mean():,.2f}")
    col2.metric("Max Cash", f"{df['Net_Cash'].max():,.2f}")
    col3.metric("Min Cash", f"{df['Net_Cash'].min():,.2f}")


# ================== PREDICTION ==================
elif option == "Prediction":

    st.subheader("🔮 Cash Flow Prediction")
    st.info("Enter values in the sidebar to predict cash flow")

    # -------- DEFAULT VALUES --------
    default_inflow = 200000.0
    default_outflow = 1670.0
    default_rate = 65.0

    # -------- RESET FUNCTION --------
    def reset_inputs():
        st.session_state["inflow"] = default_inflow
        st.session_state["outflow"] = default_outflow
        st.session_state["rate"] = default_rate
        st.session_state["date"] = pd.to_datetime("today")

    # -------- INITIALIZE SESSION --------
    if "inflow" not in st.session_state:
        reset_inputs()

    # Sidebar Inputs
    st.sidebar.header("Input Data")

    inflow = st.sidebar.number_input("Cash Inflow", key="inflow")
    outflow = st.sidebar.number_input("Cash Outflow", key="outflow")
    rate = st.sidebar.number_input("Currency Rate", key="rate")
    date = st.sidebar.date_input("Select Date", key="date")

    # Extract features
    day = date.day
    month = date.month

    # Buttons side by side
    col1, col2 = st.sidebar.columns(2)

    # Predict
    if col1.button("Predict"):
        pred = model.predict([[inflow, outflow, rate, month, day]])
        st.success(f"💰 Predicted Cash Flow: {pred[0]:,.2f}")

    # ✅ Clear Button (FIXED)
    col2.button("Clear", on_click=reset_inputs)
