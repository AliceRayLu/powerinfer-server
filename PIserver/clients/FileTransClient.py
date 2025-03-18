from PIserver.constants import POWERINFER_MODEL_HOST, CHUNK_SIZE, POWERINFER_SERVER_PORT
from pathlib import Path
import requests
from tqdm import tqdm

class FileTransClient():
    def __init__(self):
        self.host = POWERINFER_MODEL_HOST
        self.port = POWERINFER_SERVER_PORT

    def upload_file(self, path: Path):
        file_size = path.stat().st_size
        uploaded_size = 0
        
        url = "http://"+self.host+":"+str(self.port)+'/type/upload'
        
        # 检查已上传的字节数（用于断点续传）
        response = requests.head(url, params={"name": path.name})
        if 'Content-Range' in response.headers:
            uploaded_size = int(response.headers['Content-Range'].split('/')[1])
        
        # 使用tqdm创建进度条
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=path.name, initial=uploaded_size) as pbar:
            with open(path, 'rb') as f:
                f.seek(uploaded_size)  # 跳转到已上传的位置
                while uploaded_size < file_size:
                    # 读取文件块
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    # 设置Content-Range头
                    headers = {
                        'Content-Range': f'bytes {uploaded_size}-{uploaded_size + len(chunk) - 1}/{file_size}'
                    }
                    
                    # 发送PATCH请求上传文件块
                    response = requests.patch(url, headers=headers, params={"name": path.name}, data=chunk)
                    
                    if response.status_code == 200 or response.status_code == 206:
                        # 更新已上传大小
                        uploaded_size += len(chunk)
                        # 更新进度条
                        pbar.update(len(chunk))
                    else:
                        print(f"上传失败: {response.text}")
                        break
                    
    def upload(self, file_path):
        path = Path(file_path)
        
        if path.is_file():
            self.upload_file(path)
        elif path.is_dir():
            for file in path.iterdir():
                if file.is_file():
                    self.upload_file(file)