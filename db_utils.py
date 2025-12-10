import json
import os
from contextlib import contextmanager

import mysql.connector
from mysql.connector.locales.eng import client_error
from mysql.connector.plugins import mysql_native_password
import pandas as pd


# Загрузка конфигурации из файла
def load_config_from_file():
    config_path = 'db_config.json'
    if not os.path.exists(config_path):
        raise FileNotFoundError("Конфигурационный файл отсутствует")
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except json.JSONDecodeError:
        raise ValueError("Неверный формат конфигурационного файла")


# Инициализация конфигурации
try:
    DB_CONFIG = load_config_from_file()
except (FileNotFoundError, ValueError) as e:
    print(e)


@contextmanager
def get_db_connection():
    """Контекст менеджер для подключения к БД"""
    cnx = None
    try:
        cnx = mysql.connector.connect(
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database']
        )
        yield cnx
    except mysql.connector.Error as e:
        print(f"Ошибка подключения к БД: {e}")
    finally:
        if cnx:
            cnx.close()


def get_records(query):
    """Выполнения запроса на получения данных"""
    with get_db_connection() as cnx:
        cursor = cnx.cursor()
        try:
            cursor.execute(query)
            data = cursor.fetchall()
            return data
        except mysql.connector.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
        finally:
            cursor.close()


def change_data(query):
    """Выполнения запроса на изменения данных"""
    with get_db_connection() as cnx:
        cursor = cnx.cursor()
        try:
            data = cursor.execute(query)
            cnx.commit()
            return data
        except mysql.connector.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
        finally:
            cursor.close()


def get_contracts(filter_params):
    """
    Получает список договоров по заданным фильтрам.

    Args:
        filter_params (dict): словарь с параметрами фильтрации

    Returns:
        list: список словарей с данными договоров
     """
    query = f"""
        SELECT `id`, `number`, `resolution`, `grouping` 
        FROM Contract
        WHERE resolution = %s AND grouping = %s
    """

    query_params = (
        filter_params['resolution'],
        filter_params['grouping']
    )

    return get_records(query % query_params)


def get_service_id_by_code(service_code):
    """Получения id услуг по коду."""
    query = f"""
        SELECT rbService.id 
        FROM rbService 
        WHERE rbService.code='{service_code}'
        ORDER BY rbService.id desc
    """
    return get_records(query)

def get_organisation_id_by_rekviz(inn, kpp, ogrn):
    """Получения id организации по ИНН, КПП, ОГРН."""
    query = f"""
        SELECT Organisation.id 
        FROM Organisation 
        WHERE Organisation.INN='{inn}'
         AND Organisation.KPP='{kpp}' 
         AND Organisation.OGRN='{ogrn}'
        ORDER BY Organisation.id  desc
    """
    return get_records(query)

def update_service(service_id, data):
    """Обновления данных услуги"""
    query = f"""
        UPDATE rbService
        SET
            rbService.adultUetDoctor='{data['uet_v']}',
            rbService.childUetDoctor='{data['uet_d']}'
        WHERE
            rbService.id = {service_id}
    """
    return change_data(query)


def insert_service(data):
    """Вставка учлуги"""
    query = f"""
       INSERT INTO rbService (code, name, adultUetDoctor, childUetDoctor)
       VALUES ('{data['code']}', '{data['name']}', {data['uet_v']}, {data['uet_d']})

    """
    return change_data(query)


def insert_tariff(service_id, contract_id, price):
    """Добавление тарифа уcлуги"""
    query = f"""
       INSERT INTO Contract_Tariff (master_id, tariffType, service_id, price)
       VALUES ({contract_id}, 2, {service_id}, {price})

    """
    return change_data(query)


def get_contract_tariff():
    pass
    #     query = """
    #         SELECT
    #             rbService.code,
    #             rbService.name,
    #             Contract_Tariff.price,
    #             Contract_Tariff.id
    #         FROM Contract_Tariff
    #         LEFT JOIN rbService ON  rbService.id = Contract_Tariff.service_id
    #         WHERE Contract_Tariff.master_id=34 and Contract_Tariff.deleted = 0
    #     """
    #     with get_db_connection() as cnx:
    #         data = get_query(query)
    #     return data
    # column_names = [i[0] for i in cursor.description]
    # df = pd.DataFrame(data, columns=column_names)
    # cursor.close()
    # cnx.close()
    # return df

    #
    # cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    # cursor = cnx.cursor()
    # stmt = f"SELECT rbService.id " \
    #        f"FROM rbService " \
    #        f"WHERE rbService.code='{service_code}' " \
    #        f"order by rbService.id desc "
    # cursor.execute(stmt)
    # data = cursor.fetchone()
    # cursor.close()
    # cnx.close()
    # if data:
    #     return data[0]
    # else:
    #     return None


#     cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
#     stmt = f"""
#        INSERT INTO rbService (code, name, adultUetDoctor, childUetDoctor)
#        VALUES ('{data['code']}', '{data['name']}', {data['uet_v']}, {data['uet_d']})
#
#     """
#     cursor = cnx#     cursor.execute(stmt).cursor()
#     cnx.commit()
#     cursor.close()
#     cnx.close()
#     return data


def get_mse_service(data):
    pass


