from setuptools import setup
from setuptools.command.install import install
import pathlib

DEFAULT_STORAGE_PATH = pathlib.Path.home() / ".powerinfer"
DEFAULT_CONFIG_PATH = DEFAULT_STORAGE_PATH / "config.json"
DEFAULT_SYSTEM_PROMPT_FILE = DEFAULT_STORAGE_PATH / "system_prompt.json"
DEFAULT_MODEL_PATH = DEFAULT_STORAGE_PATH / "models"
DEFAULT_SSH_PUB_KEY_PATH = DEFAULT_STORAGE_PATH / "id_rsa.pub"
DEFAULT_SSH_PEM_KEY_PATH = DEFAULT_STORAGE_PATH / "id_rsa"
DEFAULT_MODEL_LIST_FILE = DEFAULT_MODEL_PATH / "models.csv"
DEFAULT_INSTALL_PATH = DEFAULT_STORAGE_PATH / "engines"
DEFAULT_ENGINE_LIST_FILE = DEFAULT_INSTALL_PATH / "list.json"

LOCAL_LIST_HEADER = ['MODEL_NAME', 'SIZE', 'BSIZE', 'VERSION', 'PATH']
DEFAULT_SYSTEM_PROMPT = {
    "system_prompt": {
        "prompt": "You are a helpful, kind, honest, good at writing assistant. Please help answer the following questions as best as you can.",
        "anti_prompt": "User:",
        "assistant_name": "Assistant:"
    }
}

def generate_ssh_key():
    import paramiko
    key = paramiko.RSAKey.generate(2048)
    key.write_private_key_file(DEFAULT_SSH_PEM_KEY_PATH)
    pub = key.get_base64()
    with open(DEFAULT_SSH_PUB_KEY_PATH, 'w') as f:
        f.write("ssh-rsa "+pub)

def generate_model_list_file():
    import csv
    DEFAULT_MODEL_LIST_FILE.touch(0o755, exist_ok=True)
    with open(DEFAULT_MODEL_LIST_FILE, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(LOCAL_LIST_HEADER)
        
def generate_system_prompt_file():
    import json
    DEFAULT_SYSTEM_PROMPT_FILE.touch(0o755, exist_ok=True)   
    with open(DEFAULT_SYSTEM_PROMPT_FILE, 'w') as f:
        json.dump(DEFAULT_SYSTEM_PROMPT, f, indent=4)

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        print(f"Starting to create default storing directory at {DEFAULT_STORAGE_PATH} ...")
        
        DEFAULT_STORAGE_PATH.mkdir(0o755, parents=True, exist_ok=True)
        DEFAULT_MODEL_PATH.mkdir(0o755, parents=True, exist_ok=True)
        generate_ssh_key()
        generate_model_list_file()
        DEFAULT_CONFIG_PATH.touch(0o755, exist_ok=True)
        DEFAULT_INSTALL_PATH.mkdir(0o755, parents=True, exist_ok=True)
        DEFAULT_ENGINE_LIST_FILE.touch(0o755, exist_ok=True)
        generate_system_prompt_file()


setup(
    name='powerinfer-server',
    version='0.1.0',
    author='ARL',
    cmdclass={
        'install': PostInstallCommand,
    }
)