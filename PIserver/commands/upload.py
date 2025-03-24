from PIserver.clients.FileUploadClient import FileUploadClient
from PIserver.commands.command import Command
from PIserver.utils.files import log_error


class Upload_Model(Command):
    def register_subcommand(self, subparser):
        upload_parser = subparser.add_parser("upload", help="Upload a local model to https://powerinfer.com. and get predictors.")
        upload_parser.add_argument("model", help="The remote model repository to upload.")
        upload_parser.add_argument("-d","--local-dir", default=None, help="The local model directory to upload.")
        upload_parser.add_argument("-hf", "--huggingface", default=None, help="Upload the model from huggingface hub.")

    def execute(self, args):
        if args.local_dir is None and args.huggingface is None:
            log_error("Please specify the local directory or huggingface model name.")
            return
        try:
            if ":" not in str(args.model):
                log_error("Invalid model name. Please specify the size in the format NAME:SIZE .")
                return
            print("Uploading model... Press Ctrl+C to stop.")
            client = FileUploadClient()
            client.upload(args.local_dir, str(args.model).split(":"))
            
            
        except KeyboardInterrupt:
            print("Upload stopped.")
            return