from tqdm import tqdm
import os
from requests import Response
from pathlib import Path
from PIserver.clients.net import send_post_request
from PIserver.utils.files import log_error
from PIserver.constants import CHUNK_SIZE

class FileDownloadClient:
    def __init__(self):
        pass
    
    def getModelInfo(self, body):
        res = send_post_request("/type/client/get", body)
        
        if res is None:
            log_error("Cannot get response from server. Please check your internet connection.")
            return None
        if res.status_code != 200:
            log_error(f"Server returned {res.status_code} - {res.text}")
            return None
        
        res = dict(res.json())
        if res["state"] == "SUCCESS":
            return res["model"]
        else:
            log_error(f"{res['state']} - {res['message']}")
            
    def download_file(self, local_path, remote_path):
        headers = {}
        local_file = Path(local_path)
        if local_file.exists():
            downloaded_size = local_file.stat().st_size
            headers["Range"] = f"bytes={downloaded_size}-"
        else:
            downloaded_size = 0

        response = send_post_request("/type/download",params={"path": remote_path}, header=headers, stream=True)
        if response is None:
            log_error("Cannot get response from server. Please check your internet connection.")
            return
        response.raise_for_status()

        content_range = response.headers.get("Content-Range", "")
        if content_range:
            total_size = int(content_range.split("/")[-1])  # 获取"/"后的完整文件大小
        else:
            total_size = int(response.headers.get("Content-Length", 0)) + downloaded_size

        mode = "ab" if downloaded_size > 0 else "wb"
        with open(local_path, mode) as file, tqdm(
            total=total_size, 
            unit='B', 
            unit_scale=True, 
            desc=os.path.basename(local_path),
            initial=downloaded_size  # 设置进度条初始值
        ) as pbar:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                file.write(chunk)
                pbar.update(len(chunk))
        
            
    def iter_folder(self, local_path: Path, files: dict):
        for name, fpath in files.items():
            if isinstance(fpath, str):
                file_path = local_path / Path(name)
                self.download_file(file_path, fpath)
            else:
                subfolder_path = local_path / Path(name)
                subfolder_path.mkdir(parents=True, exist_ok=True)
                self.iter_folder(subfolder_path, fpath)
            
    def download(self, local_path: Path, remote_path):
        try:
            folder_structure = send_post_request("/type/folder", params={"path": remote_path})
            if not folder_structure:
                return
            files = dict(folder_structure.json())
            # print(files)
            local_path.mkdir(parents=True, exist_ok=True)

            self.iter_folder(local_path, files)

            print(f"Model successfully cloned into {str(local_path.absolute())}")
            return True
        except Exception as e:
            log_error(f"Failed to clone file: {e}")
            return False