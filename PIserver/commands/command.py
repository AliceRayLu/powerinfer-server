from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def register_subcommand(self, subparser):
        pass

    @abstractmethod
    def execute(self, args):
        pass