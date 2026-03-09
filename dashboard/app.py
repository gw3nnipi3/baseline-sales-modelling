import streamlit as st
import pandas as pd
from pathlib import Path
from utils.global_const import WIDGET_DISPLAY_TYPE
from utils.ui_tools import (
    renderAll,
    saveConfig,
    exportLayout,
    importLayout,
)

st.set_page_config(
    page_title="Dashboard",
    page_icon="👋",
    layout="wide",
)

if "widgets" not in st.session_state:
    st.session_state.widgets = []

if "widget_index" not in st.session_state:
    st.session_state.widget_index = 0


st.write("# Welcome to Dashboard!")

_ = st.sidebar.success("Select a demo above.")


# NOTE: st.session_state.widget encoding
# DATA_SOURCE DISPLAY_TYPE (for the future DATE_RANGE)

renderAll()

# NOTE: side bar buttons
with st.sidebar:
    with st.popover("Upload dataset"):
        uploaded_dataset = st.file_uploader(
            "Upload dataset", type=["csv", "xlsx"])
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

        widgetTitle = st.text_input(
            "Widget Title", f"Widget #{st.session_state.widget_index + 1}"
        )
        dataSource = st.selectbox("Data Source", datasets, 0)
        displayType = st.selectbox("Display Type", WIDGET_DISPLAY_TYPE, 0)

        if dataSource == "Pick Dataset":
            st.error("Choose a valid dataset")

        else:
            if st.button("Save & Add"):
                saveConfig(
                    data_source=dataSource,
                    display_type=displayType,
                    widget_title=widgetTitle,
                )
                st.rerun()

with st.sidebar:
    if st.button("Clear All", "clearWidget"):
        st.session_state.widgets = []
        st.session_state.widget_index = 0
        print("xxxxxxxxxxxxxxxxx CLEAR ALL xxxxxxxxxxxxxxxxx")
        print(st.session_state.widgets)
        print(st.session_state.widget_index)
        print("xxxxxxxxxxxxxxxxx CLEAR ALL xxxxxxxxxxxxxxxxx")
        st.rerun()

with st.sidebar:
    with st.popover("Click to Import Layout"):
        csvLayout = st.file_uploader(
            "Import Layout",
            type=["csv"],
        )

        if st.button("Confirm Import"):
            print("||||||||||||||||||| IMPORT CALLED |||||||||||||||||||")
            print("||||||||||||||||||| IMPORT CALLED |||||||||||||||||||")
            print("||||||||||||||||||| IMPORT CALLED |||||||||||||||||||")
            importLayout(csvLayout)
            st.rerun()

with st.sidebar:
    with st.popover("Click to Export Layout"):
        # print("|||||||||||||||||||")
        # print(st.session_state.widgets)
        # print("|||||||||||||||||||")
        csv = exportLayout()
        st.download_button(
            label="Ready for Download",
            data=csv,
            file_name="layout.csv",
            mime="text/csv",
            icon=":material/download:",
            on_click="rerun",
        )
