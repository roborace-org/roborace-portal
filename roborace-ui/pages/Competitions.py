import streamlit as st
import requests
import pandas as pd

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

table = requests.get("http://127.0.0.1:8000/api/competition")
table = table.json()
reformated_table = []
try:
    for i in range(0, len(table)):
        reformated_table.append({"id": table[i]["id"], "Name": table[i]["name"], "Date": table[i]['date'], "Track length": table[i]['track_length']})
    df = pd.DataFrame(reformated_table)
    df.set_index('id', inplace=True)
    st.table(df)
except:
    st.table()
