from fastapi import FastAPI, Request, HTTPException
import os
import aiomysql
from dotenv import load_dotenv
from auth_hash import *
from contextlib import asynccontextmanager
import uvicorn

@asynccontextmanager
async def create_pool(app: FastAPI):
    load_dotenv()
    try:
        global racedb_pool
        
        conn = await aiomysql.connect(
            host=os.environ["mysql_server"],
            user=os.environ["mysql_login"],
            password=os.environ["mysql_pass"]
        )
        
        async with conn.cursor() as cursor:
            
            await cursor.execute("CREATE DATABASE IF NOT EXISTS RaceDB")
            
            await cursor.execute("USE RaceDB")
        
        racedb_pool = await aiomysql.create_pool(
                host=os.environ["mysql_server"],
                user=os.environ["mysql_login"],
                password=os.environ["mysql_pass"],
                db="RaceDB"
        )
        
        print("Connected to the database")

        app.state.db = racedb_pool
    
    except Exception as e:
       print("Error:", e)
       exit()
    
    yield
    
    if racedb_pool:
      racedb_pool.close()
      await racedb_pool.wait_closed()


app = FastAPI(lifespan=create_pool)


@app.post("/api/newCompetition")
async def create_contest(competition: Request):
   competition_info = await competition.json()
   
   if hash_code(competition_info["authorization"]) != 3237860622128:
       raise HTTPException(status_code=403, detail="Access denied")

   async with app.state.db.acquire() as connection:
      async with connection.cursor() as cursor:

          # Create 'competition' table if not exists in the database
          await cursor.execute('CREATE TABLE IF NOT EXISTS competition (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,name VARCHAR(100) NOT NULL,date DATE NOT NULL);')
          
           # Insert the competition information into the 'competition' table
          await cursor.execute('INSERT INTO competition (name, date) VALUES (%s, %s)', (
              competition_info["competition_name"], 
              competition_info["competition_date"]
          ))
          
          id = cursor.lastrowid

   return {"id": id}

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8000)
