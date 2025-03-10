# Commands

This folder contains the commands that are runnable in this project.

## Adding new commands

If you want to add new commands into this project, you should follow these steps:

1. Create a new file in this folder. 
2. Write a class which extends the `Command` class. Implement `register_subcommand` and `excute` method.
3. Export this class in `__init__.py` file.
4. Add this class with the corresponding command name in variable `command_map` in `cli.py` file. 

