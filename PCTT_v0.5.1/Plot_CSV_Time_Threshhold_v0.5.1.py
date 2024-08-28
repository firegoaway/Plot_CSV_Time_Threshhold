# Парс и io
import csv
import configparser
import re

# GUI
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# Словари
import os

# Графики
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Матан
import math

# Начнём с простого GUI
class MultiInputWindow(tk.Tk):
    def __init__(self, H=None, Cs=None, threshold=None, Fpom=None):
        super().__init__()
        self.title("PCTT v0.5.1")
        self.iconbitmap('.gitpics\\pctt.ico')
        self.wm_iconbitmap('.gitpics\\pctt.ico')
        
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
        
        ttk.Button(self, text="Draw", command=self.submit).grid(row=6, column=0, columnspan=2, padx=10, pady=10)
    
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
                self.destroy()
            else:
                raise ValueError("Заполните все поля!")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверные данные. Проверьте правильность введённых значений и попробуйте снова.")

config = configparser.ConfigParser()

file_IniHZ = 'IniHZ.ini'
file_InideltaZ = 'InideltaZ.ini'
file_IniSetpoint = 'IniSetpoint.ini'
file_IniQuantity = 'IniQuantity.ini'
file_IniFpom = 'IniFpom.ini'

value_IniHZ = None
value_InideltaZ = None
value_IniSetpoint = None
value_IniQuantity = None
value_IniFpom = None

def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)
    
if os.path.isfile(file_IniHZ) and os.path.isfile(file_InideltaZ) and os.path.isfile(file_IniSetpoint):
    try:
        config.read(file_IniHZ, encoding='utf-16')
        value_IniHZ = config['IniHZ']['HZ']
    except Exception as e:
        print(f"Error reading HZ value from {file_IniHZ}: {e}")

    try:
        config.read(file_InideltaZ, encoding='utf-16')
        value_InideltaZ = config['InideltaZ']['deltaZ']
    except Exception as e:
        print(f"Error reading deltaZ value from {file_InideltaZ}: {e}")
        
    try:
        config.read(file_IniSetpoint, encoding='utf-16')
        value_IniSetpoint = config['IniSetpoint']['setpoint']
    except Exception as e:
        print(f"Error reading setpoint value from {file_IniSetpoint}: {e}")
        
    try:
        config.read(file_IniQuantity, encoding='utf-16')
        value_IniQuantity = config['IniQuantity']['Quantity']
    except Exception as e:
        print(f"Error reading Quantity value from {file_IniQuantity}: {e}")

    try:
        config.read(file_IniFpom, encoding='utf-16')
        value_IniFpom = config['IniFpom']['Fpom']
    except Exception as e:
        print(f"Error reading Fpom value from {file_IniFpom}: {e}")

    input_window = MultiInputWindow(H=value_IniHZ, Cs=value_InideltaZ, threshold=value_IniSetpoint, Fpom=value_IniFpom)

else:
    input_window = MultiInputWindow()

input_window.mainloop()

input_file_path = input_window.file_path
input_H = float(input_window.H)
input_Cs = float(input_window.Cs)
input_threshold = float(input_window.threshold)
quantity = value_IniQuantity
input_Fpom = input_window.Fpom

R = None
if input_H <= 3.5:
    R = 6.4
elif input_H > 3.5 and input_H <= 6:
    R = 6.05
elif input_H > 6 and input_H <= 10:
    R = 5.7
elif input_H > 10:
    R = 5.35

L = R * math.sqrt(2)
print(f'L = {L}')

# Используем значение Fpom из GUI, Если оно валидно и не ранво 0, в противном случае используем значение F по умолчанию
if input_Fpom and input_Fpom != 0:
    input_Fpom = float(input_Fpom)
    F = input_Fpom
    print(f'F (используем значение Fпом = {input_Fpom} из GUI) = {F}')
