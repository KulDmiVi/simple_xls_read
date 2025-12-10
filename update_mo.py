from csv_reader import read_csv_file
from db_utils import get_organisation_id_by_rekviz


def util_mo_updater():
    keys = (
        'id', 'oid', 'oldOid', 'nameFull', 'nameShort', 'parentId',
        'medicalSubjectId', 'medicalSubjectName', 'inn', 'kpp', 'ogrn',
        'regionId', 'regionName', 'organizationType', 'moDeptId', 'moDeptName',
        'founder', 'deleteDate', 'deleteReason', 'createDate', 'modifyDate',
        'moLevel', 'moAgencyKindId', 'moAgencyKind', 'profileAgencyKindId', 'profileAgencyKind',
        'postIndex', 'cadastralNumber', 'latitude', 'longtitude', 'fiasVersion', 'aoidArea',
        'aoidStreet', 'houseid', 'addrRegionId', 'addrRegionName', 'territoryCode', 'isFederalCity',
        'areaName', 'prefixArea', 'streetName', 'prefixStreet', 'house', 'building', 'struct',
        'parentOspOid', 'ospOid', 'childrenOspOid'
    )
    csv_data = read_csv_file(keys, delimiter=';')
    with open('load_service.log', 'a', encoding='utf8') as log_file:
        for row in csv_data:
            mo_id = search_mo(row)
            # msg1 = f"""INSERT INTO rbService(code, name, adultUetDoctor, childUetDoctor,
            #  createDatetime, modifyDatetime, eisLegacy, license, infis, begDate, endDate)
            #     select '{row['code']}', '{row['name']}', {row['uet_v']}, {row['uet_d']},
            #     '2024-05-26', '2024-05-26', 0, 0, 0, '2024-01-01', '2024-01-01'
            #     from rbService
            #     where NOT EXISTS (SELECT * FROM rbService WHERE code ='{row['code']}')
            #     limit 1;
            #     """
            # if service_id:
            #     msg = f"Update service code: {row['code']} \n"
            #     update_data(service_id, row)
            # else:
            #     msg = f"Insert service code: {row['code']} \n"
            #     insert_data(row)
            # log_file.write(msg1)


def search_mo(row):
    """Поиск организации в БД по значению из справочника"""
    organisation_type = 'Медицинская организация'
    if row['regionId'] == '53' and organisation_type in row['medicalSubjectName']:
        org_data = get_organisation_id_by_rekviz(row['inn'], row['kpp'], row['ogrn'])
       # print(row['medicalSubjectName'])
        if org_data:
            print(row['oid'], row['nameFull'], row['nameShort'], row['regionId'], row['medicalSubjectName'], row['inn'], row['kpp'], row['ogrn'])
        else:
            print("!!!!!!!!!!!!")
    return None
