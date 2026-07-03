from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

JWT_SECRET = os.getenv("JWT_SECRET")

XERO_CLIENT_ID = os.getenv("XERO_CLIENT_ID")
XERO_CLIENT_SECRET = os.getenv("XERO_CLIENT_SECRET")
XERO_REDIRECT_URI = os.getenv("XERO_REDIRECT_URI")

ERPNEXT_BASE_URL = os.getenv("ERPNEXT_BASE_URL")
ERPNEXT_API_KEY = os.getenv("ERPNEXT_API_KEY")
ERPNEXT_API_SECRET = os.getenv("ERPNEXT_API_SECRET")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")