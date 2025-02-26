from fastapi import FastAPI
from uvicorn import Config, Server
from contextlib import asynccontextmanager
import sys
import signal
import os
import subprocess
import asyncio
import socket
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Server successfully started. (PID: {os.getpid()}) Running at backgroud.")
    yield
    print("Server Message: Server successfully stopped.")

logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
app = FastAPI(lifespan=lifespan)
config = Config(app, host="0.0.0.0", port=8000)

def run():
    server_process = Server(config)
    server_process.run()

def serve():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('0.0.0.0', 8000))
    except socket.error as e:
        print(f"Server is already running or port 8000 is already in use.")
        return
    finally:
        sock.close()

    print("Starting server...")

    if os.name == 'nt':  # Windows
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            subprocess.Popen(
                [sys.executable, __file__, "--run"],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                startupinfo=startupinfo
            )
        except Exception as e:
            print(f"Error: {str(e)} failed to start server.") 
        
    else:  # Linux/Mac
        if os.fork() == 0:
            if os.fork() == 0:
                run()
            else:
                os._exit(0)
        else:
            os.wait()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/kill")
async def kill():
    print("Stopping server...")
    try:
        await asyncio.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)
    except Exception as e:
        return print(f"Error: {str(e)} failed to stop server.")

if __name__ == "__main__":
    run()