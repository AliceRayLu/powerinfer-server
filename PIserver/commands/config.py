from PIserver.commands.command import Command


class Config(Command):
    def register_subcommand(self, subparser):
        cfg_parser = subparser.add_parser("config", help="Manage the store location of models.")
        cfg_parser.add_argument("-l","--list", help="Show current configurations", action="store_true")
        cfg_parser.add_argument("-r","--reset", help="Change the config back into default values.")
    
    def execute(self, args):
        pass