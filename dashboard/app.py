import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from utils.ui_tools import *

st.set_page_config(
    page_title="Dashboard",
    page_icon="👋",
)

if "widgets" not in st.session_state:
    st.session_state.widgets = []

if "widget_index" not in st.session_state:
    st.session_state.widget_index = 0


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


# NOTE: st.session_state.widget encoding
# DATA_SOURCE DISPLAY_TYPE (for the future DATE_RANGE)


# NOTE: side bar buttons
with st.sidebar:
    with st.popover("Upload dataset"):
        uploaded_dataset = st.file_uploader("Upload dataset", type=["csv", "xlsx"])
        if uploaded_dataset:
            if uploaded_dataset.name.endswith(".csv"):
                df = pd.read_csv(uploaded_dataset)
                df.to_csv(f"data/{uploaded_dataset.name}", index=False)
                st.success(f"Saved {uploaded_dataset.name} to data/ folder")

            elif uploaded_dataset.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_dataset)
                df.to_excel(f"data/{uploaded_dataset.name}", index=False)
                st.success(f"Saved {uploaded_dataset.name} to data/ folder")

with st.sidebar:
    with st.popover("+ Add Widget"):
        datasetPath = Path("data/")
        datasets = [f.name for f in datasetPath.iterdir() if f.is_file()]
        datasets.insert(0, "Pick Dataset")

        dataSource = st.selectbox("Data Source", datasets, 0)
        displayType = st.selectbox("Graph Type", widgetType, 0)

        if st.button("Save & Add"):
            saveConfig(dataSource, displayType)
            st.rerun()

with st.sidebar:
    if st.button("Clear All", "clearWidget"):
        st.session_state.widgets = []
        st.session_state.widget_index = 0
        renderAll()
        st.rerun()

with st.sidebar:
    with st.popover("Click to Import Layout"):
        csvLayout = st.file_uploader(
            "Import Layout",
            type=["csv"],
        )

    importLayout(csvLayout)

with st.sidebar:
    with st.popover("Click to Export Layout"):
        csv = exportLayout(st.session_state.widgets)
        st.download_button(
            label="Ready for Download",
            data=csv,
            file_name="layout.csv",
            mime="text/csv",
            icon=":material/download:",
            on_click="rerun",
        )

renderAll()
