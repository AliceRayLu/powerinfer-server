from PIserver.commands.command import Command
from PIserver.constants import DEFAULT_CONFIG, DEFAULT_CONFIG_FILE
from PIserver.utils.files import read_file, write_file

class Config(Command):
    def register_subcommand(self, subparser):
        cfg_parser = subparser.add_parser("config", help="Manage the store location of models.")
        cfg_parser.add_argument("-l","--list", help="Show current configurations", action="store_true")
        cfg_parser.add_argument("-r","--reset", help="Change the config back into default values.")
        cfg_parser.add_argument("-s","--set", help="Set the config in the format option=value.")
    
    def execute(self, args):
        if args.list:
            config = read_file(DEFAULT_CONFIG_FILE)
            print("Current configurations:")
            for key in config:
                print(f"{key}={config[key]}")
        elif args.reset:
            config = DEFAULT_CONFIG
            write_file(DEFAULT_CONFIG_FILE, config)
            print("Config reset to default.")
        elif args.set:
            config = read_file(DEFAULT_CONFIG_FILE)
            if '=' not in str(args.set):
                print("Invalid format. Please use option=value.")
                return
            [option, value] = str(args.set).split('=')
            config[option] = value
            write_file(DEFAULT_CONFIG_FILE, config)
            print(f"Config set: {option}={value}")
