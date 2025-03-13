import requests
from PIserver.constants import *
from PIserver.utils.files import log_error
from typing import Optional, Dict, Any
import json

backend_host = "https://" + POWERINFER_HOST + ":" + str(POWERINFER_SERVER_PORT)

def send_get_request(
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
        log_error(f"Cannot successfully get response. {e}")
        return None
    
def send_post_request(url: str, data):
    try:
        response = requests.post(url, data=json.dumps(data)).json()
        return response
    except Exception as e:
        log_error(f"Cannot successfully get response. {e}")
        return None
    
def get_user_by_pub_key(pub_key: str) -> str:
    uid = send_get_request("/key/getUser", {"pub_key": pub_key})
    print(uid)
    return ""