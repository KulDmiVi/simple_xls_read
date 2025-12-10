from csv_reader import read_csv_file
from db_utils import get_organisation_id_by_rekviz, insert_organisation


def util_mo_updater():
    organisation_type = 'Медицинская организация'
    organisation_region = '53'

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
    with open('load_org.log', 'a', encoding='utf8') as log_file:
        for row in csv_data:
            if (
                    organisation_region == row['regionId'] and
                    organisation_type in row['medicalSubjectName'] and
                    check_organisation_kind(row)
            ):

                org_data = search_mo(row)
                if org_data:
                    print('!!!!!!!!!!!!!!!!')
                else:
                    insert_organisation(row)
                    msg = f"Insert organisation: {row['nameFull']} {row['moAgencyKind']} \n"
                    print(msg)
                    log_file.write(msg)


def check_organisation_kind(data):
    """Проверяет, относится ли организация к одному из допустимых типов."""
    organisation_kind = [
        'Амбулатория',
        'Больница',
        'Диспансер',
        'Лечебно-профилактические медицинские организации',
        'Поликлиника',
        # 'Медико - санитарная часть',
        'Медицинские организации скорой медицинской помощи',
        'Специализированная больница',
        'Родильный дом'
    ]

    for item in organisation_kind:
        if item in data['moAgencyKind']:
            return True
    return False


def search_mo(row):
    """Поиск организации в БД по значению из справочника"""
    org_data = get_organisation_id_by_rekviz(row['inn'], row['kpp'], row['ogrn'])
    return org_data
