import requests
from PIserver.constants import *
from typing import Optional, Dict, Any

backend_host = "https://" + POWERINFER_HOST + ":" + str(POWERINFER_SERVER_PORT)

def send_request(
    url: str, 
    data: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(
            backend_host + url, 
            data=data
            ).json()
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def get_user_by_pub_key(pub_key: str) -> str:
    uid = send_request("/key/getUser", {"pub_key": pub_key})
    print(uid)
    return ""