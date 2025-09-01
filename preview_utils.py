from tkinter import ttk, Tk, messagebox, Frame, Button, Entry
import pandas as pd
import numpy as np


def create_preview_window(df):
    """
    Создает окно предварительного просмотра данных с возможностью редактирования
    :param df: DataFrame с данными для отображения
    :return: None
    """
    preview_window = Tk()
    preview_window.title("Предварительный просмотр данных")
    preview_window.geometry("800x600")

    frame = Frame(preview_window)
    frame.pack(fill="both", expand=True)

    table = ttk.Treeview(frame, selectmode="browse")
    table.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
    scrollbar.pack(side="right", fill="y")
    table.config(yscrollcommand=scrollbar.set)

    columns = list(df.columns)
    table["columns"] = columns
    table["show"] = "headings"

    # Создаем словарь для хранения виджетов Entry
    entry_widgets = {}

    for col in columns:
        table.heading(col, text=col, anchor="w")
        table.column(col, anchor="w", width=150)

    # Заполняем таблицу данными
    for i, row in df.iterrows():
        table.insert("", "end", values=list(row))

    def edit_cell(event, table, entry_widgets, df):
        item = table.identify_row(event.y)
        column = table.identify_column(event.x)
        if item and column:
            # Получаем индекс столбца
            col_index = int(str(column).replace('#', '')) - 1
            # Получаем значение ячейки
            row_index = table.index(item)
            current_value = table.item(item, 'values')[col_index]

            # Получаем координаты ячейки
            x = table.winfo_x() + table.column(columns[col_index], 'width') * col_index
            y = table.winfo_y() + table.bbox(item)[1]  # Используем bbox для получения Y позиции

            # Создаем виджет Entry
            entry = Entry(preview_window, width=15)
            entry.insert(0, current_value)
            entry.place(x=x, y=y)

            # Сохраняем виджет в словаре
            entry_widgets[(row_index, col_index)] = entry

            # Привязываем событие потери фокуса
            entry.bind('<FocusOut>',
                       lambda e, row=row_index, col=col_index: save_edit(e, row, col, table, entry_widgets, df))

    def save_edit(event, row, col, table, entry_widgets, df):
        entry = entry_widgets.pop((row, col))
        new_value = entry.get()
        entry.destroy()

        # Обновляем значение в таблице
        values = list(table.item(table.get_children()[row], 'values'))
        values[col] = new_value
        table.item(table.get_children()[row], values=values)

        # Обновляем DataFrame
        df.iloc[row, col] = new_value

    # Привязываем событие двойного клика
    table.bind('<Double-1>', lambda e: edit_cell(e, table, entry_widgets, df))

    def confirm():
        preview_window.destroy()
        save_csv(df)

    confirm_button = Button(preview_window, text="Подтвердить и сохранить", command=confirm)
    confirm_button.pack(pady=10)

    preview_window.mainloop()


def save_csv(df):
    """
    Сохраняет DataFrame в CSV файл
    :param df: DataFrame для сохранения
    :return: None
    """
    try:
        df.to_csv('test.csv', index=False)
        messagebox.showinfo("Успех", "Файл успешно сохранен!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при сохранении файла: {str(e)}")

