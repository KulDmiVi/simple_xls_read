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
    """Контекст-менеджер для подключения к БД"""
    cnx = None
    try:
        cnx = mysql.connector.connect(
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            connection_timeout=30
        )
        yield cnx
    except mysql.connector.Error as e:
        print(f"Ошибка подключения к БД: {e}")
        raise
    finally:
        if cnx and cnx.is_connected():
            cnx.close()


def get_records(query):
    """Выполнения запроса на получения данных"""
    with get_db_connection() as cnx:
        try:
            cursor = cnx.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        except mysql.connector.Error as e:
            print(f"Ошибка выполнения запроса: {e}")


def get_info(query):
    """Выполнения запроса на получения данных и возвращает данные в виде списка словарей"""
    with get_db_connection() as cnx:
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        except mysql.connector.Error as e:
            print(f"Ошибка выполнения запроса: {e}")


def change_data(query):
    """Выполнения запроса на изменения данных"""
    with get_db_connection() as cnx:
        try:
            cursor = cnx.cursor()
            data = cursor.execute(query)
            cnx.commit()
            cursor.close()
            return data
        except mysql.connector.Error as e:
            print(f"Ошибка выполнения запроса: {e}")


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


def get_events_type_by_contract(filter):
    """
    Получает список типов событий для договора.

    Args:
        filter (dict): словарь с параметрами фильтрации

    Returns:
        list: список словарей с данными типах событий
    """
    query = f"""
        SELECT EventType.id, EventType.code, EventType.name
        FROM Contract_Specification
            LEFT JOIN s11.EventType ON EventType.id = Contract_Specification.eventType_id
        WHERE Contract_Specification.deleted = 0 AND Contract_Specification.master_id = %s
    """

    query_params = (filter['contract_id'])

    return get_records(query % query_params)


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
        WHERE resolution = '%s' AND grouping = '%s'
    """

    query_params = (
        filter_params['resolution'],
        filter_params['grouping']
    )

    return get_records(query % query_params)


def get_contract_id_by_number(number, grouping, resolution):
    """Получения id договора по номеру."""
    query = f"""
        SELECT Contract.id 
        FROM Contract 
        WHERE Contract.number='{number}' AND 
        Contract.grouping='{grouping}' AND
        Contract.resolution='{resolution}'
        ORDER BY Contract.id desc
    """
    return get_records(query)


def get_unit_id_by_code(code):
    """Получения id способа оплаты по коду."""
    query = f"""
        SELECT rbMedicalAidUnit.id 
        FROM rbMedicalAidUnit 
        WHERE rbMedicalAidUnit.code='{code}'
        ORDER BY rbMedicalAidUnit.id desc
    """
    return get_records(query)


def get_service_id_by_code(service_code):
    """Получения id услуг по коду."""
    query = f"""
        SELECT rbService.id 
        FROM rbService 
        WHERE rbService.code='{service_code}'
        ORDER BY rbService.id desc
    """
    return get_records(query)


def get_system_id_by_urn(urn):
    """Получения id внешней учетной системы."""
    query = f"""
          SELECT rbAccountingSystem.id 
          FROM rbAccountingSystem
          WHERE rbAccountingSystem.urn='{urn}'
          ORDER BY rbAccountingSystem.id  desc
      """
    return get_records(query)


def insert_organization_indentification(org_id, system_id, data):
    """Вставка организации"""
    query = f"""
       INSERT INTO Organisation_Identification(
       master_id, system_id, value, createDatetime, modifyDatetime
       )
       VALUES (
            {org_id},
            {system_id},
            '{data['oid']}',
             NOW(),
             NOW());
    """
    return change_data(query)


def get_organization_indentification(org_id, system_id):
    """Получения идентификатора организации"""
    query = f"""
        SELECT Organisation_Identification.id 
        FROM Organisation_Identification
        WHERE Organisation_Identification.master_id='{org_id}'
         AND Organisation_Identification.system_id='{system_id}' 
        ORDER BY Organisation_Identification.id  desc
    """
    return get_records(query)


def get_organisation_info_by_rekviz(inn, kpp, ogrn):
    """Получения id организации по ИНН, КПП, ОГРН."""
    query = f"""
        SELECT *
        FROM Organisation 
        WHERE Organisation.INN='{inn}'
         AND Organisation.KPP='{kpp}' 
         AND Organisation.OGRN='{ogrn}'
        ORDER BY Organisation.id  desc
    """
    return get_info(query)


def insert_organisation(data):
    """Вставка организации"""
    query = f"""
       INSERT INTO Organisation (
       fullName, shortName, title, 
       infisCode, obsoleteInfisCode, tfomsExtCode, miacCode, smoCode, usishCode,
       isMedical, isActive, isInsurer,
       INN, KPP, OGRN, 
       OKVED, OKATO, OKPO, FSS, region, Address, chief, phone, accountant, area, notes, email,
       createDatetime, modifyDatetime
       )
       VALUES (
            '{data['nameFull']}',
            '{data['nameShort']}',
            '{data['nameShort']}',
            '', '', '', '', '', '',
             1, 1, 0,
             '{data['inn']}',
             '{data['kpp']}',
             '{data['ogrn']}',
             '', '', '', '', '', '',  '',  '', '', '', '', '',
             NOW(),
             NOW());
    """
    return change_data(query)


def insert_organisation(data):
    """Вставка организации"""
    query = f"""
       INSERT INTO Organisation (
       fullName, shortName, title, 
       infisCode, obsoleteInfisCode, tfomsExtCode, miacCode, smoCode, usishCode,
       isMedical, isActive, isInsurer,
       INN, KPP, OGRN, 
       OKVED, OKATO, OKPO, FSS, region, Address, chief, phone, accountant, area, notes, email,
       createDatetime, modifyDatetime,
       chiefPost
       )
       VALUES (
            '{data['nameFull']}',
            '{data['nameShort']}',
            '{data['nameShort']}',
            '', '', '', '', '', '',
             1, 1, 0,
             '{data['inn']}',
             '{data['kpp']}',
             '{data['ogrn']}',
             '', '', '', '', '', '',  '',  '', '', '', '', '',
             NOW(),
             NOW(),
              ''
             );

    """
    return change_data(query)


def get_tariff(data):
    """Получения действующего тарифа на дату."""
    query = f"""
        SELECT Contract_Tariff.id
        FROM Contract_Tariff
        WHERE 
            Contract_Tariff.deleted = 0 AND 
            Contract_Tariff.master_id = {data['contract_id']} AND
            Contract_Tariff.service_id = {data['service_id']} AND
            (Contract_Tariff.begDate < {data['date']} OR Contract_Tariff.begDate IS Null) AND
            (Contract_Tariff.endDate > {data['date']} OR Contract_Tariff.endDate IS Null)
    """
    return get_records(query)


def update_tariff(id, end_date):
    """Закрываем текущий тариф"""
    query = f"""
        UPDATE Contract_Tariff 
        SET endDate='{end_date}'
        WHERE
            Contract_Tariff.id = {id}
    """
    return change_data(query)


def update_organisation(org_id, params):
    """Обновления данных организации"""
    set_parts = []
    for key, value in params.items():
        set_parts.append(f"{key} = {value}")
    set_clause = ", ".join(set_parts)
    query = f"""
        UPDATE Organisation
        SET modifyDatetime=NOW(), {set_clause}
        WHERE
            Organisation.id = {org_id}
    """
    return change_data(query)


def insert_service(data):
    """Вставка учлуги"""
    query = f"""
       INSERT INTO rbService (code, name, adultUetDoctor, childUetDoctor)
       VALUES ('{data['code']}', '{data['name']}', {data['uet_v']}, {data['uet_d']})

    """
    return change_data(query)


def insert_tariff(data):
    """Добавление тарифа уcлуги"""
    query = f"""
       INSERT INTO Contract_Tariff (master_id, tariffType, service_id, unit_id, price, begDate)
       VALUES (
            {data['contract_id']},
            {data['tariff_type']},
            {data['service_id']},
            {data['unit_id']},
            {data['price']},
            '{data['beg_date']}'
       )
    """
    return change_data(query)


def update_service_indification(data):
    pass


def get_contract_tariff(data):
    pass


def update_value_price(data):
    pass


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
