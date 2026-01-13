import tkinter
from tkinter import ttk, Tk, messagebox, Frame, Button, Entry


class DataPreview:
    def __init__(self, df, tk_root):
        self.df = df
        self.preview_window = tkinter.Toplevel(tk_root)
        self.preview_window.title("Предварительный просмотр данных")
        self.preview_window.geometry("800x600")

        self.frame = Frame(self.preview_window)
        self.frame.pack(fill="both", expand=True)

        self.table = ttk.Treeview(self.frame, selectmode="browse")
        self.table.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.table.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.table.config(yscrollcommand=self.scrollbar.set)

        self.columns = list(self.df.columns)
        self.table["columns"] = self.columns
        self.table["show"] = "headings"

        self.entry_widgets = {}

        self.setup_table()
        self.bind_events()



    def setup_table(self):
        for col in self.columns:
            self.table.heading(col, text=col, anchor="w")
            self.table.column(col, anchor="w", width=150)

        for i, row in self.df.iterrows():
            self.table.insert("", "end", values=list(row))

    def bind_events(self):
        self.table.bind('<Double-1>', self.edit_cell)
        confirm_button = Button(self.preview_window, text="Подтвердить и сохранить", command=self.confirm)
        confirm_button.pack(pady=10)

    def edit_cell(self, event):
        item = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)
        if item and column:
            col_index = int(str(column).replace('#', '')) - 1
            row_index = self.table.index(item)
            current_value = self.table.item(item, 'values')[col_index]
            x = self.table.winfo_x() + self.table.column(self.columns[col_index], 'width') * col_index
            y = self.table.winfo_y() + self.table.bbox(item)[1]
            entry = Entry(self.preview_window, width=15)
            entry.insert(0, current_value)
            entry.place(x=x, y=y)
            self.entry_widgets[(row_index, col_index)] = entry
            entry.bind('<FocusOut>', lambda e, row=row_index, col=col_index: self.save_edit(e, row, col))

    def save_edit(self, event, row, col):
        entry = self.entry_widgets.pop((row, col))
        new_value = entry.get()
        entry.destroy()
        values = list(self.table.item(self.table.get_children()[row], 'values'))
        values[col] = new_value
        self.table.item(self.table.get_children()[row], values=values)
        self.df.iloc[row, col] = new_value

    def confirm(self):
        self.preview_window.destroy()
        self.save_csv()

    def save_csv(self):
        """
        Сохраняет DataFrame в CSV файл
        :param df: DataFrame для сохранения
        :return: None
        """
        try:
            self.df.to_csv('test.csv', index=False, sep=';',)
            messagebox.showinfo("Успех", "Файл успешно сохранен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при сохранении файла: {str(e)}")
