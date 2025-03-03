import requests
import argparse
from pkg_resources import get_distribution
from PIserver.constants import *

host = "https://" + POWERINFER_CLIENT_HOST + ":" + str(POWERINFER_SERVE_PORT)

def hello():
    get_simple_message(f"{host}/")

def stop():
    get_simple_message(f"{host}/kill")
        
def get_simple_message(host):
    try:
        response = requests.get(f"{host}")
        print(response.json().get("message"))
    except:
        print("Server already stopped. Use `pwi-serve` to start server.")
        
def get_version():
    return get_distribution("powerinfer-server").version

def list_models(local=True):
    if local is None or local:
        print("Local models:")
    else:
        print("Remote models:")

def run_model(model, config=None, local_dir=None):
    print("Run model:", model)
    print("Config:", config)
    print("Local dir:", local_dir)
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--version",help="show version", action="store_true")
    
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="Show all the local or remote models.")
    list_parser.add_argument("-l","--local", default=None, help="List all the local models.", action="store_true")
    list_parser.add_argument("-r","--remote", default=None, help="List all the remote models.", action="store_true")
    
    run_parser = subparsers.add_parser("run", help="Run a large language model.")
    run_parser.add_argument("model", help="The model name to run.")
    run_parser.add_argument("-cfg","--config", help="The configuration file to use.")
    run_parser.add_argument("-d","--local-dir", help="Run the model stored in local directory.")
    
    clone_parser = subparsers.add_parser("clone", help="Download a model from https://powerinfer.com or update a local model.")
    clone_parser.add_argument("model", help="The model name to clone.")
    clone_parser.add_argument("-r","--resume-download", help="Resume the download if the download is interrupted.", action="store_true")
    clone_parser.add_argument("-l","--local-dir", help="Assign local storage location.")
    
    rm_parser = subparsers.add_parser("remove", help="Remove selected local or remote model.(By default local)")
    rm_parser.add_argument("model", help="The model name to remove.")
    rm_parser.add_argument("-l","--local", default=None, help="Remove the local model.", action="store_true")
    rm_parser.add_argument("-r","--remote", default=None, help="Remove the remote model.", action="store_true")
    
    cfg_parser = subparsers.add_parser("config", help="Manage the store location of models.")
    cfg_parser.add_argument("-l","--list", help="Show current default storage location", action="store_true")
    cfg_parser.add_argument("-c","--change", help="Change model storage location.Old models will not be moved.")
    
    upload_parser = subparsers.add_parser("upload", help="Upload a local model to https://powerinfer.com. and get predictors.")
    upload_parser.add_argument("model", help="The remote model repository to upload.")
    upload_parser.add_argument("-d","--local-dir", help="The local model directory to upload.", required=True)
    upload_parser.add_argument("--hf", help="Upload the model to huggingface hub.")
    
    args = parser.parse_args()
    
    if args.version:
        print(f"powerinfer-server version {get_version()}")
        return
    elif args.command == "list":
        list_models(args.local)
    elif args.command == "run":
        print("Run model:", args.model)
        print("Config:", args.config)
        print("Local dir:", args.local_dir)

if __name__ == "__main__":
    main()    