# Парс и io
import csv
import configparser
import re

# GUI
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter import StringVar
from tkinter import Tk, Toplevel, Button, Label

# Словари
import os
import threading

# Графики
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# Матан
import math

# Начнём с простого GUI
class MultiInputWindow(tk.Tk):
    def __init__(self, H=None, Cs=None, threshold=None, Fpom=None, quantity=None):
        super().__init__()

        current_directory = os.path.dirname(__file__)
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        icon_path = os.path.join(parent_directory, '.gitpics', 'pctt.ico')

        self.title("PCTT v0.6.1")
        self.iconbitmap(icon_path)
        self.wm_iconbitmap(icon_path)
        
        self.quantity = value_IniQuantity

        self.H = H
        self.Cs = Cs
        self.file_path = None
        self.threshold = threshold
        self.Fpom = Fpom

        ttk.Label(self, text="Hпом = ").grid(row=0, column=0, padx=10, pady=10)
        self.H_entry = ttk.Entry(self)
        if H is not None:
            self.H_entry.insert(0, H)
        self.H_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self, text="Cs = ").grid(row=1, column=0, padx=10, pady=10)
        self.Cs_entry = ttk.Entry(self)
        if Cs is not None:
            self.Cs_entry.insert(0, Cs)
        self.Cs_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self, text="Предельное значение параметра, воздействующего на ИП ДОТ:").grid(row=2, column=0, padx=10, pady=10)
        self.threshold_entry = ttk.Entry(self)
        if threshold is not None:
            self.threshold_entry.insert(0, threshold)
        self.threshold_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self, text="Fпом = ").grid(row=3, column=0, padx=10, pady=10)
        self.Fpom_entry = ttk.Entry(self)
        if Fpom is not None:
            self.Fpom_entry.insert(0, Fpom)
        self.Fpom_entry.grid(row=3, column=1, padx=10, pady=10)

        ttk.Button(self, text="Выберите CSV файл", command=self.select_file).grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.file_path_label = ttk.Label(self, text="")
        self.file_path_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        ttk.Button(self, text="Рассчитать", command=self.submit).grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # Прогресс бар
        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate", length = 200)
        self.progress.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
        self.progress_label = ttk.Label(self, text="")
        self.progress_label.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Файлы формата CSV", "*.csv")])
        self.file_path_label.config(text=self.file_path if self.file_path else "")
    
    def submit(self):
        try:
            self.H = float(self.H_entry.get())
            self.Cs = float(self.Cs_entry.get())
            self.threshold = float(self.threshold_entry.get())
            Fpom_value = self.Fpom_entry.get()
            if Fpom_value:
                self.Fpom = float(Fpom_value)
            else:
                self.Fpom = None

            if self.file_path and self.H and self.threshold and self.Cs is not None:
                threading.Thread(target=self.process_csv).start()
            else:
                raise ValueError("Заполните все поля!")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверные данные. Проверьте правильность введённых значений и попробуйте снова.")

    def process_csv(self):
        input_file_path = self.file_path
        input_H = float(self.H)
        input_Cs = float(self.Cs)
        input_threshold = float(self.threshold)
        input_Fpom = self.Fpom

        R = None
        if input_H <= 3.5:
            R = 6.4
        elif input_H > 3.5 and input_H <= 6:
            R = 6.05
        elif input_H > 6 and input_H <= 10:
            R = 5.7
        elif input_H > 10:
            R = 5.35

        if input_Fpom and input_Fpom != 0:
            input_Fpom = float(input_Fpom)
            F = input_Fpom
            print(f'F (используем значение Fпом = {input_Fpom} из GUI) = {F}')
        else:
            L = R * math.sqrt(2)
            print(f'L = {L}')
            F = math.ceil((math.pi * (L**2) / 4))
            print(f'F (по умолчанию) = {F}')

        Cc = math.ceil(F / input_Cs)
        print(f'Cc = {Cc}')

        if input_file_path:
            input_file_name = os.path.basename(input_file_path)
            output_file_path = os.path.join(os.path.dirname(input_file_path), input_file_name.replace('.csv', '_output.csv'))

            def convert_scientific_to_float(value):
                try:
                    return float(value)
                except ValueError:
                    return value

            with open(input_file_path, 'r') as infile:
                reader = csv.reader(infile)
                
                next(reader)
                headers = next(reader)
                headers = [header.replace('"', '').replace(' ', '') for header in headers]
                
                #print("Заголовки CSV таблицы:", headers)  # Дебаг

                valid_columns = [i for i, header in enumerate(headers) if re.match(r'DEVC_X\d+Y\d+_MESH_\d+', header) or header == 'Time']

                total_rows = sum(1 for _ in open(input_file_path)) - 1
                self.progress['maximum'] = total_rows

                filtered_data = []
                for i, row in enumerate(reader):
                    filtered_row = [convert_scientific_to_float(row[i]) for i in valid_columns]
                    filtered_data.append(filtered_row)

                    if len(filtered_row) > 0:
                        with open(output_file_path, 'a', newline='') as outfile:
                            writer = csv.writer(outfile)
                            writer.writerow(filtered_row)

                    # Обновляем прогресс
                    self.progress['value'] = i + 1
                    self.progress_label.config(text=f"Вычисляем количество точек в области F, значение параметра в которых достигло критической отметки: {i + 1} / {total_rows} / {Cc}")
                    self.update_idletasks()

                time_index = valid_columns[headers.index('Time')]
                critical_time = None
                deff_values = []
                
                self.progress['value'] = 0
                
                for row in filtered_data:
                    if (self.quantity == "VISIBILITY"):
                        count = sum(1 for val in row if isinstance(val, float) and val <= input_threshold)
                    else:
                        count = sum(1 for val in row if isinstance(val, float) and val >= input_threshold)
                    if count >= Cc:
                        critical_time = row[time_index]
                        break
                    else:
                        deff = math.sqrt((4 * (count * input_Cs)) / math.pi)
                        L = deff
                        deff_values.append(deff)
                        self.progress['maximum'] = L
                        self.progress['value'] = deff
                        self.progress_label.config(text=f"Рассчитываем dэфф: {deff} / {L}")
                        self.update_idletasks()

                time_values = [row[time_index] for row in filtered_data if len(row) > time_index]
                relevant_time_values = time_values[:len(deff_values)]
                devc_data = {}
                for index in valid_columns:
                    if index < len(headers):
                        devc_data[headers[index]] = [row[index] for row in filtered_data if index < len(row)]
                
                self.progress['value'] = 0
                self.progress['maximum'] = 100
                
                self.progress['value'] = 25
                self.progress_label.config(text="Подготавливаем график")
                self.update_idletasks()

                # Обозначаем пути для сохранения картинок
                output_folder_path = os.path.normpath(os.path.join(os.path.dirname(input_file_path), '..', '..', '..', '..'))
                second_folder_name = os.path.basename(os.path.normpath(os.path.join(os.path.dirname(input_file_path), '..', '..')))
                output_file_name = f"deff_{second_folder_name}_plot.png"
                output_file_path = os.path.join(output_folder_path, output_file_name)
                
                measure_units = ""
                if (self.quantity == "VISIBILITY"):
                    measure_units = "м"
                elif (self.quantity == "EXTINCTION COEFFICIENT"):
                    measure_units = "дБ/м"
                elif (self.quantity == "OPTICAL DENSITY"):
                    measure_units = "Нп/м"

                # Создаем полотно
                plt.figure(figsize=(12,4))
                
                # Создаём вторую ось Y
                ax1 = plt.gca()  # Get current axis
                ax2 = ax1.twinx()  # Создаём твин-копию ax1
                
                total_cells = 0
                filled_cells = 0
                
                # Для первой оси Y рисуем значения devc_data (каждой точки)
                for header, values in devc_data.items():
                    if len(time_values) != len(values):
                        print(f"Skipping plot due to dimension mismatch: {len(time_values)} (time) vs {len(values)} (values)")
                    else:
                        ax1.plot(time_values, values, linestyle='solid', lw=0.1)
                    
                    total_cells += len(header)
                    filled_cells += sum(1 for value in header)
                    
                    self.progress['maximum'] = total_cells
                    self.progress['value'] = filled_cells
                    self.progress_label.config(text=f"Поиск ненулевых значений для вычисления tпор: {filled_cells} / {total_cells}")
                    self.update_idletasks()

                self.progress['maximum'] = 100
                self.progress['value'] = 45
                self.progress_label.config(text="Подготавливаем график.")
                self.update_idletasks()
                
                # Рисуем значения d_eff на полотне ax2 с собственной осью Y
                ax2.plot(relevant_time_values, deff_values, color='black', linewidth=5, label='dэфф (м)')
                
                if critical_time is not None:
                    ax1.axvline(x=critical_time, color='red', linestyle='--', lw=3, label=f'tпор = {critical_time:.2f} (сек)')
                else:
                    messagebox.showinfo("Проверка данных", "Проверьте введённые данные. Возможно вы неправильно указали предельное значение параметра, воздействующего на ИП ДОТ.")
                    print("Значение critical_time не найдено.")
                
                self.progress['value'] = 65
                self.progress_label.config(text="Подготавливаем график..")
                self.update_idletasks()
                
                # Назначаем строки заголовков для обеих осей Y
                ax1.set_ylabel(f'Значение параметра ({measure_units})')
                ax2.set_ylabel('dэфф (м)')
                
                f1 = critical_time + 60 + 20
                f2f4 = critical_time + 30 + 20
                
                self.progress['value'] = 78
                self.progress_label.config(text="Подготавливаем график...")
                self.update_idletasks()
                
                # Добавляем горизонтальную линию для L и input_threshold на соответствующих осях
                ax1.axhline(y=input_threshold, color='blue', linestyle='--', lw=3, label=f'Крит. знач. параметра = {input_threshold:.3f} ({measure_units})', alpha=0.5)
                ax2.axhline(y=L, color='green', linestyle='--', lw=3, label=f'dэфф = {max(deff_values):.3f} (м)', alpha=0.5)
                
                self.progress['value'] = 84
                self.progress_label.config(text="Подготавливаем график....")
                self.update_idletasks()
                
                # Периферия
                ax1.set_xlabel(f'Время (сек)\n\nВремя начала эвакуации tнэ для Ф1 = {critical_time:.2f} + 60 + 0 + 20 = {f1:.2f} (сек) \nВремя начала эвакуации tнэ для Ф2-Ф5 = {critical_time:.2f} + 30 + 0 + 20 = {f2f4:.2f} (сек)')
                plt.title(f'График dэфф и значений параметра,\nвоздействующего на ИП ДОТ, во всех точках в области F', fontsize=12)
                plt.grid(True)
                lines1, labels1 = ax1.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(lines1 + lines2, labels1 + labels2, loc='center left')
                
                self.progress['value'] = 90
                self.progress_label.config(text="Подготавливаем график......")
                self.update_idletasks()

                ax1.set_ylim(bottom=0, top=input_threshold * 1.1)
                ax1.set_xlim(left=0, right=max(critical_time, 0) * 1.1)
                
                ax2.set_ylim(bottom=min(deff_values) * 0.9, top=max(deff_values) * 1.1)
                ax2.set_xlim(left=0, right=max(critical_time, 0) * 1.1)
                
                self.progress['value'] = 90
                self.progress_label.config(text="Подготавливаем график......")
                self.update_idletasks()
                         
                # https://stackoverflow.com/questions/36162414/how-to-add-bold-annotated-text-to-a-plot
                
                addToClipBoard(second_folder_name)

                # Сохраняем график в изображение, GUI не отображаем
                plt.savefig(output_file_path, bbox_inches='tight', format='png')  # Можно добавить dpi=300 для большего разрешения картинок
                
                self.progress['value'] = 100
                self.progress_label.config(text="Сохраняем график")
                self.update_idletasks()
                
                plt.close()  # Закрываем инстанс, освобождаем память

                #messagebox.showinfo("tпор", "Расчёт tпор завершён!")
                
                self.withdraw() # Вырубаем GUI
                
                self.progress['value'] = 0  # ресетим прогресс бар
                
                #os.startfile(output_folder_path)
                #os.startfile(output_file_path)
                
                def OpenPNG():
                    os.startfile(output_file_path)

                def OpenPNGfolder():
                    os.startfile(output_folder_path)

                def Close():
                    self.quit()  # Закрываем основное окно tkinter

                custom_message_box(OpenPNG, OpenPNGfolder, Close)
                
                #self.mainloop()

