from tkinter import filedialog
import pandas as pd
from db_utils import (
    insert_tariff,
    get_service_id_by_code,
    get_contract_id_by_number,
    get_unit_id_by_code
)


def read_xls_file():
    filepath = filedialog.askopenfilename()
    df = pd.read_excel(filepath, header=8, index_col=None)
    return df


def util_tariff_insert():
    """
    Выборка договоров
    """
    contract_number = 'Прейскурант-14122025'
    unit_code = '28'
    tariff_type = {'action_as_count': 2}

    contract_ids = get_contract_id_by_number(contract_number)
    unit_ids = get_unit_id_by_code(unit_code)

    xls_df = read_xls_file()
    with open('insert_service.log', 'a', encoding='utf8') as log_file:
        for index, row in xls_df.iterrows():
            if pd.notna(row.iloc[3]):
                service = get_service_data(row)
                service_ids = get_service_id_by_code(service['code'])
                if check_service_count(service_ids, service):
                    print(f"Add tariff {service['code']}")
                    tariff_data = {
                        'contract_id': contract_ids[0][0],
                        'tariff_type': tariff_type['action_as_count'],
                        'service_id': service_ids[0][0],
                        'unit_id': unit_ids[0][0],
                        'price': service['price'],
                        'beg_date': "2025-12-14"
                    }
                    insert_tariff(tariff_data)


def check_service_count(service_ids, service):
    if len(service_ids) > 1:
        print(f"Найдено более одной услуги {service}")
        return False
    elif len(service_ids) == 0:
        print(f"Не найдено ни одной услуги {service}")
        return False
    return True


def get_service_data(row):
    service = {
        'code': str(row.iloc[1]).strip(),
        'name': " ".join(row.iloc[2].split()),
        'price': row.iloc[3]
    }
    # replace eng rus
    if service['code'].startswith("A"):
        service['code'] = "А" + service['code'][1:]
    return service
