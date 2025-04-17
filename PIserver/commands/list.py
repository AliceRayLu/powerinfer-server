from PIserver.commands.command import Command
from PIserver.constants import *
from PIserver.setup import set_up
from PIserver.utils.files import *


class List_Models(Command):
    def register_subcommand(self, subparser):
        list_parser = subparser.add_parser("list", help="Show local(default) or remote models. Show backend engines.")
        list_parser.add_argument("model", nargs='?', default=None, help="The model name to list. (Optional)")
        list_parser.add_argument("-i","--install", default=None, help="List all the backend engine packages.", action="store_true")
        
    def execute(self, args):
        if not Path(DEFAULT_STORAGE_PATH).exists():
            set_up()
        mname = args.model
        if args.install is not None:
            if args.model is not None:
                log_error("Cannot use -i and model together. Please use it seperately to list backend engines and models.")
                return
            print("Backend Engines:")
            engines = read_file(DEFAULT_ENGINE_LIST_FILE)
            print_table([[k, v] for k, v in engines.items()], ["ENGINE NAME", "ENGINE PATH"])
            return
        else:
            print("Local Models:")
            rows, rest = filter_rows(lambda x: x[0] != LOCAL_LIST_HEADER[0] if mname is None else parse_condition(mname))
            print_table(rows, LOCAL_LIST_HEADER)
