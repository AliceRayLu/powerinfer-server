import paramiko
import pathlib

class SSHClient:
    def __init__(self, host: str, port: int, uid: str, private_key_path: pathlib.Path):
        self.host = host
        self.port = port
        self.uid = uid
        self.private_key = paramiko.RSAKey.from_private_key_file(private_key_path, password="")
        
    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.host, self.port, self.uid, pkey=self.private_key,password="")
        
    def download(self, remote_path, local_path):
        with self.client.open_sftp() as sftp:
            sftp.get(remote_path, local_path)
    
    def upload(self, local_path, remote_path):
        with self.client.open_sftp() as sftp:
            sftp.put(local_path, remote_path)
    
    def close(self):
        self.client.close()