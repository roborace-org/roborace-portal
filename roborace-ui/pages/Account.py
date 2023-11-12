import streamlit as st
from auth_hash import *
import extra_streamlit_components as stx
import hashlib
import requests
import datetime
import json

json_file_path = 'cookie.json'

file = open('cookie.json', 'a')
file.close()

def cookie_rewriter(new_cookie):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        if 'cookie_info' not in data or not data['cookie_info']:
            data['cookie_info'] = new_cookie

            with open(json_file_path, 'w') as file:
                json.dump(data, file, indent=2)

            return True
        else:
            return False
    except json.JSONDecodeError:
        data = {'cookie_info': new_cookie}
        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=2)
        return True

def cookie_validator():
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        if not data or 'cookie_info' not in data:
            return False

        return data['cookie_info']
    except json.JSONDecodeError:
        return False
    except FileNotFoundError:
        with open(json_file_path, 'w') as new_file:
            new_file.write(json.dumps({}))
        return False

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
    
    if cookie_manager.get(cookie="session-key") != None and cookie_validator() == cookie_manager.get(cookie="session-key"):
            return True
    else:
            password.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        try:
            if st.session_state["password_correct"] == True:
                hashed_session = hashlib.sha256(str(hash_code(st.session_state["password"])).encode('utf-8')).hexdigest()
                new_cookie = keyGenerator(hashed_session)
                cookie_manager.set("session-key", new_cookie)
                password.empty()
                del st.session_state["password"]
                cookie_rewriter(cookie_manager.get(cookie="session-key")) 
                return True
            else:
                st.error("😕 Incorrect password")
        except Exception as e:
            st.error("😕 Error while processing you request")
            print(e)
if not password():
    st.stop()

st.write("👋 Hello Admin!")
