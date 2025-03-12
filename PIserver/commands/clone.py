from PIserver.commands.command import Command
from PIserver.utils.files import *
from PIserver.constants import *
from PIserver.utils.SSHClient import SSHClient

class Clone_Model(Command):
    def register_subcommand(self, subparser):
        clone_parser = subparser.add_parser("clone", help="Download a model from https://powerinfer.com or update a local model.")
        clone_parser.add_argument("model", help="The model name to clone.")
        clone_parser.add_argument("-d","--local-dir", help="Clone the model into assigned local directory.")
        clone_parser.add_argument("-hf", help="Clone a runnable gguf model from huggingface.")
        
    def execute(self, args):
        mname = args.model
        check = check_model_name_with_size(mname)
        uname = get_uname_from_model(mname)
        if not check:
            return
        # check remote access
        
        # check in the list about version and path
        rows, rest = filter_rows(parse_condition(mname))
        # check remote model version(metadata)

        if len(rows) > 0:
            # compare remote model version 
            # if same no download
            print()
        # connect and download
        client = SSHClient(POWERINFER_MODEL_HOST,22,"a.r.l", DEFAULT_SSH_PEM_KEY_PATH)
        client.connect()
        # add to local model list