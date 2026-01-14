import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

from csv_reader import read_csv_file
from db_utils import get_contracts, get_events_type_by_contract

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

def run_disp_updater():
    global contract_combo, event_combo, beg_date

    contract_info = get_contracts(contract_filter)
    reformat_contracts(contract_info)

    root = create_main_window()
    contract_combo = add_contract_combobox(root, list(contracts_map.keys()))
    event_combo = add_event_combobox(root, list(events_map.keys()))
    beg_date = add_date_picker(root)

    root.mainloop()


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
