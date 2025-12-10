from tkinter import filedialog
import csv

def read_csv_file(keys, delimiter='|' ):
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    data = []
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        for row in reader:
            data.append({key: row[key] for key in keys})
    return data

