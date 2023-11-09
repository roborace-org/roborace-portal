import streamlit as st
from auth_hash import *
import extra_streamlit_components as stx
import hashlib
import request

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

def password():
    def password_entered():
        if hash_code(st.session_state["password"]) == 3237860622128:
            st.session_state["password_correct"] = True 
        else:
            st.session_state["password_correct"] = False    
    global password
    password = st.empty()

    if cookie_manager.get(cookie="session-key") != None: 
        check_for_valid = requests.get("http://localhost:8000/api/isValid", params={'session': cookie_manager.get(cookie="session-key")})
        status = check_for_valid.json()
        status = status["status"]
        if status != "valid":
            st.error("Cookie not valid")
            password.text_input("Password", type="password", on_change=password_entered, key="password")
    else:
        password.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        if st.session_state["password_correct"] == True:
        try:
            hashed_session = hashlib.sha256(str(hash_code(st.session_state["password"])).encode('utf-8')).hexdigest())
            del st.session_state["password"]
            new_cookie = requests.get("http://localhost:8000/api/newSession", params={"session": hashed_session})
            cookie_manager.set("session-key": new_cookie.json())
            password.empty()
            return True
        except:
            st.error("😕 Error while processing your request")
        else:
            st.error("😕 Incorrect password")

if not password():
    st.stop()

st.write("👋 Hello Admin!")
