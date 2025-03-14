from PIserver.commands.command import Command
from PIserver.utils.install import *
from PIserver.constants import DEFAULT_ENGINE_LIST_FILE
from PIserver.utils.files import *

class Install_Backend(Command):
    def register_subcommand(self, subparser):
        install_parser = subparser.add_parser("install", help="Install the backend engine.")
        install_parser.add_argument("engine", nargs='?', default=None, help="The backend engine name to install.")
        install_parser.add_argument("-f","--file", help="The local runnable file compiled by yourself from powerinfer.")
        
    def execute(self, args):
        if args.file is not None and args.engine is None:
            log_error("Please specify the engine name in order to use.")
            return
        if args.engine is not None:
            if args.file is None:
                if args.engine not in list(get_engine_choices().keys()):
                    log_error(f"Engine {args.engine} not found. Please check the name or use `powerinfer list -i` to see all the available engines or install engine compiled by yourself using -f.")
                else:
                    remote_path = get_engine_path(args.engine)
                    res = self.add_engine(args.engine, single_install(remote_path))
                    if not res:
                        return         
            else:
                # install from file
                res = self.add_engine(args.engine, args.file)
                if not res:
                    return
        else:
            interactive_install()
        print("Engine successfully installed.")
        
    def add_engine(self, name, path):
        if not check_existence(path):
            log_error(f"File {path} does not exist. Please check the path and try again.")
            return False
        path = str(get_absolute_path(path))
        engines = read_file(DEFAULT_ENGINE_LIST_FILE)
        if name in engines:
            response = input(f"Engine {name} already exists. Do you want to overwrite it? (y/n)")
            if response != "y":
                print("Installation cancelled.")
                return False
            if engines[name] != path and check_existence(engines[name]):
                print(f"Removing old engine file {engines[name]}...")
                res = remove_file(engines[name])
                if res == REMOVE_RESULT.ERROR:
                    log_error(f"Unable to remove old engine file {engines[name]}. Remove it manually or try after fixing the error.")
                    return False
        engines[name] = path
        write_file(DEFAULT_ENGINE_LIST_FILE, engines)
        return True