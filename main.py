from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import os
import uvicorn
from xata.client import XataClient
import time

# Define Pydantic models
class Competition(BaseModel):
    authorization: str
    competition_name: str
    competition_date: str
    track_length: str
    season: str
    type: str
    city: str
    refer: str = None

class RobotList(BaseModel):
    authorization: str
    robots: list

# Initialize the FastAPI app
app = FastAPI()

# Initialize Xata client
xata = XataClient(api_key=os.environ.get("XATA_API_KEY"), db_url=os.environ.get("XATA_DB_URL"))

# Define the schema for competition tables
competition_schema = {
    "columns": [
        {"name": "competition_id", "type": "string"},
        {"name": "competition_name", "type": "string"},
        {"name": "city", "type": "string"},
        {"name": "track_length", "type": "string"},
        {"name": "season", "type": "string"},
        {"name": "type", "type": "string"},
        {"name": "competition_date", "type": "string"},
        {"name": "refer", "type": "string"},
    ]
}

# Initialize tables and schemas
def initialize_tables():
    print("Initializing competition tables")
    tables = ["all_competitions_roborace", "all_competitions_roborace_pro", "all_competitions_roborace_ok"]
    for table in tables:
        xata.table().create(table)
        xata.table().set_schema(table, competition_schema)
        time.sleep(1)
    print("Initialized tables. Starting API")

initialize_tables()

# Helper function to generate table suffix
def get_category_suffix(category):
    category_map = {"r": "roborace", "rp": "roborace_pro", "ro": "roborace_ok"}
    return category_map.get(category, None)

# Create a new competition
@app.post("/api/competitions")
async def create_competition(competition: Competition):
    if competition.authorization != os.environ.get("PASSWORD_UI"):
        raise HTTPException(status_code=403, detail="Invalid authorization")

    max_comp_id_data = xata.sql().query("SELECT Max(competition_id) FROM all_competitions_roborace_pro")
    max_comp_id = next((record.get("max") for record in max_comp_id_data.get("records", [])), None)
    comp_id = 1 if max_comp_id is None else int(max_comp_id) + 1

    city = competition.city.replace(" ", "_").lower()
    refer = competition.refer if competition.refer else str(comp_id)

    table_suffixes = [
        f"competition_{comp_id}_{competition.type}_{competition.season}_{city}_roborace",
        f"competition_{comp_id}_{competition.type}_{competition.season}_{city}_roborace-pro",
        f"competition_{comp_id}_{competition.type}_{competition.season}_{city}_roborace-ok"
    ]

    for suffix in table_suffixes:
        xata.table().create(suffix)
        print(f"Created table: {suffix}")

    new_competition_record = {
        "competition_id": str(comp_id),
        "competition_name": competition.competition_name,
        "competition_date": competition.competition_date,
        "track_length": competition.track_length,
        "season": competition.season,
        "type": competition.type,
        "city": competition.city,
        "refer": refer
    }

    for table in ["all_competitions_roborace", "all_competitions_roborace_pro", "all_competitions_roborace_ok"]:
        xata.records().insert(table, new_competition_record)
        time.sleep(1)

    return {"id": comp_id}

# Retrieve competitions
@app.get("/api/competitions/{category}")
async def get_competitions(category: str):
    suffix = get_category_suffix(category)
    if not suffix:
        raise HTTPException(status_code=404, detail="Category not found")

    table = f"all_competitions_{suffix}"
    data = xata.sql().query(f"SELECT * FROM {table}")
    return data.get('records', [])

# Retrieve robots associated with a competition
@app.get("/api/competitions/{location}/{type_comp}/{season}/{city}/{category}/{id}")
async def get_robots(id: int, location: str, type_comp: str, season: str, city: str, category: str):
    suffix = get_category_suffix(category)
    if not suffix:
        raise HTTPException(status_code=404, detail="Category not found")

    table_name = f"competition_{id}_{type_comp}_{season}_{city}_{suffix}"
    data = xata.sql().query(f"SELECT * FROM {table_name}")
    return data.get('records', [])

# Update robots associated with a competition
@app.post("/api/competitions/{location}/{type_comp}/{season}/{city}/{category}/{id}")
async def update_robot_list(id: int, location: str, type_comp: str, season: str, city: str, 
                            category: str, robots_list: RobotList):
    if robots_list.authorization != os.environ.get("PASSWORD_UI"):
        raise HTTPException(status_code=403, detail="Access denied")

    suffix = get_category_suffix(category)
    if not suffix:
        raise HTTPException(status_code=404, detail="Category not found")

    table_name = f"competition_{id}_{type_comp}_{season}_{city}_{suffix}"
    record_id = f"{id}_{type_comp}_{season}_{city}_{category}"

    response = xata.records().update(table_name, record_id, {"robots": robots_list.robots})

    if response.get('updated', 0) > 0:
        return {"status": "OK"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update robot list")

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
