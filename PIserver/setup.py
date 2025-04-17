from PIserver.constants import *

LOCAL_LIST_HEADER = ['MODEL_NAME', 'SIZE', 'BSIZE', 'VERSION', 'PATH']

def generate_ssh_key():
    try:
        import paramiko
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(DEFAULT_SSH_PEM_KEY_PATH)
        pub = key.get_base64()
        with open(DEFAULT_SSH_PUB_KEY_PATH, 'w') as f:
            f.write("ssh-rsa "+pub)
    except ImportError:
        print("paramiko is not installed. Skipping SSH key generation.")

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

def set_up():
    DEFAULT_STORAGE_PATH.mkdir(0o755, parents=True, exist_ok=True)
    DEFAULT_MODEL_PATH.mkdir(0o755, parents=True, exist_ok=True)
    generate_ssh_key() # FIXME: add ssh-key in production; in test don't change
    generate_model_list_file()
    
    DEFAULT_INSTALL_PATH.mkdir(0o755, parents=True, exist_ok=True)
    DEFAULT_ENGINE_LIST_FILE.touch(0o755, exist_ok=True)
    
    generating_config_file()