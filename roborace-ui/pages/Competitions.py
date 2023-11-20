import streamlit as st
import requests
import pandas as pd
from PIL import Image
import json
import extra_streamlit_components as stx

json_file_path = 'cookie.json'
false = "No"
true = "Yes"
null = "Unknown"

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

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()
cookie_manager.get_all()
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
params = st.experimental_get_query_params()
if params=={}:
    table = requests.get("http://127.0.0.1:8000/api/competitions")
    table = table.json()
    reformated_table = []

    for i in range(0, len(table)):
        reformated_table.append({
            "ID": table[i]["id"],
            "Name": table[i]["name"],
            "Date": table[i]['date'],
            "Track length": table[i]['track_length'],
            "Link": f"[Browse this competition](?id={table[i]['id']})"
        })
    df = pd.DataFrame(reformated_table)
    df.set_index('ID', inplace=True)

    md_table = df.to_markdown()
    st.markdown(md_table)
else:
    request = requests.get(f"http://127.0.0.1:8000/api/competitions/{params['id'][0]}")
    if cookie_manager.get(cookie="session-key") != None and cookie_validator() == cookie_manager.get(cookie="session-key"):
        st.write("Manage competition")
        if request.json() == {"error": "No info"}:
            df = pd.DataFrame([{"Name": "", 'Is Allowed?': False}])
        else: 
            false = False
            true = True
            null = None
            df = pd.DataFrame(eval(request.json()))
        df_editable = st.data_editor(df,num_rows="dynamic", hide_index=False)
        if st.button("Send new list"):
            table_send = df_editable.to_json(orient="records")
            print(table_send)
            try:
                data = {"authorization": str(cookie_manager.get(cookie="session-key")), "robots": table_send}
                request = requests.post(f"http://127.0.0.1:8000/api/competitions/{params['id'][0]}", json=data)
            except Exception as e:
             st.error(f"Error. Info: {e}")
    else:
        if request.json() == {"error": "No info"}:
            image = Image.open('notfound.jpg')
            st.image(image, "No-info robot")
        else:
            newtable = eval(request.json())
            df = pd.DataFrame(newtable)
            st.table(df)
