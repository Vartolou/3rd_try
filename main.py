from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Database connection
def get_db():
    conn = psycopg2.connect(
        "postgresql://postgres:[Data.Base.5002]@db.ftigowwlepfjkwoqluzg.supabase.co:5432/postgres",
        cursor_factory=RealDictCursor
    )
    return conn

# API to get all Hizbs
@app.get("/hizbs")
def get_hizbs(db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM hizbs")
    return cursor.fetchall()

# API to mark progress
class ProgressUpdate(BaseModel):
    user_id: int
    hizb_id: int

@app.post("/mark-complete")
def mark_complete(data: ProgressUpdate, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO progress (user_id, hizb_id) VALUES (%s, %s)",
        (data.user_id, data.hizb_id)
    )
    db.commit()
    return {"message": "Progress saved!"}