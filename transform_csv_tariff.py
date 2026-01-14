import csv
import os
import re
from tkinter import filedialog


def util_transform_disp():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not filepath:
        return None
    output_filepath = generate_output_path(filepath)
    parse_and_transform_csv(filepath, output_filepath)

def generate_output_path(input_path):
    """
    Генерирует путь для выходного файла:
    - берёт директорию исходного файла;
    - добавляет суффикс '_transformed' к имени без расширения;
    - сохраняет расширение '.csv'.

    Args:
        input_path (str): полный путь к исходному файлу.

    Returns:
        str: полный путь к выходному файлу.
    """
    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)
    name_without_ext = os.path.splitext(base_name)[0]
    output_name = f"{name_without_ext}_transformed.csv"
    return os.path.join(dir_name, output_name)

def parse_and_transform_csv(input_file, output_file):
    """
    Читает CSV с группами возрастов, разбивает на отдельные строки по возрастам.

    Args:
        input_file (str): путь к исходному CSV.
        output_file (str): путь для сохранения результата.
    """
    transformed_data = []

    with open(input_file, 'r', encoding='utf-8') as infile:
        csv_reader = csv.reader(infile, delimiter=';')
        next(csv_reader, None)
        for line_num, row in enumerate(csv_reader, 2):
            if not row or len(row) < 4:
                print(f"Строка {line_num}: пропущена (недостаточно полей): {row}")
                continue

            ages_part = row[0]
            ages = re.findall(r'\b\d+\b', ages_part)
            if not ages:
                print(f"Строка {line_num}: не найдены возрасты: {ages_part}")
                continue
            ages = [int(age) for age in ages]

            try:
                values = [float(field) for field in row[1:4]]
            except ValueError as e:
                print(f"Строка {line_num}: ошибка преобразования значений: {e}")
                continue
            for age in ages:
                transformed_data.append({
                    'age': age,
                    'price1': values[0],
                    'price2': values[1],
                    'price3': values[2]
                })

    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['age', 'price1', 'price2', 'price3']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(transformed_data)

    print(f"Обработано {len(transformed_data)} строк. Сохранено в {output_file}")

