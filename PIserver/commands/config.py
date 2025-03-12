from PIserver.commands.command import Command
from PIserver.constants import DEFAULT_CONFIG, DEFAULT_CONFIG_FILE
from PIserver.utils.files import read_file, write_file, log_error

class Config(Command):
    def register_subcommand(self, subparser):
        cfg_parser = subparser.add_parser("config", help="Manage the store location of models.")
        cfg_parser.add_argument("-l","--list", default=None, help="Show current configurations", action="store_true")
        cfg_parser.add_argument("-r","--reset", default=None, help="Change the config back into default values.", action="store_true")
        cfg_parser.add_argument("-s","--set", default=None, help="Set the config in the format option=value.")
        cfg_parser.add_argument("-rmv", "--remove", default=None, help="Remove a config option.")
    
    def execute(self, args):
        if args.list is not None:
            config = read_file(DEFAULT_CONFIG_FILE)
            print("Current configurations:")
            for key in config:
                print(f"{key}={config[key]}")
        elif args.reset is not None:
            config = DEFAULT_CONFIG
            write_file(DEFAULT_CONFIG_FILE, config)
            print("Config reset to default.")
        elif args.set is not None:
            config = read_file(DEFAULT_CONFIG_FILE)
            if '=' not in str(args.set):
                log_error("Invalid format. Please use option=value.")
                return
            [option, value] = str(args.set).split('=')
            config[option] = value
            write_file(DEFAULT_CONFIG_FILE, config)
            print(f"Config set: {option}={value}")
        elif args.remove is not None:
            config = read_file(DEFAULT_CONFIG_FILE)
            option = str(args.remove)
            if option in config:
                del config[option]
                print(f"Option {option} successfully removed.")