else:
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

    with open(input_file_path, 'r') as infile, open(output_file_path, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        next(reader)
        headers = next(reader)
        headers = [header.replace('"', '').replace(' ', '') for header in headers]
        
        writer.writerow(headers)
        
        valid_columns = [i for i, header in enumerate(headers) if re.match(r'DEVC_X\d+Y\d+_MESH_\d+', header) or header == 'Time']
        
        filtered_data = []
        for row in reader:
            filtered_row = [convert_scientific_to_float(row[i]) for i in valid_columns]
            writer.writerow(filtered_row)
            filtered_data.append(filtered_row)
        
        time_index = valid_columns.index(headers.index('Time'))
        
        critical_time = None
        deff = None
        deff_values = []
        
        for i, row in enumerate(filtered_data):
            if (quantity == "VISIBILITY"):
                count = sum(1 for val in row if isinstance(val, float) and val <= input_threshold)
            else:
                count = sum(1 for val in row if isinstance(val, float) and val >= input_threshold)
            if count >= Cc:
                critical_time = row[time_index]
                break
            else:
                deff = math.sqrt((4 * (count * input_Cs)) / math.pi)
                deff_values.append(deff)
    
    time_values = [row[time_index] for row in filtered_data]
    relevant_time_values = time_values[:len(deff_values)]
    devc_data = {headers[i]: [row[i] for row in filtered_data] for i in valid_columns if headers[i] != 'Time'}
    
    # Обозначаем пути для сохранения картинок
    output_folder_path = os.path.normpath(os.path.join(os.path.dirname(input_file_path), '..', '..', '..', '..'))
    second_folder_name = os.path.basename(os.path.normpath(os.path.join(os.path.dirname(input_file_path), '..', '..')))
    output_file_name = f"deff_{second_folder_name}_plot.png"
    output_file_path = os.path.join(output_folder_path, output_file_name)

    # Создаем полотно
    plt.figure(figsize=(12,4))
    
    for header, values in devc_data.items():
        plt.plot(time_values, values)
    
    if critical_time is not None:
        plt.axvline(x=critical_time, color='red', linestyle='--', lw=3, label=f'tпор = {critical_time:.2f} (сек)')
    else:
        messagebox.showinfo("Проверка данных", "Проверьте введённые данные. Возможно вы неправильно указали предельное значение параметра, воздействующего на ИП ДОТ.")
        print("Значение critical_time не найдено.")
    
    measure_units = ""
    if (quantity == "VISIBILITY"):
        measure_units = "м"
    elif (quantity == "EXTINCTION COEFFICIENT"):
        measure_units = "дБ/м"
    elif (quantity == "OPTICAL DENSITY"):
        measure_units = "Нп/м"
    
    f1 = critical_time + 60 + 20
    f2f4 = critical_time + 30 + 20
    
    plt.plot(relevant_time_values, deff_values, color='black', linewidth=5, label='dэфф (м)')
    plt.axhline(y=L, color='green', linestyle='--', lw=3, label=f'dэфф = {max(deff_values):.3f} (м)')
    plt.axhline(y=input_threshold, color='blue', linestyle='--', lw=3, label=f'Крит. знач. параметра = {input_threshold:.3f} ({measure_units})')
    plt.xlabel(f'Время (сек)\n\nВремя начала эвакуации tнэ для Ф1 = {critical_time:.2f} + 60 + 0 + 20 = {f1:.2f} (сек)\nВремя начала эвакуации tнэ для Ф2-Ф5 = {critical_time:.2f} + 30 + 0 + 20 = {f2f4:.2f} (сек)')
    plt.ylabel(f'Значение параметра ({measure_units})')
    plt.title(f'График dэфф и значений параметра,\nвоздействующего на ИП ДОТ, во всех точках в области F', fontsize=12)
    plt.grid(True)
    plt.legend(loc='center left')
    
    # Берём min и max от d_eff для скалировпния по оси Y
    min_deff = min(deff_values)
    max_deff = max(deff_values)
    
    # Берём min = 0 и max = critical_time для скалировпния по оси X
    min_time = 0
    max_time = critical_time

    plt.ylim(bottom=min_deff - (0.1 * (max_deff - min_deff)), 
             top=max_deff + (0.1 * (max_deff - min_deff)))  # Добавляем сверху и снизу небольшие пустоты

    plt.xlim(left=min_time - (0.1 * (max_time - min_time)), 
             right=max_time + (0.1 * (max_time - min_time)))  # Добавляем слева и справа небольшие пустоты
             
    # https://stackoverflow.com/questions/36162414/how-to-add-bold-annotated-text-to-a-plot
    
    addToClipBoard(second_folder_name)

    # Сохраняем график в изображение, GUI не отображаем
    plt.savefig(output_file_path, bbox_inches='tight', format='png')  # Можно добавить dpi=300 для большего разрешения картинок
    plt.close()  # Закрываем инстанс, освобождаем память