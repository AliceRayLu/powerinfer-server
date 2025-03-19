from PIserver.clients.FileDownloadClient import FileDownloadClient
from PIserver.commands.command import Command
from PIserver.utils.files import *
from PIserver.constants import *
from pathlib import Path

class Clone_Model(Command):
    def register_subcommand(self, subparser):
        clone_parser = subparser.add_parser("clone", help="Download a model from https://powerinfer.com or update a local model.")
        clone_parser.add_argument("model", help="The model name to clone.")
        clone_parser.add_argument("-d","--local-dir", help="Clone the model into assigned local directory.")
        clone_parser.add_argument("-hf", help="Clone a runnable gguf model from huggingface.")
        
    def execute(self, args):
        mname = args.model
        mname, tname = check_model_name_with_size(mname)
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
            # check in the list about version and path
            rows, rest = filter_rows(parse_condition(args.model))
            # check remote model version(metadata)
            if len(rows) > 0:
                if info["version"] == rows[0][3]:
                    print("The model is up to date. No need to download.")
                    return
                else: # delete old version
                    print("Removing the older version of model...")
                    remove_dir(rows[0][4])
                    write_rows(rest)  
            # download
            # parse local path to store
            local_path = Path(args.local_dir) if args.local_dir is not None else Path(DEFAULT_MODEL_PATH) / Path(mname)
            if args.local_dir is None:
                config = read_file(DEFAULT_CONFIG_FILE)
                local_path = Path(config["model_path"]) / Path(mname)
            
            # add to local model list    
            if client.download(local_path, remote_path):
                add_row([mname, tname, info["size"], info["version"], str(local_path)])
        except KeyboardInterrupt:
            print("Download stopped.")
            return