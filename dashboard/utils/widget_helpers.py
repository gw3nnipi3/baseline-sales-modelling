import streamlit as st
import pandas as pd
from typing import Any
from utils.data_tools import (
    load_data,
    process_data,
    get_valid_options,
    get_kpi_data,
    get_forecast_df,
    get_performance_metrics,
)
from utils.global_const import FILTER_LIST
from prophet.plot import plot_cross_validation_metric


def widgetOptionFilter(widget: dict[str, Any], toClear: bool = False):
    if toClear:
        print("~~~~~~~~~~~ TO CLEAR OPTION ~~~~~~~~~~~")
        print("~~~~~~~~~~~ TO CLEAR OPTION ~~~~~~~~~~~")
        print("~~~~~~~~~~~ TO CLEAR OPTION ~~~~~~~~~~~")
        for key in FILTER_LIST:
            widget["FILTERS"][key] = "----- SELECT -----"
        return

    data_source = widget["DATA_SOURCE"]
    widget_idx = widget["WIDGET_INDEX"]
    filter_selection = "Concise"

    filter_selection = st.pills(
        "Filter Type",
        ["Concise", "Verbose"],
        selection_mode="single",
        default="Concise",
        key=f"{widget_idx}_filter_selection",
    )

    valid_options = get_valid_options(data_source, widget["FILTERS"])

    # print("-------------------------- RENDER WIDGET --------------------------")
    # print(widget)
    # print("-------------------------- RENDER WIDGET --------------------------")
    if filter_selection == "Concise":
        for key in FILTER_LIST:
            if key not in ["product_sku_code", "customer"]:
                continue

            current_value = widget["FILTERS"][key]
            safe_index = 0
            if current_value in valid_options[key]:
                safe_index = valid_options[key].index(current_value)
            else:
                safe_index = 0

            widget["FILTERS"][key] = st.selectbox(
                key,
                valid_options[key],
                key=f"{widget_idx}_{key}",
                index=safe_index,
            )

            valid_options = get_valid_options(data_source, widget["FILTERS"])

    elif filter_selection == "Verbose":
        for key in FILTER_LIST:
            if key in ["product_sku_code", "customer"]:
                continue

            current_value = widget["FILTERS"][key]
            safe_index = 0
            if current_value in valid_options[key]:
                safe_index = valid_options[key].index(current_value)
            else:
                safe_index = 0

            widget["FILTERS"][key] = st.selectbox(
                key,
                valid_options[key],
                key=f"{widget_idx}_{key}",
                index=safe_index,
            )

            valid_options = get_valid_options(data_source, widget["FILTERS"])

    else:
        st.write("Select Filter Type to Continue")


def widgetOptionDate(widget: dict[str, Any], toClear: bool = False):
    widget_idx = widget["WIDGET_INDEX"]
    data_source = widget["DATA_SOURCE"]
    df = load_data(data_source)

    valid_weeks = df["date"].dt.strftime("%Y-%m-%d").unique().tolist()

    if toClear:
        print("~~~~~~~~~~~ TO CLEAR DATE ~~~~~~~~~~~")
        print("~~~~~~~~~~~ TO CLEAR DATE ~~~~~~~~~~~")
        print("~~~~~~~~~~~ TO CLEAR DATE ~~~~~~~~~~~")
        widget["START_DATE"] = valid_weeks[0]
        widget["END_DATE"] = valid_weeks[-1]
        return

    is_custom = st.toggle(
        "Custom Range",
        key=f"{widget['WIDGET_INDEX']}",
        value=True,
    )

    start_date = widget.get("START_DATE", None)
    if not start_date:
        start_date = valid_weeks[0]
    end_date = widget.get("END_DATE", None)
    if not end_date:
        end_date = valid_weeks[-1]

    if is_custom:
        start_date, end_date = st.select_slider(
            "Select Date Range",
            options=valid_weeks,
            value=(start_date, end_date),
            key=f"{widget_idx}_custom_date_slider",
        )

    else:
        cols = st.columns(2)
        end_date = cols[0].select_slider(
            "Select End Date",
            options=valid_weeks,
            value=end_date,
            key=f"{widget_idx}_preset_date_slider",
        )

        preset = cols[1].selectbox(
            "Select Range (in weeks)",
            options=[1, 4, 13, 52],
            key=f"{widget_idx}_preset_date_selectbox",
        )

        sd = pd.to_datetime(end_date) - pd.Timedelta(weeks=preset - 1)
        min_date = pd.to_datetime(valid_weeks[0])
        sd = sd if sd >= min_date else min_date
        start_date = sd.strftime("%Y-%m-%d")

    widget["START_DATE"] = start_date
    widget["END_DATE"] = end_date

    # print("--------------OPTION DATE--------------")
    # print(widget)
    # print("--------------OPTION DATE--------------")


