import tabulate
import pathlib
import csv

def print_table(path: pathlib.Path):
    with open(path, 'r') as f:
        reader = csv.reader(f)
        print(tabulate.tabulate(list(reader), headers=next(reader), tablefmt="plain"))