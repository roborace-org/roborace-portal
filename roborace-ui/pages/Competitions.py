import streamlit as st
import requests
from PIL import Image
import json
import extra_streamlit_components as stx
import pandas as pd
import time
import numpy as np

json_file_path = 'cookie.json'
false = "No"
true = "Yes"
null = "Unknown"
strike = '-'
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


@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()
cookie_manager.get_all()
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
params = st.experimental_get_query_params()

if 'race_numbers' not in st.session_state:
    st.session_state.race_numbers = 0
    st.session_state.df = pd.DataFrame()

def update_race_numbers():
    race_numbers = st.session_state.race_numbers_input
    
    if race_numbers != st.session_state.race_numbers:
        df = st.session_state.df.copy()

        for i in range(1, st.session_state.race_numbers + 1):
            df.drop([f'Race {i} Position', f'Race {i} Place', f'Race {i} Laps', f'Race {i} Time'], axis=1, inplace=True, errors='ignore')

        for i in range(1, race_numbers + 1):
            df[f'Race {i} Position'] = 0
            df[f'Race {i} Place'] = 0
            df[f'Race {i} Laps'] = 0
            df[f'Race {i} Time'] = ""
        df['Final Position'] = 0
        df['Final Place'] = 0
        df['Final Laps'] = 0
        df['Final Time'] = ""
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
        
        race_numbers = st.number_input(
            'Number of races', 
            min_value=0, 
            step=1, 
            key='race_numbers_input', 
            on_change=update_race_numbers,
            value=st.session_state.race_numbers
        )
        
        
        
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
            qualification_table = st.empty()
            race_table = st.empty()
            final_table = st.empty()
            results_table = st.empty()
            
            table = requests.get("http://127.0.0.1:8000/api/competitions").json()
            track_length = table[int(params['id'][0]) - 1]['track_length']
            if st.button("Presentation mode"):
                            table_style = """
                            <style>
                            table, th, td {
                                font-size:140%;
                                width: 100%;    
                                height: 100%
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
                        
                        columns = df.columns.tolist() 
                        place_index = columns.index('Place') + 1
                        race_columns = [col for col in columns if col.startswith('Race')]
                        columns = [col for col in columns if not col.startswith('Race')] 
                        new_order = columns[:place_index] + race_columns + columns[place_index:]
                        df = df[new_order]
                        race_columns_present = any("race" in col.lower() for col in df.columns)
 
                        if race_columns_present:
                            race_laps_columns = [col for col in df.columns if col.startswith('Race') and col.endswith('Laps')] 
                            df['Max Laps'] = df[race_laps_columns].max(axis=1)
                            max_laps = df['Max Laps'].max()
                            df['Race Score'] = df['Max Laps'].apply(lambda laps: 10 * laps / max_laps).round(2)
                            
                            if 'Race Score' in df.columns:
                                df = df.sort_values(by='Race Score', ascending=False)
                            try:
                                columns = df.columns.tolist()  
                                points_mapping = {1: 180,2: 100,3: 60,4: 40,5: 20,  6: 0}
                                def calculate_points(position):
                                    return points_mapping.get(position, 0)
                                df['Final Score'] = df['Final Position'].apply(calculate_points)
                                score_columns = [col for col in df.columns if 'Score' in col]
                                df['Total Score'] = df[score_columns].sum(axis=1)
                                df = df.sort_values(by='Total Score', ascending=False)
                            except Exception as e:
                                print(e)

                        qualification_columns = ['Name', 'Is Allowed?', 'Qualification time 1', 'Qualification time 2', 'Qualification time 3']
                        
                        final_columns = ['Name', 'Final Position', 'Final Place', 'Final Laps', 'Final Time']
                        

                        df_qualification = df[qualification_columns]
                        df_final = df[final_columns]
                        
                        qualification_table.table(df_qualification)

                        try:
                            race_columns = ['Name'] + [col for col in df.columns if col.startswith('Race')]
                            df_race = df[race_columns]
                            race_table.table(df_race)
                        except:
                            pass
                        final_table.table(df_final)
                        try:
                            score_columns = ['Name'] + [col for col in df.columns if 'Score' in col]
                            df_score_sum = df[score_columns]
                            results_table.table(df_score_sum)
                        except:
                            pass
                        

                        if 'Qualification time 1' in df.columns:
                            time_1_values = df['Qualification time 1'].values
                        if 'Qualification time 2' in df.columns:
                            time_2_values = df['Qualification time 2'].values
                        if 'Qualification time 3' in df.columns:
                            time_3_values = df['Qualification time 3'].values
                        time.sleep(4)
                    except Exception as e:
                        print(e)
                        newtable = json.loads(str(new_request.json()))                            
                        df = pd.DataFrame(newtable)
                        competition_table.table(df)
                        time.sleep(4)
                else:
                    st.rerun()