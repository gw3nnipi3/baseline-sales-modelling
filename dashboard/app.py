import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from src.data.processing import load_data, create_baseline_series
from src.models.sarima import backtest_sarima
from src.data.ingestion import save_uploaded_file, load_excel_file
from src.models.decomposition import decompose_series

st.set_page_config(page_title="Baseline Sales Dashboard", layout="wide")

# ----------------------
# Load and Prepare Data
# ----------------------
@st.cache_data
def get_data():
    return load_data("data/raw/data.csv")

df = get_data()

# ----------------------
# Product Selection Dropdown
# ----------------------
product_options = list(df["product_sku_code"].unique())
product_options.insert(0, "All Products")
selected_product = st.sidebar.selectbox("Select Product", product_options)

@st.cache_data
def get_baseline_for_product(df, selected_product):
    baseline_series = pd.Series(dtype=float)

    if selected_product == "All Products":
        for sku in df["product_sku_code"].unique():
            for customer in df["customer"].unique():
                series = create_baseline_series(df, sku_id=sku, customer_id=customer)
                baseline_series = baseline_series.add(series, fill_value=0)
    else:
        for customer in df["customer"].unique():
            series = create_baseline_series(df, sku_id=selected_product, customer_id=customer)
            baseline_series = baseline_series.add(series, fill_value=0)

    return baseline_series

# Compute baseline_series based on selection
baseline_series = get_baseline_for_product(df, selected_product)
model_df = baseline_series.to_frame(name="sales")

# ----------------------
# Run Backtest SARIMA
# ----------------------
@st.cache_resource
def get_model_results(model_df):
    return backtest_sarima(model_df)

train, test, forecast_mean, forecast_ci = get_model_results(model_df)
# ----------------------
# Seasonal Decomposition
# ----------------------
@st.cache_data
def get_decomposition(series):
    return decompose_series(series)

decomp_df = get_decomposition(baseline_series)
# ----------------------
# Initialize Session State
# ----------------------
if "widgets" not in st.session_state:
    st.session_state.widgets = []
if "openConfig" not in st.session_state:
    st.session_state.openConfig = False

# ----------------------
# Sidebar Menu
# ----------------------
st.sidebar.title("Navigation")
sections = ["Dashboard", "Backtest Performance", "Seasonal Analysis", "Cannibalisation", "Upload Data"]
page = st.sidebar.radio("Go to:", sections, index=0)

# ----------------------
# KPI Summary Function
# ----------------------
def renderKPIs():
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Weekly Sales", f"{baseline_series.sum():,.0f}")
    kpi2.metric("Average Weekly Sales", f"{baseline_series.mean():,.0f}")
    kpi3.metric("Last Week Sales", f"{baseline_series.iloc[-1]:,.0f}")

# ----------------------
# Widget Renderer
# ----------------------
def renderWidget(widget):
    data = widget["data"]
    chart_type = widget["type"]
    title = widget["title"]

    st.markdown(f"### {title}")

    if chart_type == "Line":
        chart = alt.Chart(data.reset_index()).mark_line().encode(
            x="date:T",
            y=alt.Y(data.name or "sales:Q", title="Sales"),
            tooltip=["date:T", alt.Tooltip(data.name or "sales:Q", title="Sales")]
        ).interactive().properties(height=300).configure_legend(orient="bottom").configure_view(strokeWidth=0)
        st.altair_chart(chart, use_container_width=True)

    elif chart_type == "Backtest":
        df_list = []
        if data.get("train") is not None:
            train_df = data["train"]
            train_df = train_df.to_frame(name="Train") if isinstance(train_df, pd.Series) else train_df.rename(columns={"sales":"Train"})
            df_list.append(train_df)
        if data.get("test") is not None:
            test_df = data["test"]
            test_df = test_df.to_frame(name="Test") if isinstance(test_df, pd.Series) else test_df.rename(columns={"sales":"Test"})
            df_list.append(test_df)
        if data.get("prediction") is not None:
            pred_df = pd.DataFrame(data["prediction"]).rename(columns={data["prediction"].name or "sales":"Prediction"})
            df_list.append(pred_df)

        combined = pd.concat(df_list, axis=1)
        combined_long = combined.reset_index().melt("date", var_name="Series", value_name="Sales")

        chart = alt.Chart(combined_long).mark_line().encode(
            x="date:T",
            y="Sales:Q",
            color=alt.Color("Series:N", scale=alt.Scale(scheme="category10"), legend=alt.Legend(orient="bottom")),
            tooltip=["date:T","Series:N","Sales:Q"]
        ).interactive().properties(height=300).configure_view(strokeWidth=0)

        st.altair_chart(chart, use_container_width=True)

    elif chart_type == "Decomposition":
        decomp_plot = data.dropna().reset_index().melt("date", var_name="Component", value_name="Value")
        chart = alt.Chart(decomp_plot).mark_line().encode(
            x="date:T",
            y="Value:Q",
            color=alt.Color("Component:N", scale=alt.Scale(scheme="category10"), legend=alt.Legend(orient="bottom")),
            tooltip=["date:T","Component:N","Value:Q"]
        ).interactive().properties(height=300).configure_view(strokeWidth=0)
        st.altair_chart(chart, use_container_width=True)

    if st.button("Remove", key=f"remove_{title}"):
        st.session_state.widgets = [w for w in st.session_state.widgets if w["title"] != title]
        st.rerun()

