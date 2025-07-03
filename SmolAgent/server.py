import pandas as pd
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount

# Sample claim data
df = pd.DataFrame([
    {"name": "Alice", "bill": 1200},
    {"name": "Bob", "bill": 3400},
    {"name": "Charlie", "bill": 900},
])

# Create MCP app
mcp = FastMCP("ClaimDB")

@mcp.resource("claim://{name}")
def get_claim(name: str) -> dict:
    row = df[df["name"].str.lower() == name.lower()]
    return row.iloc[0].to_dict() if not row.empty else {"error": "User not found"}

@mcp.tool("approve_claim")
def approve_claim(name: str, approve: bool = True) -> dict:
    row = df[df["name"].str.lower() == name.lower()]
    return {"status": "approved" if approve else "rejected", "name": name} if not row.empty else {"status": "error", "message": "User not found"}

# Define your custom HTTP GET route
async def http_get_claim(request):
    name = request.path_params["name"]
    row = df[df["name"].str.lower() == name.lower()]
    if not row.empty:
        return JSONResponse(row.iloc[0].to_dict())
    else:
        return JSONResponse({"error": "User not found"}, status_code=404)

# Compose the full ASGI app
app = Starlette(routes=[
    Route("/claim/{name}", http_get_claim),
    Mount("/mcp", app=mcp.sse_app)  # Keep MCP working at /mcp
])
