from datetime import datetime
from PIserver.clients.FileUploadClient import FileUploadClient
from PIserver.clients.net import send_post_request
from PIserver.commands.command import Command
from PIserver.utils.files import log_error


class Upload_Model(Command):
    def register_subcommand(self, subparser):
        upload_parser = subparser.add_parser("upload", help="Upload a local model to https://powerinfer.com. and get predictors.")
        upload_parser.add_argument("model", help="The remote model repository to upload.")
        upload_parser.add_argument("-d","--local-dir", default=None, help="The local model directory to upload.")
        upload_parser.add_argument("-hf", "--huggingface", default=None, help="Upload the model from huggingface hub.")
        upload_parser.add_argument("-s", "--status", default=None, help="Query current model training process status.", action="store_true")
        upload_parser.add_argument("-c", "--cancel", default=None, help="Cancel existing training process.", action="store_true")
        upload_parser.add_argument("--no-train", default=False, help="Upload a model without training.", action="store_true")

    def execute(self, args):
        if ':' not in str(args.model):
            log_error("Invalid model name. Please specify the size in the format NAME:SIZE.")
            return
        if args.status is not None:
            response = send_post_request("/task/client/detail", params={
                "mname": str(args.model).split(":")[0],
                "tname": str(args.model).split(":")[1]
            })
            if response is None:
                log_error("Cannot successfully get response. Please check your internet connection.")
                return
            if response.status_code == 404:
                log_error(f"Model {args.model} not found.")
                return
            task = dict(response.json())
            # {'tid': 'e8ec8383da200308f2f83fbfdf57589a', 'dir': 'D://train/73027646d141476489fd6dae05bdb217/testLlama-7b', 'version': 'd83d625b0d7683711c00bbd035eed394ea141609', 'id': 'c0ecd6558ad2e0838663e8b7b2c9bf9e', 'state': 'UPLOADING', 'created': '2025-03-27T20:56:30.123858', 'started': None, 'finished': None, 'queue': 0, 'progress': 0, 'waitingTime': 0, 'runningTime': 0}
            print("STATE: ", task["state"])
            print("version: ", task["version"])
            print("Task created at: ", datetime.fromisoformat(task["created"]).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"))
            print("Task started at: ", datetime.fromisoformat(task["started"]).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z") if task["started"] is not None else "--")
            print("Task finished at: ", datetime.fromisoformat(task["finished"]).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z") if task["finished"] is not None else "--")
            
            return
        
        client = FileUploadClient(str(args.model).split(":"))
        if args.cancel is not None:
            client.cancel()
            return 
        
        try:
            print("Uploading model... Press Ctrl+C to cancel task.")
            if args.huggingface is not None:
                client.upload(args.local_dir ,no_train=args.no_train, hf=args.huggingface)
                return
            client.upload(args.local_dir, no_train=args.no_train)
             
        except KeyboardInterrupt:
            client.cancel()
            return
        