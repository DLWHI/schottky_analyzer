import streamlit as st
import plotly.express as px
import plotly.graph_objects  as go
import pandas as pd
import schottky_analyzer as sa

st.set_page_config(page_title="Schottky diode characteristics")

class view:
    def __init__(self, dataframe, area) -> None:
        self.__df = dataframe
        self.__analyzer = sa.Analyzer(dataframe["Voltage (V)"], dataframe["Current (A)"], area)

    def logRelation(self):
        self.__df["Density (A/m^2)"] = self.__analyzer.getDensity()
        self.__df["dV/d(lnJ) (V)"] = pd.Series(self.__analyzer.getVoltageLn())

        fig = px.line(
            self.__df,
            x="Density (A/m^2)",
            y="dV/d(lnJ) (V)",
            color="Light",
            markers=True,
            line_shape="spline",
            render_mode="svg",
        )
        return fig

    def resistance(self):
        return self.__analyzer.getResistance()

    def ideality(self):
        return self.__analyzer.getIdeality()

def wipe_state(keys):
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]

def read_data(source):
    if ".csv" in source:
        return pd.read_csv(source)

with st.sidebar.form(key="Params"):
    source_file = st.text_input("I-V measurments file", placeholder="*.csv")
    active_area = st.number_input("Active Area (cm)", value=1e-4, format="%.1e")
    data = st.form_submit_button("Characterize")

if data:
    wipe_state(["fig", "fig_difference", "fig_log", "calculated", "df"])
    st.session_state["df"] = read_data(source_file)
    model_view = view(st.session_state["df"], active_area)
    st.session_state["fig"] = model_view.logRelation()
    st.plotly_chart(st.session_state["fig"], use_container_width=True)
    st.markdown(f"Resistance = {model_view.resistance():.4} Ohm")
    st.markdown(f"Ideality factor = {model_view.ideality():.4}")
    # st.markdown(f"Schottky barrier height = {calc.getResistance():.4} Ohm")
    
df = read_data("measurements_no_clusters.csv")
model_view = view(df, 1e-4)
model_view.logRelation()