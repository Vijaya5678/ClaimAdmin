from fastapi import FastAPI, HTTPException
import sqlite3
from typing import Optional

app = FastAPI()

DB_PATH = "hospital_data.db"

def get_hospital_data(incident_id: str) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT incident_id, policy_num, admitted_date, discharged_date, bill FROM hospital_data WHERE incident_id = ?", (incident_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "incident_id": row[0],
            "policy_num": row[1],
            "admitted_date": row[2],
            "discharged_date": row[3],
            "bill": row[4],
        }
    return None

@app.get("/hospital/{incident_id}")
async def hospital_info(incident_id: str):
    data = get_hospital_data(incident_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Hospital data not found")
    return data
