from fastapi import FastAPI, Request, HTTPException
import os
import aiomysql
from dotenv import load_dotenv
from auth_hash import *
from contextlib import asynccontextmanager
import uvicorn
import hashlib
import datetime

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

async def keyGenerator():
        keyInfo = os.environ["gen_token"]
        curDate = datetime.date.now() 
        new_session = keyInfo + curDate

        keyAlgo = hashlib.sha3_512(hash_code(new_session)).hexdigest()
        return keyAlgo

@app.post("/api/newCompetition")
async def create_contest(competition: Request):
   competition_info = await competition.json()
   
   if competition_info["authorization"] != keyGenerator():
       raise HTTPException(status_code=403, detail="Access denied")

   async with app.state.db.acquire() as connection:
      async with connection.cursor() as cursor:

          # Create 'competition' table if not exists in the database
          await cursor.execute('CREATE TABLE IF NOT EXISTS competition (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,name VARCHAR(100) NOT NULL,date DATE NOT NULL,track_length INT NOT NULL);')
          
           # Insert the competition information into the 'competition' table
          await cursor.execute('INSERT INTO competition (name, date, track_length) VALUES (%s, %s, %s)', (
              competition_info["competition_name"], 
              competition_info["competition_date"],
              competition_info["track_length"]
          ))
          
          id = cursor.lastrowid

   return {"id": id}

@app.get("/api/newSession")
async def newCookieSession(cookieInfo: Request):
    cookie_gen = await cookieInfo.json()
    if cookie_gen["session"] == os.environ["gen_token"]:
        newGeneration = keyGenerator()
        return newGeneration
    else:
        raise HTTPException(status_code=403, detail="Access denied")

@app.get("/api/isValid")
async def checkValid(cookie: Request):
    cookieValid = await cookie.json()
    if keyGenerator() == cookieValid["session"]:
        return {"status": "valid"}
    else:
        return {"status": "invalid"}

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8000)
