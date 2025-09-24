import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Investment Model: Property vs Super", layout="centered")
st.title("🏡 Property Investment vs 🏦 Superannuation")

st.sidebar.header("Input Parameters")

# ---- Input parameters ----
initial_property = st.sidebar.number_input("Initial Property Value ($)", value=1_300_000, step=50_000)
property_growth = st.sidebar.number_input("Annual Property Growth Rate (%)", value=3.5, step=0.1) / 100
annual_rent = st.sidebar.number_input("Annual Rent ($)", value=54_000, step=1_000)
loan_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=1)
loan_rate = st.sidebar.number_input("Loan Interest Rate (%)", value=5.09, step=0.1) / 100

super_growth = st.sidebar.number_input("Annual Super Growth Rate (%)", value=7.5, step=0.1) / 100
years = st.sidebar.slider("Projection Years", 10, 40, 30)

# ---- NSW Stamp Duty Function ----
def calculate_stamp_duty_nswd(value):
    if value <= 14000:
        return value * 0.0125
    elif value <= 30000:
        return 175 + (value - 14000) * 0.015
    elif value <= 80000:
        return 415 + (value - 30000) * 0.0175
    elif value <= 300000:
        return 1290 + (value - 80000) * 0.035
    elif value <= 1000000:
        return 8990 + (value - 300000) * 0.045
    else:
        return 40490 + (value - 1000000) * 0.055

# ---- Stamp Duty ----
stamp_duty = calculate_stamp_duty_nswd(initial_property)

# ---- Simulation ----
property_values = []
property_equity = []
super_values = []
differences = []

property_val = initial_property
super_val = stamp_duty   # super starts with stamp duty (opportunity cost)
loan_balance = initial_property  # assume 100% loan for simplicity

# annuity repayment formula (annual mortgage repayment)
r = loan_rate
n = loan_years
annual_payment = loan_balance * (r * (1 + r)**n) / ((1 + r)**n - 1)

for year in range(1, years + 1):
    # property growth
    property_val *= (1 + property_growth)

    # loan amortization
    if loan_balance > 0:
        interest = loan_balance * r
        principal = annual_payment - interest
        loan_balance = max(0, loan_balance - principal)
    else:
        interest = 0
        principal = 0

    # equity = property value - remaining loan
    equity = property_val - loan_balance

    # net cash outflow = mortgage repayment - rental income
    net_cash_out = annual_payment - annual_rent
    if net_cash_out < 0:
        net_cash_out = 0

    # super balance grows with reinvested cash outflow
    super_val = super_val * (1 + super_growth) + net_cash_out

    # difference between property equity and super
    difference = equity - super_val

    # save results
    property_values.append(property_val)
    property_equity.append(equity)
    super_values.append(super_val)
    differences.append(difference)

# ---- Results Table ----
df = pd.DataFrame({
    "Year": range(1, years + 1),
    "Forecasted Property Value": property_values,
    "Net Equity From Property": property_equity,
    "Super Value": super_values,
    "Difference (Equity - Super)": differences
})

st.subheader("Comparison Table")
st.dataframe(df.style.format("${:,.0f}"))

# ---- Chart ----
st.subheader("Comparison Chart")
fig, ax = plt.subplots()
ax.plot(df["Year"], df["Net Equity From Property"], label="Net Equity From Property", linewidth=2)
ax.plot(df["Year"], df["Super Value"], label="Super Value", linewidth=2)
ax.plot(df["Year"], df["Difference (Equity - Super)"], label="Difference", linestyle="--")
ax.set_xlabel("Year")
ax.set_ylabel("Value ($)")
ax.legend()
st.pyplot(fig)

st.info(f"Stamp Duty (NSW) = ${stamp_duty:,.0f}")
