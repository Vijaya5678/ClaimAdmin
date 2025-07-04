import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
#DB_URL = "sqlite:///hospital.db"  # Or use a file like "sqlite:///hospital.db"
DB_URL = "sqlite:///hospital.db"