# ----------------------
# Render All Widgets (2 per row)
# ----------------------
def renderAll():
    if not st.session_state.widgets:
        st.info("No widgets to display. Add some in the sidebar.")
        return
    with st.container():
        for i, widget in enumerate(st.session_state.widgets):
            if i % 2 == 0:
                row = st.columns(2)
            col = row[i % 2]
            with col:
                renderWidget(widget)

# ----------------------
# Page Layouts
# ----------------------
if page == "Dashboard":
    st.header("Dashboard Overview")
    renderKPIs()
    renderAll()

elif page == "Backtest Performance":
    st.header("Backtest Performance")
    plot_df = pd.concat([
        train.rename(columns={"sales":"Train"}),
        test.rename(columns={"sales":"Test"})
    ], axis=1)
    plot_df["Prediction"] = forecast_mean
    plot_df = plot_df.reset_index().melt("date", var_name="Series", value_name="Sales")
    chart = alt.Chart(plot_df).mark_line().encode(
        x="date:T",
        y="Sales:Q",
        color=alt.Color("Series:N", scale=alt.Scale(scheme="category10"), legend=alt.Legend(orient="bottom")),
        tooltip=["date:T","Series:N","Sales:Q"]
    ).interactive().properties(height=400).configure_view(strokeWidth=0)
    st.altair_chart(chart, use_container_width=True)

elif page == "Seasonal Analysis":
    st.header("Seasonal Decomposition")
    decomp_plot = decomp_df.dropna().reset_index()
    def make_component_chart(df, column, title):
        return alt.Chart(df).mark_line().encode(
            x="date:T",
            y=alt.Y(f"{column}:Q", title=title),
            tooltip=["date:T", f"{column}:Q"]
        ).properties(height=150)
    observed_chart = make_component_chart(decomp_plot, "observed","Observed Sales")
    trend_chart = make_component_chart(decomp_plot,"trend","Trend")
    seasonal_chart = make_component_chart(decomp_plot,"seasonal","Seasonality")
    resid_chart = make_component_chart(decomp_plot,"resid","Residual")
    stacked_chart = alt.vconcat(observed_chart, trend_chart, seasonal_chart, resid_chart).resolve_scale(x='shared')
    st.altair_chart(stacked_chart, use_container_width=True)

elif page == "Cannibalisation":
    st.header("Cannibalisation Analysis (Coming Soon)")
    st.info("This section will show cannibalisation charts once available.")

elif page == "Upload Data":
    st.header("Upload New Data")
    uploaded_file = st.file_uploader("Upload new Excel file", type=["xlsx"])
    if uploaded_file is not None:
        saved_path = save_uploaded_file(uploaded_file)
        st.success(f"Saved to {saved_path}")

# ----------------------
# Widget Config Sidebar
# ----------------------
if st.sidebar.button("+ Add Widget"):
    st.session_state.openConfig = True
    st.rerun()

if st.sidebar.button("Clear All Widgets"):
    st.session_state.widgets = []
    st.rerun()

if st.session_state.openConfig:
    with st.sidebar.expander("Configure & Save", True):
        st.write("Create a new chart")
        chart_option = st.selectbox("Select Chart", ["Baseline Sales","Backtest Performance","Forecast","Seasonal Decomposition"])
        title = st.text_input("Widget Title", value=chart_option)
        if st.button("Save & Add", key="save_widget"):
            if chart_option == "Baseline Sales":
                data = model_df["sales"]
                chart_type = "Line"
            elif chart_option == "Backtest Performance":
                data = {"train": train, "test": test, "prediction": forecast_mean, "ci": forecast_ci}
                chart_type = "Backtest"
            elif chart_option == "Forecast":
                data = forecast_mean
                chart_type = "Line"
            elif chart_option == "Seasonal Decomposition":
                data = decomp_df
                chart_type = "Decomposition"

            st.session_state.widgets.append({"data": data, "type": chart_type, "title": chart_option})
            st.session_state.openConfig = False
            st.rerun()