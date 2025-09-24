import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Investment Model: Property vs Super", layout="centered")
st.title("🏡 Property Investment vs 🏦 Superannuation")

st.sidebar.header("Input Parameters")

# ---- Inputs ----
initial_property = st.sidebar.number_input("Initial Property Value ($)", value=1_300_000, step=50_000)
property_growth = st.sidebar.number_input("Annual Property Growth Rate (%)", value=3.5, step=0.1) / 100
annual_rent = st.sidebar.number_input("Annual Rent ($)", value=54_000, step=1_000)
loan_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=1)
loan_rate = st.sidebar.number_input("Loan Interest Rate (%)", value=5.09, step=0.1) / 100
super_growth = st.sidebar.number_input("Annual Super Growth Rate (%)", value=7.5, step=0.1) / 100
years = st.sidebar.slider("Projection Years", 5, 40, 30)

# ---- Stamp Duty mode ----
stamp_mode = st.sidebar.selectbox(
    "Stamp Duty Mode",
    ["Fixed $55,000", "NSW slabs (residential)"],
    index=0
)

def calculate_stamp_duty_nsw(value: float) -> float:
    # NSW residential transfer duty (简化分档，未含优惠/首次购房减免)
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

if stamp_mode == "Fixed $55,000":
    stamp_duty = 55_000.0
else:
    stamp_duty = calculate_stamp_duty_nsw(initial_property)

st.sidebar.metric("Calculated Stamp Duty", f"${stamp_duty:,.0f}")

# ---- Simulation state ----
property_values, property_equity = [], []
super_values, differences = [], []

property_val = initial_property
loan_balance = initial_property   # 假设 100% LVR，对应模板
super_val = stamp_duty            # Year 0：仅将印花税作为机会成本投入 super

# 年度本息等额还款
r = loan_rate
n = loan_years
annual_payment = loan_balance * (r * (1 + r)**n) / ((1 + r)**n - 1)

# ---- Year 0 行 ----
equity0 = property_val - loan_balance  # 100% LVR → 0
diff0 = equity0 - super_val

year_list = [0]
fv_list = [property_val]
eq_list = [equity0]
super_list = [super_val]
diff_list = [diff0]

# ---- Years 1..N ----
for year in range(1, years + 1):
    # 房价增长
    property_val *= (1 + property_growth)

    # 贷款摊还
    if loan_balance > 0:
        interest = loan_balance * r
        principal = annual_payment - interest
        loan_balance = max(0.0, loan_balance - principal)
    else:
        interest = 0.0
        principal = 0.0

    equity = property_val - loan_balance

    # 机会成本：当年净现金流出 = 年还款 - 年租金（不为负）
    net_cash_out = max(0.0, annual_payment - annual_rent)

    # Super：先按收益增长，再加入当年机会成本
    super_val = super_val * (1 + super_growth) + net_cash_out

    difference = equity - super_val

    year_list.append(year)
    fv_list.append(property_val)
    eq_list.append(equity)
    super_list.append(super_val)
    diff_list.append(difference)

# ---- 结果表 ----
df = pd.DataFrame({
    "Year": year_list,
    "Forecasted Property Value": fv_list,
    "Net Equity From Property": eq_list,
    "Super Value": super_list,
    "Difference (Equity - Super)": diff_list
})

st.subheader("Comparison Table")
st.dataframe(
    df.style.format("${:,.0f}", subset=[
        "Forecasted Property Value", "Net Equity From Property", "Super Value", "Difference (Equity - Super)"
    ])
)

# ---- 图表 ----
st.subheader("Comparison Chart")
fig, ax = plt.subplots()
ax.plot(df["Year"], df["Net Equity From Property"], label="Net Equity From Property", linewidth=2)
ax.plot(df["Year"], df["Super Value"], label="Super Value", linewidth=2)
ax.plot(df["Year"], df["Difference (Equity - Super)"], label="Difference", linestyle="--")
ax.set_xlabel("Year")
ax.set_ylabel("Value ($)")
ax.legend()
st.pyplot(fig)

st.caption(
    "Year 0: Super 仅包含印花税（机会成本）。Year 1 起：Super = 上年余额×(1+增长率) + (年度还款 - 年租金)。"
)
