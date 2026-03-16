import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from src.data.processing import load_data, create_baseline_series
from src.models.sarima import backtest_sarima

st.set_page_config(page_title="Baseline Sales Dashboard")
st.title("Baseline Sales SARIMA Backtest")

# ----------------------
# Load and Prepare Data
# ----------------------
df = load_data("data/raw/data.csv")
sku_id = df["product_sku_code"].iloc[0]
customer_id = df["customer"].iloc[0]

baseline_series = create_baseline_series(
    df,
    sku_id=sku_id,
    customer_id=customer_id,
    exclude_promotions=True
)
model_df = baseline_series.to_frame()


# ----------------------
# Run Backtest SARIMA
# ----------------------
train, test, forecast_mean, forecast_ci = backtest_sarima(model_df)

# ----------------------
# Prepare Data for Altair
# ----------------------
plot_df = pd.concat([
    train.rename(columns={"sales": "Train"}),
    test.rename(columns={"sales": "Test"})
], axis=1)

plot_df["Prediction"] = forecast_mean
plot_df = plot_df.reset_index().melt("date", var_name="Series", value_name="Sales")

# ----------------------
# Streamlit Altair Plot
# ----------------------
chart = alt.Chart(plot_df).mark_line().encode(
    x="date:T",
    y="Sales:Q",
    color="Series:N",
    tooltip=["date:T", "Series:N", "Sales:Q"]
).interactive().properties(
    width=800,
    height=400,
    title="Backtesting: Predicted vs Actual Baseline Sales"
)

st.altair_chart(chart, use_container_width=True)

# ----------------------
# Optional: Show Forecast Only
# ----------------------
st.write("### Forecast for Test Period")
st.line_chart(forecast_mean)

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

print(f"Type of session_state is: {type(st.session_state)}")
print(f"Value is: {st.session_state}")

if "widgets" not in st.session_state:
    st.session_state.widgets = []
if "openConfig" not in st.session_state:
    st.session_state.openConfig = False

widgetType = ["Line", "Bar", "Scatter"]

st.write("# Welcome to Dashboard!")

_ = st.sidebar.success("Select a demo above.")

topBar = st.columns(3)

with topBar[0]:
    heading = st.write("Total Weekly Sales")
    randomStat = st.write(np.random.randint(0, 100000))
    pressMe = st.button("Press me", key="pressMe")
    if pressMe:
        randomStat = np.random.randint(0, 100000)

with topBar[1]:
    heading = st.write("another stat")
    df = pd.DataFrame(np.random.randn(10, 20))
    
    _ = st.line_chart(df)


with topBar[2]:
    test = st.write("More stats")
    if st.toggle("", key="surprise"):
        _ = st.write("surprise")

_ = st.markdown(
    """
    text text text text text text text text text text text 
    text text text text text text text text text text text 
    text text text text text text text text text text text 
    text text text text text text text text text text text 
    text text text text text text text text text text text 
    text text text text text text text text text text text 
    """
)


def renderWidget(data: pd.DataFrame, type: str):
    match type:
        case "Line":
            _ = st.line_chart(data)
        case "Bar":
            _ = st.bar_chart(data)
        case "Scatter":
            _ = st.scatter_chart(data)
        case _:
            pass


def saveConfig(data: pd.DataFrame, type: str):
    st.session_state.widgets.append([data, type])
    st.session_state.openConfig = False


def renderAll():
    widgetCols = st.columns(3)
    for i, w in enumerate(st.session_state.widgets):
        col = i % 3
        # if not w:
        #     break
        data, t = w[0], w[1]
        with widgetCols[col]:
            renderWidget(data, t)


renderAll()
cols = st.columns(2)
with cols[0]:
    if st.button("+ Add Widget", "addWidget"):
        if not st.session_state.openConfig:
            st.session_state.openConfig = True

with cols[1]:
    if st.button("Clear All", "clearWidget"):
        st.session_state.widgets = []
        renderAll()
        st.rerun()

if st.session_state.openConfig:
    with st.expander("Configure & Save", True):
        st.write("somethign something")

        data = pd.DataFrame(np.random.randn(4, 100))
        t = st.selectbox("Graph Type", widgetType, 0)

        if st.button("Save & Add"):
            saveConfig(data, t)
            st.rerun()
