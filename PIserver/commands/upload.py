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
        upload_parser.add_argument("-s", "--status", default=None, help="Query current training process status.", action="store_true")
        upload_parser.add_argument("-c", "--cancel", default=None, help="Cancel existing training process.", action="store_true")

    def execute(self, args):
        if args.status is not None:
            response = send_post_request("/type/client/query", params={"name": args.model})
            print(response.json())
            return
        if args.local_dir is None and args.huggingface is None:
            log_error("Please specify the local directory or huggingface model name.")
            return
        
        try:
            if ":" not in str(args.model):
                log_error("Invalid model name. Please specify the size in the format NAME:SIZE .")
                return
            print("Uploading model... Press Ctrl+C to cancel task.")
            client = FileUploadClient()
            client.upload(args.local_dir, str(args.model).split(":"))
            print(f"Upload successfully. Visit xxx.com or use `powerinfer upload {args.model} -s` to check the process.")
            
            
        except KeyboardInterrupt:
            print("Upload stopped. Rerun the command to continue.")
            return