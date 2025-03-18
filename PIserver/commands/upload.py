from PIserver.clients.FileTransClient import FileTransClient
from PIserver.commands.command import Command
from PIserver.utils.files import log_error


class Upload_Model(Command):
    def register_subcommand(self, subparser):
        upload_parser = subparser.add_parser("upload", help="Upload a local model to https://powerinfer.com. and get predictors.")
        upload_parser.add_argument("model", help="The remote model repository to upload. Must create before uploading.")
        upload_parser.add_argument("-d","--local-dir", default=None, help="The local model directory to upload.")
        upload_parser.add_argument("--hf", default=None, help="Upload the model to huggingface hub.")

    def execute(self, args):
        if args.local_dir is None and args.hf is None:
            log_error("Please specify the local directory or huggingface model name.")
            return
        print("Uploading model...")
        client = FileTransClient()
        client.upload(args.local_dir)