import streamlit as st
from auth_hash import *
import extra_streamlit_components as stx
import hashlib
import requests
import datetime
from .. import cookie_checker

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
def keyGenerator(keyInfo):
        curDate = datetime.date.today()
        print(curDate)
        new_session = keyInfo + str(curDate)

        keyAlgo = hashlib.sha3_512(str(hash_code(new_session)).encode('utf-8')).hexdigest()
        return keyAlgo

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
def password():
    def password_entered():
        if hash_code(st.session_state["password"]) == 3237860622128:
            st.session_state["password_correct"] = True 
        else:
            st.session_state["password_correct"] = False    
    global password
    password = st.empty()

    if cookie_manager.get(cookie="session-key") != None and cookie_checker.cookie_validator() == cookie_manager.get(cookie="session-key"):
        return True
    else:
        password.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        if st.session_state["password_correct"] == True:
         try:
            hashed_session = hashlib.sha256(str(hash_code(st.session_state["password"])).encode('utf-8')).hexdigest()
            new_cookie = keyGenerator(hashed_session)
            cookie_manager.set("session-key", new_cookie)
            password.empty()
            del st.session_state["password"]
            cookie_checker.cookie_rewriter(new_cookie) 
            return True
         except Exception as e:
            st.error(f"😕 Error while processing your request. Error code {e}")
        else:
            st.error("😕 Incorrect password")

if not password():
    st.stop()

st.write("👋 Hello Admin!")
