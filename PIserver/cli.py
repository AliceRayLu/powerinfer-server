import argparse
from pkg_resources import get_distribution
from PIserver.constants import *
from PIserver.commands import *

        
def get_version():
    return get_distribution("powerinfer-server").version 

command_map = {
    "list": List_Models(),
    "remove": Remove_Models(),
    "clone": Clone_Model(),
    "config": Config(),
    "upload": Upload_Model(),
    "run": Run_Model(),
}
    
def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--version",help="show version", action="store_true")
    
    subparsers = parser.add_subparsers(dest="command")
    
    for cmd in command_map:
        command_map[cmd].register_subcommand(subparsers) 
    
    return parser
        
def main():
    parser = create_parser()
    args = parser.parse_args()
    
    if args.version:
        print(f"powerinfer-server version {get_version()}")
        return

    if args.command is None or args.command not in command_map:
        parser.print_help()
        return
    
    command_map[args.command].execute(args)
    

if __name__ == "__main__":
    main()    