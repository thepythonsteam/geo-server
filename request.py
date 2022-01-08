import requests
import json


url = str(input('Enter server IP:'))

payload = json.dumps({})

headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
