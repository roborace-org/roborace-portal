import streamlit as st
from auth_hash import *
import extra_streamlit_components as stx
import hashlib
import requests
import datetime
import json
import time


json_file_path = 'cookie.json'

file = open('cookie.json', 'a')
file.close()

st.experimental_set_query_params() 
def cookie_rewriter(new_cookie):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        if 'cookie_info' not in data or not data['cookie_info'] or data['cookie_info'] != new_cookie:
            data['cookie_info'] = new_cookie

            with open(json_file_path, 'w') as file:
                json.dump(data, file)
                file.close()
            return True
        else:
            return False
    except json.JSONDecodeError:
        data = {'cookie_info': new_cookie}
        with open(json_file_path, 'w') as file:
            json.dump(data, file)
            file.close()
        return True

def cookie_validator():
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            file.close()
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
    cookie_manager.get_all()
    time.sleep(1)
    def password_entered():
        if "password" in st.session_state and hash_code(st.session_state["password"]) == 3237860622128:
            st.session_state["password_correct"] = True 
        else:
            st.session_state["password_correct"] = False  
    global password_row
    password_row = st.empty()
    
    if cookie_manager.get(cookie="session-key") != None and cookie_validator() == cookie_manager.get(cookie="session-key"):
            return True
    else:
            password_row.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state and cookie_manager.get(cookie="session-key") == None:
        try:
            if st.session_state["password_correct"] == True:
                hashed_session = hashlib.sha256(str(hash_code(st.session_state["password"])).encode('utf-8')).hexdigest()
                new_cookie = keyGenerator(hashed_session)
                cookie_manager.set("session-key", new_cookie)
                password_row.empty()
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

if cookie_validator() == cookie_manager.get(cookie="session-key"):
    print(cookie_manager.get(cookie="session-key"))
    st.write("👋 Hello Admin!")
    chosen_id = stx.tab_bar(data=[
    stx.TabBarItemData(id=1, title="Create competiton", description=""),
    stx.TabBarItemData(id=2, title="Just a test buttom", description="")
    ], default=2)
    if chosen_id == '1':
            col1raw1, col2raw1, col3raw1, col4raw1 = st.columns([2,2,2,2])
            with col1raw1:
                contest_name = st.text_input("Competition name")
            with col2raw1:
                date = st.date_input("Competition date")
            with col3raw1:
                length = st.number_input("Track length", step=1, value=0)
            with col4raw1:
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
        st.info(f"{chosen_id=}")
