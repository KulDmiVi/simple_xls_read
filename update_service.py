from csv_reader import read_csv_file
from db_utils import (
    get_service_id_by_code,
    update_service,
    insert_service,
)


def update_data(id, data):
    update_service(id, data)

def insert_data(data):
    insert_service(data)

def check_service(row):
    service_id = get_service_id_by_code(row['code'])
    return service_id


def util_load_service():
    keys = ('code', 'name', 'uet_v', 'uet_d')
    csv_data = read_csv_file(keys)
    for row in csv_data:

        service_id = check_service(row)
        if service_id:
            with open('load_service.log', 'a') as file:
                msg = f"Update service code: {row['code']} \n"
                file.write(msg)
            update_data(service_id, row)
        else:
            with open('load_service.log', 'a') as file:
                msg = f"Insert service code: {row['code']} \n"
                file.write(msg)
            insert_data(row)
