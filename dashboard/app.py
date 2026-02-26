import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="Dashboard",
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


# NOTE: st.session_state.widget encoding
# DATA_SOURCE DISPLAY_TYPE (for the future DATE_RANGE)


def renderWidget(data_source: str, type: str):
    df = pd.DataFrame({})
    if data_source == "RANDOM":
        df = pd.DataFrame(np.random.randn(10, 20))
    elif data_source.endswith(".csv"):
        df = pd.read_csv(f"data/{data_source}")
        df = df.set_index("yearweek")[["nielsen_total_volume"]]
        df = df.iloc[:1000]
    elif data_source.endswith(".xlsx"):
        df = pd.read_excel(f"data/{data_source}")
        df = df.set_index("yearweek")[["nielsen_total_volume"]]
        df = df.iloc[:1000]
    else:
        st.error("invalid file format")

    match type:
        case "Line":
            _ = st.line_chart(df)
        case "Bar":
            _ = st.bar_chart(df)
        case "Scatter":
            _ = st.scatter_chart(df)
        case _:
            pass


def saveConfig(data_source: str, type: str):
    st.session_state.widgets.append([data_source, type])
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


def exportLayout():
    data = {"DATA_SOURCE": [], "DISPLAY_TYPE": []}
    for setting in st.session_state.widgets:
        data["DATA_SOURCE"].append(setting[0])
        data["DISPLAY_TYPE"].append(setting[1])

    df = pd.DataFrame(data)
    return df.to_csv().encode("utf-8")


renderAll()
cols = st.columns(4)
with cols[0]:
    if st.button("+ Add Widget", "addWidget"):
        if not st.session_state.openConfig:
            st.session_state.openConfig = True

with cols[1]:
    if st.button("Clear All", "clearWidget"):
        st.session_state.widgets = []
        renderAll()
        st.rerun()

with cols[2]:
    csvLayout = st.file_uploader("Upload layout", type=["csv"])
    if csvLayout is not None:
        st.session_state.widgets = []
        dfLayout = pd.read_csv(csvLayout)
        for i in range(len(dfLayout)):
            widget = dfLayout["DATA_SOURCE"].iloc[i] + dfLayout["DISPLAY_TYPE"].iloc[i]
            st.session_state.widgets.append(widget)
        renderAll()
        st.rerun()

with cols[3]:
    if st.button("Export Layout", "exportLayout"):
        csv = exportLayout()
        st.download_button(
            label="Ready for Download",
            data=csv,
            file_name="layout.csv",
            mime="text/csv",
            icon=":material/download:",
            on_click="rerun",
        )

if st.session_state.openConfig:
    with st.expander("Configure & Save", True):
        st.write("somethign something")

        displayType = st.selectbox("Graph Type", widgetType, 0)

        datasetPath = Path("data/")
        datasets = [f.name for f in datasetPath.iterdir() if f.is_file()]

        dataSource = st.selectbox("Data Source", datasets)

        if st.button("Save & Add"):
            saveConfig(dataSource, displayType)
            st.rerun()
