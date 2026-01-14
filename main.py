import tkinter as tk
from tkinter import messagebox, ttk

# Импортируем необходимые модули
from transform_csv_tariff import util_transform_disp

try:
    from update_lsimn import util_lsimn_updater, util_mse_service
    from update_tariff import util_tariff_updater
    from update_service import util_load_service
    from insert_tariff import util_tariff_insert
    from update_mo import util_mo_updater

    from update_disp import run_disp_updater

except ImportError as e:
    messagebox.showerror("Ошибка импорта", f"Не удалось импортировать модули: {str(e)}")
    raise




def run_tariff_insert():
    """Запуск вставки тарифов"""
    try:
        util_tariff_insert()
        messagebox.showinfo("Успех", "Вставка тарифов выполнена успешно")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при вставке тарифов: {str(e)}")


def run_load_service():
    """Запуск загрузки услуг"""
    try:
        util_load_service()
        messagebox.showinfo("Успех", "Загрузка услуг выполнена успешно")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при загрузке услуг: {str(e)}")


def run_mse_service():
    """Запуск загрузки услуг МСЭ"""
    try:
        util_mse_service()
        messagebox.showinfo("Успех", "Загрузка услуг МСЭ выполнена успешно")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при загрузке услуг МСЭ: {str(e)}")


def run_tariff_updater():
    """Запуск обновления тарифов"""
    try:
        util_tariff_updater(root)
        messagebox.showinfo("Успех", "Обновление тарифов выполнено успешно")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при обновлении тарифов: {str(e)}")


def run_mo_updater():
    """Запуск обновления справочника организаций"""
    try:
        util_mo_updater()
        messagebox.showinfo("Успех", "Обновление справочника организаций выполнено успешно")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при обновлении справочника организаций: {str(e)}")


def run_csv_disp_transformer():
    """Запуск переформатирования CSV тарифов по диспансеризации"""
    try:
        util_transform_disp()
        messagebox.showinfo("Успех", "Обработка файла выполнена успешно")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при обработке файла: {str(e)}")

def run_selected():
    """Обработчик выбора функции"""
    selected = var.get()
    if selected == 1:
        run_tariff_insert()
    elif selected == 2:
        run_load_service()
    elif selected == 3:
        run_mse_service()
    elif selected == 4:
        run_tariff_updater()
    elif selected == 5:
        run_mo_updater()
    elif selected == 6:
        run_disp_updater()
    elif selected == 7:
        run_csv_disp_transformer()
    else:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите функцию")


# Создание главного окна
root = tk.Tk()
root.title("Утилиты системы")
root.geometry("350x300")
root.resizable(False, False)  # Запрет изменения размера окна

# Стилизация окна
style = ttk.Style()
style.theme_use('clam')

# Переменная для хранения выбора
var = tk.IntVar()

# Создание радиокнопок
frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="Выберите утилиту:").pack(anchor=tk.W, pady=5)

ttk.Radiobutton(frame,
                text="Вставка тарифов",
                variable=var,
                value=1).pack(anchor=tk.W)

ttk.Radiobutton(frame,
                text="Загрузка услуг",
                variable=var,
                value=2).pack(anchor=tk.W)

ttk.Radiobutton(frame,
                text="Загрузка услуг МСЭ",
                variable=var,
                value=3).pack(anchor=tk.W)

ttk.Radiobutton(frame,
                text="Обновление тарифов",
                variable=var,
                value=4).pack(anchor=tk.W)

ttk.Radiobutton(frame,
                text="Обновление справочника организаций",
                variable=var,
                value=5).pack(anchor=tk.W)
ttk.Radiobutton(frame,
                text="Вставка тарифов диспансеризации",
                variable=var,
                value=6).pack(anchor=tk.W)

ttk.Radiobutton(frame,
                text="Преобразования файла тарифов по диспансеризации",
                variable=var,
                value=7).pack(anchor=tk.W)




ttk.Button(frame,
           text="Запустить",
           command=run_selected).pack(pady=15)


root.mainloop()
