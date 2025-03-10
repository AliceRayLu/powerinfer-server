from PIserver.commands.command import Command
from PIserver.utils.csv import *

class Remove_Models(Command):
    def register_subcommand(self, subparser):
        rm_parser = subparser.add_parser("remove", help="Remove selected local or remote model.(By default local)")
        rm_parser.add_argument("model", nargs='?', help="The model name to remove. If not set, remove all the models.")
        rm_parser.add_argument("-r","--remote", default=None, help="Remove the remote model.", action="store_true")
        rm_parser.add_argument("-i","--install", default=None, help="Remove the selected backend engine package.")
        
    def execute(self, args):
        model = args.model
        if args.remote:
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
                print("Model successfully removed.")
        
        