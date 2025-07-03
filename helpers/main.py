
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import streamlit as st
from pymongo import MongoClient
from helpers.get_policy_and_claim_summary import get_policy_and_claim_summary
from helpers.query_handler import PolicyQueryHandler
from query_handler import PolicyQueryHandler
import google.generativeai as genai
import os
from dotenv import load_dotenv

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")
handler = PolicyQueryHandler()
answer = handler.get_response("tell me about Individual health insurance plan?")
print(answer)
