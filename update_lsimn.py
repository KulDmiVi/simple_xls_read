from csv_reader import read_csv_file
from db_utils import (
    insert_lsimn,
    get_lsimn,
    get_mse_service,
    update_mse_service,
    get_services_by_mse_id,
    get_identification_mnu_code,
    get_mse_update_record,
    update_service_indification
)


def util_lsimn_updater():
    keys = ('ID', 'NAME_TRADE', 'STANDARD_INN', 'NORMALIZED_DOSAGE', 'CODE_ATC', 'NAME_ATC')
    csv_data = read_csv_file(keys)
    for row in csv_data:
        base_data = get_lsimn(row)
        if not base_data:
            insert_lsimn(row)


def update_reference_book_mse(row):
    base_data = get_mse_service(row)
    if not base_data:
        print(row)
    else:
        print(row['ID'])
        for table_row in base_data:
            if str(table_row[1]) != row['ID']:
                update_mse_service(table_row[0], row)
                print(row)


def check_service_indentification_update(row, white_list):
    if row['SECTION'] == '1':
        data = get_services_by_mse_id(row['ID'])
        if not data:
            return 1
        else:
            for i in data:
                nmu_code = get_identification_mnu_code(i[0])
                if nmu_code:
                    if nmu_code[0][0] == row['NMU_CODE']:
                        white_list.append(i[0])
                        return 0
                    else:
                        return 1
                else:
                    return 1
    else:
        return 0


def util_mse_service():
    keys = ('ID', 'CATEGORY_ICD10', 'NMU_CODE', 'DESCRIPTION', 'BASIC_ADDITIONAL', 'SECTION', 'FLC_REMD')
    csv_data = read_csv_file(keys)
    update_data = []
    white_list = []
    for row in csv_data:
        print(f"Read row ID: {row['ID']}")
        update = check_service_indentification_update(row, white_list)
        if update:
            update_data.append(row)

    if update_data:
        for data in update_data:
            record_id = get_mse_update_record(white_list, data['NMU_CODE'] )
            if record_id:
                print(f"update: {data['ID']}")
                white_list.append(record_id[0][0])
                update_service_indification(record_id[0][0], data['ID'],  data['BASIC_ADDITIONAL'])
            else:
                print(f"Not updated: {data['ID']}")
