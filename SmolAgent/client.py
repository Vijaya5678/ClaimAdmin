import asyncio
from mcp.client.streamable_http import create_mcp_http_client


async def main():
    async with create_mcp_http_client() as client:
        response = await client.get("http://127.0.0.1:9000/claim/Alice")
        print("Status:", response.status_code)
        text = response.text  # no await here
        print("Raw response text:", text)
        try:
            data = response.json()
        except Exception as e:
            print("Error parsing JSON:", e)
            data = None

        print("Parsed JSON data:", data)

asyncio.run(main())
