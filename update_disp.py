import csv
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, filedialog
from tkcalendar import DateEntry

from csv_reader import read_csv_file
from db_utils import get_contracts, get_events_type_by_contract, get_tariff, get_event_tariff, update_tariff, \
    get_columns, copy_row, update_new_row

# Глобальные переменные для хранения данных и виджетов
contract_filter = {
    'resolution': 'Диспансеризация',
    'grouping': '2025'
}

contracts_map = {
    'не задано': False,
}

events_map = {
    'не задано': False,
}

contract_combo = None  # Глобальная ссылка на Combobox договоров
event_combo = None  # Глобальная ссылка на Combobox событий
beg_date = None
file_path_var = None

def run_disp_updater():
    global contract_combo, event_combo, beg_date, file_path_var

    contract_info = get_contracts(contract_filter)
    reformat_contracts(contract_info)

    root = create_main_window()
    file_path_var = create_file_selection_widget(root)
    contract_combo = add_contract_combobox(root, list(contracts_map.keys()))
    event_combo = add_event_combobox(root, list(events_map.keys()))
    beg_date = add_date_picker(root)
    export_btn = tk.Button(
        root,
        text="Экспорт",
        command=lambda: export_data(file_path_var.get()),
        bg="lightgreen",
        font=("Arial", 10, "bold")
    )
    export_btn.pack(pady=15, padx=10, fill='x')
    root.mainloop()


def export_data(csv_path):
    """
    Заглушка для логики экспорта данных.

    Args:
        csv_path (str): путь к CSV‑файлу для обработки.
    """
    global contract_combo, event_combo, beg_date, file_path_var
    print(f"Начинаем экспорт из: {csv_path}")
    contract_id = contracts_map[contract_combo.get()]
    event_id = events_map[event_combo.get()]
    date_str = beg_date.get()
    dt = datetime.strptime(date_str, '%d.%m.%Y')
    iso_beg_date = dt.strftime('%Y-%m-%d')

    end_date = dt - timedelta(days=1)
    iso_end_date = end_date.strftime('%Y-%m-%d')
    file_path = file_path_var.get()

    columns = get_columns('Contract_Tariff')
    columns_expected_id = [row[0] for row in columns if row[0] != 'id']
    columns_str = ', '.join(columns_expected_id)
    with open(file_path, 'r', encoding='utf-8') as infile:

        csv_reader = csv.reader(infile, delimiter=';')
        next(csv_reader, None)
        for line_num, row in enumerate(csv_reader, 2):
            age = f'{row[0]}г-{row[0]}г'
            sex = row[1]
            price = row[2]
            params = {
                'contract_id': contract_id,
                 'event_id': event_id,
                 'date': iso_beg_date,
                 'end_date': iso_end_date,
                 'age': age,
                 'sex': sex,
                 'price': price
             }
            result = get_event_tariff(params)
            if result:
                update_tariff(result[0][0], iso_end_date)
                new_id = copy_row('Contract_Tariff', columns_str, result[0][0])
                print(new_id)
                update_new_row(new_id, iso_beg_date, price)
    print("Экспорт завершён (заглушка).")


def choose_csv_file(parent_window):
    """
    Открывает диалоговое окно для выбора CSV‑файла и возвращает путь к нему.

    Args:
        parent_window (tk.Tk): родительское окно (для позиционирования диалога).

    Returns:
        str or None: путь к файлу или None, если файл не выбран.
    """
    filepath = filedialog.askopenfilename(
        title="Выберите CSV‑файл для обработки",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        parent=parent_window
    )
    if not filepath:
        print("Файл не выбран.")
        return None

    return filepath


def create_file_selection_widget(parent):
    """
    Создаёт виджет с кнопкой «Обзор…» и полем для отображения пути к файлу.

    Args:
        parent (tk.Widget): родительский контейнер (например, tk.Frame).

    Returns:
        tk.StringVar: переменная, хранящая путь к файлу.
    """
    file_frame = tk.Frame(parent)
    file_frame.pack(pady=10, padx=10, fill='x')

    tk.Label(file_frame, text="CSV‑файл:").pack(side='left')

    file_path_var = tk.StringVar()

    file_entry = tk.Entry(
        file_frame,
        textvariable=file_path_var,
        width=50
    )

    file_entry.pack(side='left', padx=5, fill='x', expand=True)

    def on_choose():
        filepath = choose_csv_file(parent)
        print(f"Получен путь: {filepath}")
        if filepath:
            file_entry.config(state='normal')
            file_path_var.set(filepath)
            file_entry.update_idletasks()
            file_entry.config(state='readonly')
            print(f"Путь установлен: {file_path_var.get()}")

    choose_btn = tk.Button(file_frame, text="Обзор...", command=on_choose)
    choose_btn.pack(side='left')
    return file_path_var


def add_contract_combobox(root, options):
    """Создаёт Combobox для договоров и возвращает виджет"""
    combo = ttk.Combobox(root, values=options, state="readonly", width=40)
    combo.set("Выберите договор")
    combo.pack(pady=5)
    combo.bind("<<ComboboxSelected>>", on_select_contract)
    return combo


def add_event_combobox(root, options):
    """Создаёт Combobox для событий и возвращает виджет"""
    combo = ttk.Combobox(root, values=options, state="readonly", width=40)
    combo.set("Выберите тип события")
    combo.pack(pady=5)
    combo.bind("<<ComboboxSelected>>", on_select_event)
    return combo


def add_date_picker(root):
    """Создаёт поля для выбора даты"""
    frame = tk.Frame(root)
    frame.pack(pady=5, fill='x')
    tk.Label(frame, text="Начальная дата:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
    date_picker = DateEntry(frame, date_pattern='dd.mm.yyyy')
    date_picker.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
    frame.columnconfigure(1, weight=1)
    return date_picker


def on_select_event(event):
    """Обработчик выбора события (пока пустой)"""
    selected = event.widget.get()


def on_select_contract(event):
    """Обработчик выбора договора — обновляет список событий"""
    contract_widget = event.widget
    selected_contract_name = contract_widget.get()

    if selected_contract_name in contracts_map:
        contract_id = contracts_map[selected_contract_name]
        update_event_combobox_options(contract_id)


def reformat_contracts(contracts_info):
    """Форматирует список договоров в словарь {имя: ID}"""
    global contracts_map
    contracts_map = {'не задано': False}
    for contract in contracts_info:
        name = f"{contract[0]} {contract[1]}"
        contract_id = contract[0]
        contracts_map[name] = contract_id


def update_event_combobox_options(contract_id):
    """Обновляет список событий для выбранного договора"""
    global events_map, event_combo

    events_info = get_events_type_by_contract({'contract_id': contract_id})
    events_map = reformat_events(events_info)

    if event_combo:
        event_combo.configure(values=list(events_map.keys()))
        event_combo.set("Выберите тип события")


def reformat_events(events_info):
    """Форматирует список событий в словарь {имя: ID}"""
    events_dict = {'не задано': False}
    for event in events_info:
        name = f"{event[0]} {event[2]}"
        event_id = event[0]
        events_dict[name] = event_id
    return events_dict


def create_main_window():
    """Создаёт главное окно приложения"""
    root = tk.Tk()
    root.title("Параметры импорта")
    root.geometry("600x400")
    return root