def custom_message_box(callback_open_png, callback_open_folder, callback_close):
    def on_open_png():
        callback_open_png()
        #top.destroy()
    
    def on_open_folder():
        callback_open_folder()
        #top.destroy()
    
    def on_close():
        callback_close()
        top.destroy()

    top = Toplevel()
    top.title("PCTT v0.6.1")
    top.geometry("400x100")
    
    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    icon_path = os.path.join(parent_directory, '.gitpics', 'pctt.ico')
    
    top.iconbitmap(icon_path)
    top.wm_iconbitmap(icon_path)
    
    top.overrideredirect(False)  # Скрываем стандартную рамку

    label = Label(top, text="Выберите действие", padx=10, pady=10)
    label.pack(pady=(10, 0))
    
    button_frame = ttk.Frame(top)
    button_frame.pack(pady=10)
    
    Button(button_frame, text="Показать график dэфф", command=on_open_png).pack(side='left', padx=5)
    Button(button_frame, text="Открыть папку с графиком", command=on_open_folder).pack(side='left', padx=5)
    Button(button_frame, text="Выйти", command=on_close).pack(side='left', padx=5)
    
    top.update_idletasks()
    width = top.winfo_width()
    height = top.winfo_height()
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry(f'{width}x{height}+{x}+{y}')

    top.transient()  # Поверх других окон
    top.grab_set()  # Модальное окно
    top.protocol("WM_DELETE_WINDOW", on_close)  # Закрытие окна

