from tkinter import filedialog
import pandas as pd
from db_utils import insert_tariff, get_service_id_by_code



def read_xls_file():
    filepath = filedialog.askopenfilename()
    df = pd.read_excel(filepath, header=8, index_col=None)
    return df


def clear_df(df):
    # df = df.drop('Unnamed: 4', axis=1)
    # df = df.drop('Код СКМУ', axis=1)
    df = df.dropna(subset=[2])
    # df = df.dropna(subset=['5'])
    return df


def util_tariff_insert():
    """
    Выборка договоров
        SELECT *
        FROM Contract
        WHERE resolution = '2025' AND grouping = 'ГТС'
        ORDER BY id DESC
    """
    contract_ids = [26, 27, 28]
    xls_df = read_xls_file()
    xls_df = clear_df(xls_df)
    with open('insert_service.log', 'a',  encoding='utf8') as log_file:
        for index, row in xls_df.iterrows():
            service_code = row[1]
            adult_price = row[5]
            child_price = row[6]
            service_ids = get_service_id_by_code(service_code)
            price = adult_price
            if pd.isna(adult_price):
                price = child_price
            for contract_id in contract_ids:
                insert_tariff(service_ids[0][0],  contract_id, price)
                msg = f"service: {service_ids}, contract_id: {contract_id}, price: {price}"
                log_file.write(msg)

