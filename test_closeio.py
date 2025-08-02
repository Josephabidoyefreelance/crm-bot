import os
import requests
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env

api_key = os.getenv("CLOSE_IO_API_KEY")

url = "https://api.close.com/api/v1/me/"

response = requests.get(url, auth=(api_key, ''))

print("Status:", response.status_code)
print("Response:", response.json())
