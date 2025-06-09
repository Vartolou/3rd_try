from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List

app = FastAPI()
# Database connection with error handling
def get_db():
    try:
        conn = psycopg2.connect(
            "postgresql://postgres:[Data.Base.5002]@db.ftigowwlepfjkwoqluzg.supabase.co:5432/postgres",
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

# Response model for better API documentation
class HizbResponse(BaseModel):
    id: int
    name: str
    description: str = None

# API to get all Hizbs with error handling
@app.get("/hizbs", response_model=List[HizbResponse])
def get_hizbs(db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM hizbs")
        return cursor.fetchall()
    except psycopg2.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database query failed: {str(e)}"
        )
    finally:
        cursor.close()

# API to mark progress with validation
class ProgressUpdate(BaseModel):
    user_id: int
    hizb_id: int

@app.post("/mark-complete")
def mark_complete(data: ProgressUpdate, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        # Check if user exists (optional security check)
        cursor.execute("SELECT 1 FROM users WHERE id = %s", (data.user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
            
        # Check if hizb exists
        cursor.execute("SELECT 1 FROM hizbs WHERE id = %s", (data.hizb_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Hizb not found")
            
        # Insert progress
        cursor.execute(
            "INSERT INTO progress (user_id, hizb_id) VALUES (%s, %s)",
            (data.user_id, data.hizb_id)
        )
        db.commit()
        return {"message": "Progress saved successfully!"}
    except psycopg2.Error as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database operation failed: {str(e)}"
        )
    finally:
        cursor.close()
