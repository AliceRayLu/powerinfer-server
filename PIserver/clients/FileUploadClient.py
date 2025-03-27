import hashlib
import json
from PIserver.clients.net import getHeader, send_post_request
from PIserver.constants import *
from pathlib import Path
import requests
from tqdm import tqdm

from PIserver.utils.files import log_error

class FileUploadClient():
    def __init__(self, model_name: list):
        self.host = POWERINFER_MODEL_HOST
        self.port = POWERINFER_SERVER_PORT
        self.mname = model_name[0]
        self.tname = model_name[1]
        
    def generate_md5(self, file_path):
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()


    def upload_file(self, path: Path) -> bool:
        file_size = path.stat().st_size
        uploaded_size = 0
        auth_header = getHeader()
        response = requests.head(
            backend_host+"/task/client/upload",  
            headers=auth_header,
            data=json.dumps({
                "mname": self.mname, 
                "tname": self.tname, 
                "fname": path.name, 
                "md5": self.generate_md5(path)
            })
        )
        if response.status_code == 403:
            print(response.text)
            return False
        if 'Content-Range' in response.headers:
            uploaded_size = int(response.headers['Content-Range'].split('/')[1])
            
        if uploaded_size == file_size:
            print(f"File {path.name} is already uploaded.")
            return True
        
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
                        backend_host+"/task/client/upload", 
                        headers=headers, 
                        params={"mname": self.mname, "tname": self.tname, "fname": path.name}, 
                        data=chunk
                    )
                    
                    if response.status_code == 200 or response.status_code == 206:
                        uploaded_size += len(chunk)
                        pbar.update(len(chunk))
                    else:
                        log_error(f"Failed to Upload. {response.text}")
                        break
        return True
    
    def iter_folder(self, path: Path):
        if path.is_file():
            self.upload_file(path)
        elif path.is_dir():
            for file in path.iterdir():
                if file.is_file():
                    self.upload_file(file)
                # forbid any sub directory
                    
    def upload(self, file_path):
        response = send_post_request("/task/client/add", params={"mname": self.mname, "tname": self.tname})
        
        if response.status_code == 403:
            log_error(response.text)
            return
        self.iter_folder(Path(file_path))
        
        send_post_request("/task/client/done", params={"mname": self.mname, "tname": self.tname})
                    
        print(f"Upload successfully. Visit xxx.com or use \
            `powerinfer upload {self.mname+":"+self.tname} -s` to check the process.")
    
    def fetch_history(self):
        response = send_post_request("/task/client/query", params={"mname": self.mname, "tname": self.tname}, stream=True)
        if response.status_code == 200:
            try:
                for line in response.iter_lines():
                    if line:
                        task = json.loads(line)
                        yield task
            except Exception as e:
                log_error(f"Failed to parse task stream: {e}")
                yield None
        
    def cancel(self):
        print("Starting to cancel training task for model", self.mname + ":" + self.tname)
        response = send_post_request("/task/client/cancel", params={"mname": self.mname, "tname": self.tname})
        if response.text == "true":
            print("Cancelled successfully.")
        else:
            print("Training task not found.")
        