import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("CLOSE_API_KEY", "").strip()
print("Using Close API key:", api_key[:5] + "...")

response = requests.get("https://api.close.com/api/v1/me/", auth=(api_key, ""))
print("Status:", response.status_code)
print(response.json())
