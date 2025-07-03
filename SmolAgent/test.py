import sqlite3
import asyncio

def get_hospital_data(incident_id):
    conn = sqlite3.connect('hospital_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hospital_records WHERE incident_id = ?", (incident_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "incident_id": row[0],
            "policy_num": row[1],
            "admission_date": row[2],
            "discharge_date": row[3],
            "bill": row[4]
        }
    return None
