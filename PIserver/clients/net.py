import requests
from PIserver.constants import *
from PIserver.utils.files import log_error
from typing import Optional
import json
from pathlib import Path
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import base64

def getHeader():
    pubkey = Path(DEFAULT_SSH_PUB_KEY_PATH).read_text()
    timestamp = str(int(time.time() * 1000))
    
    # get private key
    with open(DEFAULT_SSH_PEM_KEY_PATH, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

    signature = private_key.sign(
        timestamp.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    signature_b64 = base64.b64encode(signature).decode('utf-8')
    
    return {"pubkey": pubkey, "timestamp": timestamp, "signature": signature_b64, "Content-Type": "application/json"}

# def send_get_request(
#     url: str, 
#     data: Optional[Dict[str, Any]] = None
# ) -> Optional[Dict[str, Any]]:
#     try:
#         response = requests.get(
#             backend_host + url, 
#             data=data
#             ).json()
#         return response
#     except Exception as e:
#         log_error(f"Cannot successfully get response. {e}")
#         return None
    
def send_post_request(url: str, data=None, stream: bool = False, header: dict=None, params:dict = None) -> Optional[requests.Response]:
    try:
        headers = getHeader()
        if header is not None:
            headers.update(header)
        param = {} if params is None else params
        response = requests.post(
            backend_host+url, 
            data=json.dumps(data if data is not None else {}), 
            headers=headers, 
            stream=stream, 
            params=param
        )
        return response
    except Exception as e:
        log_error(f"Cannot successfully get response. {e}")
        return None
    
def get_user_by_pub_key(pub_key: str) -> str:
    # uid = send_get_request("/key/getUser", {"pub_key": pub_key})
    # print(uid)
    return ""