from PIserver.commands.command import Command
from PIserver.utils.files import *

class Remove_Models(Command):
    def register_subcommand(self, subparser):
        rm_parser = subparser.add_parser("remove", help="Remove selected local or remote model.(By default local) Remove the backend engine package.")
        rm_parser.add_argument("model", nargs='?', help="The model name to remove. If not set, remove all the models.")
        rm_parser.add_argument("-r","--remote", default=None, help="Remove the remote model.", action="store_true")
        rm_parser.add_argument("-i","--install", default=None, help="Remove the selected backend engine package.", action="store_true")
        
    def execute(self, args):
        model = str(args.model)
        if args.install is not None:
            if args.remote is not None:
                log_error("Cannot use -i and -r together. Please use it seperately to remove backend engine and models.")
                return
            if model is None:
                log_error("Please specify the engine name to remove.")
                return
            engines = read_file(DEFAULT_ENGINE_LIST_FILE)
            if model not in engines:
                log_error(f"Engine {model} not found. Please check the name or use `powerinfer list -i` to see all the available engines.")
                return
            print(f"Removing engine {model}...")
            res = remove_file(engines[model])
            if res == REMOVE_RESULT.ERROR:
                log_error(f"Unable to remove engine {model}. Remove it manually or try after fixing the error.")
                return
            if res == REMOVE_RESULT.NOT_FOUND:
                log_error(f"Unable to find the engine file {model}.")
            # delete record from config file
            del engines[model]
            write_file(DEFAULT_ENGINE_LIST_FILE, engines)
            
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
                    log_error(f"Unable to find model: {model} locally. Please check your models using `pwi list`.")
                    return
                elif len(rows) > 1:
                    response = input(f"Found multiple models with name {model}. Do you want to remove all of them? (y/n)")
                    if response != 'y':
                        return
            
            for row in rows:
                res = remove_dir(row[4])
                if res != REMOVE_RESULT.SUCCESS:
                    log_error(f"Unable to remove model {row[0]}:{row[1]}.")
                    return
                write_rows(rest)
                print("Model successfully removed.")
        
        