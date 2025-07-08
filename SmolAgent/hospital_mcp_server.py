import sqlite3
import pandas as pd
from mcp.server.fastmcp import FastMCP
from starlette.responses import PlainTextResponse

# === Describe the DB dynamically ===
def describe_db(db_path: str) -> str:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        schema = ""
        for (table_name,) in tables:
            schema += f"\nTable: {table_name}\n"
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                col_id, name, col_type, notnull, default, pk = col
                schema += f"  - {name} ({col_type})\n"

        return schema.strip() if schema else "No tables found."
    except Exception as e:
        return f"Error describing database: {e}"
    finally:
        conn.close()

# === FastMCP App Setup ===
mcp = FastMCP("HospitalDB")


def hospital_sql_query(query: str):
    """
    Run a SQL query on hospital_data.db and return the results as list of tuples.
    """
    db_path = "hospital_data.db"
    try:
        conn = sqlite3.connect(db_path)
        with conn:
            result = list(conn.execute(query))  # ✅ Materialize results here
        return result if result else "No matching records found."
    except Exception as e:
        return f"SQL error: {e}"
    finally:
        conn.close()  # ✅ Safe to close now that data is fetched

# === Set Dynamic Docstring ===
db_path = "hospital_data.db"
description = describe_db(db_path)
hospital_sql_query.__doc__ = f"""
Execute SQL query on the hospital admission database.

Database schema:
{description}

Args:
    query (str): A valid SQL query string targeting the tables described above.

Returns:
    str: Query result or error message.
"""

# === Register tool with dynamic doc ===
mcp.tool("get_hospital_data")(hospital_sql_query)

# === Run MCP Server ===
mcp.run()
