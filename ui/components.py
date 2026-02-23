import streamlit as st
from src.ui import visualization
import numpy as np
from database.db_connector import DatabaseConnector

#Startseite mit Eingabefeldern für Länge, Breite und Lagerungsbedingungen des Balkens
def show_home_page():
    st.title("Startseite")
    st.write("Mit dieser Applikation können Sie Balken optimieren und die Verbiegung berechnen.")
    input_length_and_width()
    input_support_conditions()
    previous_calculation_results()
    if st.button("Berechnung starten"):
        st.session_state.page = "results"
        st.rerun()

# Eingabefelder für Länge und Breite des Balkens    
def input_length_and_width():
    col1, col2 = st.columns(2)
    with col1:
        st.header("Balkenlänge")
        length = st.number_input("Länge des Balkens (cm)", min_value=1, step=1)
        

    with col2:
        st.header("Balkenbreite")
        width = st.number_input("Breite des Balkens (cm)", min_value=1, step=1)
    return length, width

# Eingabefelder für die Lagerungsbedingungen des Balkens
def input_support_conditions():
    support_options = ["Festlager", "Loslager"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Lagerung links")
        left = st.selectbox("Typ:", support_options, key="sup_left") 
        
    with col2:
        st.header("Lagerung rechts")
        right = st.selectbox("Typ:", support_options, key="sup_right")
        
    return left, right

def previous_calculation_results():
    st.header("Vorherige Berechnungen")
    st.selectbox("Wähle eine vorherige Berechnung aus:", ["Berechnung 1", "Berechnung 2", "Berechnung 3"])

def show_result_page():
    st.title("Ergebnisse")
    st.write("Hier werden die Ergebnisse der Balkenberechnung angezeigt.")
    st.pyplot(visualization.plot_dense_beam(visualization.x_plot, visualization.y_plot, visualization.farb_werte))
    if st.button("Zurück zur Eingabe"):
        st.session_state.page = "home"
        st.rerun()