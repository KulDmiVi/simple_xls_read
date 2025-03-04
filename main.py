from tkinter import filedialog
import pandas as pd
import mysql.connector

UPDATE_TARIFF = 0


def get_mysql_data(df1):
    cnx = mysql.connector.connect(user='dbuser', password='dbpassword', host='127.0.0.1', database='s11')
    mycursor = cnx.cursor()
    mycursor.execute("SELECT  rbService.code,  rbService.name, Contract_Tariff.price, Contract_Tariff.id  FROM Contract_Tariff \
                     LEFT JOIN rbService ON  rbService.id = Contract_Tariff.service_id \
                     WHERE Contract_Tariff.master_id=34 and Contract_Tariff.deleted = 0"
                     )

    data = mycursor.fetchall()
    column_names = [i[0] for i in mycursor.description]
    # print(column_names)
    df2 = pd.DataFrame(data, columns=column_names)
    merged = df1.merge(df2,
                       right_on='code',
                       left_on='№ п/п',
                       how='outer',
                       indicator=True
                       )
    # print(merged)
    merged.to_csv('f2.csv')
    # print(df1.iloc[0])
    cnx.close()
    return merged


def update_value_price(merged):
    cnx = mysql.connector.connect(user='dbuser',
                                  password='dbpassword',
                                  host='127.0.0.1',
                                  database='s11')
    cursor = cnx.cursor()
    update_query = "UPDATE Contract_Tariff SET price = %s WHERE id = %s"
    for index, row in merged.iterrows():
        # print(update_query, (row['Стоимость за процедуру/ манипуляцию, руб.'], row['id']))
        cursor.execute(update_query, (row['Стоимость за процедуру/ манипуляцию, руб.'], row['id']))

    cnx.commit()
    cursor.close()
    cnx.close()


def open_file():
    filepath = filedialog.askopenfilename()
    df = pd.read_excel(filepath, header=7, index_col=None)
    # print(df.columns)
    # столбцы по имени
    df = df.drop('Unnamed: 4', axis=1)
    df = df.drop('Код СКМУ', axis=1)
    df = df.dropna(subset=['Стоимость за процедуру/ манипуляцию, руб.'])
    merged = get_mysql_data(df)
    if UPDATE_TARIFF:
        update_value_price(merged)


if __name__ == '__main__':
    open_file()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
