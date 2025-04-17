import os
import subprocess
import zipfile
from PIserver.constants import *
import requests

def download_source_code():
    source_url = "https://github.com/SJTU-IPADS/PowerInfer/archive/refs/heads/main.zip"
    tmp_path = DEFAULT_STORAGE_PATH / "main.zip"
    
    try:
        print(f"Downloading source code from {source_url} to {tmp_path}...")
        response = requests.get(source_url, stream=True)
        response.raise_for_status()
        
        with open(tmp_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print("Download completed.")
        with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
            zip_ref.extractall(DEFAULT_STORAGE_PATH)
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading source code: {e}")
        return None
    except zipfile.BadZipFile as e:
        print(f"Error extracting ZIP file: {e}")
        return None
    finally:
        if tmp_path.exists():
            os.remove(tmp_path)
        return DEFAULT_STORAGE_PATH / "PowerInfer-main"


def local_compile() -> str:
    '''
    Download the source code and compile it.
    Return the path of the compiled binary. (server)
    '''
    
    try:
        source_dir = download_source_code()
        if source_dir is None:
            return None

        os.chdir(source_dir)
        try:
            subprocess.run(["cmake", "-S", ".", "-B", "build", "-DLLAMA_CUBLAS=ON"], check=True)
            
            subprocess.run(["cmake", "--build", "build", "--config", "Release"], check=True)
            
            binary_name = "server.exe" if os.name == 'nt' else "server" 
            binary_path = os.path.join(source_dir, "build", "bin", binary_name)
            if os.path.exists(binary_path):
                print(f"Compilation successful. Binary located at: {binary_path}")
                return binary_path
            else:
                print("Compilation failed. Unable to find the binary file.")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"Compilation failed with error - input cmd `{e.cmd}`: {e}")
            print(f"Error output: {e.stderr} - {e.output}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None