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
    services = get_service_id_by_code(row['code'])
    if services:
        return services[0][0]
    else:
        return None


def util_load_service():
    keys = ('code', 'name', 'uet_v', 'uet_d')
    csv_data = read_csv_file(keys)
    with open('load_service.log', 'a',  encoding='utf8') as log_file:
        for row in csv_data:
            service_id = check_service(row)
            msg1 = f"""INSERT INTO rbService(code, name, adultUetDoctor, childUetDoctor,
             createDatetime, modifyDatetime, eisLegacy, license, infis, begDate, endDate)
                select '{row['code']}', '{row['name']}', {row['uet_v']}, {row['uet_d']}, 
                '2024-05-26', '2024-05-26', 0, 0, 0, '2024-01-01', '2024-01-01' 
                from rbService
                where NOT EXISTS (SELECT * FROM rbService WHERE code ='{row['code']}') 
                limit 1;
                """
            if service_id:
                msg = f"Update service code: {row['code']} \n"
                update_data(service_id, row)
            else:
                msg = f"Insert service code: {row['code']} \n"
                insert_data(row)
            log_file.write(msg1)
