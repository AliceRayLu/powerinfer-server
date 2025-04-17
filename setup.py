from setuptools import setup
from setuptools.command.install import install
from PIserver.constants import *
from PIserver.install import local_compile
from PIserver.utils.files import add_engine, log_error

LOCAL_LIST_HEADER = ['MODEL_NAME', 'SIZE', 'BSIZE', 'VERSION', 'PATH']

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
        
def generating_config_file():
    import json
    DEFAULT_CONFIG_FILE.touch(0o755, exist_ok=True)
    with open(DEFAULT_CONFIG_FILE, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        print(f"Starting to create default storing directory at {DEFAULT_STORAGE_PATH} ...")
        
        DEFAULT_STORAGE_PATH.mkdir(0o755, parents=True, exist_ok=True)
        DEFAULT_MODEL_PATH.mkdir(0o755, parents=True, exist_ok=True)
        # generate_ssh_key() # FIXME: add ssh-key in production; in test don't change
        generate_model_list_file()
        
        DEFAULT_INSTALL_PATH.mkdir(0o755, parents=True, exist_ok=True)
        DEFAULT_ENGINE_LIST_FILE.touch(0o755, exist_ok=True)
        
        # compile and install the engine
        # try:
        #     engine_path = local_compile()
        #     if engine_path is not None:
        #         add_engine(DEFAULT_ENGINE_NAME, engine_path)
        #         DEFAULT_CONFIG["engine"] = DEFAULT_ENGINE_NAME
        # except Exception as e:
        #     log_error(f"Failed to compile the engine: {e}")
        #     print("Skipping engine installation. You can install it later using `powerinfer install` command.")
        
        
        generating_config_file()

setup(
    name='powerinfer-server',
    version='0.1.0',
    author='ARL',
    cmdclass={
        'install': PostInstallCommand,
    }
)