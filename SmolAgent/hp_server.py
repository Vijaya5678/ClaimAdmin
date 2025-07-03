import sqlite3
import re
import pandas as pd
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount

# === Load hospital data (same as in hospital_data.db) for demo ===
conn = sqlite3.connect("hospital_data.db")
df = pd.read_sql_query("SELECT * FROM hospital_data", conn)
conn.close()

# === Create MCP app ===
mcp = FastMCP("HospitalDB")

# === MCP Resource: Get claim via incident ID ===
@mcp.resource("incident://{incident_id}")
def get_hospital_claim(incident_id: str) -> dict:
    row = df[df["incident_id"] == incident_id]
    return row.iloc[0].to_dict() if not row.empty else {"error": "Incident not found"}

# === Optional MCP Tool: mark reviewed, approve, etc. ===
@mcp.tool("approve_hospital_claim")
def approve_hospital_claim(incident_id: str, approve: bool = True) -> dict:
    row = df[df["incident_id"] == incident_id]
    return {"status": "approved" if approve else "rejected", "incident": incident_id} if not row.empty else {"status": "error", "message": "Not found"}

# === Direct HTTP GET endpoint (non-MCP) ===
async def http_get_incident(request):
    incident_id = request.path_params["incident_id"]
    row = df[df["incident_id"] == incident_id]
    if not row.empty:
        return JSONResponse(row.iloc[0].to_dict())
    return JSONResponse({"error": "Incident not found"}, status_code=404)

# === Compose full app ===
app = Starlette(routes=[
    Route("/incident/{incident_id}", http_get_incident),
    Mount("/mcp", app=mcp.sse_app)
])
