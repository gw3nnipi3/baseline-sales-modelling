import streamlit as st
from datetime import timedelta
import pandas as pd
from typing import Any
from utils.data_tools import (
    load_data,
    process_data,
    get_valid_options,
    get_kpi_data,
    get_forecast_df,
    plot_forecast_with_promos,
    get_pred_obs_df,
    get_performance_metrics,
)
from utils.global_const import FILTER_LIST
from prophet.plot import plot_cross_validation_metric


@st.fragment
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


@st.fragment
def widgetOptionDate(widget: dict[str, Any], toClear: bool = False):
    widget_idx = widget["WIDGET_INDEX"]
    data_source = widget["DATA_SOURCE"]
    df = load_data(data_source)

    # WARNING: prob do not need this now that
    # all sku code data are cleaned to have 0 sales
    valid_weeks = df["date"].dt.strftime("%Y-%m-%d").unique().tolist()

    if toClear:
        print("~~~~~~~~~~~ TO CLEAR DATE ~~~~~~~~~~~")
        print("~~~~~~~~~~~ TO CLEAR DATE ~~~~~~~~~~~")
        print("~~~~~~~~~~~ TO CLEAR DATE ~~~~~~~~~~~")
        widget["START_DATE"] = valid_weeks[0]
        widget["END_DATE"] = valid_weeks[-1]
        return

    start_date = widget.get("START_DATE", None)
    if not start_date:
        start_date = valid_weeks[0]
    end_date = widget.get("END_DATE", None)
    if not end_date:
        end_date = valid_weeks[-1]

    if widget["DISPLAY_TYPE"] != "Forecast":
        is_custom = st.toggle(
            "Custom Range",
            key=f"{widget['WIDGET_INDEX']}",
            value=True,
        )
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
    else:
        cols = st.columns(2)
        start_date = cols[0].select_slider(
            "Select Start Date",
            options=valid_weeks,
            value=start_date,
            key=f"{widget_idx}_forecast_date_slider",
        )

        widget["START_DATE"] = start_date
        widget["END_DATE"] = valid_weeks[-1]

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


def processForecastLength(forecast_len_str: str) -> (int, str, pd.Timedelta):
    forecast_length = int(forecast_len_str[:-1])
    match(forecast_len_str[-1]):
        case "W":
            time_delta = pd.Timedelta(forecast_length*1, "W")
            time_period = "weeks"
        case "M":
            time_delta = pd.Timedelta(forecast_length*4, "W")
            time_period = "months (4 weeks)"
        case "Y":
            time_delta = pd.Timedelta(forecast_length*52, "W")
            time_period = "years (52 weeks)"
    return forecast_length, time_period, time_delta


def createForecastOption(widget: dict[str, Any]):
    widget_idx = widget["WIDGET_INDEX"]
    # forecast_len = int(widget["FORECAST_LENGTH"][:-1])
    # time_period = "weeks"
    # if widget["FORECAST_LENGTH"]:
    #    match(widget["FORECAST_LENGTH"][-1]):
    #        case "W":
    #            time_period = "weeks"
    #        case "M":
    #            time_period = "months (4 weeks)"
    #        case "Y":
    #            time_period = "years (52 weeks)"

    # NOTE: get existing widget value
    #
    # forecast_len = (
    #     int(widget["FORECAST_LENGTH"][:-1])
    #     if widget.get("FORECAST_LENGTH", None) else 3  # default value
    # )
    # time_period = "months (4 weeks)"  # default value
    # if widget["FORECAST_LENGTH"]:
    #     match(widget["FORECAST_LENGTH"][-1]):
    #         case "W":
    #             time_period = "weeks"
    #         case "M":
    #             time_period = "months (4 weeks)"
    #         case "Y":
    #             time_period = "years (52 weeks)"
    forecast_len, time_period, _ = processForecastLength(
        widget["FORECAST_LENGTH"])

    # NOTE: real render
    cols = st.columns(2)
    forecast_len = cols[0].number_input(
        "Forecast Window:",
        value=forecast_len,
        min_value=1,
        max_value=1000,
        key=f"{widget_idx}_forecast_window_input"
    )

    period_options = ["weeks", "months (4 weeks)", "years (52 weeks)"]
    time_period = cols[1].selectbox(
        "Time Period:",
        options=period_options,
        key=f"{widget_idx}_time_period",
        index=period_options.index(time_period)
    )

    match(time_period):
        case "weeks":
            widget["FORECAST_LENGTH"] = str(forecast_len)+"W"
        case "months (4 weeks)":
            widget["FORECAST_LENGTH"] = str(forecast_len)+"M"
        case "years (52 weeks)":
            widget["FORECAST_LENGTH"] = str(forecast_len)+"Y"


