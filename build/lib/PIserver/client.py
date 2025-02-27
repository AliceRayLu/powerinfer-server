import requests
import argparse
from pkg_resources import get_distribution

host = "http://localhost:8000"

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