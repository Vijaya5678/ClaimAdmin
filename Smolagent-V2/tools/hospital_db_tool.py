# from smolagents import tool
# from sqlalchemy import text
# from database.hospital_schema import engine

# @tool
# def sql_engine(query: str) -> str:
#     """
#     Allows you to perform SQL queries on the patients table.
#     The table is named 'patients' and includes:
#       - patient_id: INTEGER
#       - patient_name: STRING
#       - age: INTEGER
#       - gender: STRING
#       - diagnosis: STRING
#       - amount: FLOAT
#     """
#     result = ""
#     with engine.connect() as conn:
#         rows = conn.execute(text(query))
#         for row in rows:
#             result += "\n" + str(row)
#     return result if result else "No matching records found."
"""
from smolagents import tool
from sqlalchemy import text
import sqlite3

@tool
def sql_engine(query: str) -> str:
    """
"""
    Execute SQL query on the hospital database.

    Args:
        query (str): A valid SQL query string to run on the 'patients' table.

    Returns:
        str: Result of the query formatted as plain text.
    """
"""
    conn = sqlite3.connect("hospital.db")
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

"""

from smolagents import tool
import sqlite3

@tool
def sql_engine(query: str) -> str:
    """
    Execute SQL query on the hospital database.

    The table is named `patients` and has the following columns:
      - patient_id (INTEGER): Unique ID of the patient
      - patient_name (TEXT): Full name of the patient
      - age (INTEGER): Age of the patient
      - gender (TEXT): Gender of the patient (Male/Female)
      - diagnosis (TEXT): Medical condition or diagnosis
      - amount (REAL): Total bill amount in INR

    Args:
        query (str): A valid SQL query string to run on the 'patients' table.

    Returns:
        str: Result of the query formatted as plain text.
    """
    conn = sqlite3.connect("hospital.db")
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
