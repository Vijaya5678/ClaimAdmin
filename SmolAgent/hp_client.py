import asyncio
from mcp.client.streamable_http import create_mcp_http_client
from hospital_smolagent import HospitalDataTool, GeminiInferenceModel, CodeAgent

async def main():
    # Step 1: Ask the agent (simulates patient asking)
    question = "Can you tell me the bill amount for IND-2025-0004?"

    tools = [HospitalDataTool()]
    model = GeminiInferenceModel()
    agent = CodeAgent(model=model, tools=tools)

    agent_response = agent(question)
    print("\n🤖 Agent Response:\n", agent_response)

    # Step 2: Call MCP for the same incident (from server)
    async with create_mcp_http_client() as client:
        response = await client.get("http://127.0.0.1:9001/incident/IND-2025-0004")
        print("\n🌐 MCP Status:", response.status_code)
        print("📦 MCP Raw response:", response.text)
        try:
            json_data = response.json()
            print("✅ MCP JSON response:", json_data)
        except Exception as e:
            print("❌ Error parsing MCP JSON:", e)

asyncio.run(main())
