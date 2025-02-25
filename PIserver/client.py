import requests

host = "http://localhost:8000"

def hello():
    response = requests.get(host)
    print(response.json())

def stop():
    response = requests.get(f"{host}/kill")
    print(response.json())    