def createKPI(widget: dict[str, Any]):
    value, delta = get_kpi_data(
        widget["DATA_SOURCE"],
        widget["FILTERS"],
        widget["START_DATE"],
        widget["END_DATE"],
    )

    deltaPercent = f"{delta * 100:.1f}%"
    st.metric("Total Sales", value=value, delta=deltaPercent)


def createForecast(widget: dict[str, Any]):
    forecast = get_forecast_df(
        widget["DATA_SOURCE"],
        widget["FILTERS"],
        widget["START_DATE"],
        widget["END_DATE"],
    )

    observed = process_data(widget["DATA_SOURCE"], widget["FILTERS"])
    sd = pd.to_datetime(widget["START_DATE"])
    ed = pd.to_datetime(widget["END_DATE"])
    start_idx = observed[observed["date"] >= sd].index[0]
    end_idx = observed[observed["date"] <= ed].index[-1]

    st.write("### Predicted vs Observed")
    chart_data = pd.DataFrame({
        "date": observed["date"].iloc[start_idx:end_idx+1],
        "Observed": observed["nielsen_total_volume"].iloc[start_idx:end_idx+1],
        "Predicted": forecast["yhat"],
    })
    chart_data = chart_data.set_index("date")

    st.line_chart(chart_data)


def createBacktest(widget: dict[str, Any]):
    df_cv = get_performance_metrics(
        widget["DATA_SOURCE"],
        widget["FILTERS"],
    )

    rmse_fig = plot_cross_validation_metric(df_cv, metric='rmse')
    mape_fig = plot_cross_validation_metric(df_cv, metric='mape')
    mae_fig = plot_cross_validation_metric(df_cv, metric='mae')

    st.write("### RMSE")
    st.pyplot(rmse_fig)

    st.write("### MAPE")
    st.pyplot(mape_fig)

    st.write("### MAE")
    st.pyplot(mae_fig)


def createDecomposition(widget: dict[str, Any]):
    forecast = get_forecast_df(
        widget["DATA_SOURCE"],
        widget["FILTERS"],
        widget["START_DATE"],
        widget["END_DATE"],
    )

    st.write("### Decomposition")
    st.write("#### Trend")
    trend_data = pd.DataFrame({
        "date": forecast["ds"],
        "baseline": forecast["trend"],
    })
    trend_data = trend_data.set_index("date")
    st.line_chart(trend_data)

    st.write("#### Seasonal Sales")
    seasonal_data = pd.DataFrame({
        "date": forecast["ds"],
        "baseline": forecast["yhat"] - forecast["extra_regressors_additive"],
        # "baseline": forecast["trend"] * forecast["multiplicative_terms"],
    })
    seasonal_data = seasonal_data.set_index("date")
    st.line_chart(seasonal_data)

    st.write("#### Promotion Uplift")
    promotion_data = pd.DataFrame({
        "date": forecast["ds"],
        "uplift": forecast["extra_regressors_additive"],
        # "uplift": forecast["trend"]*forecast["extra_regressors_multiplicative"],
    })
    promotion_data = promotion_data.set_index("date")
    st.line_chart(promotion_data)

    st.write("#### Residuals")
    observed = process_data(widget["DATA_SOURCE"], widget["FILTERS"])
    sd = pd.to_datetime(widget["START_DATE"])
    ed = pd.to_datetime(widget["END_DATE"])
    start_idx = observed[observed["date"] >= sd].index[0]
    end_idx = observed[observed["date"] <= ed].index[-1]
    observed = observed.iloc[start_idx:end_idx+1]

    residual_data = pd.DataFrame({
        "date": forecast["ds"],
        "residual": observed["nielsen_total_volume"] - forecast["yhat"],
    })
    residual_data = residual_data.set_index("date")
    st.line_chart(residual_data)
