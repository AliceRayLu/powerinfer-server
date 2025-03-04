from PIserver.commands.command import Command
from PIserver.utils.csv import *


class Clone_Model(Command):
    def register_subcommand(self, subparser):
        clone_parser = subparser.add_parser("clone", help="Download a model from https://powerinfer.com or update a local model.")
        clone_parser.add_argument("model", help="The model name to clone.")
        clone_parser.add_argument("-l","--local-dir", help="Assign local storage location.")
        
    def execute(self, args):
        mname = args.model
        if ':' not in mname:
            print("Please specify the model size to clone. Format the model name like 'NAME:SIZE'.")
            return
        # check in the list about version and path
        rows, rest = filter_rows(parse_condition(mname))
        # check remote model version(metadata)
        # before fetch, check access to the remote model
        if len(rows) > 0:
            # compare remote model version 
            # if same no download
            print()
        # connect and download
        # add to local model list