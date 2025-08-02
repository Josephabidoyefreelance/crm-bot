import requests

CLOSE_API_KEY = "api_0EGy0bKxb2gy8Mxp6Q8xEU.63jttk8josvYzeCIIA66O9"

response = requests.get(
    "https://api.close.com/api/v1/webhook/",
    auth=(CLOSE_API_KEY, "")
)

print("Status Code:", response.status_code)
print("Response:", response.json())
