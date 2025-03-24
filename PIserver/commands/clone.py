from PIserver.clients.FileDownloadClient import FileDownloadClient
from PIserver.commands.command import Command
from PIserver.utils.files import *
from PIserver.constants import *
from pathlib import Path
from huggingface_hub import snapshot_download, HfApi
from tqdm import tqdm

class Clone_Model(Command):
    def register_subcommand(self, subparser):
        clone_parser = subparser.add_parser("clone", help="Download a model from https://powerinfer.com or update a local model.")
        clone_parser.add_argument("model", help="The model name to clone.")
        clone_parser.add_argument("local_dir", nargs='?', help="Clone the model into assigned local directory.")
        clone_parser.add_argument("-hf", help="Clone a runnable gguf model from huggingface.")
        
    def execute(self, args):
        mname = args.model
        mname, tname = check_model_name_with_size(mname)
        
        # parse local path to store
        local_dir_name = str(args.model).replace(":", "-").replace("/", "-")
        local_path = Path(args.local_dir) if args.local_dir is not None else Path(DEFAULT_MODEL_PATH) / Path(local_dir_name)
        if args.local_dir is None:
            config = read_file(DEFAULT_CONFIG_FILE)
            local_path = Path(config["model_path"]) / Path(local_dir_name)
        local_path.mkdir(parents=True, exist_ok=True)
            
        if args.hf is not None:
            print("Cloning from huggingface...")
            try:
                api = HfApi()
                commits = api.list_repo_commits(args.hf)
                model_version = commits[0].commit_id[:8] if commits else "unknown"
                
                need_download = self.check_model(args.model, model_version)
                
                snapshot_download(
                    args.hf, 
                    local_dir=local_path, 
                    tqdm_class=tqdm
                )
                
                total_size = get_folder_size(local_path)
                add_row([mname, tname, total_size, model_version, str(local_path)])
                print(f"Successfully cloned model {args.model} into {str(local_path)}.")
            except KeyboardInterrupt:
                print("Download stopped.")
            return
        
        mname, uname = get_uname_from_model(mname)
        print(f"Trying to clone model {mname} size {tname}...")
        if tname == "":
            return
        # check remote access
        getModelRequest = {
            "mname": mname,
            "tname": tname
        }
        if uname != "":
            getModelRequest["uname"] = uname
            
        try:
            client = FileDownloadClient()
            info = client.getModelInfo(getModelRequest)
            if info is None:
                return
            remote_path = info["dir"]
            need_download = self.check_model(args.model, info["version"])
            if not need_download:
                return
            # download & add to local model list    
            if client.download(local_path, remote_path):
                add_row([mname, tname, info["size"], info["version"], str(local_path)])
        except KeyboardInterrupt:
            print("Download stopped.")
            return
        
    def check_model(self, mname, version) -> bool:
        # check in the list about version and path
        rows, rest = filter_rows(parse_condition(mname))
        # check remote model version(metadata)
        if len(rows) > 0:
            if version == rows[0][3]:
                print("The model is up to date. No need to download.")
                return False
            else: # delete old version
                print("Removing the older version of model...")
                remove_dir(rows[0][4])
                write_rows(rest)
        return True