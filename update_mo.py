from csv_reader import read_csv_file
from db_utils import (
    get_organisation_info_by_rekviz,
    insert_organisation,
    update_organisation,
    get_system_id_by_urn,
    get_organization_indentification,
    insert_organization_indentification
)


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
    system_data = get_system_id_by_urn('urn:oid:1.2.643.5.1.13.2.1.1.178')
    system_id = system_data[0]
    moDeptName = 'Органы исполнительной власти субъектов Российской Федерации, осуществляющие функции в области здравоохранения'
    with open('load_org.log', 'a', encoding='utf8') as log_file:
        if not system_id:
            msg = f"Не найден идентификатор urn:oid:1.2.643.5.1.13.2.1.1.178\n"
            print(msg)
            log_file.write(msg)
        for row in csv_data:
            if row_filter(row):
                org_data = search_mo(row)
                if org_data:
                    update_data = cheсk_update(org_data, row)

                    if update_data:
                        #update_organisation(org_data['id'], update_data)
                        msg = f"Update organisation: {row['oid']}. data {update_data}\n"
                        print(msg)
                        log_file.write(msg)
                    identification_data = get_organization_indentification(org_data['id'], system_id[0])

                    if not identification_data:
                        insert_organization_indentification(org_data['id'], system_id[0], row)
                        msg = f"Insert identification: {row['oid']}\n"
                        print(msg)
                        log_file.write(msg)
                else:
                    if row['deleteDate'] != '' and row['moDeptName'] == moDeptName:
                        org_id = insert_organisation(row)
                        #insert_organization_indentification(org_id, system_id[0], row)
                        msg = f"Insert organisation: {row['nameFull']} {row['moAgencyKind']} \n"
                        print(msg)
                        log_file.write(msg)

def cheсk_update(org_data, row):
    """Проверка записи на необходимиость обновления"""
    updated_data = {}
    moDeptName = 'Органы исполнительной власти субъектов Российской Федерации, осуществляющие функции в области здравоохранения'
    if row['deleteDate'] or row['moDeptName'] != moDeptName:
        if org_data['isActive'] != 0 or org_data['deleted'] != 1:
            updated_data = {'isActive': 0, 'deleted': 1}
    else:
        if org_data['isActive'] != 1 or org_data['deleted'] != 0 or org_data['isMedical'] != 1:
            updated_data = {'isActive': 1, 'deleted': 0, 'isMedical': 1}
    return updated_data


def row_filter(row):
    """Проверка записи на соотвествия условиям"""
    organisation_type = 'Медицинская организация'
    organisation_region = '53'
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

    if (
            organisation_region == row['regionId'] and
            organisation_type in row['medicalSubjectName'] and
            check_organisation_kind(row, organisation_kind)
    ):
        return True
    else:
        return False


def check_organisation_kind(data, organisation_kind):
    """Проверяет, относится ли организация к одному из допустимых типов."""

    for item in organisation_kind:
        if item in data['moAgencyKind']:
            return True
    return False


def search_mo(row):
    """Поиск организации в БД по значению из справочника"""
    org_data = get_organisation_info_by_rekviz(row['inn'], row['kpp'], row['ogrn'])
    if org_data:
        return org_data[0]
    else:
        return None
