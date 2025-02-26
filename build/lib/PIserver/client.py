import requests

host = "http://localhost:8000"

def hello():
    get_simple_message(f"{host}/")

def stop():
    get_simple_message(f"{host}/kill")
        
def get_simple_message(host):
    try:
        response = requests.get(f"{host}")
        print(response.json().get("message"))
    except:
        print("Server already stopped. Use `pwi-serve` to start server.")