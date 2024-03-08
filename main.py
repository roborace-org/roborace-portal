from fastapi import FastAPI, Request, HTTPException
import os
import json
import uvicorn
from xata.client import XataClient
import time
print("Initializng competition table")

all_competitions_table_schema = {
  "columns": [
    {
      "name": "competition_id",
      "type": "string"
    },
    {
      "name": "competition_name",
      "type": "string",
    },
    {
      "name": "city",
      "type": "string"
    },
    {
        "name": "track_length",
        "type": "string"
    },
    {
      "name": "season",
      "type": "string"
    },
    {
      "name": "type",
      "type": "string"
    },
    {
        "name": "competition_date",
        "type": "string"
    },
    {
        "name": "refer",
        "type": "string"
    }
  ]
}

xata = XataClient(api_key="", db_url="")
app = FastAPI()

xata.table().create("all_competitions_roborace")
xata.table().set_schema("all_competitions_roborace", all_competitions_table_schema)
time.sleep(1)
xata.table().create("all_competitions_roborace_pro")
xata.table().set_schema("all_competitions_roborace_pro", all_competitions_table_schema)
time.sleep(1)
xata.table().create("all_competitions_roborace_ok")
xata.table().set_schema("all_competitions_roborace_ok", all_competitions_table_schema)


print("Initialized. Starting API")
key_to_exclude = "xata"
lambda_resp = lambda resp, key_to_exclude: [
{key: value for key, value in item.items() if key != key_to_exclude}
for item in resp['records']
]

def get_data_type(data, str):
    if isinstance(data, str):
        return "string"
    elif isinstance(data, int):
        return "int"
    elif isinstance(data, bool):
        return "boolean"
    else:
        return "string"

def convert_json_to_schema(json_data):
    schema = {"columns": []}
    for key, value in json_data.items():
        schema["columns"].append({
            "name": key,
            "type": get_data_type(value)
        })
    return schema

@app.post("/api/competitions")
async def create_contest(competition: Request):
    competition_info = await competition.json()
    if competition_info["authorization"] != os.environ.get("PASSWORD_UI"):
        raise HTTPException(status_code=403, detail="Invalid cookie. Relogin and create competition again")

    data = xata.sql().query("SELECT Max(competition_id) FROM all_competitions_roborace_pro")
    data_p=json.loads(json.dumps(data))
    if data_p["records"][0]["max"] == None:
        id_count = 1
    else:
        id_count = int(data_p['records'][0]['max']) + 1
    city = competition_info['city'].replace(" ", "_").lower()
    data = xata.table().create(f"competition_{str(id_count)}_{competition_info['type']}_{competition_info['season']}_{city}_roborace")
    print(data)
    data = xata.table().create(f"competition_{str(id_count)}_{competition_info['type']}_{competition_info['season']}_{city}_roborace-pro")
    print(data)
    data = xata.table().create(f"competition_{str(id_count)}_{competition_info['type']}_{competition_info['season']}_{city}_roborace-ok")
    print(data)

    refer = ""
    try:
            refer =str(competition_info['refer'])
    except:
            refer = str(id_count)
    new_competition = {
        "competition_id": str(id_count),
        "competition_name": competition_info["competition_name"],
        "competition_date": competition_info["competition_date"],
        "track_length": str(competition_info["track_length"]),
        "season": competition_info["season"],
        "type": competition_info["type"],
        "city": competition_info["city"],
        "refer": refer
    }
    print(new_competition)
    data = xata.records().insert("all_competitions_roborace", dict(new_competition))
    print(data)
    time.sleep(1)
    data = xata.records().insert("all_competitions_roborace_pro", dict(new_competition))
    print(data)
    time.sleep(1)
    data = xata.records().insert("all_competitions_roborace_ok", dict(new_competition))
    print(data)
    return {"id": id_count}

@app.get("/api/competitions/{category}")
async def getCompetitions(category: str):
    competitions_data = []

    if category == "r":
        cat = "roborace"
    elif category == "rp":
            cat = "roborace_pro"
    elif category == "ro":
            cat = "roborace_ok"
    resp = xata.sql().query(f"SELECT * FROM all_competitions_{cat}")
    print(resp)
    competitions_data = lambda_resp(resp, key_to_exclude)
    return competitions_data

@app.get("/api/competitions/{location}/{type_comp}/{season}/{city}/{category}/{id}")
async def get_robots(id: int, comp_info: Request):
    if comp_info['category'] == "r":
        cat = "roborace"
    elif comp_info['category'] == "rp":
            cat = "roborace pro"
    elif comp_info['category'] == "ro":
            cat = "roborace ok"

    resp = xata.sql().query(f"SELECT * FROM 'competition - {comp_info['id']} - {comp_info['type_comp']} - {comp_info['season']} - {comp_info['city']} - {cat}'")


# @app.post("/api/competitions/{location}/{type_comp}/{season}/{city}/{id}")
# async def robot_list(id: int, robots_list: Request):
#     robot_callback = await robots_list.json()
#
#     if robot_callback["authorization"] != get_cookie():
#         raise HTTPException(status_code=403, detail="Access denied")
#
#     xata.

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
