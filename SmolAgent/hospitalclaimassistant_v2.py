# 📁 File: hospital_admin.py

from smolagents import tool, CodeAgent, InferenceClientModel
import sqlite3
from typing import Optional

class HospitalAdminAssistant:
    def __init__(self, db_path: str = "hospital_data.db", model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct", hf_token: Optional[str] = None):
        self.db_path = db_path
        self.sql_tool = self._build_sql_tool()
        self.agent = CodeAgent(
            tools=[self.sql_tool],
            model=InferenceClientModel(model_id=model_id, token=hf_token)
        )

    def _build_sql_tool(self):
        @tool
        def query_hospital_db(query: str) -> str:
            """
            Run a SQL query on the admissions table.

            Table: `hospital_data`
            Columns:
              - incident_id (TEXT): Unique policy_user_id ID (e.g., IND-2025-0004)
              - diagnosis (TEXT) : the disease,diagnosis what patient had.
              - admitted (TEXT): Date of admission
              - discharged (TEXT): Date of discharged
              - patient_name (TEXT): Name of the patient
              - bill (REAL): Total bill amount
            

            Args:
                query (str): SQL query string

            Returns:
                str: Query result 
            """
            conn = sqlite3.connect(self.db_path)
            result = ""
            try:
                with conn:
                    rows = conn.execute(query)
                    for row in rows:
                        result += "\n" + str(row)
                return result if result else "No matching records found."
            except Exception as e:
                return f"SQL error: {e}"
            finally:
                conn.close()

        return query_hospital_db

    def ask(self, query: str) -> str:
        return self.agent.run(query)


# ✅ Main usage (can be a test or entry point)
if __name__ == "__main__":
    HF_TOKEN = "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"  # Replace with env var or config
    assistant = HospitalAdminAssistant(hf_token=HF_TOKEN)

    query = "What is the bill amount and admission date for IND-2025-0004?"
    response = assistant.ask(query)
    print("\n🤖 Agent Response:\n", response)
