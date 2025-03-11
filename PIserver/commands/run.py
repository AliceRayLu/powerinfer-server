from PIserver.commands.command import Command


class Run_Model(Command):
    def register_subcommand(self, subparser):
        run_parser = subparser.add_parser("run", help="Run a large language model.")
        run_parser.add_argument("model", help="The model name to run.")
        run_parser.add_argument("-cfg","--config", default=None, help="The configuration file to use.")
        run_parser.add_argument("-d","--local-dir", help="Run the model stored in local directory.")
        
    def execute(self, args):
        if args.config is None:
            print("Running model {args.model} using default configuration...")
        # check backend engine
        # check model existence