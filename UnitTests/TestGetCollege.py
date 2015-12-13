import requests

url = "http://0.0.0.0:5000/api/college"

headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "8f823bfd-1c31-938f-8933-0e82ed9b7e97"
    }

response = requests.request("GET", url, headers=headers)

print(response.text)
