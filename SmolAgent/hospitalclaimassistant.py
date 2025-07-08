# 📁 File: hospital_admin.py

from smolagents import CodeAgent, InferenceClientModel
from smolagents.tools import ToolCollection
from mcp import StdioServerParameters

class HospitalAdminAssistant:
    def __init__(self, model_id: str, hf_token: str):
        self.model_id = model_id
        self.hf_token = hf_token

    def ask(self, query: str) -> str:
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "hospital_mcp_server.py"]
        )

        with ToolCollection.from_mcp(server_params, trust_remote_code=True) as tool_collection:
            model = InferenceClientModel(model_id=self.model_id, token=self.hf_token)
            agent = CodeAgent(tools=tool_collection.tools, model=model)
            return agent.run(query)

# ✅ Example usage
if __name__ == "__main__":
    assistant = HospitalAdminAssistant(
        model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
        hf_token="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"
    )

    result = assistant.ask("what was discharge date of incident_id IND-2025-0004")
    print("\n🤖 Agent Response:\n", result)
