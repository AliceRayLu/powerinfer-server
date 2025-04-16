import hashlib
import json
from PIserver.clients.net import getHeader, send_post_request
from PIserver.constants import *
from pathlib import Path
import requests
from tqdm import tqdm

from PIserver.utils.files import log_error
import mmap

class FileUploadClient():
    def __init__(self, model_name: list):
        self.host = POWERINFER_MODEL_HOST
        self.port = POWERINFER_SERVER_PORT
        self.mname = model_name[0]
        self.tname = model_name[1]
        
    def generate_md5(self, file_path: Path):
        print(f"Validating file changes {str(file_path)}...")
        md5_hash = hashlib.md5()
        buffer_size = 1024 * 1024  # 1MB
        
        with open(file_path, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                while chunk := mmapped_file.read(buffer_size):
                    md5_hash.update(chunk)
        return md5_hash.hexdigest()


    def upload_file(self, path: Path, need_train: bool) -> bool:
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
                "md5": self.generate_md5(path),
                "need_train": need_train
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
                        params={
                            "mname": self.mname, 
                            "tname": self.tname, 
                            "fname": path.name,
                            "need_train": need_train
                        }, 
                        data=chunk
                    )
                    
                    if response.status_code == 200 or response.status_code == 206:
                        uploaded_size += len(chunk)
                        pbar.update(len(chunk))
                    else:
                        log_error(f"Failed to Upload. {response.text}")
                        return False
        return True
    
    def iter_folder(self, path: Path, need_train: bool):
        print(f"Iterating folder {str(path)}...")
        success = True 
        if path.is_file() and not path.name.startswith("."):
            success = self.upload_file(path, need_train) and success
        elif path.is_dir() and not path.name.startswith("."):
            for file in path.iterdir():
                if file.is_file() and not file.name.startswith("."):
                    success = self.upload_file(file, need_train) and success
                elif file.is_dir() and not file.name.startswith("."):
                    success = self.iter_folder(file, need_train) and success
        return success
                    
    def upload(self, file_path, no_train: bool = False, hf: str = ""):
        if hf == "" and not Path(file_path).exists():
            log_error(f"Folder {file_path} does not exist.")
            return
        
        params = {
            "mname": self.mname,
            "tname": self.tname,
            "need_train": not no_train
        }
        if hf is not None and hf != "":
            params["hf"] = hf
        response = send_post_request("/task/client/add", params=params)
        if response is None:
            log_error("Cannot successfully get response. Please check your internet connection.")
            return
        
        if response.status_code == 403:
            log_error(response.text)
            return
        if response.status_code != 200:
            log_error(f"Failed to upload. Please try it later.")
            return
        
        if hf is not None and hf != "":
            print(f"Uploading huggingface model {hf} to {self.mname+":"+self.tname} task submitted successfully.")
            print(f"Use `powerinfer upload {self.mname+":"+self.tname} -s` to check the process.")
            return
        
        success = self.iter_folder(Path(file_path), need_train=not no_train)
        
        send_post_request("/task/client/done", params={"mname": self.mname, "tname": self.tname, "success": success})
        if success:      
            print(f"Upload successfully. Visit xxx.com or use `powerinfer upload {self.mname+":"+self.tname} -s` to check the process.")
            print(f"Use `powerinfer upload {self.mname+":"+self.tname} -c` to cancel the training process.")
        else:
            log_error("Upload failed. Please rerun the command to resume uploading model.")
            return
    
    # def fetch_history(self):
    #     response = send_post_request("/task/client/query", params={"mname": self.mname, "tname": self.tname}, stream=True)
    #     if response.status_code == 200:
    #         try:
    #             for line in response.iter_lines():
    #                 if line:
    #                     task = json.loads(line)
    #                     yield task
    #         except Exception as e:
    #             log_error(f"Failed to parse task stream: {e}")
    #             yield None
        
    def cancel(self):
        print("Starting to cancel training task for model", self.mname + ":" + self.tname)
        response = send_post_request("/task/client/cancel", params={"mname": self.mname, "tname": self.tname})
        if response is None:
            log_error("Cannot successfully get response. Please check your internet connection.")
            return
        if response.text == "true":
            print("Cancelled successfully.")
        else:
            print("No running task found.")
        