from PIserver.commands.command import Command
from PIserver.constants import *
from pathlib import Path
from PIserver.utils.files import *
import subprocess

class Run_Model(Command):
    def register_subcommand(self, subparser):
        run_parser = subparser.add_parser("run", help="Run a large language model.")
        run_parser.add_argument("model", help="The model name or local path to run.")
        run_parser.add_argument("-cfg","--config", default=None, help="The configuration file to use.")
        
    def execute(self, args):
        # check config file
        cfg = self.check_config(args.config)

        # check backend engine
        engine = self.check_engine(cfg['engine'])
        if engine is None:
            log_error(f"Unable to find {engine}. Please change an engine or install it.")
        
        # check model existence
        mname = str(args.model)
        row, rest = filter_rows(parse_condition(mname))
        mpath = ""
        if len(row) == 0:
            mpath = mname if check_existence(mname) else None
        else:
            mpath = row[4] if check_existence(row[4]) else None
        if mpath is None:
            log_error(f"Unable to find model {mname}. Please clone it first or use correct local model path.")
            return
        
        # format command
        cmd = f"{engine} -m {mpath}"
        for option in cfg:
            if self.filter_options(option):
                cmd += f" --{option} {cfg[option] if type(cfg[option]) is not bool else ""}"
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print("Loading model...")
        
        while True:
            output = str(process.stdout.readline())
            err = process.stderr.readline() if process.stderr is not None else ''
            if err != '':
                log_error(err)
                return
            if "llama server listening at" in output:
                print("Model successfully loaded.")
                break
            print(output)
            
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            process.wait()
            print("Model service successfully stopped.")
        except Exception as e:
            log_error(e)
            process.terminate()
            process.wait()
            
        return
        
        
    def check_engine(self, name):
        engines = read_file(DEFAULT_ENGINE_LIST_FILE)
        if name not in engines:
            log_error(f"Engine {name} not found. Please install it using `powerinfer install` first.")
            return None
        return engines[name]
    
    def check_config(self, file):
        cfg_file = DEFAULT_CONFIG_FILE
        if file is None:
            print("Running model using default configuration...")
        else:
            cfg_file = Path(file)
            print(f"Running model using configuration file {file}...")
        cfg = read_file(cfg_file)
        if len(cfg) == 0:
            cfg = DEFAULT_CONFIG
            write_file(cfg_file, cfg)
        return cfg
    
    def filter_options(self, option: str):
        anti = ["model_path", "engine", "options"]
        for a in anti:
            if a == option:
                return False
        return True