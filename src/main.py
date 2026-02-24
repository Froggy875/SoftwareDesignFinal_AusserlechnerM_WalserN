import streamlit as st
from ui import components

def main():

    st.set_page_config(
    page_title="Balkenbiegung-Simulation",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded"
    )
    # States initialiseren
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "current_calc_id" not in st.session_state:
        st.session_state.current_calc_id = None
    if "mode" not in st.session_state:
        st.session_state.mode = None
    if "app_step" not in st.session_state:
        st.session_state.app_step = "input_form"

    # Startseite anzeigen
    if st.session_state.page == "home":
        components.show_home_page()
    #Ergebnisseite anzeigen
    elif st.session_state.page == "results":
        components.show_result_page()

if __name__ == "__main__":
    main()
