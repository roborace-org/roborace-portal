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

@app.post("/api/newCompetition")
async def create_contest(competition: Request):
   competition_info = await competition.json()
   
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

   new_competition ={
      "id": id_count,
      "name": competition_info["competition_name"],
      "date": competition_info["competition_date"],
      "track_length": int(competition_info["track_length"])
   }

   competitions_data.append(new_competition)

   with open("competitions.json", "w") as file:
       json.dump(competitions_data, file)

   return {"id": id_count}

@app.get("/api/competition")
async def getCompetitions():
    competitions_data = []

    if os.path.isfile("competitions.json"):
        with open("competitions.json", "r") as file:
            competitions_data = json.load(file)
        
    return competitions_data

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8000)
