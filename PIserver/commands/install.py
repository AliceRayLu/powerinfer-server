from PIserver.commands.command import Command
from PIserver.install import local_compile
from PIserver.utils.install import *
from PIserver.constants import DEFAULT_ENGINE_NAME
from PIserver.utils.files import *

class Install_Backend(Command):
    def register_subcommand(self, subparser):
        install_parser = subparser.add_parser("install", help="Install the backend engine.")
        install_parser.add_argument("engine", nargs='?', default=None, help="The backend engine name to install.")
        install_parser.add_argument("-f","--file", help="The local runnable file compiled by yourself from powerinfer.")
        install_parser.add_argument("-c","--compile", help="Download the source code and compile it automatically. Require c compilers and cmake installed.")
        
    def execute(self, args):
        if args.file is not None and args.engine is None:
            log_error("Please specify the engine name in order to use.")
            return
        if args.compile is not None:
            engine_path = local_compile()
            if engine_path is None:
                log_error("Unable to compile the engine. Please check the source code and cmake and try again.")
                log_error("If you have already manually compiled the engine, please use -f to install it.")
                return
            res = add_engine(
                args.engine if args.engine is not None else DEFAULT_ENGINE_NAME,
                engine_path
            )
            if not res:
                return
            
            print("Modifying default config file: change engine to default-cuda...")
            config = read_file(DEFAULT_CONFIG_FILE)
            config["engine"] = DEFAULT_ENGINE_NAME
            write_file(DEFAULT_CONFIG_FILE, config)
            print("Successfully installed the engine and modified the default config file.")
            
        if args.engine is not None:
            if args.file is None:
                if args.engine not in list(get_engine_choices().keys()):
                    log_error(f"Engine {args.engine} not found. Please check the name or use `powerinfer list -i` to see all the available engines or install engine compiled by yourself using -f.")
                else:
                    remote_path = get_engine_path(args.engine)
                    res = add_engine(args.engine, single_install(remote_path))
                    if not res:
                        return         
            else:
                # install from file
                res = add_engine(args.engine, args.file)
                if not res:
                    return
        else:
            interactive_install()
        print("Engine successfully installed.")
        
    