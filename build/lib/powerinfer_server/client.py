import requests

host = "http://localhost:8000"

def hello():
    response = requests.get(host)
    print(response.json())
    