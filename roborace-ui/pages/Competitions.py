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
    st.write(params)
