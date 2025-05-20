from tkinter import filedialog
import pandas as pd
from db_utils import get_contract_tariff, update_value_price


def read_xls_file():
    filepath = filedialog.askopenfilename()
    df = pd.read_excel(filepath, header=7, index_col=None)
    return df


def clear_df(df):
    # df = df.drop('Unnamed: 4', axis=1)
    # df = df.drop('Код СКМУ', axis=1)
    df = df.dropna()
    # df = df.dropna(subset=['5'])
    return df


def util_tariff_updater():
    UPDATE_TARIFF = 0
    xls_df = read_xls_file()
    xls_df = clear_df(xls_df)
    xls_df.to_csv('test.csv')
    base_df = get_contract_tariff()
    merged = xls_df.merge(
        base_df,
        right_on='code',
        left_on='№ п/п',
        how='outer',
        indicator=True
    )
    merged.to_csv('f2.csv')
    if UPDATE_TARIFF:
        update_value_price(merged)
