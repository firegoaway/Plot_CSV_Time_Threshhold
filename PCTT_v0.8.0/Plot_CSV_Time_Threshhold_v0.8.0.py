# Парс и io
import csv
import configparser
import re
import sys

# Функторы
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
from tqdm import tqdm
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
import concurrent.futures

# GUI
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter import StringVar
from tkinter import Tk, Toplevel, Button, Label, Frame
import tkinter.font as tkFont

# Словари
import os
import threading
import time

# Графики
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# Матан
import math

# Класс для создания всплывающих подсказок
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        frame = Frame(self.tooltip, background="#2c3e50", borderwidth=1, relief="solid")
        frame.pack(fill="both", expand=True)

        label = Label(frame, text=self.text, background="#2c3e50", foreground="white",
                     padx=8, pady=4, wraplength=250, font=("Segoe UI", 9))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

# Начнём с простого GUI
class MultiInputWindow(tk.Tk):
    def __init__(self, H=None, Cs=None, threshold=None, Fpom=None, quantity=None):
        super().__init__()

        # Определение цветовой схемы
        self.colors = {
            "primary": "#3498db",       # Основной цвет (синий)
            "secondary": "#2ecc71",     # Вторичный цвет (зеленый)
            "accent": "#e74c3c",        # Акцентный цвет (красный)
            "bg_light": "#f5f5f5",      # Светлый фон
            "bg_dark": "#2c3e50",       # Темный фон
            "text_light": "#ecf0f1",    # Светлый текст
            "text_dark": "#34495e",     # Темный текст
            "border": "#bdc3c7",        # Цвет границ
            "success": "#27ae60",       # Цвет успеха
            "warning": "#f39c12",       # Цвет предупреждения
            "error": "#c0392b"          # Цвет ошибки
        }

        current_directory = os.path.dirname(__file__)
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        icon_path = os.path.join(parent_directory, '.gitpics', 'pctt.ico')

        self.title("PCTT v0.8.0")
        self.iconbitmap(icon_path)
        self.wm_iconbitmap(icon_path)
        self.geometry("600x780")
        self.configure(bg=self.colors["bg_light"])
        self.minsize(600, 700)  # Устанавливаем минимальный размер окна
        
        self.quantity = quantity or value_IniQuantity
        self.H = H
        self.Cs = Cs # Store the initial Cs value (might be None)
        self.file_path = None
        self.threshold = threshold
        self.Fpom = Fpom
        
        # Флаг завершения предобработки файла
        self.preprocessing_complete = False
        self.processing_in_progress = False
        
        # Создаем стиль для виджетов
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Используем более современную тему
        
        # Настраиваем стили для разных виджетов
        self.style.configure("TFrame", background=self.colors["bg_light"])
        self.style.configure("TLabel", background=self.colors["bg_light"], font=("Segoe UI", 10))
        self.style.configure("TButton", 
                            font=("Segoe UI", 10, "bold"), 
                            background=self.colors["primary"], 
                            foreground=self.colors["text_light"])
        self.style.map("TButton",
                      background=[("active", self.colors["secondary"]), 
                                  ("disabled", self.colors["border"])])
        
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground=self.colors["primary"])
        self.style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"), foreground=self.colors["text_dark"])
        
        # Стиль для LabelFrame
        self.style.configure("TLabelframe", background=self.colors["bg_light"])
        self.style.configure("TLabelframe.Label", 
                            background=self.colors["bg_light"], 
                            foreground=self.colors["primary"],
                            font=("Segoe UI", 11, "bold"))
        
        # Стиль для прогресс-бара
        self.style.configure("TProgressbar", 
                            troughcolor=self.colors["bg_light"], 
                            background=self.colors["secondary"])
        
        # Основной контейнер
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок приложения
        header_label = ttk.Label(main_frame, text="Расчет tпор", style="Header.TLabel")
        header_label.pack(fill=tk.X, pady=(0, 15))
        
        # Раздел с параметрами
        param_frame = ttk.LabelFrame(main_frame, text="Параметры расчета", padding="15")
        param_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Сетка для параметров (2 колонки на каждой строке)
        param_grid = ttk.Frame(param_frame)
        param_grid.pack(fill=tk.X, padx=5, pady=5)
        
        for i in range(2):
            param_grid.columnconfigure(i*2, weight=1)
            param_grid.columnconfigure(i*2+1, weight=2)
        
        # Поле Hпом
        ttk.Label(param_grid, text="Hпом = ").grid(row=0, column=0, sticky=tk.W, padx=5, pady=8)
        self.H_entry = ttk.Entry(param_grid, width=15)
        if H is not None:
            self.H_entry.insert(0, H)
        self.H_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=8)
        ToolTip(self.H_entry, "Высота помещения, м")
        
        # Поле Cs
        ttk.Label(param_grid, text="Cs = ").grid(row=0, column=2, sticky=tk.W, padx=5, pady=8)
        self.Cs_entry = ttk.Entry(param_grid, width=15) # Restore original width
        if self.Cs is not None: # Populate only if Cs has a value from ini
            self.Cs_entry.insert(0, self.Cs)
        self.Cs_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=8)
        ToolTip(self.Cs_entry, "Размер ячейки, м")

        # Button to calculate Cs from FDS
        cs_calc_btn = ttk.Button(param_grid, text="...", width=3, command=self.get_cs_from_fds_ini) # Connect button here
        cs_calc_btn.grid(row=0, column=4, sticky=tk.W, padx=(0, 5), pady=8)
        ToolTip(cs_calc_btn, "Рассчитать Cs из FDS файла (требуется ID процесса)")

        # Поле порогового значения
        ttk.Label(param_grid, text="Предельное значение:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=8)
        self.threshold_entry = ttk.Entry(param_grid, width=15)
        if threshold is not None:
            self.threshold_entry.insert(0, threshold)
        self.threshold_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=8)
        ToolTip(self.threshold_entry, "Предельное значение параметра, воздействующего на пожарный извещатель")
        
        # Поле Fпом
        ttk.Label(param_grid, text="Fпом = ").grid(row=1, column=2, sticky=tk.W, padx=5, pady=8)
        self.Fpom_entry = ttk.Entry(param_grid, width=15)
        if Fpom is not None:
            self.Fpom_entry.insert(0, Fpom)
        self.Fpom_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=8)
        ToolTip(self.Fpom_entry, "Площадь помещения, м² (если не указана, будет рассчитана автоматически)")
        
        # Раздел выбора файла
        file_frame = ttk.LabelFrame(main_frame, text="Файл данных", padding="15")
        file_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Стилизованная кнопка выбора файла с иконкой
        file_btn_frame = ttk.Frame(file_frame)
        file_btn_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Кнопка выбора файла
        select_file_btn = ttk.Button(file_btn_frame, text="Выберите CSV файл", 
                                   command=self.select_file, 
                                   style="TButton", width=25)
        select_file_btn.pack(side='left', padx=5)
        
        # Добавляем подсказку о горячей клавише
        file_shortcut_label = ttk.Label(file_btn_frame, text="Ctrl+O", 
                                      font=("Segoe UI", 9, "italic"),
                                      foreground=self.colors["text_dark"])
        file_shortcut_label.pack(side='left', padx=5)
        
        self.file_path_label = ttk.Label(file_frame, text="", wraplength=550)
        self.file_path_label.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Кнопка расчета с подсказкой о горячей клавише
        calc_btn_frame = ttk.Frame(main_frame)
        calc_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.calculate_btn = ttk.Button(calc_btn_frame, text="Рассчитать", 
                                      command=self.submit, state="disabled", 
                                      style="TButton")
        self.calculate_btn.pack(side='left', fill=tk.X, expand=True, padx=5)
        
        # Подсказка о горячей клавише для расчета
        calc_shortcut_label = ttk.Label(calc_btn_frame, text="F5", 
                                      font=("Segoe UI", 9, "italic"),
                                      foreground=self.colors["text_dark"])
        calc_shortcut_label.pack(side='left', padx=5)
        
        # Прогресс бар и статус
        progress_frame = ttk.Frame(main_frame, padding="5")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", 
                                       mode="determinate", length=550)
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="", 
                                       wraplength=550, 
                                       font=("Segoe UI", 10, "bold"),
                                       foreground=self.colors["primary"])
        self.progress_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Детальная информация о процессе
        self.detail_label = ttk.Label(progress_frame, text="", 
                                     wraplength=550, 
                                     font=("Segoe UI", 9),
                                     foreground=self.colors["text_dark"])
        self.detail_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Добавляем информацию о типе данных в статусную строку
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(10, 5))
        
        info_text = f"Тип данных: {self.quantity}" if self.quantity else ""
        self.info_label = ttk.Label(status_frame, text=info_text, 
                                   font=("Segoe UI", 9), 
                                   foreground=self.colors["text_dark"])
        self.info_label.pack(side=tk.LEFT)
        
        # Добавляем версию в правый угол статусной строки
        version_label = ttk.Label(status_frame, text="v0.8.0", 
                                 font=("Segoe UI", 9, "italic"), 
                                 foreground=self.colors["text_dark"])
        version_label.pack(side=tk.RIGHT)
        
        # Регистрация горячих клавиш
        self.bind("<Control-o>", lambda event: self.select_file())
        self.bind("<F5>", lambda event: self.try_submit())
        self.bind("<Return>", lambda event: self.try_submit())
        self.bind("<Escape>", lambda event: self.quit())
        
        # Создаем связь между полями ввода по Tab
        self.H_entry.bind("<Return>", lambda event: self.Cs_entry.focus_set())
        self.Cs_entry.bind("<Return>", lambda event: self.threshold_entry.focus_set())
        self.threshold_entry.bind("<Return>", lambda event: self.Fpom_entry.focus_set())
        self.Fpom_entry.bind("<Return>", lambda event: self.try_submit())
        
        # Центрирование окна на экране
        self.center_window()
        
        # Начальная подсказка
        self.update_progress_label("Введите параметры и выберите файл")
        self.update_detail_label("Для начала работы заполните все поля и выберите CSV файл с данными")
        
        # Устанавливаем фокус на первое поле ввода
        self.H_entry.focus_set()

        # Automatically attempt to calculate Cs from FDS ini on startup
        self.get_cs_from_fds_ini()
    
    def get_cs_from_fds_ini(self):
        """Reads FDS path from ini based on ProcessID, calculates min Cs, and updates the Cs_entry field."""
        global ProcessID # Access the global ProcessID variable

        if ProcessID is None:
            messagebox.showerror("Ошибка", "ID процесса не найден. Невозможно определить путь к FDS файлу в .ini.")
            self.update_progress_label("Ошибка: ID процесса не найден")
            self.update_detail_label("Запустите скрипт с ID процесса в качестве аргумента командной строки")
            return

        try:
            # Construct the ini file path
            current_directory = os.path.dirname(__file__)
            parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
            inis_path = os.path.join(parent_directory, 'inis')
            ini_file_path = os.path.join(inis_path, f'filePath_{ProcessID}.ini')

            if not os.path.exists(ini_file_path):
                messagebox.showerror("Ошибка", f"Файл .ini не найден: {ini_file_path}")
                self.update_progress_label("Ошибка: .ini файл не найден")
                self.update_detail_label(f"Проверьте наличие файла {os.path.basename(ini_file_path)} в папке 'inis'")
                return

            # Read the ini file
            config = configparser.ConfigParser()
            config.read(ini_file_path, encoding='utf-16') # Assume utf-16 like in Refine

            if 'filePath' in config and 'filePath' in config['filePath']:
                fds_path = config['filePath']['filePath']
            else:
                messagebox.showerror("Ошибка", f"Не удалось найти ключ 'filePath' в секции '[filePath]' файла {os.path.basename(ini_file_path)}")
                self.update_progress_label("Ошибка: Не найден путь в .ini")
                self.update_detail_label(f"Проверьте структуру файла {os.path.basename(ini_file_path)}")
                return

            if not fds_path or not os.path.exists(fds_path):
                    messagebox.showerror("Ошибка", f"FDS файл не найден по пути из .ini: {fds_path}")
                    self.update_progress_label("Ошибка: FDS файл не найден")
                    self.update_detail_label(f"Путь из .ini: {fds_path}")
                    return

            # Calculate Cs using the existing method
            self.update_progress_label(f"Расчет Cs из файла: {os.path.basename(fds_path)}...")
            self.update_detail_label("Анализ строк MESH...")
            self.update_idletasks()

            min_cs = self.calculate_cs_from_fds(fds_path)

            if min_cs is not None:
                self.Cs_entry.delete(0, tk.END)
                self.Cs_entry.insert(0, f"{min_cs:.6f}") # Format to 6 decimal places
                self.update_progress_label(f"Cs рассчитан: {min_cs:.6f} м")
                self.update_detail_label(f"Минимальный размер ячейки из файла '{os.path.basename(fds_path)}' (ID: {ProcessID})")
            else:
                # Error message likely shown by calculate_cs_from_fds
                self.update_progress_label("Ошибка расчета Cs")
                self.update_detail_label("Не удалось рассчитать Cs из FDS файла, указанного в .ini")

        except configparser.Error as e:
            messagebox.showerror("Ошибка чтения .ini", f"Ошибка при чтении файла {os.path.basename(ini_file_path)}: {str(e)}")
            self.update_progress_label("Ошибка чтения .ini")
            self.update_detail_label(f"Проверьте формат файла: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка при расчете Cs из .ini: {str(e)}")
            self.update_progress_label("Непредвиденная ошибка")
            self.update_detail_label(f"Ошибка: {str(e)}")
    
    def calculate_cs(self, xmin, xmax, i):
        """Вспомогательная функция для расчета размера ячейки по одной оси."""
        if i == 0: return float('inf') # Избегаем деления на ноль
        return (xmax - xmin) / i

    def calculate_cs_from_fds(self, file_path):
        """Читает FDS файл, парсит MESH и возвращает минимальный размер ячейки Cs."""
        min_cs = float('inf')
        meshes_found = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as file: # Используем utf-8 для большей совместимости
                for line in file:
                    # Используем более надежный regex для парсинга MESH
                    match = re.search(r'&MESH\s+.*?IJK\s*=\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*.*?XB\s*=\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*,\s*([-\d\.]+)', line, re.IGNORECASE)
                    if match:
                        meshes_found += 1
                        try:
                            I, J, K = map(int, match.group(1, 2, 3))
                            Xmin, Xmax, Ymin, Ymax, Zmin, Zmax = map(float, match.group(4, 5, 6, 7, 8, 9))
                            
                            cs_x = self.calculate_cs(Xmin, Xmax, I)
                            cs_y = self.calculate_cs(Ymin, Ymax, J)
                            cs_z = self.calculate_cs(Zmin, Zmax, K)
                            
                            current_min_cs = min(cs_x, cs_y, cs_z)
                            if current_min_cs < min_cs:
                                min_cs = current_min_cs
                        except ValueError:
                            # Пропускаем строку, если не удалось преобразовать числа
                            print(f"Предупреждение: Не удалось распарсить числа в строке MESH: {line.strip()}")
                            continue 
                            
            if meshes_found == 0:
                messagebox.showwarning("Не найдено", f"В файле '{os.path.basename(file_path)}' не найдено строк MESH.")
                return None
                
            if min_cs == float('inf'):
                messagebox.showerror("Ошибка расчета", "Не удалось рассчитать Cs. Возможно, неверный формат MESH.")
                return None
            
            return min_cs
            
        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл не найден: {file_path}")
            return None
        except Exception as e:
            messagebox.showerror("Ошибка чтения FDS", f"Произошла ошибка при чтении файла '{os.path.basename(file_path)}': {str(e)}")
            return None

    def select_fds_for_cs(self):
        """Открывает диалог выбора FDS файла и обновляет поле Cs."""
        try:
            filetypes = [("FDS файлы", "*.fds"), ("Все файлы", "*.*")]
            fds_path = filedialog.askopenfilename(
                filetypes=filetypes,
                title="Выберите FDS файл для расчета Cs"
            )
            
            if not fds_path:
                return # Пользователь отменил выбор
                
            self.update_progress_label(f"Расчет Cs из файла: {os.path.basename(fds_path)}...")
            self.update_detail_label("Анализ строк MESH...")
            self.update_idletasks()
            
            min_cs = self.calculate_cs_from_fds(fds_path)
            
            if min_cs is not None:
                self.Cs_entry.delete(0, tk.END)
                self.Cs_entry.insert(0, f"{min_cs:.6f}") # Форматируем до 6 знаков
                self.update_progress_label(f"Cs рассчитан: {min_cs:.6f} м")
                self.update_detail_label(f"Минимальный размер ячейки из файла '{os.path.basename(fds_path)}'")
            else:
                # Сообщение об ошибке уже показано в calculate_cs_from_fds
                self.update_progress_label("Ошибка расчета Cs")
                self.update_detail_label("Не удалось рассчитать Cs из выбранного файла")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при выборе FDS файла: {str(e)}")
            self.update_progress_label("Ошибка")
            self.update_detail_label(f"Ошибка при обработке FDS файла: {str(e)}")

    def try_submit(self, event=None):
        """Пытается запустить расчет если кнопка активна"""
        if self.calculate_btn['state'] == 'normal':
            self.submit()
    
    def center_window(self):
        """Центрирует окно на экране"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def select_file(self):
        try:
            # Сбрасываем флаг готовности и деактивируем кнопку расчета
            self.preprocessing_complete = False
            self.calculate_btn.config(state="disabled")
            
            # Сбрасываем прогресс-бар и метки статуса
            self.update_progress(0, 100)
            self.update_progress_label("Ожидание выбора файла...")
            self.update_detail_label("Выберите CSV файл с данными")
            
            # Создаем фильтр для CSV файлов
            filetypes = [
                ("CSV файлы", "*.csv"),
                ("Все файлы", "*.*")
            ]
            
            # Открываем диалог выбора файла
            self.file_path = filedialog.askopenfilename(
                filetypes=filetypes,
                title="Выберите CSV файл с данными для анализа"
            )
            
            if not self.file_path:
                # User canceled file selection
                self.update_progress_label("Выбор файла отменен")
                self.update_detail_label("Пожалуйста, выберите CSV файл для обработки")
                return
            
            # Обновляем UI с информацией о файле
            file_name = os.path.basename(self.file_path)
            file_dir = os.path.dirname(self.file_path)
            display_path = f"{file_name}\n{file_dir}"
            
            self.file_path_label.config(
                text=display_path,
                foreground=self.colors["primary"],
                font=("Segoe UI", 9, "bold")
            )
                
            # Check if file exists and is readable
            if not os.path.exists(self.file_path):
                messagebox.showerror("Ошибка", "Выбранный файл не существует")
                self.file_path_label.config(text="", foreground=self.colors["text_dark"])
                self.file_path = None
                return
                
            # Check if file is too large
            file_size_mb = os.path.getsize(self.file_path) / (1024 * 1024)
            
            # Показываем информацию о файле
            self.update_progress_label(f"Выбран файл: {file_name}")
            self.update_detail_label(f"Размер файла: {file_size_mb:.1f} МБ")
            
            # Запрос подтверждения для больших файлов
            if file_size_mb > 100:  # If file is larger than 100MB
                self.update_detail_label(f"Большой файл ({file_size_mb:.1f} МБ) - запрос подтверждения...")
                if not messagebox.askyesno("Предупреждение", 
                                          f"Выбранный файл имеет размер {file_size_mb:.1f} МБ. "
                                          f"Обработка может занять длительное время. Продолжить?"):
                    self.file_path_label.config(text="", foreground=self.colors["text_dark"])
                    self.file_path = None
                    self.update_progress_label("Обработка отменена")
                    self.update_detail_label("Выберите другой файл меньшего размера")
                    return
            
            # Определяем выходной файл
            input_file_name = os.path.basename(self.file_path)
            self.output_file_path = os.path.join(os.path.dirname(self.file_path), input_file_name.replace('.csv', '_output.csv'))
            
            # Настройка индикаторов обработки
            self.update_progress(0, 100)
            self.update_progress_label("Подготовка к предобработке файла...")
            self.update_detail_label(f"Файл: {input_file_name} | Размер: {file_size_mb:.1f} МБ")
            self.update_idletasks()
            
            # Информируем пользователя о предстоящей обработке
            strategy = "pandas" if file_size_mb < 500 else "dask с многопоточностью"
            self.update_detail_label(f"Будет использован метод: {strategy}")
            
            # Обновляем UI для плавности
            self.after(100, lambda: self.update_progress(2, 100))
            
            # Показываем анимацию загрузки на кнопке
            self.file_path_label.config(text=f"{display_path}\n\nОбработка...", foreground=self.colors["secondary"])
            
            # Запускаем предобработку в отдельном потоке
            self.processing_in_progress = True
            process_thread = threading.Thread(
                target=self.remove_zero_only_columns,
                args=(self.file_path, self.output_file_path),
                daemon=True
            )
            process_thread.start()
            
            # Запускаем функцию мониторинга статуса
            self.after(500, self.monitor_preprocessing_status)
            
        except Exception as e:
            error_msg = f"Произошла ошибка при выборе файла: {str(e)}"
            messagebox.showerror("Ошибка", error_msg)
            self.file_path_label.config(text="", foreground=self.colors["text_dark"])
            self.file_path = None
            self.processing_in_progress = False
    
    def monitor_preprocessing_status(self):
        """Функция для обновления статуса предобработки"""
        if self.processing_in_progress and not self.preprocessing_complete:
            # Получаем информацию о выходном файле, если он существует
            if hasattr(self, 'output_file_path') and os.path.exists(self.output_file_path):
                output_size_mb = os.path.getsize(self.output_file_path) / (1024 * 1024)
                input_size_mb = 0
                if hasattr(self, 'file_path') and os.path.exists(self.file_path):
                    input_size_mb = os.path.getsize(self.file_path) / (1024 * 1024)
                
                # Оценка прогресса на основе размера файла
                if input_size_mb > 0:
                    progress_pct = min(95, (output_size_mb / input_size_mb) * 100)
                    
                    # Обновляем индикатор прогресса
                    self.update_progress(progress_pct, 100)
                    
                    # Показываем подробную информацию о процессе
                    details = f"Обработано: {output_size_mb:.1f} МБ из {input_size_mb:.1f} МБ | "
                    if hasattr(self, 'detail_label'):
                        current_detail = self.detail_label['text']
                        if current_detail and "Обработка" in current_detail:
                            parts = current_detail.split(' | ')
                            if len(parts) > 1:
                                # Сохраняем информацию о текущей обработке
                                details = f"{parts[0]} | {details}"
                
                self.update_detail_label(details)
            
            # Проверяем активность кнопки "Рассчитать"
            if self.preprocessing_complete:
                self.update_progress_label("Предобработка завершена, файл готов к анализу")
                if self.calculate_btn['state'] != 'normal':
                    self.calculate_btn.config(state="normal")
            
            # Продолжаем мониторинг
            self.after(1000, self.monitor_preprocessing_status)
        else:
            # Если обработка завершена, но кнопка еще не активирована
            if self.preprocessing_complete and self.calculate_btn['state'] != 'normal':
                self.calculate_btn.config(state="normal")
    
    def remove_zero_only_columns(self, input_file_path, output_file_path):
        try:
            # First check if file exists and is readable
            if not os.path.exists(input_file_path):
                self.update_progress_label("Ошибка: Файл не найден")
                self.processing_in_progress = False
                return
                
            # Удаляем существующий output файл, если он существует
            if os.path.exists(output_file_path):
                try:
                    os.remove(output_file_path)
                    self.update_detail_label(f"Удален существующий файл: {os.path.basename(output_file_path)}")
                except Exception as e:
                    self.update_detail_label(f"Не удалось удалить существующий файл: {str(e)}")
            
            # Check file size first to avoid processing extremely large files
            file_size_mb = os.path.getsize(input_file_path) / (1024 * 1024)
            self.update_progress_label(f"Анализ файла размером {file_size_mb:.2f} МБ")
            self.update_detail_label("Определение стратегии обработки...")
            
            # Быстрая проверка структуры файла (чтение только первых нескольких строк)
            with open(input_file_path, 'r') as f:
                first_lines = [next(f) for _ in range(10) if f]
                
            # Подсчет примерного числа колонок и строк
            if first_lines:
                approx_columns = len(first_lines[0].strip().split(','))
                
                # Быстрый подсчет строк
                with open(input_file_path, 'r') as f:
                    line_count = sum(1 for _ in f)
                
                self.update_detail_label(f"Структура файла: ~{approx_columns} колонок, ~{line_count} строк")
                
                # Определяем оптимальную стратегию на основе соотношения колонок к строкам
                column_to_row_ratio = approx_columns / max(1, line_count - 1)  # -1 for header
                self.update_detail_label(f"Соотношение колонок к строкам: {column_to_row_ratio:.1f}:1")
                
                # Если у нас гораздо больше колонок чем строк, используем специализированный метод
                if column_to_row_ratio > 10:  # Если колонок в 10+ раз больше чем строк
                    self.update_progress_label("Обнаружен широкий формат данных - используем оптимизированную обработку по колонкам")
                    self.update_progress(5, 100)
                    self.wide_csv_processor(input_file_path, output_file_path, approx_columns, line_count)
                    return
            
            # Выбираем стратегию в зависимости от размера файла для стандартных случаев
            use_pandas = file_size_mb < 500  # Используем pandas для файлов меньше 500MB
            
            self.update_progress(5, 100)
            
            if use_pandas:
                self.update_progress_label("Используем pandas для обработки файла")
                self.process_with_pandas(input_file_path, output_file_path)
            else:
                self.update_progress_label("Используем dask с многопоточностью для обработки большого файла")
                self.process_with_dask(input_file_path, output_file_path)
            
            # Проверка успешности обработки
            if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
                self.update_progress(100, 100)
                self.update_progress_label("Файл успешно подготовлен и готов к обработке")
                self.update_detail_label(f"Создан файл: {os.path.basename(output_file_path)}")
                
                # Активируем кнопку расчета
                self.preprocessing_complete = True
                self.after(0, lambda: self.calculate_btn.config(state="normal"))
            else:
                self.update_progress_label("Ошибка при подготовке файла")
                self.update_detail_label("Результирующий файл не создан или пуст")
            
            self.processing_in_progress = False
                
        except Exception as e:
            self.update_progress_label(f"Ошибка обработки файла: {str(e)}")
            self.update_detail_label("Проверьте структуру CSV файла и его доступность")
            self.processing_in_progress = False
            
    def wide_csv_processor(self, input_file_path, output_file_path, approx_columns, line_count):
        """Специализированный метод для обработки CSV с очень большим количеством колонок"""
        try:
            start_time = time.time()
            self.update_detail_label("Инициализация обработки колонок...")
            
            # Определяем максимальное число строк для хранения в памяти
            max_lines = min(10000, line_count)  # Не храним больше 10000 строк в памяти
            self.update_detail_label(f"Будет считано до {max_lines} строк для анализа колонок")
            
            # Определяем оптимальное число рабочих процессов
            num_workers = min(32, max(4, multiprocessing.cpu_count()))
            self.update_detail_label(f"Будет использовано {num_workers} потоков для параллельной обработки")
            
            # Первый проход - чтение файла по строкам для получения заголовков и нескольких строк данных
            self.update_progress_label("Чтение заголовков и данных...")
            self.update_progress(10, 100)
            
            headers = []
            data_rows = []
            
            with open(input_file_path, 'r', buffering=1024*1024) as f:  # Увеличиваем буфер чтения
                # Пропускаем первую строку (обычно это пустая строка или комментарий)
                first_line = next(f, None)
                
                # Читаем заголовки (вторая строка)
                header_line = next(f, None)
                if header_line:
                    headers = [h.strip() for h in header_line.strip().split(',')]
                
                # Оптимизированное чтение данных с использованием буфера
                buffer_size = 1024 * 1024 * 8  # 8MB буфер
                self.update_detail_label(f"Используем буфер {buffer_size/1024/1024:.1f} МБ для оптимизации чтения")
                
                # Создаем csv reader с большим буфером
                csv_reader = csv.reader(f)
                
                # Читаем строки данных
                for i, row in enumerate(csv_reader):
                    if i >= max_lines:
                        break
                    
                    data_rows.append(row)
                    
                    if i % 100 == 0:
                        self.update_detail_label(f"Считано {i+1} строк данных")
                        self.update_progress(10 + (10 * i / max_lines), 100)
            
            self.update_progress(20, 100)
            self.update_detail_label(f"Считано {len(headers)} колонок и {len(data_rows)} строк")
            
            # Второй проход - параллельный анализ по колонкам
            self.update_progress_label("Параллельный анализ колонок на наличие ненулевых значений...")
            
            # Функция для проверки колонки на наличие ненулевых значений
            def has_non_zero_values(column_data):
                return any(val and val != '0' and val != '0.0' for val in column_data)
            
            # Функция для обработки группы колонок в параллельном процессе
            def process_column_batch(col_start, col_end, headers_batch, data_rows):
                result_columns = []
                result_indices = []
                result_data = []
                
                for col_idx in range(col_start, min(col_end, len(headers_batch))):
                    # Извлекаем данные для текущей колонки
                    try:
                        col_data = [row[col_idx] if col_idx < len(row) else "" for row in data_rows]
                        
                        # Проверяем на ненулевые значения
                        # Всегда сохраняем колонку Time и первую колонку
                        if col_idx == 0 or "Time" in headers_batch[col_idx] or has_non_zero_values(col_data):
                            result_columns.append(headers_batch[col_idx])
                            result_indices.append(col_idx)
                            result_data.append(col_data)
                    except Exception as e:
                        print(f"Error processing column {col_idx}: {str(e)}")
                
                return result_columns, result_indices, result_data
            
            # Подготовка к параллельной обработке
            column_batches = []
            batch_size = max(100, approx_columns // (num_workers * 2))  # Размер пакета колонок
            
            for i in range(0, len(headers), batch_size):
                column_batches.append((i, min(i + batch_size, len(headers))))
            
            self.update_detail_label(f"Разделяем колонки на {len(column_batches)} пакетов для параллельной обработки")
            
            # Многопроцессорная обработка колонок
            non_zero_columns = []
            non_zero_indices = []
            column_data = []
            
            if len(column_batches) > 1 and approx_columns > 1000:
                # Для больших данных используем параллельную обработку
                with ThreadPoolExecutor(max_workers=num_workers) as executor:
                    future_to_batch = {
                        executor.submit(
                            process_column_batch, start, end, headers, data_rows
                        ): (i, start, end) 
                        for i, (start, end) in enumerate(column_batches)
                    }
                    
                    # Собираем результаты по мере их готовности
                    for i, future in enumerate(concurrent.futures.as_completed(future_to_batch)):
                        batch_idx, start, end = future_to_batch[future]
                        try:
                            batch_columns, batch_indices, batch_data = future.result()
                            
                            non_zero_columns.extend(batch_columns)
                            non_zero_indices.extend(batch_indices)
                            column_data.extend(batch_data)
                            
                            # Обновляем прогресс
                            progress = 20 + (60 * (i + 1) / len(column_batches))
                            self.update_progress(progress, 100)
                            self.update_detail_label(
                                f"Обработано {i+1}/{len(column_batches)} пакетов колонок "
                                f"({start}-{end}) - найдено {len(batch_columns)} непустых"
                            )
                        except Exception as e:
                            self.update_detail_label(f"Ошибка при обработке пакета {batch_idx}: {str(e)}")
            else:
                # Для небольших данных используем последовательную обработку
                for col_idx in range(len(headers)):
                    if col_idx % 100 == 0 or col_idx == len(headers) - 1:
                        progress = 20 + (60 * col_idx / len(headers))
                        self.update_progress(progress, 100)
                        self.update_detail_label(f"Анализ колонки {col_idx+1}/{len(headers)}: {headers[col_idx][:20]}")
                    
                    # Извлекаем данные для текущей колонки
                    try:
                        col_data = [row[col_idx] if col_idx < len(row) else "" for row in data_rows]
                        
                        # Проверяем на ненулевые значения
                        if col_idx == 0 or "Time" in headers[col_idx] or has_non_zero_values(col_data):
                            non_zero_columns.append(headers[col_idx])
                            non_zero_indices.append(col_idx)
                            column_data.append(col_data)
                    except Exception as e:
                        self.update_detail_label(f"Ошибка при обработке колонки {col_idx}: {str(e)}")
            
            # Освобождаем память
            data_rows = None
            
            self.update_progress(80, 100)
            self.update_progress_label(f"Найдено {len(non_zero_columns)} колонок с данными, записываем результат...")
            self.update_detail_label(f"Будет сохранено {len(non_zero_columns)} из {len(headers)} колонок")
            
            # Оптимизированная запись результата в новый файл
            with open(output_file_path, 'w', newline='', buffering=1024*1024*4) as outfile:  # 4MB буфер
                writer = csv.writer(outfile)
                
                # Записываем первую строку (как есть, если она была)
                if first_line:
                    writer.writerow([first_line.strip()])
                
                # Записываем заголовки
                writer.writerow(non_zero_columns)
                
                # Определяем, сколько у нас данных для записи
                num_rows = len(column_data[0]) if column_data else 0
                
                # Транспонируем обратно и записываем блоками для эффективности
                batch_size = 1000  # Записываем блоками по 1000 строк
                for batch_start in range(0, num_rows, batch_size):
                    batch_end = min(batch_start + batch_size, num_rows)
                    rows_to_write = []
                    
                    # Формируем блок строк
                    for i in range(batch_start, batch_end):
                        row_to_write = [column_data[col_idx][i] for col_idx in range(len(column_data))]
                        rows_to_write.append(row_to_write)
                    
                    # Записываем блок
                    writer.writerows(rows_to_write)
                    
                    # Обновляем прогресс
                    if batch_start % 2000 == 0:
                        progress = 80 + (10 * batch_start / num_rows)
                        self.update_progress(progress, 100)
                        self.update_detail_label(f"Записано {batch_end}/{num_rows} строк")
            
            self.update_progress(90, 100)
            self.update_detail_label(f"Записано {num_rows} строк с {len(non_zero_columns)} колонками")
            
            # Освобождаем память
            column_data = None
            
            # Теперь читаем остаток файла и дозаписываем в выходной файл
            if line_count > max_lines + 2:  # +2 for headers
                self.update_progress_label(f"Обработка оставшихся {line_count - max_lines - 2} строк...")
                
                # Используем буферы для оптимизации
                with open(input_file_path, 'r', buffering=1024*1024*4) as infile, \
                     open(output_file_path, 'a', newline='', buffering=1024*1024*4) as outfile:
                    writer = csv.writer(outfile)
                    reader = csv.reader(infile)
                    
                    # Пропускаем уже прочитанные строки
                    for _ in range(max_lines + 2):
                        next(reader, None)
                    
                    # Обрабатываем оставшиеся строки блоками
                    batch_size = 5000
                    batch_rows = []
                    processed_rows = 0
                    
                    for row in reader:
                        if len(row) > 1:  # Проверка на пустые строки
                            # Выбираем только нужные колонки
                            row_to_write = [row[idx] if idx < len(row) else "" for idx in non_zero_indices]
                            batch_rows.append(row_to_write)
                        
                        # Когда накопили достаточно, записываем
                        if len(batch_rows) >= batch_size:
                            writer.writerows(batch_rows)
                            processed_rows += len(batch_rows)
                            batch_rows = []
                            
                            # Обновляем прогресс
                            progress = 90 + (10 * processed_rows / (line_count - max_lines - 2))
                            self.update_progress(min(100, progress), 100)
                            percent = processed_rows / (line_count - max_lines - 2) * 100
                            self.update_detail_label(f"Обработано дополнительно {processed_rows} строк ({percent:.1f}%)")
                    
                    # Записываем оставшиеся строки
                    if batch_rows:
                        writer.writerows(batch_rows)
                        processed_rows += len(batch_rows)
            
            # Финальное обновление
            total_time = time.time() - start_time
            self.update_progress(100, 100)
            self.update_progress_label("Обработка завершена успешно")
            self.update_detail_label(
                f"Обработано {len(headers)} колонок, оставлено {len(non_zero_columns)}. "
                f"Время: {total_time:.1f} сек."
            )
            
            # Активируем кнопку расчета
            self.preprocessing_complete = True
            self.after(0, lambda: self.calculate_btn.config(state="normal"))
            self.processing_in_progress = False
            
        except Exception as e:
            self.update_progress_label(f"Ошибка при обработке широкого CSV: {str(e)}")
            self.update_detail_label("Ошибка в специализированном обработчике")
            self.processing_in_progress = False
    
    def process_with_pandas(self, input_file_path, output_file_path):
        """Обработка файла с использованием pandas с построчным чтением и многопроцессорной обработкой"""
        try:
            # Оценка размера файла и оптимизация размера чанка
            file_size_mb = os.path.getsize(input_file_path) / (1024 * 1024)
            # Больший размер чанка для больших файлов обеспечивает лучшую производительность
            chunk_size = min(500000, max(50000, int(file_size_mb * 1000)))
            
            # Используем ThreadPoolExecutor для ускорения операций ввода-вывода
            num_threads = min(32, max(4, multiprocessing.cpu_count() * 2))
            self.update_detail_label(f"Используем {num_threads} потоков для параллельной обработки")
            self.update_progress(5, 100)
            
            # Для больших файлов, читаем только первые несколько строк для анализа заголовков
            header_sample_size = min(5000, int(file_size_mb * 50))
            header_df = pd.read_csv(input_file_path, nrows=header_sample_size, 
                                    memory_map=True, low_memory=True)
            
            header = header_df.columns.tolist()
            self.update_detail_label(f"Прочитано {len(header)} колонок | Размер чанка: {chunk_size}")
            self.update_progress(10, 100)
            
            # Оценка количества строк в файле без полного чтения
            est_rows_per_mb = len(header_df) / (header_sample_size * header_df.memory_usage(deep=True).sum() / (1024 * 1024))
            estimated_total_rows = int(est_rows_per_mb * file_size_mb)
            
            self.update_detail_label(f"Оценка: ~{estimated_total_rows} строк в файле {file_size_mb:.1f} МБ")
            
            # Быстрая проверка наличия нулевых колонок на образце
            non_zero_columns_initial = set(header_df.columns[header_df.astype(bool).any(axis=0)])
            self.update_detail_label(f"Предварительно выявлено {len(non_zero_columns_initial)} ненулевых колонок из {len(header)}")
            
            # Функция для параллельной обработки чанков
            def process_chunk(chunk_idx, chunk):
                # Находим колонки с ненулевыми значениями в текущем чанке
                non_zero_cols = set(chunk.columns[chunk.astype(bool).any(axis=0)])
                # Отчет о прогрессе через callback
                self.after(0, lambda: self.update_detail_label(
                    f"Чанк {chunk_idx}: найдено {len(non_zero_cols)}/{len(chunk.columns)} ненулевых колонок"))
                return non_zero_cols
            
            # Подготовка для чтения файла большими частями
            try:
                # Более эффективная опция для чтения файла
                reader = pd.read_csv(input_file_path, chunksize=chunk_size, 
                                     memory_map=True, low_memory=True, 
                                     usecols=lambda x: x in non_zero_columns_initial or True)
            except Exception as e:
                self.update_detail_label(f"Ошибка при оптимизированном чтении: {str(e)}. Использую стандартное чтение.")
                reader = pd.read_csv(input_file_path, chunksize=chunk_size)
            
            # Обработка первого прохода - сбор всех ненулевых колонок
            self.update_progress_label("Анализ данных: определение значимых колонок")
            
            non_zero_columns = set(non_zero_columns_initial)
            processed_rows = 0
            processed_chunks = 0
            
            # Используем ThreadPoolExecutor для параллельной обработки чанков
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                # Подготовим задачи для выполнения
                future_results = []
                
                # Читаем и обрабатываем первые N чанков для поиска ненулевых колонок
                max_analyze_chunks = min(50, int(file_size_mb / 100) + 5)  # Ограничиваем количество анализируемых чанков
                
                self.update_detail_label(f"Запуск анализа на {max_analyze_chunks} чанках...")
                
                for i, chunk in enumerate(reader):
                    if i >= max_analyze_chunks:
                        break
                    
                    # Передаем задачу в пул потоков
                    future = executor.submit(process_chunk, i+1, chunk)
                    future_results.append(future)
                    
                    # Обновляем статус
                    processed_rows += len(chunk)
                    processed_chunks += 1
                    progress = 10 + (30 * processed_chunks / max_analyze_chunks)
                    
                    if i % 2 == 0 or i == max_analyze_chunks - 1:
                        self.update_progress(progress, 100)
                        self.update_detail_label(f"Запущен анализ чанка {i+1}/{max_analyze_chunks} ({processed_rows:,} строк)")
                
                # Собираем результаты
                for future in future_results:
                    non_zero_columns.update(future.result())
            
            # Преобразуем в список для дальнейшего использования
            non_zero_columns = list(non_zero_columns)
            self.update_progress_label(f"Найдено {len(non_zero_columns)} ненулевых колонок из {len(header)}")
            self.update_detail_label(f"Обработано {processed_rows:,} строк в {processed_chunks} чанках")
            self.update_progress(45, 100)
            
            # Если нашли колонки с ненулевыми значениями, запускаем второй проход для записи
            if non_zero_columns:
                # Новый подход для ускорения: параллельная запись фильтрованных данных
                self.update_progress_label("Запись очищенных данных в файл")
                
                # Функция для обработки и сохранения чанка
                def process_and_save_chunk(idx, chunk, write_header=False):
                    # Фильтруем только ненулевые колонки
                    filtered = chunk[list(set(chunk.columns) & set(non_zero_columns))]
                    
                    # Путь для временного файла
                    temp_path = f"{output_file_path}.part{idx}"
                    
                    # Сохраняем во временный файл
                    filtered.to_csv(temp_path, index=False, header=write_header)
                    
                    # Возвращаем путь к временному файлу и количество обработанных строк
                    return temp_path, len(filtered)
                
                # Сбрасываем счетчики
                processed_rows = 0
                processed_chunks = 0
                temp_files = []
                
                # Второй проход по файлу - используем только нужные колонки для экономии памяти
                try:
                    # Оптимизированное чтение с указанием только нужных колонок
                    reader = pd.read_csv(input_file_path, chunksize=chunk_size, 
                                          usecols=lambda x: x in non_zero_columns,
                                          memory_map=True, low_memory=True)
                except Exception as e:
                    self.update_detail_label(f"Ошибка при оптимизированном чтении: {str(e)}. Использую стандартное чтение.")
                    reader = pd.read_csv(input_file_path, chunksize=chunk_size)
                
                start_time = time.time()
                with ThreadPoolExecutor(max_workers=num_threads) as executor:
                    future_results = []
                    
                    for i, chunk in enumerate(reader):
                        # Передаем задачу в пул потоков
                        future = executor.submit(
                            process_and_save_chunk, 
                            i, 
                            chunk, 
                            i == 0  # Записываем заголовок только для первого чанка
                        )
                        future_results.append(future)
                        
                        processed_chunks += 1
                        
                        # Обновляем прогресс каждые несколько чанков
                        if i % 5 == 0 or processed_chunks == 1:
                            # Оценка прогресса на основе обработанных строк и примерного общего количества
                            progress = 45 + (50 * processed_rows / (estimated_total_rows or 1))
                            progress = min(95, progress)  # Ограничиваем максимальным значением
                            
                            # Расчет скорости и оценка времени
                            elapsed = time.time() - start_time
                            if elapsed > 0 and processed_rows > 0:
                                rows_per_sec = processed_rows / elapsed
                                estimated_remaining = (estimated_total_rows - processed_rows) / (rows_per_sec or 1)
                                
                                self.update_progress(progress, 100)
                                self.update_detail_label(
                                    f"Обработано {processed_rows:,}/{estimated_total_rows:,} строк "
                                    f"({processed_rows/estimated_total_rows*100:.1f}%) | "
                                    f"{rows_per_sec:.0f} строк/сек | "
                                    f"Осталось: ~{estimated_remaining/60:.1f} мин"
                                )
                            else:
                                self.update_progress(progress, 100)
                                self.update_detail_label(f"Запуск обработки чанка {i+1}...")
                    
                    # Собираем результаты и пути к временным файлам
                    for i, future in enumerate(future_results):
                        try:
                            temp_path, rows = future.result()
                            temp_files.append(temp_path)
                            processed_rows += rows
                            
                            # Обновляем прогресс периодически
                            if i % 10 == 0 or i == len(future_results) - 1:
                                progress = 45 + (50 * (i+1) / len(future_results))
                                progress = min(95, progress)
                                self.update_progress(progress, 100)
                        except Exception as e:
                            self.update_detail_label(f"Ошибка при обработке чанка {i}: {str(e)}")
                
                # Объединяем временные файлы в один результирующий
                self.update_progress_label("Объединение обработанных данных...")
                self.update_detail_label(f"Объединение {len(temp_files)} временных файлов...")
                
                # Удаляем существующий файл, если он есть
                if os.path.exists(output_file_path):
                    try:
                        os.remove(output_file_path)
                    except Exception as e:
                        self.update_detail_label(f"Не удалось удалить существующий файл: {str(e)}")
                
                # Записываем финальный файл, объединяя все временные
                with open(output_file_path, 'w') as outfile:
                    for i, temp_file in enumerate(temp_files):
                        if i % 10 == 0:
                            self.update_detail_label(f"Объединение файла {i+1}/{len(temp_files)}")
                        
                        try:
                            with open(temp_file, 'r') as infile:
                                # Для первого файла копируем все строки (включая заголовок)
                                if i == 0:
                                    outfile.write(infile.read())
                                else:
                                    # Пропускаем заголовок для всех последующих файлов
                                    next(infile)
                                    outfile.write(infile.read())
                            
                            # Удаляем временный файл
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                        except Exception as e:
                            self.update_detail_label(f"Ошибка при объединении файла {i+1}: {str(e)}")
                            continue
                
                self.update_progress(98, 100)
                total_time = time.time() - start_time
                self.update_detail_label(
                    f"Обработка завершена за {total_time:.1f} сек | "
                    f"Общая скорость: {processed_rows/total_time:.0f} строк/сек | "
                    f"Всего строк: {processed_rows:,}"
                )
            else:
                self.update_progress_label("Не найдено ненулевых колонок")
                self.update_detail_label("Проверьте формат входного файла")
        
        except Exception as e:
            self.update_progress_label(f"Ошибка при обработке с pandas: {str(e)}")
            self.update_detail_label("Попробуйте использовать меньший файл или проверьте его структуру")
            raise
    
    def process_with_dask(self, input_file_path, output_file_path):
        """Обработка файла с использованием dask с многопоточностью"""
        try:
            # Устанавливаем количество рабочих потоков для dask
            num_workers = max(2, multiprocessing.cpu_count())
            self.update_detail_label(f"Используем {num_workers} процессов для обработки с Dask")
            
            # Настраиваем параметры для dask
            # Увеличиваем размер блока для чтения для лучшей производительности
            # Блок 128MB дает хороший баланс между памятью и скоростью
            blocksize = "128MB"
            
            self.update_progress_label("Запуск распределенной обработки с Dask...")
            self.update_progress(10, 100)
            
            # Создаем локальный кластер с заданным числом потоков 
            from dask.distributed import Client, LocalCluster
            
            # Настройка памяти для воркеров
            memory_limit = "4GB"  # Лимит памяти на одного воркера
            
            self.update_detail_label("Создание распределенного кластера...")
            
            start_time = time.time()
            
            # Создаем кластер с параметрами
            cluster = LocalCluster(
                n_workers=num_workers, 
                threads_per_worker=2,  # Увеличиваем число потоков на воркера
                memory_limit=memory_limit,
                processes=True,  # Используем процессы для лучшей параллелизации
                scheduler_port=0,  # Автоматический выбор порта
                dashboard_address=None  # Отключаем дашборд для экономии ресурсов
            )
            
            client = Client(cluster)
            self.update_detail_label(f"Кластер создан: {num_workers} воркеров, {memory_limit} память на воркера")
            
            # Функция для отчета о прогрессе
            def report_progress(stage, detail=""):
                elapsed = time.time() - start_time
                self.update_detail_label(f"[{elapsed:.1f}с] {stage} - {detail}")
            
            report_progress("Сбор информации о файле")
            
            # Используем быстрое чтение с оптимизированными параметрами
            try:
                # Проверяем параметры файла
                file_size_mb = os.path.getsize(input_file_path) / (1024 * 1024)
                report_progress("Анализ файла", f"Размер: {file_size_mb:.1f} MB")
                
                # Чтение заголовка для понимания структуры данных
                import pandas as pd
                headers = pd.read_csv(input_file_path, nrows=2).columns.tolist()
                report_progress("Чтение заголовков", f"Найдено {len(headers)} колонок")
                
                # Определяем предполагаемые колонки, которые нужно оставить на основе имени
                # (Часто это важно для оптимизации при работе с очень большими файлами)
                potential_columns = [col for col in headers if 'DEVC_X' in col or 'Time' in col]
                report_progress("Предварительный анализ", f"Предполагаемо важных колонок: {len(potential_columns)}")
                
                # Читаем файл с оптимизированными параметрами
                sample_df = dd.read_csv(
                    input_file_path, 
                    blocksize=blocksize,
                    assume_missing=True,  # Предполагаем, что могут быть пропущенные значения
                    sample=100000,  # Увеличенный размер выборки для более точного анализа
                    storage_options={'anon': True}
                )
                
                # Получаем информацию о размере данных
                total_partitions = sample_df.npartitions
                report_progress("Структура данных", f"Всего разделов: {total_partitions}")
                
                # Оптимизированный подход для поиска только нужных колонок
                # Сначала находим колонки в небольшой выборке
                self.update_progress(20, 100)
                self.update_progress_label("Выявление значимых колонок на выборке...")
                
                # Получаем выборку из первых нескольких разделов для первоначального анализа
                sample_size = min(5, total_partitions)
                first_partitions = sample_df.partitions[0:sample_size]
                sample_result = first_partitions.compute()
                
                report_progress("Анализ выборки", f"Обработано {len(sample_result)} строк")
                
                # Находим ненулевые колонки в выборке
                non_zero_cols = sample_result.columns[sample_result.astype(bool).any(axis=0)].tolist()
                report_progress("Найдены ненулевые колонки", f"{len(non_zero_cols)} из {len(sample_result.columns)}")
                
                self.update_progress(30, 100)
                self.update_progress_label("Применение фильтрации по колонкам...")
                
                # Определяем функцию для обработки разделов
                def non_zero_columns(df_chunk):
                    # Оставляем только колонки, где есть хотя бы одно ненулевое значение
                    return df_chunk.loc[:, (df_chunk != 0).any(axis=0)]
                
                # Применяем обработку к каждому разделу
                self.update_progress_label("Параллельная обработка разделов данных...")
                
                # Если колонок очень много, ограничиваем только важными
                if len(non_zero_cols) > 500:
                    report_progress("Оптимизация", f"Ограничение до 500 колонок из {len(non_zero_cols)}")
                    # Приоритизируем колонки с "DEVC_" и "Time"
                    priority_cols = [col for col in non_zero_cols if 'DEVC_' in col or 'Time' in col]
                    if len(priority_cols) < 500:
                        remaining = 500 - len(priority_cols)
                        other_cols = [col for col in non_zero_cols if col not in priority_cols][:remaining]
                        non_zero_cols = priority_cols + other_cols
                    else:
                        non_zero_cols = priority_cols[:500]
                
                # Создаем новый dataframe только с нужными колонками для экономии памяти
                try:
                    df_filtered = dd.read_csv(
                        input_file_path, 
                        blocksize=blocksize,
                        usecols=non_zero_cols,  # Читаем только нужные колонки
                        storage_options={'anon': True}
                    )
                    report_progress("Чтение с фильтрацией", f"Выбрано {len(non_zero_cols)} колонок")
                except Exception as e:
                    report_progress("Ошибка при чтении отфильтрованных колонок", str(e))
                    # Если не удалось прочитать с фильтрацией, используем обработку всего файла
                    df_filtered = sample_df.map_partitions(non_zero_columns)
                
                # Распределяем вычисления
                self.update_progress(40, 100)
                self.update_progress_label("Распределение задач по рабочим процессам...")
                
                # Подготовка оптимизированных данных для записи
                df_cleaned = df_filtered.persist()
                
                # Отображаем текущий статус
                task_info = client.processing()
                report_progress("Статус задач", f"Выполняется: {len(task_info)}")
                
                # Отображаем прогресс
                self.update_progress(50, 100)
                self.update_progress_label("Запись обработанных данных...")
                
                # Класс для отслеживания прогресса
                class DaskProgressReporter:
                    def __init__(self, update_fn, total_partitions):
                        self.update_fn = update_fn
                        self.total = total_partitions
                        self.completed = 0
                        self.start_time = time.time()
                    
                    def __call__(self, **kwargs):
                        status = kwargs.get('status')
                        key = kwargs.get('key')
                        
                        if status == 'finished':
                            self.completed += 1
                            elapsed = time.time() - self.start_time
                            progress = 50 + (45 * self.completed / self.total)
                            
                            # Оценка оставшегося времени
                            if self.completed > 0 and elapsed > 0:
                                rate = self.completed / elapsed
                                remaining = (self.total - self.completed) / rate
                                
                                # Обновляем UI
                                self.update_fn(
                                    f"Обработано {self.completed}/{self.total} разделов "
                                    f"({self.completed/self.total*100:.1f}%) | "
                                    f"Осталось: ~{remaining/60:.1f} мин"
                                )
                            
                            # Чтобы не слишком часто обновлять UI
                            if self.completed % 5 == 0 or self.completed == self.total:
                                self.update_fn.progress_fn(progress, 100)
                
                # Создаем объект репортера
                reporter = DaskProgressReporter(
                    update_fn=self.update_detail_label,
                    total_partitions=df_cleaned.npartitions
                )
                reporter.progress_fn = self.update_progress
                
                # Регистрируем callback
                client.register_worker_callbacks(lambda **kwargs: reporter(**kwargs))
                
                # Сохраняем с максимально эффективной записью
                report_progress("Начало сохранения", f"Запись в {os.path.basename(output_file_path)}")
                
                # Используем метод сохранения с параллельной записью
                df_cleaned.to_csv(
                    output_file_path, 
                    single_file=True,  # Один файл для удобства дальнейшей обработки
                    compute_kwargs={'scheduler': client},  # Используем наш кластер
                    index=False
                )
                
                # Закрываем клиент и кластер
                client.close()
                cluster.close()
                
                total_time = time.time() - start_time
                self.update_progress(95, 100)
                self.update_detail_label(
                    f"Завершено за {total_time:.1f} сек | Очищены нулевые колонки: "
                    f"{len(headers) - len(non_zero_cols)} из {len(headers)}"
                )
                
            except Exception as e:
                report_progress("Ошибка в основной обработке", str(e))
                
                # Закрываем клиент и кластер
                try:
                    client.close()
                    cluster.close()
                except:
                    pass
                
                raise
                
        except Exception as e:
            self.update_progress_label(f"Ошибка при обработке с dask: {str(e)}")
            self.update_detail_label("Переключение на pandas, если возможно...")
            
            # Если размер файла позволяет, пробуем использовать pandas как запасной вариант
            file_size_mb = os.path.getsize(input_file_path) / (1024 * 1024)
            if file_size_mb < 1000:  # Если файл меньше 1GB
                self.process_with_pandas(input_file_path, output_file_path)
            else:
                raise
    
    def update_progress_label(self, text):
        # This must be called from main thread, so we use after()
        self.after(0, lambda: self.progress_label.config(text=text))
        
        # Change the color based on the context of the message
        if "ошибка" in text.lower() or "ошибки" in text.lower():
            self.after(0, lambda: self.progress_label.config(foreground=self.colors["error"]))
        elif "успешно" in text.lower() or "завершен" in text.lower() or "готов" in text.lower():
            self.after(0, lambda: self.progress_label.config(foreground=self.colors["success"]))
        elif "подождите" in text.lower() or "ожидание" in text.lower():
            self.after(0, lambda: self.progress_label.config(foreground=self.colors["warning"]))
        else:
            self.after(0, lambda: self.progress_label.config(foreground=self.colors["primary"]))
        
        self.after(0, self.update_idletasks)

    def update_detail_label(self, text):
        # Similar to update_progress_label but for detailed information
        self.after(0, lambda: self.detail_label.config(text=text))
        
        # Highlight important information in the detail text
        if "ошибка" in text.lower():
            self.after(0, lambda: self.detail_label.config(foreground=self.colors["error"]))
        elif "найдено" in text.lower() or "создан" in text.lower() or "готов" in text.lower():
            self.after(0, lambda: self.detail_label.config(foreground=self.colors["success"]))
        elif "предупреждение" in text.lower() or "внимание" in text.lower():
            self.after(0, lambda: self.detail_label.config(foreground=self.colors["warning"]))
        else:
            self.after(0, lambda: self.detail_label.config(foreground=self.colors["text_dark"]))
        
        self.after(0, self.update_idletasks)

    def update_progress(self, value, maximum=None):
        """Update progress bar safely from a non-main thread"""
        try:
            if maximum is not None:
                self.after(0, lambda: self.progress.configure(maximum=maximum))
            
            self.after(0, lambda: self.progress.configure(value=value))
            
            # Add percentage display to progress_label
            if maximum is not None and maximum > 0:
                percentage = min(100, max(0, int((value / maximum) * 100)))
                
                # Update progress bar color based on percentage
                if percentage < 30:
                    self.style.configure("TProgressbar", background=self.colors["primary"])
                elif percentage < 70:
                    self.style.configure("TProgressbar", background=self.colors["secondary"])
                else:
                    self.style.configure("TProgressbar", background=self.colors["success"])
                
                # Always update the detail label with progress information
                current_detail = self.detail_label['text']
                if current_detail and "Прогресс:" not in current_detail:
                    # If we have meaningful information, append progress percentage to it
                    self.update_detail_label(f"{current_detail} | Прогресс: {percentage}%")
                else:
                    # Otherwise just show the progress information
                    self.update_detail_label(f"Прогресс: {percentage}% ({value}/{maximum})")
        except Exception as e:
            print(f"Error updating progress: {str(e)}")
    
    def submit(self):
        try:
            # Проверка готовности предобработки
            if not self.preprocessing_complete:
                messagebox.showwarning("Предупреждение", "Подождите окончания предобработки файла")
                return
                
            # Проверяем, не запущен ли уже процесс
            if self.processing_in_progress:
                messagebox.showwarning("Предупреждение", "Обработка уже запущена")
                return
            
            # Создаем словарь для проверки заполнения полей
            fields = {
                "Высота помещения (Hпом)": self.H_entry.get().strip(),
                "Размер ячейки (Cs)": self.Cs_entry.get().strip(),
                "Предельное значение параметра": self.threshold_entry.get().strip()
            }
            
            # Проверяем заполнение полей
            missing_fields = [name for name, value in fields.items() if not value]
            
            if missing_fields:
                msg = "Пожалуйста, заполните следующие поля:\n\n" + "\n".join(f"• {field}" for field in missing_fields)
                messagebox.showwarning("Не все поля заполнены", msg)
                return
            
            # Проверяем файл
            if not self.file_path:
                messagebox.showwarning("Не выбран файл", "Пожалуйста, выберите CSV файл с данными для анализа")
                return
                
            # Парсим входные параметры
            try:
                self.H = float(self.H_entry.get())
                self.Cs = float(self.Cs_entry.get())
                self.threshold = float(self.threshold_entry.get())
                
                # Проверяем диапазоны значений
                if self.H <= 0:
                    raise ValueError("Высота помещения должна быть положительным числом")
                if self.Cs <= 0:
                    raise ValueError("Размер ячейки должен быть положительным числом")
                
                # Обрабатываем опциональное значение Fpom
                Fpom_value = self.Fpom_entry.get().strip()
                if Fpom_value:
                    self.Fpom = float(Fpom_value)
                    if self.Fpom <= 0:
                        raise ValueError("Площадь помещения должна быть положительным числом")
                else:
                    self.Fpom = None
                    
            except ValueError as e:
                messagebox.showerror("Ошибка в данных", f"Пожалуйста, проверьте корректность введенных значений: {str(e)}")
                return
            
            # Если все проверки пройдены, начинаем обработку
            # Деактивируем кнопку расчета во время обработки
            self.calculate_btn.config(state="disabled")
            self.processing_in_progress = True
            
            # Сбрасываем прогресс-бар
            self.update_progress(0, 100)
            self.update_progress_label("Начинаем обработку данных...")
            self.update_detail_label("Подготовка к расчету параметров...")
            self.update_idletasks()
            
            # Make sure the window doesn't freeze
            self.after(100, self.start_processing)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверные данные: {str(e)}. Проверьте правильность введённых значений.")
            
    def start_processing(self):
        # Use daemon=True to ensure thread terminates when main program exits
        process_thread = threading.Thread(
            target=self.process_csv,
            daemon=True
        )
        process_thread.start()

    def process_csv(self):
        try:
            input_file_path = self.file_path
            input_H = float(self.H)
            input_Cs = float(self.Cs)
            input_threshold = float(self.threshold)
            input_Fpom = self.Fpom

            start_time = time.time()  # Начало отсчета времени
            
            # Calculate parameters
            self.update_progress_label("Расчет параметров...")
            self.update_progress(5, 100)
            
            R = None
            if input_H <= 3.5:
                R = 6.4
            elif input_H > 3.5 and input_H <= 6:
                R = 6.05
            elif input_H > 6 and input_H <= 10:
                R = 5.7
            elif input_H > 10:
                R = 5.35

            # Обновляем интерфейс подробной информацией
            detail_info = f"Используем R = {R} для высоты {input_H} м"
            self.update_detail_label(detail_info)
            self.update_progress(10, 100)

            if input_Fpom and input_Fpom != 0:
                input_Fpom = float(input_Fpom)
                F = input_Fpom
                detail_info = f'F (используем значение Fпом = {input_Fpom} из GUI) = {F}'
                self.update_detail_label(detail_info)
            else:
                L = R * math.sqrt(2)
                detail_info = f'L = {L:.2f} м'
                self.update_detail_label(detail_info)
                F = math.ceil((math.pi * (L**2) / 4))
                detail_info += f' | F (по умолчанию) = {F} м²'
                self.update_detail_label(detail_info)

            Cc = math.ceil(F / input_Cs)
            detail_info += f' | Cc = {Cc}'
            self.update_detail_label(detail_info)
            self.update_progress(15, 100)

            if input_file_path:
                self.update_progress_label("Чтение CSV файла...")
                
                # Определяем формат выходного файла
                input_file_name = os.path.basename(input_file_path)
                output_file_path = os.path.join(os.path.dirname(input_file_path), input_file_name.replace('.csv', '_output.csv'))
                
                def convert_scientific_to_float(value):
                    try:
                        return float(value)
                    except ValueError:
                        return value

                self.update_detail_label(f"{detail_info} | Открытие файла для чтения...")
                self.update_progress(20, 100)
                
                # Подсчет общего количества строк
                with open(input_file_path, 'r') as f:
                    total_rows = sum(1 for _ in f)
                
                self.update_detail_label(f"{detail_info} | Всего строк в файле: {total_rows}")
                
                with open(input_file_path, 'r') as infile:
                    reader = csv.reader(infile)
                    
                    next(reader)  # Пропускаем первую строку
                    headers = next(reader)
                    headers = [header.replace('"', '').replace(' ', '') for header in headers]
                    
                    # Фильтруем заголовки
                    valid_columns = [i for i, header in enumerate(headers) if re.match(r'DEVC_X\d+Y\d+_MESH_\d+', header) or header == 'Time']
                    
                    # Обновляем интерфейс с подробной информацией о ходе обработки
                    detail_info = f"Параметры: R={R}, F={F}, Cc={Cc} | Найдено {len(valid_columns)} релевантных колонок из {len(headers)}"
                    self.update_detail_label(detail_info)
                    self.update_progress(25, 100)

                    # Устанавливаем максимум для прогресс-бара
                    self.update_progress(0, total_rows)
                    self.update_progress_label("Фильтрация и обработка данных...")

                    # Обрабатываем строки и сохраняем отфильтрованные данные
                    filtered_data = []
                    
                    # Если выходной файл существует, удаляем его
                    if os.path.exists(output_file_path):
                        try:
                            os.remove(output_file_path)
                        except Exception as e:
                            self.update_detail_label(f"{detail_info} | Не удалось удалить существующий файл: {str(e)}")
                    
                    # Оптимизация для больших файлов
                    batch_size = 2000  # Увеличиваем размер пакета для большей производительности
                    batch_rows = []
                    
                    # Определяем частоту обновления интерфейса
                    update_frequency = max(500, total_rows // 50)  # Обновляем UI максимум 50 раз за весь процесс
                    
                    # Оптимизированная обработка с минимумом обновлений UI
                    start_batch_time = time.time()
                    last_update_time = start_time
                    rows_since_last_update = 0
                    
                    for i, row in enumerate(reader):
                        # Process row
                        filtered_row = [convert_scientific_to_float(row[i]) for i in valid_columns]
                        filtered_data.append(filtered_row)
                        batch_rows.append(filtered_row)
                        rows_since_last_update += 1
                        
                        # Write batches to reduce disk operations
                        if len(batch_rows) >= batch_size:
                            with open(output_file_path, 'a', newline='') as outfile:
                                writer = csv.writer(outfile)
                                writer.writerows(batch_rows)
                            
                            # Measure batch processing time
                            batch_time = time.time() - start_batch_time
                            rows_per_second_batch = batch_size / batch_time if batch_time > 0 else 0
                            
                            # Reset batch
                            batch_rows = []
                            start_batch_time = time.time()
                        
                        # Update UI only occasionally or after significant time has passed
                        current_time = time.time()
                        time_since_update = current_time - last_update_time
                        
                        if (i % update_frequency == 0 or time_since_update > 2.0) and rows_since_last_update > 0:  # Update every 2 seconds at most
                            elapsed_time = current_time - start_time
                            if elapsed_time > 0:
                                rows_per_second = i / elapsed_time
                                estimated_total_time = total_rows / rows_per_second if rows_per_second > 0 else 0
                                remaining_time = estimated_total_time - elapsed_time if estimated_total_time > 0 else 0
                                
                                # More efficient progress calculation
                                progress_pct = min(99, (i / total_rows) * 100)
                                
                                # Update UI with comprehensive information
                                processing_info = (
                                    f"Параметры: R={R}, F={F}, Cc={Cc} | "
                                    f"Обработано {i:,}/{total_rows:,} строк ({progress_pct:.1f}%) | "
                                    f"Скорость: {rows_per_second:.1f} строк/сек | "
                                    f"Осталось: ~{remaining_time/60:.1f} мин"
                                )
                                self.update_detail_label(processing_info)
                                self.update_progress(i, total_rows)
                                
                                # Reset counters
                                last_update_time = current_time
                                rows_since_last_update = 0
                    
                    # Записываем оставшиеся строки
                    if batch_rows:
                        with open(output_file_path, 'a', newline='') as outfile:
                            writer = csv.writer(outfile)
                            writer.writerows(batch_rows)
                    
                    self.update_progress_label("Анализ данных для определения критического времени...")
                    
                    # Находим индекс времени
                    time_index = headers.index('Time')
                    if time_index >= len(valid_columns):
                        time_index = 0  # Если индекс за пределами, берем первую колонку
                    else:
                        time_index = valid_columns.index(time_index)
                    
                    critical_time = None
                    deff_values = []
                    
                    self.update_progress(0, len(filtered_data))
                    self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | Вычисление dэфф и поиск критического времени...")
                    
                    # Проход по отфильтрованным данным для поиска критического времени
                    total_filtered_rows = len(filtered_data)
                    update_frequency = max(100, total_filtered_rows // 50)  # Update UI ~50 times total

                    self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | Анализ {total_filtered_rows} строк данных...")

                    # Initialize max_deff to track maximum value
                    max_deff = 0
                    for i, row in enumerate(filtered_data):
                        # Minimize UI updates for better performance
                        if i % update_frequency == 0:
                            progress_pct = i * 100.0 / total_filtered_rows
                            self.update_progress(i, total_filtered_rows)
                            self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | Поиск критического времени: {progress_pct:.1f}%")

                        # Optimize count calculation - this is a performance-critical inner loop
                        # Подсчет точек, достигших порогового значения
                        if (self.quantity == "VISIBILITY"):
                            count = sum(1 for val in row if isinstance(val, float) and val <= input_threshold)
                        else:
                            count = sum(1 for val in row if isinstance(val, float) and val >= input_threshold)
                        
                        # Проверка достижения критического значения
                        if count >= Cc:
                            critical_time = row[time_index]
                            self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | Критическое время найдено: {critical_time} сек")
                            break
                        else:
                            # Вычисление dэфф - только считаем, но обновляем GUI редко
                            deff = math.sqrt((4 * (count * input_Cs)) / math.pi)
                            L = deff
                            deff_values.append(deff)
                            
                            # Track maximum deff value
                            if deff > max_deff:
                                max_deff = deff
                                
                            # Существенно реже обновляем информацию - только для значимых изменений
                            if i % (update_frequency * 5) == 0 and i > 0:
                                self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | dэфф: {deff:.2f} м, макс: {max_deff:.2f} м, порог: {L:.2f} м")
                    
                    self.update_progress_label("Подготовка данных для графика...")
                    self.update_progress(60, 100)
                    
                    # Собираем данные для графика
                    time_values = [row[time_index] for row in filtered_data if len(row) > time_index]
                    relevant_time_values = time_values[:len(deff_values)]
                    devc_data = {}
                    
                    self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | Собираем данные по {len(valid_columns)} колонкам...")
                    
                    for j, index in enumerate(valid_columns):
                        if index < len(headers):
                            # Drastically reduce UI updates for large column sets
                            update_frequency = max(1000, len(valid_columns) // 100)  # Update only ~100 times during the entire process
                            
                            # Only update progress in larger chunks
                            if j % update_frequency == 0 or j == len(valid_columns) - 1:
                                # Calculate progress percentage
                                progress_value = 60 + int(20 * j / len(valid_columns))
                                self.update_progress(progress_value, 100)
                                
                                # Show processing status with completion percentage
                                column_percent = (j / len(valid_columns)) * 100
                                self.update_detail_label(
                                    f"Параметры: R={R}, F={F}, Cc={Cc} | "
                                    f"Обработка колонок: {column_percent:.1f}% ({j}/{len(valid_columns)})"
                                )
                            
                            # Process column data without UI updates
                            devc_data[headers[index]] = [row[j] for row in filtered_data if j < len(row)]
                    
                    self.update_progress(80, 100)
                    self.update_progress_label("Формирование графика...")
                    
                    # Подготавливаем график
                    plt.figure(figsize=(12,4))
                    
                    # Создаём вторую ось Y
                    ax1 = plt.gca()  # Берём текущую ось
                    ax2 = ax1.twinx()  # Создаём твин-копию ax1
                    
                    total_cells = len(devc_data)
                    filled_cells = 0
                    
                    self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | Начинаем построение графика для {total_cells} наборов данных")
                    
                    # Для первой оси Y рисуем значения devc_data (каждой точки)
                    # Optimize for large datasets by reducing UI updates and plotting in batches
                    update_frequency = max(500, total_cells // 50)  # Update UI ~50 times during the process
                    
                    # Pre-allocate memory for plot data
                    if total_cells > 1000:
                        # For very large datasets, use downsampling to improve performance
                        self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | Оптимизация построения графика ({total_cells} наборов)")
                        
                        # Plot time values in batches for better performance
                        batch_counter = 0
                        batch_size = 100  # Process 100 datasets at a time
                        
                        for batch_start in range(0, total_cells, batch_size):
                            batch_end = min(batch_start + batch_size, total_cells)
                            batch_items = list(devc_data.items())[batch_start:batch_end]
                            
                            for header, values in batch_items:
                                if len(time_values) != len(values):
                                    continue  # Skip mismatched datasets
                                
                                ax1.plot(time_values, values, linestyle='solid', lw=0.1)
                                filled_cells += 1
                            
                            batch_counter += 1
                            
                            # Update UI only occasionally
                            if batch_counter % max(1, (total_cells // batch_size) // 20) == 0 or batch_end == total_cells:
                                progress = 80 + (5 * filled_cells / total_cells)
                                self.update_progress(progress, 100)
                                self.update_detail_label(
                                    f"Параметры: R={R}, F={F}, Cc={Cc} | "
                                    f"Построение графика: {(filled_cells/total_cells*100):.1f}% ({filled_cells}/{total_cells})"
                                )
                    else:
                        # For smaller datasets, use the original approach
                        for i, (header, values) in enumerate(devc_data.items()):
                            if len(time_values) != len(values):
                                continue  # Skip mismatched datasets
                            
                            ax1.plot(time_values, values, linestyle='solid', lw=0.1)
                            filled_cells += 1
                            
                            # Update progress less frequently
                            if i % update_frequency == 0 or i == total_cells - 1:
                                progress = 80 + (5 * filled_cells / total_cells)
                                self.update_progress(progress, 100)
                                self.update_detail_label(
                                    f"Параметры: R={R}, F={F}, Cc={Cc} | "
                                    f"Построение графика: {(filled_cells/total_cells*100):.1f}% ({filled_cells}/{total_cells})"
                                )
                    
                    self.update_progress(85, 100)
                    self.update_progress_label("Добавление кривой dэфф...")
                    self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | Добавление кривой dэфф на график...")
                    
                    # Рисуем значения d_eff на полотне ax2 с собственной осью Y
                    ax2.plot(relevant_time_values, deff_values, color='black', linewidth=5, label='dэфф (м)')
                    
                    self.update_progress(87, 100)
                    self.update_progress_label("Добавление пороговых линий...")
                    
                    if critical_time is not None:
                        self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | Построение критической линии tпор = {critical_time:.2f} сек")
                        ax1.axvline(x=critical_time, color='red', linestyle='--', lw=3, label=f'tпор = {critical_time:.2f} (сек)')
                    else:
                        error_msg = "Критическое время не найдено. Проверьте предельное значение параметра."
                        self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | ОШИБКА: {error_msg}")
                        messagebox.showinfo("Проверка данных", "Проверьте введённые данные. Возможно вы неправильно указали предельное значение параметра, воздействующего на пожарный извещатель.")
                    
                    self.update_progress(90, 100)
                    
                    # Назначаем строки заголовков для обеих осей Y
                    measure_units = ""
                    if (self.quantity == "VISIBILITY"):
                        measure_units = "м"
                    elif (self.quantity == "EXTINCTION COEFFICIENT"):
                        measure_units = "дБ/м"
                    elif (self.quantity == "OPTICAL DENSITY"):
                        measure_units = "Нп/м"
                    elif (self.quantity == "TEMPERATURE"):
                        measure_units = "*С"
                    elif (self.quantity == "Аспирационный"):
                        measure_units = "Нп/м"
                        
                    ax1.set_ylabel(f'Значение параметра ({measure_units})')
                    ax2.set_ylabel('dэфф (м)')
                    
                    if critical_time is not None:
                        f1 = critical_time + 60 + 20
                        f2f4 = critical_time + 30 + 20
                        self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | Расчетные значения: F1={f1:.2f} сек, F2-F5={f2f4:.2f} сек")
                    
                    self.update_progress(92, 100)
                    self.update_progress_label("Оформление графика...")
                    
                    # Добавляем горизонтальную линию для L и input_threshold на соответствующих осях
                    ax1.axhline(y=input_threshold, color='blue', linestyle='--', lw=3, label=f'Крит. знач. параметра = {input_threshold:.3f} ({measure_units})', alpha=0.5)
                    ax2.axhline(y=L, color='green', linestyle='--', lw=3, label=f'dэфф = {max(deff_values):.3f} (м)', alpha=0.5)
                    
                    self.update_progress(94, 100)
                    
                    # Периферия
                    xlabel_text = f'Время (сек)'
                    if critical_time is not None:
                        xlabel_text += f'\n\nВремя начала эвакуации tнэ для Ф1 = {critical_time:.2f} + 60 + 0 + 20 = {f1:.2f} (сек)'
                        xlabel_text += f' \nВремя начала эвакуации tнэ для Ф2-Ф5 = {critical_time:.2f} + 30 + 0 + 20 = {f2f4:.2f} (сек)'
                    
                    ax1.set_xlabel(xlabel_text)
                    plt.title(f'График dэфф и значений параметра,\nвоздействующего на пожарный извещатель, во всех точках в области F', fontsize=12)
                    plt.grid(True)
                    lines1, labels1 = ax1.get_legend_handles_labels()
                    lines2, labels2 = ax2.get_legend_handles_labels()
                    ax1.legend(lines1 + lines2, labels1 + labels2, loc='center left')
                    
                    self.update_progress(96, 100)
                    self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | Настройка осей графика...")

                    # Настройка осей
                    try:
                        ax1.set_ylim(bottom=0, top=input_threshold * 1.1)
                        if critical_time is not None:
                            ax1.set_xlim(left=0, right=max(critical_time, 0) * 1.1)
                        
                        if deff_values:
                            ax2.set_ylim(bottom=min(deff_values) * 0.9, top=max(deff_values) * 1.1)
                        if critical_time is not None:
                            ax2.set_xlim(left=0, right=max(critical_time, 0) * 1.1)
                    except Exception as e:
                        self.update_detail_label(f"Параметры: R={R}, F={F}, Cc={Cc} | Ошибка настройки осей: {str(e)}")
                    
                    self.update_progress(98, 100)
                    self.update_progress_label("Сохранение графика...")
                    
                    # Определение пути для сохранения
                    output_folder_path = os.path.normpath(os.path.join(os.path.dirname(input_file_path), '..', '..', '..', '..'))
                    second_folder_name = os.path.basename(os.path.normpath(os.path.join(os.path.dirname(input_file_path), '..', '..')))
                    output_file_name = f"deff_{second_folder_name}_plot.png"
                    output_file_path = os.path.join(output_folder_path, output_file_name)
                    
                    # Копирование имени папки в буфер обмена для удобства
                    addToClipBoard(second_folder_name)
                    self.update_detail_label(
                        f"Параметры: R={R}, F={F}, Cc={Cc} | "
                        f"Имя папки '{second_folder_name}' скопировано в буфер обмена"
                    )

                    # Сохраняем график в изображение
                    try:
                        plt.savefig(output_file_path, bbox_inches='tight', format='png')
                        self.update_detail_label(
                            f"Параметры: R={R}, F={F}, Cc={Cc} | "
                            f"График сохранен в файл: {output_file_path}"
                        )
                    except Exception as e:
                        error_msg = f"Ошибка сохранения графика: {str(e)}"
                        self.update_detail_label(
                            f"Параметры: R={R}, F={F}, Cc={Cc} | ОШИБКА: {error_msg}"
                        )
                        messagebox.showerror("Ошибка", error_msg)
                    
                    self.update_progress(100, 100)
                    self.update_progress_label("График успешно сохранен")
                    
                    # Закрываем фигуру для освобождения памяти
                    plt.close()
                    
                    # Скрываем основное окно
                    self.withdraw()
                    
                    # Сбрасываем статус обработки
                    self.processing_in_progress = False
                    
                    # Функции для обработки событий в диалоговом окне
                    def OpenPNG():
                        os.startfile(output_file_path)

                    def OpenPNGfolder():
                        os.startfile(output_folder_path)

                    def Close():
                        self.quit()  # Закрываем основное окно tkinter

                    # Запустим диалог в главном потоке
                    self.after(0, lambda: custom_message_box(OpenPNG, OpenPNGfolder, Close))

        except Exception as e:
            error_msg = f"Ошибка при обработке: {str(e)}"
            self.update_progress_label(error_msg)
            self.update_detail_label("Проверьте входные данные и формат CSV файла")
            messagebox.showerror("Ошибка обработки", f"Произошла ошибка при обработке файла: {str(e)}")
            
            # Восстанавливаем кнопку расчета
            self.processing_in_progress = False
            self.after(0, lambda: self.calculate_btn.config(state="normal"))
            return
            
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
    top.title("PCTT v0.8.0")
    top.geometry("500x260")
    
    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    icon_path = os.path.join(parent_directory, '.gitpics', 'pctt.ico')
    
    top.iconbitmap(icon_path)
    top.wm_iconbitmap(icon_path)
    
    # Словарь цветов для стилизации
    colors = {
        "primary": "#3498db",       # Основной цвет (синий)
        "secondary": "#2ecc71",     # Вторичный цвет (зеленый)
        "accent": "#e74c3c",        # Акцентный цвет (красный)
        "bg_light": "#f5f5f5",      # Светлый фон
        "bg_dark": "#2c3e50",       # Темный фон
        "text_light": "#ecf0f1",    # Светлый текст
        "text_dark": "#34495e",     # Темный текст
        "success": "#27ae60",       # Цвет успеха
    }
    
    # Создаем стили для диалога
    style = ttk.Style()
    style.configure("Success.TLabel", 
                   font=("Segoe UI", 14, "bold"), 
                   foreground=colors["success"],
                   background=colors["bg_light"])
    
    style.configure("Message.TLabel", 
                   font=("Segoe UI", 11), 
                   foreground=colors["text_dark"],
                   background=colors["bg_light"])
    
    style.configure("Dialog.TButton", 
                   font=("Segoe UI", 10, "bold"),
                   padding=10)
    
    style.map("Dialog.TButton",
             background=[("active", colors["secondary"]), 
                         ("!active", colors["primary"])],
             foreground=[("active", colors["text_light"]), 
                         ("!active", colors["text_light"])])
    
    # Стилизация диалога результатов
    top_frame = ttk.Frame(top, padding="20", style="TFrame")
    top_frame.pack(fill=tk.BOTH, expand=True)
    
    # Иконка успеха (эмодзи или текстовый символ)
    success_icon = ttk.Label(top_frame, text="✓", font=("Segoe UI", 36, "bold"), 
                           foreground=colors["success"], background=colors["bg_light"])
    success_icon.pack(pady=(0, 5))
    
    # Заголовок с сообщением об успехе
    label = ttk.Label(top_frame, text="Расчёт tпор успешно завершён!", 
                     style="Success.TLabel")
    label.pack(pady=(0, 15))
    
    # Дополнительное сообщение
    message = ttk.Label(top_frame, 
                       text="Результаты расчета сохранены. Что вы хотите сделать дальше?",
                       style="Message.TLabel", wraplength=450)
    message.pack(pady=(0, 20))
    
    # Кнопки в отдельном фрейме
    button_frame = ttk.Frame(top_frame, style="TFrame")
    button_frame.pack(pady=5)
    
    # Стилизованные кнопки
    view_btn = ttk.Button(button_frame, text="Показать график", 
                         command=on_open_png, style="Dialog.TButton", width=16)
    view_btn.pack(side='left', padx=8)
    
    folder_btn = ttk.Button(button_frame, text="Открыть папку", 
                           command=on_open_folder, style="Dialog.TButton", width=16)
    folder_btn.pack(side='left', padx=8)
    
    exit_btn = ttk.Button(button_frame, text="Выйти", 
                         command=on_close, style="Dialog.TButton", width=16)
    exit_btn.pack(side='left', padx=8)
    
    # Центрирование окна
    top.update_idletasks()
    width = top.winfo_width()
    height = top.winfo_height()
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry(f'{width}x{height}+{x}+{y}')

    # Делаем диалог модальным
    top.transient()  # Поверх других окон
    top.grab_set()  # Модальное окно
    top.protocol("WM_DELETE_WINDOW", on_close)  # Закрытие окна
    
    # Фокусируем кнопку просмотра графика по умолчанию
    view_btn.focus_set()

def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)

# Конфигурация ini
config = configparser.ConfigParser()

current_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
inis_path = os.path.join(parent_directory, 'inis')

# Determine ProcessID from command line argument
if len(sys.argv) > 1:
    ProcessID = int(sys.argv[1])
    print(f"Process ID received: {ProcessID}")
else:
    print("No Process ID received.")

# Define paths for ini files
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

print(f"Debug: ProcessID before creating MultiInputWindow: {ProcessID}") # Debug print
# Обработка начальной загрузки
input_window = MultiInputWindow(H=value_IniHZ, Cs=value_InideltaZ, threshold=value_IniSetpoint, Fpom=value_IniFpom, quantity=value_IniQuantity)
input_window.mainloop()