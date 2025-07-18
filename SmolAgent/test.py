import os
import re
import requests
import json

from smolagents import CodeAgent, Tool
from smolagents.models import ChatMessage
import google.generativeai as genai


class HospitalClaimAssistant:
    def __init__(self, gemini_api_key: str):
        os.environ["GEMINI_API_KEY"] = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

        self.agent = CodeAgent(model=self.GeminiInferenceModel(self.model), tools=[self.MCPHospitalTool()])

    class GeminiLLM:
        def __init__(self, model):
            self.model = model

        def __call__(self, prompt: str) -> str:
            response = self.model.generate_content(prompt)
            return response.text

    class GeminiInferenceModel:
        def __init__(self, model):
            self.llm = HospitalClaimAssistant.GeminiLLM(model)

        def generate(self, messages, **kwargs):
            prompt_parts = []
            for m in messages:
                if isinstance(m, ChatMessage):
                    contents = m.content if isinstance(m.content, list) else [{"type": "text", "text": str(m.content)}]
                    for item in contents:
                        if item.get("type") == "text":
                            prompt_parts.append(item["text"])
                elif isinstance(m, dict) and isinstance(m.get("content"), str):
                    prompt_parts.append(m["content"])
            prompt = "\n".join(prompt_parts)
            response_text = self.llm(prompt)
            return ChatMessage(role="assistant", content=response_text)

    class MCPHospitalTool(Tool):
        name = "MCPHospitalTool"
        description = "Fetch hospital data by incident ID from MCP server. Return entire row as is without evaluation."
        inputs = {
            "query": {
                "type": "string",
                "description": "User query that contains an incident ID like IND-2025-0004.",
            }
        }
        output_type = "string"

        def forward(self, query: str) -> str:
            match = re.search(r"(IND-\d{4}-\d{4})", query)
            if not match:
                return "Please provide a valid incident ID like IND-2025-0004."
            incident_id = match.group(1)
            url = f"http://127.0.0.1:9001/incident/{incident_id}"

            try:
                res = requests.get(url)
                res.raise_for_status()
                data = res.json()
            except Exception as e:
                return f"Error retrieving data for {incident_id}: {str(e)}"

            return json.dumps(data, indent=2)  # Pretty JSON string

    def process_query(self, user_question: str) -> str:
        system_instruction = (
            "You are a hospital claim assistant. Use the tool to get incident data. "
            "From the tool output, extract only what the user asked for (e.g. bill amount, patient ID, date). "
            "Be concise. Don’t add explanations. Format currency properly (₹). "
            "Do not guess or add any extra explanation unless the data is missing. "
            "Return like 'The bill is ₹15000. Patient ID is P1234.' etc."
        )

        formatted_query = f"{system_instruction}\n\nUser query: {user_question}"

        # Step 1: Get tool-based agent response (raw data)
        tool_output = self.agent(formatted_query)

        # Step 2: Ask Gemini to generate final answer from tool output
        followup_prompt = f"""
You are a helpful assistant. Below is hospital incident data (may include multiple records):

{tool_output}

Extract the following: patient's name, patient_id, admission date, discharge date, and bill amount — ONLY based on what was asked.

Do not include explanations. Write as if you're replying in a chat.
Now, based on the above data, answer the following user query:
"{user_question}"
"""

        final_llm = self.GeminiLLM(self.model)
        answer = final_llm(followup_prompt)
        return answer


# === Example usage ===
if __name__ == "__main__":
    assistant = HospitalClaimAssistant(gemini_api_key="AIzaSyCBcfGzHVrp6O8cMxu3v-rPhaQsWFRaTvA")
    query = "What is the bill amount, admission date, and patient ID for IND-2025-0004?"
    result = assistant.process_query(query)
    print("\n=== Final Answer ===\n", result)
