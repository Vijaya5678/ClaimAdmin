import os
import sqlite3
import re

from smolagents import Tool, CodeAgent
from smolagents.models import ChatMessage
import google.generativeai as genai

# === Set Gemini API key ===
os.environ["GEMINI_API_KEY"] = "AIzaSyBKMV8TARxNEOnTvA4sviV1wEb0uZA9pv4"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# === Gemini LLM wrapper ===
class GeminiLLM:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def __call__(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

# === Gemini Inference Model with hardcoded system prompt ===
class GeminiInferenceModel:
    def __init__(self):
        self.llm = GeminiLLM()

    def generate(self, messages, **kwargs):
        prompt_parts = [
            "**SYSTEM:** You are a hospital billing assistant. "
            "If a question includes an incident ID like IND-XXXX-YYYY, you must call the HospitalDataTool to answer. "
            "Do not answer it yourself."
            "Don not give anydata that is not preset in hospital db. Do not makeup any data."
        ]
        for m in messages:
            if isinstance(m, ChatMessage):
                content = m.content if isinstance(m.content, list) else [{"type": "text", "text": str(m.content)}]
                for part in content:
                    if part.get("type") == "text":
                        prompt_parts.append(part["text"])
        prompt = "\n".join(prompt_parts)
        response_text = self.llm(prompt)
        return ChatMessage(role="assistant", content=response_text)

# === Tool: Hospital Billing Info ===
class HospitalDataTool(Tool):
    name = "HospitalDataTool"
    description = (
        "Fetch hospital billing data by incident ID. "
        "Use this tool if the user question includes an incident ID (e.g., IND-2025-0004)."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "User query with incident ID",
        }
    }
    output_type = "string"

    def forward(self, query: str) -> str:
        incident_match = re.search(r"(IND-\d{4}-\d{4})", query)
        if not incident_match:
            return "Please provide a valid incident ID like IND-2025-0004."
        incident_id = incident_match.group(1)
        conn = sqlite3.connect("hospital_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hospital_data WHERE incident_id=?", (incident_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return (
                f"Incident ID: {row[0]}\n"
                f"Patient Name: {row[1]}\n"
                f"Policy Number: {row[2]}\n"
                f"Admitted: {row[3]}\n"
                f"Discharged: {row[4]}\n"
                f"Bill Amount: ₹{row[5]}"
            )
        return f"No data found for incident {incident_id}."

# === Main ===
def cmain():
    tools = [HospitalDataTool()]
    inference_model = GeminiInferenceModel()
    agent = CodeAgent(model=inference_model, tools=tools)

    question = "What is the bill amount for IND-2025-0004?"
    response = agent(question)
    print("Agent response:\n", response)

if __name__ == "__main__":
    cmain()
