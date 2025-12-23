import pandas as pd
import logging
from tkinter import filedialog
from db_utils import (
    insert_tariff,
    get_service_id_by_code,
    get_contract_id_by_number,
    get_unit_id_by_code
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('insert_service.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

EXCEL_CONFIG = {
    'header_rows': 12,
    'columns': {
        'service_code': 0,  # Код услуги
        'service_name': 1,  # Название услуги
        'service_price': 2  # Цена
    },
    'expected_sheet_name': None,  # Если нужно указывать лист
    'usecols': None  # Если нужно ограничить столбцы
}

PROCESS_CONFIG = {
    'contract_number': 'Прейскурант_лаборатория-14122025',
    'unit_code': '28',
    'tariff_type': 2,  # action_as_count
    'beg_date': '2025-12-14'
}

def select_and_read_excel_file() -> pd.DataFrame:
    """
    Открывает диалоговое окно для выбора Excel-файла и считывает его.

    Returns:
        DataFrame с данными из выбранного файла (на основе EXCEL_CONFIG).

    Raises:
        FileNotFoundError: если файл не выбран или не найден.
        pd.errors.EmptyDataError: если файл пуст.
        Exception: для прочих ошибок чтения.
    """
    filepath = filedialog.askopenfilename(
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )

    if not filepath:
        logger.error("Файл не выбран через диалоговое окно.")
        raise FileNotFoundError("Файл не выбран.")

    logger.info(f"Выбран файл для обработки: {filepath}")

    try:
        df = pd.read_excel(
            filepath,
            header=EXCEL_CONFIG['header_rows'],
            index_col=None,
            sheet_name=EXCEL_CONFIG['expected_sheet_name'],
            usecols=EXCEL_CONFIG['usecols']
        )

        if df.empty:
            logger.error(f"Файл {filepath} прочитан, но оказался пустым.")
            raise pd.errors.EmptyDataError(f"Файл {filepath} пуст.")

        logger.info(f"Файл успешно прочитан. Количество строк: {len(df)}")
        return df

    except pd.errors.EmptyDataError as e:
        logger.exception("Файл пуст")
        raise

    except Exception as e:
        logger.exception(f"Ошибка при чтении файла {filepath}")
        raise Exception(f"Ошибка при чтении файла {filepath}: {e}")


def get_contract_unit_ids(contract_number: str, unit_code: str) -> tuple:
    """
    Получает ID договора и единицы измерения из БД.

    Args:
        contract_number: номер договора.
        unit_code: код единицы измерения.

    Returns:
        Tuple из (contract_id, unit_id).

    Raises:
        ValueError: если ID не найдены.
    """
    logger.info(f"Поиск ID договора по номеру: {contract_number}")
    contract_ids = get_contract_id_by_number(contract_number)

    if not contract_ids:
        logger.error(f"Договор с номером {contract_number} не найден в БД.")
        raise ValueError(f"Договор с номером {contract_number} не найден.")

    logger.info(f"Найден ID договора: {contract_ids[0][0]}")

    logger.info(f"Поиск ID единицы измерения по коду: {unit_code}")
    unit_ids = get_unit_id_by_code(unit_code)

    if not unit_ids:
        logger.error(f"Единица измерения с кодом {unit_code} не найдена в БД.")
        raise ValueError(f"Единица измерения с кодом {unit_code} не найдена.")

    logger.info(f"Найден ID единицы измерения: {unit_ids[0][0]}")

    return contract_ids[0][0], unit_ids[0][0]



def parse_service_row(row: pd.Series) -> dict:
    """
    Извлекает данные услуги из строки DataFrame.

    Args:
        row: строка DataFrame с данными услуги.

    Returns:
        Словарь с полями: code, name, price.
    """

    code_idx = EXCEL_CONFIG['columns']['service_code']
    name_idx = EXCEL_CONFIG['columns']['service_name']
    price_idx = EXCEL_CONFIG['columns']['service_price']

    code = str(row.iloc[code_idx]).strip()
    # Замена латинской 'A' на русскую
    if code.startswith("A"):
        code = "А" + code[1:]
        logger.debug(f"Заменён код услуги: {code}")

    name = " ".join(str(row.iloc[name_idx]).split()) if pd.notna(row.iloc[name_idx]) else ""
    price = row.iloc[price_idx] if pd.notna(row.iloc[price_idx]) else 0.0

    service_data = {
        'code': code,
        'name': name,
        'price': float(price)
    }

    logger.debug(f"Извлечены данные услуги: {service_data}")
    return service_data


def validate_service_ids(service_ids: list, service_code: str) -> bool:
    """
    Проверяет корректность найденных ID услуги.

    Args:
        service_ids: список найденных ID.
        service_code: код услуги для логирования.

    Returns:
        True, если ID корректны (ровно один найден).
    """
    if len(service_ids) > 1:
        logger.warning(f"Найдено более одной услуги с кодом {service_code}: {len(service_ids)} записей. Пропускаем.")
        return False
    if len(service_ids) == 0:
        logger.warning(f"Не найдено ни одной услуги с кодом {service_code}. Пропускаем.")
        return False

    logger.debug(f"Для кода {service_code} найден ровно один ID: {service_ids[0][0]}")
    return True


def insert_tariff_record(
        contract_id: int,
        unit_id: int,
        service_id: int,
        price: float,
        tariff_type: int,
        beg_date: str
):
    """
    Вставляет тариф в БД.
    Args:
        contract_id: ID договора.
        unit_id: ID единицы измерения.
        service_id: ID услуги.
        price: цена.
        tariff_type: тип тарифа.
        beg_date: дата начала действия.
    """
    tariff_data = {
        'contract_id': contract_id,
        'tariff_type': tariff_type,
        'service_id': service_id,
        'unit_id': unit_id,
        'price': price,
        'beg_date': beg_date
    }

    try:
        insert_tariff(tariff_data)
        logger.info(
            f"Тариф успешно добавлен: "
            f"договор = {contract_id}, "
            f"услуга = {service_id}, "
            f"цена={price}, "
            f"дата_начала={beg_date}"
        )
    except Exception as e:
        logger.error(
            f"Ошибка при вставке тарифа для услуги {service_id}: {e}. "
            f"Данные: {tariff_data}"
        )
        raise


def util_tariff_insert():
    """Основной процесс: считывает Excel, извлекает данные и вставляет тарифы в БД."""

    logger.info("Запуск процесса импорта тарифов из Excel")

    try:
        xls_df = select_and_read_excel_file()
        contract_id, unit_id = get_contract_unit_ids(
            PROCESS_CONFIG['contract_number'],
            PROCESS_CONFIG['unit_code']
        )
        processed_count = 0
        skipped_count = 0

        for index, row in xls_df.iterrows():
            if not pd.notna(row.iloc[3]):
                skipped_count += 1
                logger.debug(f"Строка {index}: пропущена из-за отсутствия цены")
                continue

            service = parse_service_row(row)
            service_ids = get_service_id_by_code(service['code'])

            if not validate_service_ids(service_ids, service['code']):
                skipped_count += 1
                continue

            try:
                insert_tariff_record(
                    contract_id=contract_id,
                    unit_id=unit_id,
                    service_id=service_ids[0][0],
                    price=service['price'],
                    tariff_type=PROCESS_CONFIG['tariff_type'],
                    beg_date=PROCESS_CONFIG['beg_date']
                )
                processed_count += 1
            except Exception as e:
                skipped_count += 1
                logger.error(
                    f"Строка {index}: ошибка при вставке тарифа для услуги {service['code']}: {e}"
                )

        logger.info(
            f"Обработка завершена. "
            f"Обработано: {processed_count}, "
            f"пропущено: {skipped_count}, "
            f"всего строк: {len(xls_df)}"
        )

    except Exception as e:
        logger.critical(f"Критическая ошибка при выполнении импорта: {e}")
        raise
    finally:
        logger.info("Завершение процесса импорта тарифов.")
