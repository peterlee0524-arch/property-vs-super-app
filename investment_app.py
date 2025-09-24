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

# ---- Simulation ----
property_values = []
property_equity = []
super_values = []
cash_outflows = []

property_val = initial_property
super_val = 0.0
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
        net_cash_out = 0  # don't allow negative, assume extra rent isn't invested
    cash_outflows.append(net_cash_out)

    # super balance grows with reinvested cash outflow
    super_val = super_val * (1 + super_growth) + net_cash_out

    # save results
    property_values.append(property_val)
    property_equity.append(equity)
    super_values.append(super_val)

# ---- Results Table ----
df = pd.DataFrame({
    "Year": range(1, years + 1),
    "Property Value": property_values,
    "Property Equity": property_equity,
    "Super Value": super_values,
    "Net Cash Outflow": cash_outflows
})

st.subheader("Comparison Table")
st.dataframe(df.style.format("${:,.0f}"))

# ---- Chart ----
st.subheader("Comparison Chart")
fig, ax = plt.subplots()
ax.plot(df["Year"], df["Property Equity"], label="Property Equity", linewidth=2)
ax.plot(df["Year"], df["Super Value"], label="Super Value", linewidth=2)
ax.set_xlabel("Year")
ax.set_ylabel("Value ($)")
ax.legend()
st.pyplot(fig)
