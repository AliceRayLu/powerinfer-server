import csv
from PIserver.constants import *
import tabulate

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
        rows = [row for row in reader if len(row) > 0 and check(row)]
        return rows
    
def write_rows(rows: list):
    check_list_file()
    with open(DEFAULT_MODEL_LIST_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(LOCAL_LIST_HEADER)
        writer.writerows(rows)