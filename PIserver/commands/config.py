from PIserver.commands.command import Command
from PIserver.constants import DEFAULT_CONFIG, DEFAULT_CONFIG_FILE
from PIserver.utils.files import read_file, write_file, log_error

class Config(Command):
    def register_subcommand(self, subparser):
        cfg_parser = subparser.add_parser("config", help="Manage the store location of models.")
        group = cfg_parser.add_mutually_exclusive_group()
        group.add_argument("-l","--list", default=None, help="Show current configurations", action="store_true")
        group.add_argument("-r","--reset", default=None, help="Change the config back into default values.", action="store_true")
        group.add_argument("-s","--set", default=None, help="Set the config in the format option=value.")
        group.add_argument("-rm", "--remove", default=None, help="Remove a config option.")
        group.add_argument("-cp", "--copy", default=None, help="Copy a config file into a new location.")
    
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
            else:
                log_error(f"Option {option} not found.")
        elif args.copy is not None:
            config = read_file(DEFAULT_CONFIG_FILE)
            new_path = str(args.copy)
            success = write_file(new_path, config)
            if success:
                print(f"Config file copied to {new_path}.")