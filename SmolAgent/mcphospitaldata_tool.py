import aiohttp
import re
from smolagents import Tool

class MCPHospitalDataTool(Tool):
    name = "HospitalDataTool"
    description = "Fetch hospital billing data by incident ID from MCP server."
    inputs = {
        "query": {
            "type": "string",
            "description": "User question containing an incident ID",
        }
    }
    output_type = "string"

    async def forward(self, query: str) -> str:
        incident_match = re.search(r"(IND-\d{4}-\d{4})", query)
        if not incident_match:
            return "Please provide a valid incident ID like IND-2025-0004."
        incident_id = incident_match.group(1)

        url = f"http://127.0.0.1:9000/incident/{incident_id}"  # your MCP server URL
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return f"Bill amount for incident {incident_id} is ₹{data.get('bill', 'N/A')}."
                else:
                    return f"No data found for incident {incident_id}."
