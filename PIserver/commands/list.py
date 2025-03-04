from PIserver.commands.command import Command
from PIserver.constants import *
from PIserver.utils.csv import *


class List_Models(Command):
    def register_subcommand(self, subparser):
        list_parser = subparser.add_parser("list", help="Show all the local(default) or remote models.")
        list_parser.add_argument("model", nargs='?', default=None, help="The model name to list. (Optional)")
        list_parser.add_argument("-r","--remote", default=None, help="List the remote models belongs to you.", action="store_true")
        
    def execute(self, args):
        mname = args.model
        if args.remote is not None:
            print("Remote Models:")
        else:
            print("Local Models:")
            rows, rest = filter_rows(lambda x: x[0] != LOCAL_LIST_HEADER[0] if mname is None else parse_condition(mname))
            print_table(rows, LOCAL_LIST_HEADER)
