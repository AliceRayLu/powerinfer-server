import json
from tqdm import tqdm
import os
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

        try:
            response = send_post_request("/type/download",params={"path": remote_path}, header=headers, stream=True)
            if response is None:
                log_error("Cannot get response from server. Please check your internet connection.")
                return False
            if response.status_code == 404:
                log_error(f"File not found: {remote_path}")
                return False
            response.raise_for_status()

            content_range = response.headers.get("Content-Range", "")
            if content_range:
                total_size = int(content_range.split("/")[-1])
            else:
                total_size = int(response.headers.get("Content-Length", 0)) + downloaded_size

            mode = "ab" if downloaded_size > 0 else "wb"
            with open(local_path, mode) as file, tqdm(
                total=total_size, 
                unit='B', 
                unit_scale=True, 
                desc=os.path.basename(local_path),
                initial=downloaded_size
            ) as pbar:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    file.write(chunk)
                    pbar.update(len(chunk))
            return True
        except Exception as e:
            log_error(f"Failed to download file {remote_path}: {e}")
            return False

    def iter_folder(self, local_path: Path, files: dict):
        for name, fpath in files.items():
            if isinstance(fpath, str):
                file_path = local_path / Path(name)
                if not self.download_file(file_path, fpath):
                    continue  # Skip to next file if download fails
            else:
                subfolder_path = local_path / Path(name)
                subfolder_path.mkdir(parents=True, exist_ok=True)
                self.iter_folder(subfolder_path, fpath)
            
    def download(self, local_path: Path, structure: str):
        try:
            files = dict(json.loads(structure))
            # print("parsing files=======>",files) 
            local_path.mkdir(parents=True, exist_ok=True)

            self.iter_folder(local_path, files)

            print(f"Model successfully cloned into {str(local_path.absolute())}")
            return True
        except Exception as e:
            log_error(f"Failed to clone file: {e}")
            return False