from tkinter import filedialog
import csv

delimiter = '|'

def read_csv_file(keys):
    filepath = filedialog.askopenfilename()
    data = []
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        for row in reader:
            data.append({key: row[key] for key in keys})
    return data

