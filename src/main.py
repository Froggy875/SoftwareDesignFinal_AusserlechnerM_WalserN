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
    if "current_calc_id" not in st.session_state:
        st.session_state.current_calc_id = None
    if "mode" not in st.session_state:
        st.session_state.mode = None
    if "app_step" not in st.session_state:
        st.session_state.app_step = "input_form"

    # UI anzeigen
    if st.session_state.app_step:
        components.streamlit_ui()

if __name__ == "__main__":
    main()
