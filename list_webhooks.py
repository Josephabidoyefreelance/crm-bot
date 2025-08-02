import requests

CLOSE_API_KEY = "api_2syo0UnYRkhah2CxWw9fxI.380io3msbLAsxh6EaqMl4B"

response = requests.get(
    "https://api.close.com/api/v1/webhook/",
    auth=(CLOSE_API_KEY, "")
)

print("Status Code:", response.status_code)
print("Response:", response.json())
