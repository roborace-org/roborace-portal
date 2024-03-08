import streamlit as st
from auth_hash import *
import requests
import extra_streamlit_components as stx

st.experimental_set_query_params()
@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

hide_streamlit_style = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@900&display=swap');
html, body, head, div, p, table, [class*="css"] {
    font-family: 'Roboto Condensed', black; 
    font-size: 18px;
    font-weight: 500;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.write("Welcome to RoboRace Portal 🤖")
