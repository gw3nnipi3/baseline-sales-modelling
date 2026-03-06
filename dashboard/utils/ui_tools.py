import streamlit as st
import pandas as pd
from typing import Any
import ast
from utils.global_const import (
    WIDGET_SETTING,
    WIDGET_DISPLAY_TYPE,
    WIDGET_COLUMN_COUNT,
    FILTER_LIST,
)
from utils.widget_helpers import (
    widgetOptionFilter,
    widgetOptionDate,
    createKPI,
    createForecast,
    createBacktest,
    createDecomposition,
)


# NOTE: Widget render function
def renderWidget(widget: dict[str, Any]):
    display_type = widget["DISPLAY_TYPE"]
    widget_idx = widget["WIDGET_INDEX"]
    widget_title = widget["WIDGET_TITLE"]

    widget["FILTERS"] = (
        {key: "----- SELECT -----" for key in FILTER_LIST}
        if not widget["FILTERS"]
        else widget["FILTERS"]
    )

    # NOTE: REVAMPED RENDER WIGET
    title_container = st.empty()
    title_container.title(f"{widget_title}")

    col = st.columns(2)
    with col[0].popover("Change Title"):
        new_title = st.text_input("New Title", widget["WIDGET_TITLE"])
        widget["WIDGET_TITLE"] = new_title
        title_container.title(new_title)

    with col[1].popover("Select Product"):
        # Insert Option Code HERE
        widgetOptionFilter(widget)

        # Insert Date Code HERE
        widgetOptionDate(widget)

        if st.button("Clear Option", key=f"{widget_idx}_clear_btn"):
            widgetOptionFilter(widget, toClear=True)
            widgetOptionDate(widget, toClear=True)

    match display_type:
        case "KPI":
            createKPI(widget)
            pass
        case "Forecast":
            createForecast(widget)
            pass
        case "Backtest Performance":
            createBacktest(widget)
            pass
        case "Decomposition":
            createDecomposition(widget)
            pass
        case _:
            st.success(f"widget display for {display_type}")
            pass

    # NOTE:--------New Widget Render END-------------


def renderAll():
    widgetCols = st.columns(WIDGET_COLUMN_COUNT)
    for i, widget in enumerate(st.session_state.widgets):
        col = i % WIDGET_COLUMN_COUNT

        with widgetCols[col]:
            renderWidget(widget)
            print("|||||||||| RENDER ALL ||||||||||")
            print(widget)
            print("|||||||||| RENDER ALL ||||||||||")


def saveConfig(
    widget_title: str,
    data_source: str,
    display_type: str,
    widget: dict[str, Any] = dict(),
):
    w = dict()
    for s in WIDGET_SETTING:
        w[s] = widget.get(s, None)

    w["DATA_SOURCE"] = widget.get("DATA_SOURCE", data_source)
    w["DISPLAY_TYPE"] = widget.get("DISPLAY_TYPE", display_type)
    w["WIDGET_TITLE"] = widget.get("WIDGET_TITLE", widget_title)

    index = 0
    if not widget or not widget.get("WIDGET_INDEX", None):
        st.session_state.widget_index += 1
        index = st.session_state.widget_index
    else:
        index = widget["WIDGET_INDEX"]

    w["WIDGET_INDEX"] = index

    st.session_state.widgets.append(w)


# NOTE: Layout Function
def exportLayout():
    data = {"DATA_SOURCE": [], "DISPLAY_TYPE": []}
    for widget in st.session_state.widgets:
        for s in WIDGET_SETTING:
            data[s] = data.get(s, [])
            data[s].append(widget.get(s, None))

    df = pd.DataFrame(data)
    return df.to_csv().encode("utf-8")


def importLayout(csvLayout):
    if csvLayout is not None:
        st.session_state.widgets = []
        dfLayout = pd.read_csv(csvLayout, converters={"FILTERS": ast.literal_eval})
        dfLayout = dfLayout.sort_values(by="WIDGET_INDEX")

        for i in range(len(dfLayout)):
            widget = dict()
            for s in WIDGET_SETTING:
                widget[s] = dfLayout[s].iloc[i]

            saveConfig(
                data_source=widget["DATA_SOURCE"],
                display_type=widget["DISPLAY_TYPE"],
                widget_title=widget["WIDGET_TITLE"],
                widget=widget,
            )
        st.session_state.widget_index = dfLayout["WIDGET_INDEX"].max()
