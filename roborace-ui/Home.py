import streamlit as st
from auth_hash import *
import requests
import extra_streamlit_components as stx

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.write("Welcome to RoboRace Portal 🤖")
value = cookie_manager.get(cookie="session-key")
st.write(value)
