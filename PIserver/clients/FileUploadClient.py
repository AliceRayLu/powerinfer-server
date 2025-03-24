from PIserver.clients.net import getHeader
from PIserver.constants import *
from pathlib import Path
import requests
from tqdm import tqdm

from PIserver.utils.files import log_error

class FileUploadClient():
    def __init__(self):
        self.host = POWERINFER_MODEL_HOST
        self.port = POWERINFER_SERVER_PORT

    def upload_file(self, path: Path, model_name: list):
        file_size = path.stat().st_size
        uploaded_size = 0
        auth_header = getHeader()
        response = requests.head(
            backend_host+"/type/client/upload", 
            params={"mname": model_name[0], "tname": model_name[1], "fname": path.name}, 
            headers=auth_header
        )
        if 'Content-Range' in response.headers:
            uploaded_size = int(response.headers['Content-Range'].split('/')[1])
        
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=path.name, initial=uploaded_size) as pbar:
            with open(path, 'rb') as f:
                f.seek(uploaded_size)
                while uploaded_size < file_size:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    headers = {
                        'Content-Range': f'bytes {uploaded_size}-{uploaded_size + len(chunk) - 1}/{file_size}'
                    }
                    headers.update(auth_header)
                    response = requests.patch(
                        backend_host+"/type/client/upload", 
                        headers=headers, 
                        params={"mname": model_name[0], "tname": model_name[1], "fname": path.name}, 
                        data=chunk
                    )
                    
                    if response.status_code == 200 or response.status_code == 206:
                        uploaded_size += len(chunk)
                        pbar.update(len(chunk))
                    else:
                        log_error(f"Failed to Upload. {response.text}")
                        break
                    
    def upload(self, file_path, model_name:list):
        path = Path(file_path)
        
        if path.is_file():
            self.upload_file(path, model_name)
        elif path.is_dir():
            for file in path.iterdir():
                if file.is_file():
                    self.upload_file(file, model_name)