from setuptools import setup, Command
from setuptools.command.install import install
import pathlib

DEFAULT_STORAGE_PATH = pathlib.Path.home() / ".powerinfer"


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        print(f"Starting to create default storing directory at {DEFAULT_STORAGE_PATH} ...")
        
        DEFAULT_STORAGE_PATH.mkdir(0o755, parents=True, exist_ok=True)

class BeforeUninstallCommand(Command):
    def run(self):
        if DEFAULT_STORAGE_PATH.exists():
            response = input(f"Do you want to remove all the model storage at {DEFAULT_STORAGE_PATH}? (y/n)")
            if(response == "y"):
                print(f"Starting to remove default storing directory at {DEFAULT_STORAGE_PATH}...")
                DEFAULT_STORAGE_PATH.rmdir()
                print("Model storage successfully removed.")


setup(
    name='powerinfer-server',
    version='0.1.0',
    author='ARL',
    cmdclass={
        'install': PostInstallCommand,
        'uninstall': BeforeUninstallCommand
    }
)