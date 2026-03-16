import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from pathlib import Path
from utils.global_const import WIDGET_DISPLAY_TYPE
from utils.ui_tools import (
    renderAll,
    addWidget,
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
    addWidget()

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
    with st.popover("Export Layout", icon=":material/download:"):
        st.write("Clicking below will sync all widget changes and prepare your file.")

        generate_btn = st.button("Generate CSV")
        if generate_btn:
            csv_data = exportLayout()

            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="layout.csv",
                mime="text/csv",
                on_click=(lambda: not generate_btn)
            )