#     cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
#     stmt = f"""
#        select *
#        from rbMedicalExaminationsMSE
#        where
#            MKB = '{data['CATEGORY_ICD10']}' and
#            NMU_code = '{data['NMU_CODE']}' and
#            BASIC_ADDITIONAL = '{data['BASIC_ADDITIONAL']}' and
#            SECTION = '{data['SECTION']}' and
#            DESCRIPTION = '{data['DESCRIPTION']}'
#     """
#     cursor = cnx.cursor()
#     cursor.execute(stmt)
#     data = cursor.fetchall()
#     cursor.close()
#     cnx.close()
#     return data


def update_mse_service(id, data):
    pass


#     cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
#     stmt = f"""
#        update rbMedicalExaminationsMSE
#        set rbMedicalExaminationsMSE.CODE = '{data['ID']}'
#        where
#            rbMedicalExaminationsMSE.id = {id}
#     """
#     cursor = cnx.cursor()
#     cursor.execute(stmt)
#     cnx.commit()
#     cursor.close()
#     cnx.close()
#     return data


def get_services_by_nmu_code(nmu_code):
    pass


#     cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
#     stmt = f"""
#        select *
#        from ActionType_Identification
#        where ActionType_Identification.value = '{nmu_code}' and
#        ActionType_Identification.system_id IN (
#        SELECT id
#        FROM rbAccountingSystem
#        WHERE rbAccountingSystem.urn LIKE '%1.2.643.5.1.13.13.99.2.857'
#        )
#     """
#     cursor = cnx.cursor()
#     cursor.execute(stmt)
#     data = cursor.fetchall()
#     cursor.close()
#     cnx.close()
#     return data


def get_services_by_mse_id(mse_id):
    pass


#     cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
#     stmt = f"""
#        SELECT master_id
#        FROM ActionType_Identification
#        WHERE ActionType_Identification.value = '{mse_id}' and
#         ActionType_Identification.system_id IN (
#         SELECT id
#         FROM rbAccountingSystem
#         WHERE rbAccountingSystem.urn LIKE '%1.2.643.5.1.13.13.99.2.857**'
#         )
#     """
#     cursor = cnx.cursor()
#     cursor.execute(stmt)
#     data = cursor.fetchall()
#     cursor.close()
#     cnx.close()
#     return data


def get_identification_mnu_code(master_id):
    pass


#     cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
#     stmt = f"""
#            select value
#            from ActionType_Identification
#            where ActionType_Identification.master_id = '{master_id}' and
#             ActionType_Identification.system_id IN (
#             SELECT id
#             FROM rbAccountingSystem
#             WHERE rbAccountingSystem.urn LIKE '%1.2.643.5.1.13.13.99.2.857'
#             )
#         """
#     cursor = cnx.cursor()
#     cursor.execute(stmt)
#     data = cursor.fetchall()
#     cursor.close()
#     cnx.close()
#     return data


def get_mse_update_record(white_list, nmu_code, basic_additional):
    pass


#     cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
#     str_white_lst = str(white_list).replace('[', '(').replace(']', ')')
#     stmt = f"""
#         SELECT ActionType_Identification.id
#         FROM ActionType_Identification
#         WHERE
#             ActionType_Identification.master_id not IN {str_white_lst}
#              and ActionType_Identification.master_id in (
#                 SELECT ActionType_Identification.master_id
#                 FROM ActionType_Identification
#                     left join rbAccountingSystem on ActionType_Identification.system_id = rbAccountingSystem.id and rbAccountingSystem.urn LIKE '%1.2.643.5.1.13.13.99.2.857'
#                 WHERE ActionType_Identification.value = '{nmu_code}'
#             )
#             and ActionType_Identification.master_id in (
#                 SELECT ActionType_Identification.master_id
#                 FROM ActionType_Identification
#                     left join rbAccountingSystem on ActionType_Identification.system_id = rbAccountingSystem.id and rbAccountingSystem.urn LIKE '%1.2.643.5.1.13.13.99.2.857*'
#                 WHERE ActionType_Identification.value = '{basic_additional}'
#             )
#              and ActionType_Identification.system_id in (
#              SELECT id
#              FROM rbAccountingSystem
#              where rbAccountingSystem.urn LIKE '%1.2.643.5.1.13.13.99.2.857**')
#             LIMIT 1
#     """
#     cursor = cnx.cursor()
#     cursor.execute(stmt)
#     data = cursor.fetchall()
#     cursor.close()
#     cnx.close()
#     return data


def update_service_indification(id, value):
    pass


#     cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
#     stmt = f"""
#         update ActionType_Identification
#         set ActionType_Identification.value = '{value}'
#         where
#             ActionType_Identification.id = {id}
#      """
#     cursor = cnx.cursor()
#     cursor.execute(stmt)
#     cnx.commit()
#     cursor.close()
#     cnx.close()


def get_lsimn(data):
    pass


def insert_lsimn(data):
    pass


#     cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
#     stmt = f"INSERT INTO  \
#             rbNomenclature (`code`,`name`, dosageValue) \
#             VALUE ('{data['ID']}', '{data['NAME_TRADE']}', '{data['NORMALIZED_DOSAGE']}')"
#     cursor = cnx.cursor()
#     cursor.execute(stmt)
#     cnx.commit()
#     cursor.close()
#     cnx.close()


def update_value_price(merged):
    pass
#     cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
#     cursor = cnx.cursor()
#     update_query = "UPDATE Contract_Tariff SET price = %s WHERE id = %s"
#     for index, row in merged.iterrows():
#         cursor.execute(update_query, (row['Стоимость за процедуру/ манипуляцию, руб.'], row['id']))
#     cnx.commit()
#     cursor.close()
#     cnx.close()
