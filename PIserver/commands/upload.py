from PIserver.commands.command import Command


class Upload_Model(Command):
    def register_subcommand(self, subparser):
        upload_parser = subparser.add_parser("upload", help="Upload a local model to https://powerinfer.com. and get predictors.")
        upload_parser.add_argument("model", help="The remote model repository to upload.")
        upload_parser.add_argument("-d","--local-dir", help="The local model directory to upload.", required=True)
        upload_parser.add_argument("--hf", help="Upload the model to huggingface hub.")

    def execute(self, args):
        pass