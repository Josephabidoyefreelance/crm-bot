import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

CLOSE_API_KEY = os.getenv("CLOSE_IO_API_KEY")

response = requests.get(
    "https://api.close.com/api/v1/webhook/",
    auth=(CLOSE_API_KEY, "")
)

print("Status Code:", response.status_code)
print("Response:", response.json())