def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)

# Конфигурация ini
config = configparser.ConfigParser()

current_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
inis_path = os.path.join(parent_directory, 'inis')

iniHZ_path = os.path.join(inis_path, 'IniHZ.ini')
InideltaZ_path = os.path.join(inis_path, 'InideltaZ.ini')
IniSetpoint_path = os.path.join(inis_path, 'IniSetpoint.ini')
IniQuantity_path = os.path.join(inis_path, 'IniQuantity.ini')
IniFpom_path = os.path.join(inis_path, 'IniFpom.ini')

value_IniHZ = None
value_InideltaZ = None
value_IniSetpoint = None
value_IniQuantity = None
value_IniFpom = None

if os.path.isfile(iniHZ_path):
    try:
        config.read(iniHZ_path, encoding='utf-16')
        value_IniHZ = config['IniHZ']['HZ']
    except Exception as e:
        print(f"Error reading HZ value from {iniHZ_path}: {e}")

if os.path.isfile(InideltaZ_path):
    try:
        config.read(InideltaZ_path, encoding='utf-16')
        value_InideltaZ = config['InideltaZ']['deltaZ']
    except Exception as e:
        print(f"Error reading deltaZ value from {InideltaZ_path}: {e}")

if os.path.isfile(IniSetpoint_path):
    try:
        config.read(IniSetpoint_path, encoding='utf-16')
        value_IniSetpoint = config['IniSetpoint']['setpoint']
    except Exception as e:
        print(f"Error reading setpoint value from {IniSetpoint_path}: {e}")

if os.path.isfile(IniQuantity_path):
    try:
        config.read(IniQuantity_path, encoding='utf-16')
        value_IniQuantity = config['IniQuantity']['Quantity']
    except Exception as e:
        print(f"Error reading Quantity value from {IniQuantity_path}: {e}")

if os.path.isfile(IniFpom_path):
    try:
        config.read(IniFpom_path, encoding='utf-16')
        value_IniFpom = config['IniFpom']['Fpom']
    except Exception as e:
        print(f"Error reading Fpom value from {IniFpom_path}: {e}")

# Обработка начальной загрузки
input_window = MultiInputWindow(H=value_IniHZ, Cs=value_InideltaZ, threshold=value_IniSetpoint, Fpom=value_IniFpom, quantity=value_IniQuantity)
input_window.mainloop()