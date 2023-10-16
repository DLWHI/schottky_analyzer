import streamlit as st
import plotly.express as px
import plotly.graph_objects  as go
import pandas as pd
import schottky_analyzer as sa

st.set_page_config(page_title="Schottky diode characteristics")
pd.options.mode.chained_assignment = None 

class view:
    def __init__(self, dataframe, area) -> None:
        self.__df = dataframe[dataframe["Light"] == "Disabled"].reset_index(drop=True)

        self.__model = sa.Analyzer(
            self.__df["Voltage (V)"], 
            self.__df["Current (A)"],
            area
        )
        self.__params = None
        self.__fit_data = None

    def logRelation(self):
        self.__df["Density (A/m^2)"] = pd.Series(self.__model.getDensity())
        self.__df["dV/d(lnJ) (V)"] = pd.Series(self.__model.getVoltageLn())

        fig = px.scatter(
            self.__df,
            x="Density (A/m^2)",
            y="dV/d(lnJ) (V)",
            render_mode="svg",
            trendline='ols'
        )
        return fig

    def hRelation(self):
        self.__df["Density (A/m^2)"] = pd.Series(self.__model.getDensity())
        self.__df["H(J) (V)"] = pd.Series(self.__model.getH())

        fig = px.scatter(
            self.__df,
            x="Density (A/m^2)",
            y="H(J) (V)",
            color="Light",
            render_mode="svg",
            trendline='ols'
        )
        return fig
    
    def parameters(self):
        if self.__params is None:
            self.__params = self.__model.getParameters()
        return self.__params
    
    def fit_data(self):
        if self.__fit_data is None:
            self.__fit_data = self.__model.getFitData()
        return self.__fit_data

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
    wipe_state(["fig_H", "fig_log", "calculated", "df"])
    st.session_state["df"] = read_data(source_file)
    model_view = view(st.session_state["df"], active_area)
    st.session_state["fig_log"] = model_view.logRelation()
    st.session_state["fig_H"] = model_view.hRelation()
    model_view.parameters()
    st.markdown(f"Resistance = {model_view.parameters()[0]:.4} Ohm")
    st.markdown(f"Ideality factor = {model_view.parameters()[1]:.4}")
    st.markdown(f"Schottky barrier height = {model_view.parameters()[2]:.4} ")
    st.markdown("---")
    st.plotly_chart(st.session_state["fig_log"], use_container_width=True)
    st.markdown(f"Fitting data:")
    st.markdown(f"RAeff (slope): {model_view.fit_data()[0][0]:.4}")
    st.markdown(f"n/β (intesection): {model_view.fit_data()[0][1]:.4}")
    st.markdown("---")
    st.plotly_chart(st.session_state["fig_H"], use_container_width=True)
    st.markdown(f"Fitting data:")
    st.markdown(f"RAeff (slope): {model_view.fit_data()[1][0]:.4}")
    st.markdown(f"nφ (intesection): {model_view.fit_data()[1][1]:.4}")
