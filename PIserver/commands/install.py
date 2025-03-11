from PIserver.commands.command import Command
from PIserver.powerinfer.install import *
from PIserver.constants import DEFAULT_ENGINE_LIST_FILE
from PIserver.utils.files import read_file, write_file
import sys
from pathlib import Path

class Install_Backend(Command):
    def register_subcommand(self, subparser):
        install_parser = subparser.add_parser("install", help="Install the backend engine.")
        install_parser.add_argument("engine", nargs='?', default=None, help="The backend engine name to install.")
        install_parser.add_argument("-f","--file", help="The local runnable file compiled by yourself from powerinfer.")
        
    def execute(self, args):
        if args.file is not None and args.engine is None:
            sys.stderr.write("Error: Please specify the engine name in order to use.")
            return
        if args.engine is not None:
            if args.file is None:
                if args.engine not in list(get_engine_choices().keys()):
                    sys.stderr.write(f"Engine {args.engine} not found. Please check the name or use `powerinfer list` to see all the available engines or install engine compiled by yourself using -f.")
                else:
                    remote_path = get_engine_path(args.engine)
                    self.add_engine(args.engine, single_install(remote_path))         
            else:
                # install from file
                self.add_engine(args.engine, args.file)
            return
        interactive_install()
        print("Engine successfully installed.")
        
    def add_engine(self, name, path):
        engines = read_file(DEFAULT_ENGINE_LIST_FILE)
        if name in engines:
            response = input(f"Engine {name} already exists. Do you want to overwrite it? (y/n)")
            if response != "y":
                print("Installation cancelled.")
                return
            old_path = Path(engines[name])
            if engines[name] != path and old_path.exists():
                print(f"Removing old engine file {old_path}...")
                try:
                    Path(old_path).unlink()
                except PermissionError:
                    sys.stderr.write(f"Error: Permission denied. Unable to remove {old_path}.")
                    return
        engines[name] = path
        write_file(DEFAULT_ENGINE_LIST_FILE, engines)