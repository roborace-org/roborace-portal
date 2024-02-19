from fastapi import FastAPI, Request, HTTPException
import os
import json
import uvicorn

app = FastAPI()

def get_cookie():
    cookie_file = "roborace-ui/cookie.json"
    with open(cookie_file, "r") as file:
        data = json.load(file)
        try:
            cookie_info = data['cookie_info']
            return cookie_info
        except:
            return False
        file.close()

@app.post("/api/competitions", response_model=Competition)
async def create_contest(competition: Competition):
    competition_info = competition.dict()

    if competition_info["authorization"] != get_cookie():
        raise HTTPException(status_code=403, detail="Access denied")

    competitions_data = []
    file = open('competitions.json', 'a')
    file.close()

    if os.path.isfile("competitions.json"):
        with open("competitions.json", "r") as file:
            try:
                competitions_data = json.load(file)
            except:
                competitions_data = []

    id_count = len(competitions_data) + 1

    new_competition = {
        "id": id_count,
        "name": competition_info["competition_name"],
        "date": competition_info["competition_date"],
        "track_length": int(competition_info["track_length"]),
        "season": competition_info["season"],
        "type": competition_info["type"],
        "city": competition_info["city"]
    }

    competitions_data.append(new_competition)

    with open("competitions.json", "w") as file:
        json.dump(competitions_data, file)

    location = competition_info["location"]
    season = competition_info["season"]
    type_comp = competition_info["type"]
    city = competition_info["city"]

    if not os.path.isdir("competitions-data"):
        os.mkdir("competitions-data")
    if not os.path.isdir(f"competitions-data/{location}"):
        os.mkdir(f"competitions-data/{location}")
    if not os.path.isdir(f"competitions-data/{location}/{type_comp}"):
        os.mkdir(f"competitions-data/{location}/{type_comp}")
    if not os.path.isdir(f"competitions-data/{location}/{type_comp}/{season}"):
        os.mkdir(f"competitions-data/{location}/{type_comp}/{season}")
    if not os.path.isdir(f"competitions-data/{location}/{type_comp}/{season}/{city}"):
        os.mkdir(f"competitions-data/{location}/{type_comp}/{season}/{city}")

    return {"id": id_count}

@app.get("/api/competitions")
async def getCompetitions():
    competitions_data = []

    if os.path.isfile("competitions.json"):
        with open("competitions.json", "r") as file:
            competitions_data = json.load(file)
    
    return competitions_data

@app.get("/api/competitions/{location}/{type_comp}/{season}/{city}/{id}")
async def get_robots(id: int):

    if os.path.isfile(f"competitions-data/{location}/{type_comp}/{season}/{city}/{id}.json"):
        with open(f'competitions-data/{location}/{type_comp}/{season}/{city}/{id}.json', 'r') as file:
            info = json.load(file)
            if info == "[]":
                info = {"error": "No info"}
            return info
    else:
        return {"error":"No info"}

@app.post("/api/competitions/{location}/{type_comp}/{season}/{city}/{id}")
async def robot_list(id: int, robots_list: Request):
    robot_callback = await robots_list.json()

    if robot_callback["authorization"] != get_cookie():
        raise HTTPException(status_code=403, detail="Access denied") 

    with open(f"competitions-data/{location}/{type_comp}/{season}/{city}/{id}.json", "w") as file:
        json.dump(robot_callback['robots'], file)
        file.close()
        return {"status": "OK"}

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
