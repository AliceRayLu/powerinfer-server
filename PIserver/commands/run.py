from PIserver.clients.LLMClient import *
from PIserver.commands.command import Command
from PIserver.constants import *
from pathlib import Path
from PIserver.utils.files import *
import subprocess
from tqdm import tqdm
import time

class Run_Model(Command):
    def register_subcommand(self, subparser):
        run_parser = subparser.add_parser("run", help="Run a large language model.")
        run_parser.add_argument("model", help="The model name or local path to run.")
        run_parser.add_argument("-cfg","--config", default=None, help="The configuration file to use.")
        
    def execute(self, args):
        # check config file
        cfg = self.check_config(args.config)

        # check backend engine
        if 'engine' not in cfg:
            log_error("Must specify the backend engine in the configuration file!")
            return
        engine = self.check_engine(cfg['engine'])
        if engine is None:
            log_error(f"Unable to find {engine} in the installed list. Trying to install remote engine and find local files...")
            # TODO: check local path
            # TODO: check remote name
        
        # check model existence
        mname = str(args.model)
        row, rest = filter_rows(parse_condition(mname))
        mpath = ""
        if len(row) == 0:
            mpath = mname if check_existence(mname) else None
        else:
            mpath = row[4] if check_existence(row[4]) else None
        if mpath is None:
            print(f"Unable to find model {mname} locally. Trying to download it from remote...")
            # TODO: download model from remote
            
        
        # format command
        cmd = f"{engine} -m {mpath} -np 4"
        for option in cfg:
            if self.filter_options(option):
                cmd += f" --{option} {cfg[option] if type(cfg[option]) is not bool else ""}"
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        time.sleep(1)
        if process.poll() is not None:
            _, err = process.communicate()
            log_error(f"Unable to start the model service. {err}")
            return
        print("Start to load model...")
        pbar = tqdm(total=100, desc="Loading model", unit="%")
        
        while True:
            output = str(process.stdout.readline())
            err = process.stderr.readline() if process.stderr is not None else ''
            if err != '':
                log_error(err)
                return
            
            if pbar.n < 13 and "llama_model_loader" in output:
                pbar.update(13-pbar.n)
            if pbar.n < 33 and "kv" in output:
                pbar.update(33-pbar.n)
            if pbar.n < 40 and "llama_model_load" in output:
                pbar.update(40-pbar.n)
            if pbar.n < 52 and "llama_new_context" in output:
                pbar.update(52-pbar.n)
            if pbar.n < 71 and "llama_build_graph" in output:
                pbar.update(71-pbar.n)
            if "llama server listening at" in output:
                pbar.update(100-pbar.n)
                pbar.close()
                print("Model successfully loaded.")
                break
            # print(output)
        
        
        print()
        print("Pressing 'CTRL+C' to stop inferencing.")
        print()
        stop_handler = StopHandler()
        prompt_manager = PromptManager(cfg['system-prompt'] if 'system-prompt' in cfg else '')
            
        while True:
            try:
                prompt = input(">>> ")
                params = {
                    "prompt": prompt_manager.format_prompt(prompt),
                    "stream": True,
                }
                if 'options' in cfg:
                    params.update(cfg["options"])
                
                stop_handler.start()
                client = LLMClient(POWERINFER_LOCAL_MODEL_HOST)
                answer = ""
                for chunk in client.generate(params):
                    if stop_handler.has_stoppend():
                        client.close()
                        break
                    data = json.loads(chunk)
                    if 'choices' in data and len(data['choices']) > 0:
                        if 'delta' in data['choices'][0] and 'content' in data['choices'][0]['delta']:
                            content = data['choices'][0]['delta']['content']
                            print(content, end="", flush=True)
                            answer += content
                            
                stop_handler.stop()
                prompt_manager.save_dialog(prompt, answer)

            except json.JSONDecodeError:
                log_error("Unable to decode json from server.")
                break
            except KeyboardInterrupt:
                print()
                print("Trying to stop model service...")
                process.terminate()
                process.wait()
                print("Model service successfully stopped.")
                stop_handler.stop()
                break
            except Exception as e:
                log_error(e)
                process.terminate()
                process.wait()
                stop_handler.stop()
                break
            
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
        if not cfg_file.exists():
            print(f"Configuration file {file} not found. Creating configuration file with default config options...")
        cfg = read_file(cfg_file)
        if len(cfg) == 0:
            cfg = DEFAULT_CONFIG
            write_file(cfg_file, cfg)
        return cfg
    
    def filter_options(self, option: str):
        anti = ["model_path", "engine", "options", "system-prompt"]
        for a in anti:
            if a == option:
                return False
        return True