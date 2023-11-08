import streamlit as st
from auth_hash import *
import extra_streamlit_components as stx
import hashlib

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

def password():
    def password_entered():
        if hash_code(st.session_state["password"]) == 3237860622128:
            st.session_state["password_correct"] = True 
        else:
            st.session_state["password_correct"] = False    
    global password
    password = st.empty()
    if cookie_manager.get(cookie="session-key") != None:
        return True
    else:
        password.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        if st.session_state["password_correct"] == True:
            password.empty()
            cookie_manager.set("session-key", hashlib.sha256(str(hash_code(st.session_state["password"])).encode('utf-8')).hexdigest())
            del st.session_state["password"]
            return True
        else:
            st.error("😕 Incorrect password")

if not password():
    st.stop()

st.write("👋 Hello Admin!")
