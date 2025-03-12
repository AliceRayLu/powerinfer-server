from PIserver.commands.command import Command
from PIserver.constants import *
from pathlib import Path

from PIserver.utils.files import read_file, log_error, write_file

class Run_Model(Command):
    def register_subcommand(self, subparser):
        run_parser = subparser.add_parser("run", help="Run a large language model.")
        run_parser.add_argument("model", help="The model name to run.")
        run_parser.add_argument("-cfg","--config", default=None, help="The configuration file to use.")
        run_parser.add_argument("-d","--local-dir", help="Run the model stored in local directory.")
        
    def execute(self, args):
        cfg_file = DEFAULT_CONFIG_FILE
        if args.config is None:
            print("Running model {args.model} using default configuration...")
        else:
            cfg_file = Path(args.config)
            print(f"Running model {args.model} using configuration file {args.config}...")
        # check backend engine
        cfg = read_file(cfg_file)
        if len(cfg) == 0:
            cfg = DEFAULT_CONFIG
            write_file(cfg_file, cfg)
        engine = cfg['engine']
        all_engines = read_file(DEFAULT_ENGINE_LIST_FILE)
        if engine not in all_engines:
            log_error(f"Engine {engine} not found. Please install it using `powerinfer install` first.")
            return
        # check engine file exists
        
        
        # check model existence