from pathlib import Path
from enum import Enum

POWERINFER_HOST = "127.0.0.1"
POWERINFER_MODEL_HOST = POWERINFER_HOST # TODO: keep the same with backend host for now
POWERINFER_SERVER_PORT = 8000

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

# Engine Choices
WINDOWS_ENGINE_CHOICES = {
    "windows-cpu-x64-843195e": "1mmmmm",
    "windows-cpu-x86": "2",
    "windows-cuda-x64": "3",
    "windows-cuda-x86": "4",

}

LINUX_ENGINE_CHOICES = {

}

MAC_ENGINE_CHOICES = {}

ENGINE_CHOICES = {
    "Windows": WINDOWS_ENGINE_CHOICES,
    "Linux": LINUX_ENGINE_CHOICES,
    "Darwin": MAC_ENGINE_CHOICES
}

DEFAULT_CONFIG = {
    "model_path": str(DEFAULT_MODEL_PATH),
    "engine": "powerinfer-server-windows-cpu-x86-843195e",
    "options": {
        "n-predict": 512,
        "top-k": 40,
        "top-p": 0.9,
        "min-p": 0.05,
        "temp": 0.7,
    },
    "ctx-size": 512,
    "gpu-layers": 32,
}

class REMOVE_RESULT(Enum):
    SUCCESS = 0
    NOT_FOUND = 1
    ERROR = 2