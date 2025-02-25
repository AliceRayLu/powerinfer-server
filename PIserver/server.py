from fastapi import FastAPI
from uvicorn import Config, Server
import sys
import signal
import os
import subprocess

app = FastAPI()
config = Config(app, host="0.0.0.0", port=8000)
server_process = None

def run():
    global server_process
    server_process = Server(config)
    server_process.run()
    
if __name__ == "__main__":
    run()

def serve():
    global server_process
    # 在Windows中创建后台进程
    if os.name == 'nt':  # Windows系统
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        server_process = subprocess.Popen(
            [sys.executable, __file__],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            startupinfo=startupinfo
        )
        print(f"PowerInfer server is running in background. (PID: {server_process.pid}) Use pwi-stop to stop it.")
    else:  # Unix/Linux系统
        if os.fork() == 0:
            if os.fork() == 0:
                run()
            else:
                os._exit(0)
        else:
            os.wait()
            print(f"PowerInfer server is running in background. (PID: {os.getpid()}) Use pwi-stop to stop it.")

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/kill")
def kill():
    pid = os.getpid()  # 获取当前进程 ID
    os.kill(pid, signal.SIGTERM)  # 发送终止信号
    return {"message": "Server is shutting down..."}