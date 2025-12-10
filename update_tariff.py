import tkinter
from tkinter import filedialog, Tk, messagebox, TOP, LEFT, RIGHT, END
from tkinter import ttk, scrolledtext
import pandas as pd

from preview_utils import DataPreview

from db_utils import (
    get_contract_tariff,
    update_value_price,
    get_contracts
)


def read_xls_file():
    """
    Функция для открытия и чтения Excel файла.

    Returns:
        DataFrame: прочитанные данные или None если файл не выбран
    """
    filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xls *.xlsx")])
    if not filepath:
        return None
    df = pd.read_excel(filepath, header=7, index_col=None)
    return df


def clear_df(df):
    """
    Функция очистки DataFrame от пустых значений.

    Args:
        df (DataFrame): исходный DataFrame

    Returns:
        DataFrame: очищенный DataFrame
    """
    df = df.dropna()
    return df


def select_contracts(tk_root):
    """Функция для выбора и отображения договоров по заданным фильтрам."""

    contract_filter = {
        'resolution': 'Диспансеризация',
        'grouping': '2025'
    }

    contracts = get_contracts(contract_filter)

    try:
        if not contracts:
            messagebox.showinfo("Информация", "Договоры не найдены")
            return
        show_contracts_dialog(contracts, tk_root)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")


def show_contracts_dialog(contracts, tk_root):
    """
    Отображает диалоговое окно со списком договоров
    """
    dialog = tkinter.Toplevel(tk_root)
    dialog.title("Список договоров")
    dialog.geometry("600x400")

    frame = ttk.Frame(dialog)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(frame, columns=("ID", "Номер", "Основание", "Группа"), show="headings")
    tree.pack(side=TOP, fill="both", expand=True)

    tree.heading("ID", text="ID")
    tree.heading("Номер", text="Номер договора")
    tree.heading("Основание", text="Основание")
    tree.heading("Группа", text="Группа")

    tree.column("ID", width=50)
    tree.column("Номер", width=150)
    tree.column("Основание", width=150)
    tree.column("Группа", width=150)

    for contract in contracts:
        tree.insert("", END, values=(contract['id'], contract['number'],
                                     contract['resolution'], contract['grouping']))

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side=RIGHT, fill="y")
    tree.config(yscrollcommand=scrollbar.set)

    def close_dialog():
        dialog.destroy()

    close_button = ttk.Button(dialog, text="Закрыть", command=close_dialog)
    close_button.pack(pady=10)



def util_tariff_updater(tk_root):
    """Утилита обновление тарифов"""

    xls_df = read_xls_file()
    if xls_df is not None:
        xls_df = clear_df(xls_df)
        preview = DataPreview(xls_df, tk_root)
        print("Данные сохранены в файл test.csv")
    select_contracts(tk_root)