def createPromotionOption(widget: dict[str, Any]):
    widget_idx = widget["WIDGET_INDEX"]

    # # NOTE: Prepare existing value

    _, _, time_delta = processForecastLength(
        widget["FORECAST_LENGTH"])
    start_forecast_date = pd.to_datetime(
        widget["END_DATE"]) + pd.Timedelta(weeks=1)
    end_forecast_date = start_forecast_date + time_delta

    # NOTE: real render
    window_set = widget["PROMOTION_WINDOWS"]

    # NOTE: for the promotion
    cols = st.columns(2)
    promo_start_date = cols[0].slider(
        "Promotion Start Date:",
        min_value=start_forecast_date.to_pydatetime(),
        max_value=end_forecast_date.to_pydatetime(),
        step=timedelta(weeks=1),
        key=f"{widget_idx}_promo_start_date"
    )

    promo_length = cols[1].number_input(
        "Promotion Length (weeks):",
        value=0,
        min_value=0,
        max_value=1000,
        key=f"{widget_idx}_promo_len_input"
    )

    cols = st.columns(2)
    if cols[0].button("Add Promotion", key=f"{widget_idx}_add_promo_btn"):
        promo_date_list = pd.date_range(
            start=promo_start_date, periods=promo_length, freq="W-MON"
        ).strftime("%Y-%m-%d").tolist()  # this is a list of strings

        window_set.update(promo_date_list)
        widget["PROMOTION_WINDOWS"] = window_set
        # st.write(promo_start_date)
        st.write(date for date in widget["PROMOTION_WINDOWS"])
        # st.write(date for date in widget["PROMOTION_WINDOWS"])


@st.fragment
def createForecast(widget: dict[str, Any]):
    # NOTE: prepare existing value
    if not widget.get("FORECAST_LENGTH", None):
        widget["FORECAST_LENGTH"] = "3M"

    if not widget.get("PROMOTION_WINDOWS", None):
        widget["PROMOTION_WINDOWS"] = set()

    # NOTE: real render
    st.write("### Forecast")
    chart_box = st.empty()
    cols = st.columns(3)
    with cols[0].popover("Forecast Config"):
        createForecastOption(widget)

    with cols[1].popover("Promotion Config"):
        createPromotionOption(widget)
    # st.write("this is promotion window")
    # st.write(data for data in widget["PROMOTION_WINDOWS"])
    # st.write("promotion window end")

    # if cols[2].button("Confirm Config"):

    forecast_length, time_period, time_delta = processForecastLength(
        widget["FORECAST_LENGTH"])
    start_forecast_date = (pd.to_datetime(widget["END_DATE"]) +
                           pd.Timedelta(1, "W"))
    end_forecast_date = start_forecast_date + time_delta

    forecast_df = get_forecast_df(
        widget["DATA_SOURCE"],
        widget["FILTERS"],
        end_forecast_date,
        widget["PROMOTION_WINDOWS"]
    )
    chart_box.pyplot(plot_forecast_with_promos(
        forecast_df, widget["START_DATE"]))


def createPredObs(widget: dict[str, Any]):
    forecast = get_pred_obs_df(
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
    forecast = get_pred_obs_df(
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
