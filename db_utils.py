import mysql.connector
from mysql.connector.locales.eng import client_error
from mysql.connector.plugins import mysql_native_password
import pandas as pd

user = 'dbuser'
password = 'dbpassword'
host = '192.168.0.237'
base_name = 's11'


def get_contract_tariff():
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    cursor = cnx.cursor()
    cursor.execute("SELECT  rbService.code,  rbService.name, Contract_Tariff.price, Contract_Tariff.id  FROM Contract_Tariff \
                     LEFT JOIN rbService ON  rbService.id = Contract_Tariff.service_id \
                     WHERE Contract_Tariff.master_id=34 and Contract_Tariff.deleted = 0"
                   )
    data = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    df = pd.DataFrame(data, columns=column_names)
    cursor.close()
    cnx.close()
    return df


def get_service_id_by_code(service_code):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    cursor = cnx.cursor()
    stmt = f"SELECT rbService.id " \
           f"FROM rbService " \
           f"WHERE rbService.code='{service_code}' " \
           f"order by rbService.id desc "
    cursor.execute(stmt)
    data = cursor.fetchone()
    cursor.close()
    cnx.close()
    if data:
        return data[0]
    else:
        return None


def update_service(service_id, data):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    stmt = f"""
       UPDATE rbService 
       SET
           rbService.adultUetDoctor='{data['uet_v']}',
           rbService.childUetDoctor='{data['uet_d']}'
       WHERE
           rbService.id = {service_id}
    """
    cursor = cnx.cursor()
    cursor.execute(stmt)
    cnx.commit()
    cursor.close()
    cnx.close()
    return data


def insert_service(data):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    stmt = f"""
       INSERT INTO rbService (code, name, adultUetDoctor, childUetDoctor)
       VALUES ('{data['code']}', '{data['name']}', {data['uet_v']}, {data['uet_d']})

    """
    cursor = cnx.cursor()
    cursor.execute(stmt)
    cnx.commit()
    cursor.close()
    cnx.close()
    return data


def get_lsimn(data):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    stmt = f"select * from rbNomenclature " \
           f"where name = '{data['NAME_TRADE']}' and dosageValue = '{data['NORMALIZED_DOSAGE']}'"
    cursor = cnx.cursor()
    cursor.execute(stmt)
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return data


def get_mse_service(data):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    stmt = f"""
       select * 
       from rbMedicalExaminationsMSE 
       where
           MKB = '{data['CATEGORY_ICD10']}' and 
           NMU_code = '{data['NMU_CODE']}' and
           BASIC_ADDITIONAL = '{data['BASIC_ADDITIONAL']}' and
           SECTION = '{data['SECTION']}' and
           DESCRIPTION = '{data['DESCRIPTION']}' 
    """
    cursor = cnx.cursor()
    cursor.execute(stmt)
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return data


def update_mse_service(id, data):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    stmt = f"""
       update rbMedicalExaminationsMSE 
       set rbMedicalExaminationsMSE.CODE = '{data['ID']}' 
       where
           rbMedicalExaminationsMSE.id = {id}
    """
    cursor = cnx.cursor()
    cursor.execute(stmt)
    cnx.commit()
    cursor.close()
    cnx.close()
    return data


def get_services_by_nmu_code(nmu_code):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    stmt = f"""
       select * 
       from ActionType_Identification 
       where ActionType_Identification.value = '{nmu_code}' and  
       ActionType_Identification.system_id IN (
       SELECT id 
       FROM rbAccountingSystem
       WHERE rbAccountingSystem.urn LIKE '%1.2.643.5.1.13.13.99.2.857' 
       )
    """
    cursor = cnx.cursor()
    cursor.execute(stmt)
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return data


def get_services_by_mse_id(mse_id):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    stmt = f"""
       SELECT master_id
       FROM ActionType_Identification 
       WHERE ActionType_Identification.value = '{mse_id}' and  
        ActionType_Identification.system_id IN (
        SELECT id 
        FROM rbAccountingSystem
        WHERE rbAccountingSystem.urn LIKE '%1.2.643.5.1.13.13.99.2.857**'
        )
    """
    cursor = cnx.cursor()
    cursor.execute(stmt)
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return data


def get_identification_mnu_code(master_id):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    stmt = f"""
           select value
           from ActionType_Identification 
           where ActionType_Identification.master_id = '{master_id}' and  
            ActionType_Identification.system_id IN (
            SELECT id 
            FROM rbAccountingSystem
            WHERE rbAccountingSystem.urn LIKE '%1.2.643.5.1.13.13.99.2.857' 
            )
        """
    cursor = cnx.cursor()
    cursor.execute(stmt)
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return data


def get_mse_update_record(white_list, nmu_code, basic_additional):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    str_white_lst = str(white_list).replace('[', '(').replace(']', ')')
    stmt = f"""
        SELECT ActionType_Identification.id
        FROM ActionType_Identification
        WHERE
            ActionType_Identification.master_id not IN {str_white_lst}
             and ActionType_Identification.master_id in (
                SELECT ActionType_Identification.master_id
                FROM ActionType_Identification
                    left join rbAccountingSystem on ActionType_Identification.system_id = rbAccountingSystem.id and rbAccountingSystem.urn LIKE '%1.2.643.5.1.13.13.99.2.857'
                WHERE ActionType_Identification.value = '{nmu_code}'
            ) 
            and ActionType_Identification.master_id in (
                SELECT ActionType_Identification.master_id
                FROM ActionType_Identification
                    left join rbAccountingSystem on ActionType_Identification.system_id = rbAccountingSystem.id and rbAccountingSystem.urn LIKE '%1.2.643.5.1.13.13.99.2.857*'
                WHERE ActionType_Identification.value = '{basic_additional}'
            )
             and ActionType_Identification.system_id in (
             SELECT id
             FROM rbAccountingSystem
             where rbAccountingSystem.urn LIKE '%1.2.643.5.1.13.13.99.2.857**')
            LIMIT 1
    """
    cursor = cnx.cursor()
    cursor.execute(stmt)
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return data


def update_service_indification(id, value):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    stmt = f"""
        update ActionType_Identification 
        set ActionType_Identification.value = '{value}' 
        where
            ActionType_Identification.id = {id}
     """
    cursor = cnx.cursor()
    cursor.execute(stmt)
    cnx.commit()
    cursor.close()
    cnx.close()


def insert_lsimn(data):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    stmt = f"INSERT INTO  \
            rbNomenclature (`code`,`name`, dosageValue) \
            VALUE ('{data['ID']}', '{data['NAME_TRADE']}', '{data['NORMALIZED_DOSAGE']}')"
    cursor = cnx.cursor()
    cursor.execute(stmt)
    cnx.commit()
    cursor.close()
    cnx.close()


def update_value_price(merged):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=base_name)
    cursor = cnx.cursor()
    update_query = "UPDATE Contract_Tariff SET price = %s WHERE id = %s"
    for index, row in merged.iterrows():
        cursor.execute(update_query, (row['Стоимость за процедуру/ манипуляцию, руб.'], row['id']))
    cnx.commit()
    cursor.close()
    cnx.close()
