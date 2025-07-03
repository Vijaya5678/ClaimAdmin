import os
import asyncio
import sqlite3
import re
import google.generativeai as genai
from smolagents import CodeAgent, InferenceClientModel
from smolagents.tools import Tool

# === Configure Gemini API key ===
os.environ["GEMINI_API_KEY"] = "AIzaSyBKMV8TARxNEOnTvA4sviV1wEb0uZA9pv4"  # Replace with your actual key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
GEMINI_MODEL = "models/gemini-1.5-flash"

# === SQLite DB Access ===
def get_hospital_data(incident_id: str):
    conn = sqlite3.connect('hospital_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hospital_data WHERE incident_id=?", (incident_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "incident_id": row[0],
            "patient_name": row[1],
            "policy_num": row[2],
            "admitted": row[3],
            "discharged": row[4],
            "bill": row[5]
        }
    return None

# === Define Tool for the Agent ===
class HospitalDataTool(Tool):
    name = "HospitalDataTool"
    description = "Fetches hospital bill info using incident ID like IND-2025-0004."
    inputs = {
        "query": "User question containing an incident ID"
    }
    output_type = "string"

    async def __call__(self, query: str):
        match = re.search(r"(IND-\d{4}-\d{4})", query)
        if not match:
            return "Please provide a valid incident ID like IND-2025-0004."

        incident_id = match.group(1)
        data = get_hospital_data(incident_id)
        if not data:
            return f"No data found for incident {incident_id}."
        return f"Bill amount for {incident_id} is ₹{data['bill']}."

# === Main Execution ===
async def main():
    inference_model = InferenceClientModel(model=GEMINI_MODEL)
    tools = [HospitalDataTool()]
    agent = CodeAgent(model=inference_model, tools=tools)

    user_question = "What is the bill amount for IND-2025-0004?"
    response = await agent.acall(user_question)
    print("Agent response:", response)

if __name__ == "__main__":
    asyncio.run(main())
