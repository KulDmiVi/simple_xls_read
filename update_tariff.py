from tkinter import filedialog, Tk, messagebox, Frame, Button
from tkinter import ttk  # Импортируем ttk для Treeview
import pandas as pd
from preview_utils import create_preview_window
from db_utils import get_contract_tariff, update_value_price

def read_xls_file():
    filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xls *.xlsx")])
    if not filepath:
        return None
    df = pd.read_excel(filepath, header=7, index_col=None)
    return df

def clear_df(df):
    df = df.dropna()
    return df

def util_tariff_updater():
    xls_df = read_xls_file()
    if xls_df is not None:
        xls_df = clear_df(xls_df)
        create_preview_window(xls_df)

if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Скрываем основное окно
    util_tariff_updater()
