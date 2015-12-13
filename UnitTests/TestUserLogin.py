import requests

url = "http://0.0.0.0:5000/api/user/login"

payload = "{\n    \"email\": \"evan.hopkins1@marist.edu\",\n    \"password\": \"alpine\"\n}"
headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "19829ea8-2334-83fe-34d3-88fa45f4ec87"
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)
