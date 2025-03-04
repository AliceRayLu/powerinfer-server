import csv
from PIserver.constants import *
import tabulate
import shutil
import pathlib

def print_table(data: list, header: list):
    print(tabulate.tabulate(data, headers=header, tablefmt="plain"))

def check_list_file():
    if not DEFAULT_MODEL_LIST_FILE.exists():
        with open(DEFAULT_MODEL_LIST_FILE, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(LOCAL_LIST_HEADER)

def add_row(model: list):
    check_list_file()
    with open(DEFAULT_MODEL_LIST_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(model)
    
def filter_rows(check):
    check_list_file()
    with open(DEFAULT_MODEL_LIST_FILE, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        rows, rest = [], []
        for row in reader:
            if len(row) > 0 and check(row):
                rows.append(row)
            else:
                rest.append(row)
        return rows, rest
    
def write_rows(rows: list):
    check_list_file()
    with open(DEFAULT_MODEL_LIST_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(LOCAL_LIST_HEADER)
        writer.writerows(rows)
        
def parse_model(name):
    arr = name.split(':')
    return arr[0], arr[1] if len(arr) > 1 else None

def parse_condition(model):
    name, size = parse_model(model)
    if size is None:
        return lambda x: x[0] == name
    else:
        return lambda x: x[0] == name and x[1] == size
    
def remove_dir(path: pathlib.Path, name):
    if path.exists():
        shutil.rmtree(path)
        print(f"Model {name} successfully removed.")
    else:
        print(f"Model {name} not found.")