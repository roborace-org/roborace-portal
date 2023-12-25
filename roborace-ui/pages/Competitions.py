import streamlit as st
import requests
import pandas as pd
from PIL import Image
import json
import extra_streamlit_components as stx
import time
import numpy as np

json_file_path = 'cookie.json'
false = "No"
true = "Yes"
null = "Unknown"
strike = '-'

def convert_seconds_to_custom_format(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60 / 10
    formated_time = minutes + remaining_seconds
    return formated_time

def cookie_validator():
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        if not data or 'cookie_info' not in data:
            return False

        return data['cookie_info']
    except (json.JSONDecodeError, FileNotFoundError):
        with open(json_file_path, 'w') as new_file:
            new_file.write(json.dumps({}))
        return False

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

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()
cookie_manager.get_all()
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
params = st.experimental_get_query_params()

# Инициализация session_state, если это еще не сделано
if 'race_numbers' not in st.session_state:
    st.session_state.race_numbers = 0
    st.session_state.df = pd.DataFrame()

# Функция для обновления количества гонок и структуры DataFrame
def update_race_numbers():
    race_numbers = st.session_state.race_numbers_input
    # Если количество гонок изменилось, обновляем DataFrame
    if race_numbers != st.session_state.race_numbers:
        df = st.session_state.df.copy()
        # Удаляем старые столбцы заездов
        for i in range(1, st.session_state.race_numbers + 1):
            df.drop([f'Race {i} Position', f'Race {i} Place', f'Race {i} Laps', f'Race {i} Time'], axis=1, inplace=True, errors='ignore')
        # Добавляем новые столбцы заездов
        for i in range(1, race_numbers + 1):
            df[f'Race {i} Position'] = np.nan
            df[f'Race {i} Place'] = np.nan
            df[f'Race {i} Laps'] = np.nan
            df[f'Race {i} Time'] = np.nan
        # Обновляем session_state
        st.session_state.race_numbers = race_numbers
        st.session_state.df = df
        st.rerun()
        

if params == {}:
    table = requests.get("http://127.0.0.1:8000/api/competitions").json()
    reformated_table = [
        {
            "ID": entry["id"],
            "Name": entry["name"],
            "Date": entry['date'],
            "Track length": entry['track_length'],
            "Link": f"[Browse this competition](?id={entry['id']})"
        } for entry in table
    ]
    df = pd.DataFrame(reformated_table).set_index('ID')
    md_table = df.to_markdown()
    st.markdown(md_table)
else:
    request = requests.get(f"http://127.0.0.1:8000/api/competitions/{params['id'][0]}")
    if cookie_manager.get(cookie="session-key") is not None and cookie_validator() == cookie_manager.get(cookie="session-key"):
        st.write("Manage competition")
        if request.json() == {"error": "No info"}:
            st.session_state.df = pd.DataFrame([{"Name": "", 'Is Allowed?': False}])
        else:
            if st.session_state.df.empty:
                st.session_state.df = pd.DataFrame(json.loads(str(request.json())))
        
        # Получаем количество гонок от пользователя и обновляем session_state
        race_numbers = st.number_input(
            'Number of races', 
            min_value=0, 
            step=1, 
            key='race_numbers_input', 
            on_change=update_race_numbers,
            value=st.session_state.race_numbers  # Устанавливаем текущее значение
        )
        
        
        
        # Создаем редактируемую таблицу с использованием DataFrame из session_state
        df_editable = st.empty()
        competition_editable_table = df_editable.data_editor(st.session_state.df, num_rows="dynamic", hide_index=False)

        if st.button("Send new list"):
            table_send = competition_editable_table.to_json(orient="records")
            try:
                data = {"authorization": str(cookie_manager.get(cookie="session-key")), "robots": table_send}
                request = requests.post(f"http://127.0.0.1:8000/api/competitions/{params['id'][0]}", json=data)
                st.success("Success")
                time.sleep(0.4)
                st.rerun()
            except Exception as e:
                st.error(f"Error. Info: {e}")
        
        if st.button("Rank mode"):
            try:
                current_table = competition_editable_table.to_dict(orient="records")
                for record in current_table:
                    record["Qualification time 1"] = 0.00
                    record["Qualification time 2"] = 0.00
                    record["Qualification time 3"] = 0.00
                df = pd.DataFrame.from_records(current_table)
                time_table = df_editable.data_editor(df, num_rows="dynamic", hide_index=False)
                table_send = time_table.to_json(orient="records")
                data = {"authorization": str(cookie_manager.get(cookie="session-key")), "robots": table_send}
                request = requests.post(f"http://127.0.0.1:8000/api/competitions/{params['id'][0]}", json=data)
                st.rerun()
            except:
                pass

    else:
        if request.json() == {"error": "No info"}:
            image = Image.open('notfound.jpg')
            st.image(image, "No-info robot")
            time.sleep(4)
            st.rerun()
        else:
            competition_table = st.empty()
            table = requests.get("http://127.0.0.1:8000/api/competitions").json()
            track_length = table[int(params['id'][0]) - 1]['track_length']
            if st.button("Presentation mode"):
                            table_style = """
                            <style>
                            table, th, td {
                                font-size:140%;
                            }
                            </style>
                            """
                            st.markdown(table_style, unsafe_allow_html=True)
            while True:
                new_request = requests.get(f"http://127.0.0.1:8000/api/competitions/{params['id'][0]}")
                
                if new_request.json() != {"error": "No info"}:
                    try:
                        newtable = list(eval(new_request.json()))
                        df = pd.DataFrame(newtable)

                        best_times = []

                        for col_name in ['Qualification time 1', 'Qualification time 2', 'Qualification time 3']:
                            if col_name in df.columns:
                                    non_negative_times = df[col_name].clip(lower=0)
                                    best_times.append(non_negative_times)
                        best_times_array = np.array(best_times)
                        best_times_array[best_times_array == 0] = np.nan

                        df['Best Time'] = np.nanmin(best_times_array, axis=0)  
                        df.loc[df['Best Time'] > track_length * 2, 'Best Time'] = np.nan

                        if np.isnan(df['Best Time']).all():
                            df['Best Time'] = np.nan
                            df['Score'] = 0
                            df['Place'] = np.nan
                        else:
                            best_time = np.nanmin(df['Best Time'])
                            limit_time = track_length * 2

                        df['Score'] = np.where(df['Best Time'] == 0, 0, 10 - 10 * (df['Best Time'] - best_time) / (limit_time - best_time))
                        df['Score'] = np.where(df['Score'] < 0, 0, df['Score'].round())
                        df = df.sort_values(by='Best Time')
                        df['Place'] = np.arange(1, len(df) + 1)

                        for col_name in ['Qualification time 1', 'Qualification time 2', 'Qualification time 3']:
                            if col_name in df.columns:
                                df[col_name] = df[col_name].apply(lambda x: f"({x})" if x > track_length * 2 else "" if x == 0 else '-' if x < 0 else x)

                        competition_table.table(df)

                        if 'Qualification time 1' in df.columns:
                            time_1_values = df['Qualification time 1'].values
                        if 'Qualification time 2' in df.columns:
                            time_2_values = df['Qualification time 2'].values
                        if 'Qualification time 3' in df.columns:
                            time_3_values = df['Qualification time 3'].values
                        time.sleep(4)
                    except Exception as e:
                        print(e)
                        ewtable = json.loads(str(new_request.json()))                            
                        df = pd.DataFrame(newtable)
                        competition_table.table(df)
                        time.sleep(4)
                else:
                    st.rerun()
