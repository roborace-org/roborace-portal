import streamlit as st
from auth_hash import *
import extra_streamlit_components as stx
import hashlib
import requests
import datetime
import json
import os
import time


st.experimental_set_query_params()

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

def check_password():
    def password_entered():
        if st.session_state["password"] == os.environ.get("PASSWORD_UI"):
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect or logged out")
    return False


if not check_password():
    st.stop()


st.write("👋 Hello Admin!")
chosen_id = stx.tab_bar(data=[
stx.TabBarItemData(id=1, title="Create competiton", description=""),
stx.TabBarItemData(id=2, title="Log out", description="")
    ], default=2)
if chosen_id == '1':
            col1raw1, col2raw1, col3raw1, col4raw1, col5raw1, col6raw1, col6raw1, col7raw1, col8raw1, col9raw1 = st.columns([2,2,2,2,2,2,2,2,2])
            with col1raw1:
                contest_name = st.text_input("Competition name")
            with col2raw1:
                date = st.date_input("Competition date")
            with col3raw1:
                length = st.number_input("Track length", step=1, value=0)
            with col4raw1:
                season = st.text_input("Season (YYYY-YYYY)")
            # with col5raw1:

            with col9raw1:
                if st.button("Create competition"):
                    data = {
                            "competition_name": contest_name,
                            "competition_date": str(date),
                            "track_length": str(length),
                             "authorization": f"{cookie_manager.get(cookie='session-key')}"
                            }
                    try:
                        response = requests.post("http://127.0.0.1:8000/api/competitions", json=data)
                        getId = response.json()['id']
                        st.success(f'Competition created. ID: {getId}')
                    except Exception as e:
                        st.error(f"Error while processing your request. Error {e}")
else:
        st.write("Deletes all sessions and disables write mode for API (until the first login)")
        if st.button("Log out"):
            st.session_state["password_correct"] = False
            st.rerun()
