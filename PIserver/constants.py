from pathlib import Path
from enum import Enum

POWERINFER_HOST = "192.168.1.82"
POWERINFER_MODEL_HOST = POWERINFER_HOST # TODO: keep the same with backend host for now
POWERINFER_LOCAL_MODEL_HOST = "http://127.0.0.1:8080/completion"
POWERINFER_SERVER_PORT = 8088
backend_host = "http://" + POWERINFER_HOST + ":" + str(POWERINFER_SERVER_PORT)

DEFAULT_STORAGE_PATH = Path.home() / ".powerinfer"
DEFAULT_CONFIG_FILE = Path.home() / ".powerinfer" / "config.json"
DEFAULT_SSH_PEM_KEY_PATH = DEFAULT_STORAGE_PATH / "id_rsa"
DEFAULT_SSH_PUB_KEY_PATH = DEFAULT_STORAGE_PATH / "id_rsa.pub"
DEFAULT_MODEL_PATH = DEFAULT_STORAGE_PATH / "models"
DEFAULT_MODEL_LIST_FILE = DEFAULT_MODEL_PATH / "models.csv"
DEFAULT_INSTALL_PATH = DEFAULT_STORAGE_PATH / "engines"
DEFAULT_ENGINE_LIST_FILE = DEFAULT_INSTALL_PATH / "list.json"
TEST_SSH_PATH = Path.home() / ".ssh" / "id_rsa"

LOCAL_LIST_HEADER = ['MODEL_NAME', 'SIZE', 'BSIZE', 'VERSION', 'PATH']
REMOTE_LIST_HEADER = ['MODEL_NAME', 'ARCH', 'DOWNLOADS', 'LAST_UPDATED']
REMOTE_MODEL_TYPE_HEADER = ['SIZE', 'BSIZE', 'VERSION']

CHUNK_SIZE = 1024 * 1024 * 10  # 10MB per chunk

# Engine Choices
WINDOWS_ENGINE_CHOICES = {
    "windows-cpu-x64-843195e": "",
    "windows-cpu-x86": "",
    "windows-cuda-x64": "",
    "windows-cuda-x86": "",

}

LINUX_ENGINE_CHOICES = {

}

MAC_ENGINE_CHOICES = {}

ENGINE_CHOICES = {
    "Windows": WINDOWS_ENGINE_CHOICES,
    "Linux": LINUX_ENGINE_CHOICES,
    "Darwin": MAC_ENGINE_CHOICES
}

DEFAULT_ENGINE_NAME = "default-cuda"

DEFAULT_CONFIG = {
    "model_path": str(DEFAULT_MODEL_PATH),
    # "engine": str(DEFAULT_STORAGE_PATH / "PowerInfer" / "build" / "bin" / "server"),
    "options": {
        "n_predict": 512,
        "top_k": 40,
        "top_p": 0.9,
        "min_p": 0.05,
        "temp": 0.7,
        "stop": ["\nUser: "]
    },
    "ctx-size": 512,
    "gpu-layers": 32,
    "system-prompt": "Transcript of a never ending dialog, where the User interacts with an Assistant.\nThe Assistant is helpful, kind, honest, good at writing, and never fails to answer the User's requests immediately and with precision.\nUser: Hi, Who are you?\n Assistant: I'm a helpful AI assistant. How can I help you today?\n",
}

class REMOVE_RESULT(Enum):
    SUCCESS = 0
    NOT_FOUND = 1
    ERROR = 2
    
class LLMState(Enum):
    RUNNING = 0
    STOPPED = 1
    ERROR = 2