from pathlib import Path

POWERINFER_SERVER_HOST = "0.0.0.0"
POWERINFER_CLIENT_HOST = "127.0.0.1"
POWERINFER_SERVE_PORT = 8000

DEFAULT_STORAGE_PATH = Path.home() / ".powerinfer"
DEFAULT_CONFIG_PATH = Path.home() / ".powerinfer" / "config.json"
DEFAULT_SSH_PEM_KEY_PATH = DEFAULT_STORAGE_PATH / "id_rsa"