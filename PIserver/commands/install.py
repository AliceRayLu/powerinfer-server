from PIserver.commands.command import Command
from PIserver.powerinfer.install import interactive_install


class Install_Backend(Command):
    def register_subcommand(self, subparser):
        install_parser = subparser.add_parser("install", help="Install the backend engine.")
        install_parser.add_argument("engine", nargs='?', default=None, help="The backend engine name to install.")
        install_parser.add_argument("-f","--file", help="The local runnable file compiled by yourself from powerinfer.")
        
    def execute(self, args):
        print("Installing the backend engine...")
        interactive_install()
        print("Installed.")