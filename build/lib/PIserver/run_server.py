import subprocess
import sys

def run():
    process = subprocess.Popen(
        [sys.executable, "PIserver/server.py"]
    )
    print(f"PowerInfer server is running. (PID: {process.pid})")
    return

if __name__ == "__main__":
    run()