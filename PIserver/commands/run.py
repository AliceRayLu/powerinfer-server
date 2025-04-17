from PIserver.clients.FileDownloadClient import FileDownloadClient
from PIserver.clients.LLMClient import *
from PIserver.commands.command import Command
from PIserver.constants import *
from pathlib import Path
from PIserver.install import local_compile
from PIserver.utils.files import *
import subprocess
from tqdm import tqdm
import time
import keyboard

class Run_Model(Command):
    def __init__(self):
        super().__init__()
        self.state = LLMState.STOPPED
        
    def register_subcommand(self, subparser):
        run_parser = subparser.add_parser("run", help="Run a large language model.")
        run_parser.add_argument("model", help="The model to run. Can be a local model path or a remote model name.")
        run_parser.add_argument("-cfg","--config", default=None, help="The configuration file to use.")
        run_parser.add_argument("--no-update", action="store_true", default=None, help="Do not update the model if it is outdated.")
        
    def execute(self, args):
        # check config file
        cfg = self.check_config(args.config)

        # check backend engine
        if 'engine' not in cfg:
            engine = local_compile()
            
            if engine is not None:
                add_engine(DEFAULT_ENGINE_NAME, engine)
                cfg['engine'] = engine
                write_file(DEFAULT_CONFIG_FILE, cfg)
                print("Engine successfully installed.")
            else:
                log_error("Unable to compile engine. \
                    Please compile the code from PowerInfer repo https://github.com/SJTU-IPADS/PowerInfer manually and install it in order to use.")
                return
        else:    
            engine = self.check_engine(cfg['engine'])
            
        if engine is None:
            log_error(f"Unable to find {engine} in the installed list. Trying to install remote engine and find local files...")
            # check local path
            engine = cfg['engine']
            if not Path(engine).exists():
                log_error(f"Unable to find {engine} locally. Please install the engine first.")
                return
                
        
        # check model existence
        mname = str(args.model)
        row, rest = filter_rows(parse_condition(mname))
        mpath = None
        if len(row) == 0:
            # check if it is local model dir
            mpath = mname if check_existence(mname) else None
        else:
            model_info = row[0]
            mpath = model_info[4] if check_existence(model_info[4]) else None
        if mpath is None or args.no_update is None:
            # download model from remote
            client = FileDownloadClient()
            local_dir_name = str(args.model).replace(":", "-").replace("/", "-")
            local_path = Path(read_file(DEFAULT_CONFIG_FILE)["model_path"]) / Path(local_dir_name)
            local_path.mkdir(parents=True, exist_ok=True)
            mname, tname = check_model_name_with_size(args.model)
            mname, uname = get_uname_from_model(mname)
            if tname == "":
                log_error("Please specify the model size. Format the model name like 'USR/NAME:SIZE'.")
                return
            getModelRequest = {
                "mname": mname,
                "tname": tname
            }
            if uname!= "":
                getModelRequest["uname"] = uname
            
            try:
                info = client.getModelInfo(getModelRequest)
                if info is None:
                    return 
                if mpath is not None and row[0][3] == info["version"]:
                    print(f"Model {mname} is up to date.")
                else:
                    print(f"Model {mname} is outdated. Downloading new version...")
                    print(f"Downloading model {mname} from remote...")
                    if client.download(local_path, info["dir_info"]):
                        add_row([mname, tname, info["size"], info["version"], str(local_path)])
                        mpath = str(local_path)
            except KeyboardInterrupt:
                print("Download stopped.")
                return
            
        # find gguf model weight, if multiple, use first one found
        mpath = Path(mpath)
        if mpath.is_dir():
            model_files = list(mpath.glob("*.gguf"))
            if len(model_files) == 0:
                log_error(f"Unable to find model weight file in {mpath}. Please check the model directory.")
                return
            elif len(model_files) > 1:
                print(f"Multiple model weight files detected. Using `powerinfer run local_model_path` to specify what you need. Currently using {str(model_files[0])}.")
            mpath = model_files[0]
        
        # format command
        cmd = f"{engine} -m {str(mpath)} -np 4"
        for option in cfg:
            if self.filter_options(option):
                cmd += f" --{option} {cfg[option] if type(cfg[option]) is not bool else ""}"
                
        print(f"Running model with command: {cmd}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        time.sleep(1)
        if process.poll() is not None:
            out, err = process.communicate()
            log_error(f"Unable to start the model service. {out} {err}")
            log_error("This could possibly be caused by unsupported model architecture or invalid engine. \
                Please check your engine or leave an issure in the github respository.")
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
        print("Pressing 'CTRL+D' to stop inferencing.")
        print()
        prompt_manager = PromptManager(cfg['system-prompt'] if 'system-prompt' in cfg else '')
        keyboard.add_hotkey("ctrl+d", self.set_stop, suppress=True)
            
        while True:
            try:
                prompt = input(">>> ")
                self.state = LLMState.RUNNING
                params = {
                    "prompt": prompt_manager.format_prompt(prompt),
                    "stream": True,
                }
                if 'options' in cfg:
                    params.update(cfg["options"])
                
                client = LLMClient(POWERINFER_LOCAL_MODEL_HOST)
                answer = ""
                for chunk in client.generate(params):
                    if self.state == LLMState.STOPPED:
                        break
                    data = json.loads(chunk)
                    if 'choices' in data and len(data['choices']) > 0:
                        if 'delta' in data['choices'][0] and 'content' in data['choices'][0]['delta']:
                            content = data['choices'][0]['delta']['content']
                            print(content, end="", flush=True)
                            answer += content
                
                print()            
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
                break
            except Exception as e:
                log_error(e)
                process.terminate()
                process.wait()
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
    
    def set_stop(self):
        if self.state == LLMState.RUNNING:
            print()
            print("Stopping signal sent. Inference stopped.")
            
            self.state = LLMState.STOPPED