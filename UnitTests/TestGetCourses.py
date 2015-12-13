import requests

url = "http://0.0.0.0:5000/api/user/courses"

headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "a2e48734-7d28-dc62-a08a-f3edca000f1b"
    }

response = requests.request("GET", url, headers=headers)

print(response.text)
