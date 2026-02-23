import streamlit as st
from ui import components


st.set_page_config(
    page_title="Balkenbiegung-Simulation",
    page_icon="⬛",
    layout="wide",  # "centered" oder "wide"
    initial_sidebar_state="expanded"
)

def main():
    if "page" not in st.session_state:
        st.session_state.page = "home"

    # Weiche: Welche Seite soll angezeigt werden?
    if st.session_state.page == "home":
        components.show_home_page()
    elif st.session_state.page == "results":
        components.show_result_page()
