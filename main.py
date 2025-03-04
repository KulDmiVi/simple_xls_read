from tkinter import filedialog
import pandas as pd
import mysql.connector

UPDATE_TARIFF = 0


def get_mysql_data():
    cnx = mysql.connector.connect(user='dbuser', password='dbpassword', host='127.0.0.1', database='s11')
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


def update_value_price(merged):
    cnx = mysql.connector.connect(user='dbuser',
                                  password='dbpassword',
                                  host='127.0.0.1',
                                  database='s11')
    cursor = cnx.cursor()
    update_query = "UPDATE Contract_Tariff SET price = %s WHERE id = %s"
    for index, row in merged.iterrows():
        cursor.execute(update_query, (row['Стоимость за процедуру/ манипуляцию, руб.'], row['id']))
    cnx.commit()
    cursor.close()
    cnx.close()


def read_file():
    filepath = filedialog.askopenfilename()
    df = pd.read_excel(filepath, header=7, index_col=None)
    return df


def clear_df(df):
    df = df.drop('Unnamed: 4', axis=1)
    df = df.drop('Код СКМУ', axis=1)
    df = df.dropna(subset=['Стоимость за процедуру/ манипуляцию, руб.'])
    return df


if __name__ == '__main__':
    xls_df = read_file()
    xls_df = clear_df(xls_df)
    base_df = get_mysql_data()
    merged = xls_df.merge(
        base_df,
        right_on='code',
        left_on='№ п/п',
        how='outer',
        indicator=True
    )
    merged.to_csv('f2.csv')
    if UPDATE_TARIFF:
        update_value_price(merged)