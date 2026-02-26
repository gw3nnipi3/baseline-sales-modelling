import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="this is second page",
    page_icon="👋",
)

print(f"Type of session_state is: {type(st.session_state)}")
print(f"Value is: {st.session_state}")

if "widgets" not in st.session_state:
    st.session_state.widgets = []
if "openConfig" not in st.session_state:
    st.session_state.openConfig = False

widgetType = ["Line", "Bar", "Scatter"]

st.write("# Welcome to Second Page!")

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
