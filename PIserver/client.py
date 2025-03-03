import requests
import argparse
from pkg_resources import get_distribution
from PIserver.constants import *
from PIserver.utils import print_table, filter_rows, write_rows, parse_condition, remove_dir

host = "https://" + POWERINFER_HOST + ":" + str(POWERINFER_SERVER_PORT)
        
def get_version():
    return get_distribution("powerinfer-server").version

def list_models(remote, model):
    if remote is not None:
        print("Remote Models:")
    else:
        print("Local Models:")
        rows = filter_rows(lambda x: True if model is None else parse_condition(model))
        print_table(rows, LOCAL_LIST_HEADER)   

def remove_model(remote, model):
    if remote:
        print("Remove remote model:", model)
    else:
        rows, rest = filter_rows(lambda x: True if model is None else parse_condition(model))
        if model is None and len(rows) > 0:
            response = input(f"Are you sure you want to remove all the local models? (y/n)")
            if response != "y":
                return
        
        if model is not None:
            if len(rows) == 0:
                print(f"Unable to find model: {model} locally. Please check your models using `pwi list`.")
                return
            elif len(rows) > 1:
                response = input(f"Found multiple models with name {model}. Do you want to remove all of them? (y/n)")
                if response != 'y':
                    return
        
        for row in rows:
            remove_dir(row[4], row[0]+":"+row[1])
            write_rows(rest)
            print("All the models have been removed.")
        

def run_model(model, config=None, local_dir=None):
    print("Run model:", model)
    print("Config:", config)
    print("Local dir:", local_dir)
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--version",help="show version", action="store_true")
    
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="Show all the local(default) or remote models.")
    list_parser.add_argument("model", nargs='?', default=None, help="The model name to list. (Optional)")
    list_parser.add_argument("-r","--remote", nargs='?', const=True, default=None, help="List the remote models belongs to you.")
    
    run_parser = subparsers.add_parser("run", help="Run a large language model.")
    run_parser.add_argument("model", help="The model name to run.")
    run_parser.add_argument("-cfg","--config", help="The configuration file to use.")
    run_parser.add_argument("-d","--local-dir", help="Run the model stored in local directory.")
    
    clone_parser = subparsers.add_parser("clone", help="Download a model from https://powerinfer.com or update a local model.")
    clone_parser.add_argument("model", help="The model name to clone.")
    clone_parser.add_argument("-r","--resume-download", help="Resume the download if the download is interrupted.", action="store_true")
    clone_parser.add_argument("-l","--local-dir", help="Assign local storage location.")
    
    rm_parser = subparsers.add_parser("remove", help="Remove selected local or remote model.(By default local)")
    rm_parser.add_argument("model", nargs='?', help="The model name to remove. If not set, remove all the models.")
    rm_parser.add_argument("-r","--remote", nargs='?', const=True, default=None, help="Remove the remote model.", action="store_true")
    
    cfg_parser = subparsers.add_parser("config", help="Manage the store location of models.")
    cfg_parser.add_argument("-l","--list", help="Show current default storage location", action="store_true")
    cfg_parser.add_argument("-r","--reset", help="Change the config back into default values.")
    
    upload_parser = subparsers.add_parser("upload", help="Upload a local model to https://powerinfer.com. and get predictors.")
    upload_parser.add_argument("model", help="The remote model repository to upload.")
    upload_parser.add_argument("-d","--local-dir", help="The local model directory to upload.", required=True)
    upload_parser.add_argument("--hf", help="Upload the model to huggingface hub.")
    
    args = parser.parse_args()
    
    if args.version:
        print(f"powerinfer-server version {get_version()}")
        return
    elif args.command == "list":
        list_models(args.remote, args.model)
    elif args.command == "run":
        print("Run model:", args.model)
        print("Config:", args.config)
        print("Local dir:", args.local_dir)
    elif args.command == "remove":
        remove_model(args.remote, args.model)
        
    

if __name__ == "__main__":
    main()    