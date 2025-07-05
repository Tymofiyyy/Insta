  
  #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сучасний графічний інтерфейс для Instagram Bot v2.0
Повна реалізація з усіма функціями
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import json
import queue
import os
from datetime import datetime
import webbrowser
from typing import Dict, List, Any
import logging

try:
    import sv_ttk  # Sun Valley TTK theme для сучасного вигляду
    SV_TTK_AVAILABLE = True
except ImportError:
    SV_TTK_AVAILABLE = False

from config import BotConfig
from utils import ValidationUtils, FileManager, StatisticsManager, DatabaseManager


class ModernStyle:
    """Сучасні стилі для інтерфейсу"""
    
    # Кольорова палітра
    COLORS = {
        'primary': '#0095f6',      # Instagram blue
        'secondary': '#262626',    # Dark gray
        'success': '#0a7c42',      # Green
        'warning': '#ffa726',      # Orange
        'error': '#ed4956',        # Red
        'background': '#fafafa',   # Light gray
        'surface': '#ffffff',      # White
        'text_primary': '#262626', # Dark gray
        'text_secondary': '#8e8e8e', # Gray
        'border': '#dbdbdb'        # Light border
    }
    
    # Шрифти
    FONTS = {
        'heading': ('Segoe UI', 12, 'bold'),
        'subheading': ('Segoe UI', 10, 'bold'),
        'body': ('Segoe UI', 9),
        'small': ('Segoe UI', 8),
        'monospace': ('Consolas', 9)
    }


class StatusBar:
    """Розширена панель статусу"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.pack(side='bottom', fill='x', padx=5, pady=2)
        
        # Основний статус
        self.status_var = tk.StringVar(value="Готовий до роботи")
        self.status_label = ttk.Label(self.frame, textvariable=self.status_var)
        self.status_label.pack(side='left', padx=5)
        
        # Роздільник
        ttk.Separator(self.frame, orient='vertical').pack(side='left', fill='y', padx=5)
        
        # Лічильники
        self.accounts_var = tk.StringVar(value="Акаунти: 0")
        self.accounts_label = ttk.Label(self.frame, textvariable=self.accounts_var)
        self.accounts_label.pack(side='left', padx=5)
        
        self.targets_var = tk.StringVar(value="Цілі: 0")
        self.targets_label = ttk.Label(self.frame, textvariable=self.targets_var)
        self.targets_label.pack(side='left', padx=5)
        
        # Прогрес
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, variable=self.progress_var, 
            length=150, mode='determinate'
        )
        self.progress_bar.pack(side='right', padx=5)
        
        # Час
        self.time_var = tk.StringVar()
        self.time_label = ttk.Label(self.frame, textvariable=self.time_var)
        self.time_label.pack(side='right', padx=5)
        
        self.update_time()
    
    def update_time(self):
        """Оновлення часу"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_var.set(current_time)
        self.frame.after(1000, self.update_time)
    
    def set_status(self, status: str, color: str = None):
        """Встановлення статусу"""
        self.status_var.set(status)
        if color:
            self.status_label.configure(foreground=color)
    
    def update_counters(self, accounts: int, targets: int):
        """Оновлення лічильників"""
        self.accounts_var.set(f"Акаунти: {accounts}")
        self.targets_var.set(f"Цілі: {targets}")
    
    def set_progress(self, value: float):
        """Встановлення прогресу"""
        self.progress_var.set(min(100, max(0, value)))


class NotificationSystem:
    """Система сповіщень"""
    
    def __init__(self, parent):
        self.parent = parent
        self.notifications = []
    
    def show_notification(self, message: str, type_: str = "info", duration: int = 3000):
        """Показ сповіщення"""
        notification = self.create_notification(message, type_)
        
        # Анімація появи
        self.animate_in(notification)
        
        # Автоматичне приховування
        self.parent.after(duration, lambda: self.hide_notification(notification))
    
    def create_notification(self, message: str, type_: str):
        """Створення віджета сповіщення"""
        notification = tk.Toplevel(self.parent)
        notification.withdraw()
        notification.overrideredirect(True)
        
        color_map = {
            'success': '#4CAF50',
            'error': '#F44336', 
            'warning': '#FF9800',
            'info': '#2196F3'
        }
        bg_color = color_map.get(type_, '#2196F3')
        notification.configure(bg=bg_color)
        
        # Позиціонування
        x = self.parent.winfo_x() + self.parent.winfo_width() - 300
        y = self.parent.winfo_y() + 50 + len(self.notifications) * 60
        notification.geometry(f"280x50+{x}+{y}")
        
        # Контент
        label = tk.Label(
            notification, 
            text=message, 
            bg=bg_color, 
            fg='white',
            font=ModernStyle.FONTS['body'],
            wraplength=260
        )
        label.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.notifications.append(notification)
        return notification
    
    def animate_in(self, notification):
        """Анімація появи"""
        notification.deiconify()
        notification.attributes('-alpha', 0.0)
        
        def fade_in(alpha=0.0):
            alpha += 0.1
            notification.attributes('-alpha', alpha)
            if alpha < 1.0:
                self.parent.after(50, lambda: fade_in(alpha))
        
        fade_in()
    
    def hide_notification(self, notification):
        """Приховування сповіщення"""
        def fade_out(alpha=1.0):
            alpha -= 0.1
            try:
                notification.attributes('-alpha', alpha)
                if alpha > 0.0:
                    self.parent.after(50, lambda: fade_out(alpha))
                else:
                    notification.destroy()
                    if notification in self.notifications:
                        self.notifications.remove(notification)
            except tk.TclError:
                # Вікно вже закрито
                if notification in self.notifications:
                    self.notifications.remove(notification)
        
        fade_out()


class InstagramBotGUI:
    """Головний клас GUI з сучасним дизайном"""
    
    def __init__(self, root):
        self.root = root
        self.setup_main_window()
        
        # Ініціалізація компонентів
        self.config = BotConfig()
        self.db_manager = DatabaseManager()
        self.stats_manager = StatisticsManager(self.db_manager)
        self.file_manager = FileManager()
        
        # Система логування
        self.log_queue = queue.Queue()
        self.setup_logging()
        
        # Стан автоматизації
        self.bot = None
        self.automation_running = False
        self.automation_thread = None
        
        # Створення інтерфейсу
        self.setup_modern_theme()
        self.create_interface()
        
        # Система сповіщень
        self.notifications = NotificationSystem(self.root)
        
        # Запуск фонових процесів
        self.start_background_tasks()
        
        # Завантаження збережених даних
        self.load_initial_data()
    
    def setup_main_window(self):
        """Налаштування головного вікна"""
        self.root.title("Instagram Automation Bot v2.0 - Професійна версія")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Іконка вікна
        try:
            self.root.iconbitmap('assets/icon.ico')
        except:
            pass
        
        # Центрування вікна
        self.center_window()
    
    def center_window(self):
        """Центрування вікна на екрані"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        size = tuple(int(_) for _ in self.root.geometry().split('+')[0].split('x'))
        x = screen_width // 2 - size[0] // 2
        y = screen_height // 2 - size[1] // 2
        self.root.geometry(f"{size[0]}x{size[1]}+{x}+{y}")
    
    def setup_modern_theme(self):
        """Налаштування сучасної теми"""
        if SV_TTK_AVAILABLE:
            try:
                sv_ttk.set_theme("light")
            except:
                self.setup_fallback_theme()
        else:
            self.setup_fallback_theme()
        
        # Додаткові стилі
        self.configure_custom_styles()
    
    def setup_fallback_theme(self):
        """Fallback тема"""
        style = ttk.Style()
        style.theme_use('clam')
    
    def configure_custom_styles(self):
        """Налаштування користувацьких стилів"""
        style = ttk.Style()
        
        # Стилі для заголовків
        style.configure('Heading.TLabel', 
                       font=ModernStyle.FONTS['heading'],
                       foreground=ModernStyle.COLORS['text_primary'])
        
        style.configure('Subheading.TLabel',
                       font=ModernStyle.FONTS['subheading'],
                       foreground=ModernStyle.COLORS['text_secondary'])
        
        # Стилі для статусів
        style.configure('Success.TLabel',
                       foreground=ModernStyle.COLORS['success'])
        
        style.configure('Warning.TLabel',
                       foreground=ModernStyle.COLORS['warning'])
        
        style.configure('Error.TLabel',
                       foreground=ModernStyle.COLORS['error'])
        
        # Стилі для кнопок
        style.configure('Primary.TButton',
                       font=ModernStyle.FONTS['body'])
        
        style.configure('Success.TButton',
                       font=ModernStyle.FONTS['body'])
        
        style.configure('Danger.TButton',
                       font=ModernStyle.FONTS['body'])
    
    def setup_logging(self):
        """Налаштування системи логування"""
        class QueueHandler(logging.Handler):
            def __init__(self, log_queue):
                super().__init__()
                self.log_queue = log_queue
            
            def emit(self, record):
                self.log_queue.put(self.format(record))
        
        # Додавання обробника черги
        queue_handler = QueueHandler(self.log_queue)
        queue_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        
        logger = logging.getLogger()
        logger.addHandler(queue_handler)
        logger.setLevel(logging.INFO)
    
    def create_interface(self):
        """Створення головного інтерфейсу"""
        # Меню
        self.create_menu_bar()
        
        # Головний контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Бічна панель
        self.create_sidebar(main_container)
        
        # Основна область
        self.create_main_area(main_container)
        
        # Панель статусу
        self.status_bar = StatusBar(self.root)
    
    def create_menu_bar(self):
        """Створення меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Файл", menu=file_menu)
        file_menu.add_command(label="🆕 Новий проект", command=self.new_project)
        file_menu.add_command(label="📂 Відкрити проект", command=self.open_project)
        file_menu.add_command(label="💾 Зберегти проект", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="📥 Імпорт акаунтів", command=self.import_accounts)
        file_menu.add_command(label="📤 Експорт акаунтів", command=self.export_accounts)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Вихід", command=self.on_closing)
        
        # Меню інструменти
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔧 Інструменти", menu=tools_menu)
        tools_menu.add_command(label="🌐 Тест проксі", command=self.test_all_proxies)
        tools_menu.add_command(label="🧹 Очистити логи", command=self.clear_all_logs)
        tools_menu.add_command(label="🔄 Перезапуск бота", command=self.restart_bot)
        tools_menu.add_command(label="⚙️ Налаштування", command=self.open_settings)
        
        # Меню допомога
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Допомога", menu=help_menu)
        help_menu.add_command(label="📖 Документація", command=self.open_documentation)
        help_menu.add_command(label="🎬 Відео інструкції", command=self.open_video_tutorials)
        help_menu.add_command(label="💬 Підтримка", command=self.open_support)
        help_menu.add_command(label="ℹ️ Про програму", command=self.show_about)
    
    def create_sidebar(self, parent):
        """Створення бічної панелі"""
        sidebar_frame = ttk.Frame(parent, width=200)
        sidebar_frame.pack(side='left', fill='y', padx=(0, 10))
        sidebar_frame.pack_propagate(False)
        
        # Логотип та назва
        logo_frame = ttk.Frame(sidebar_frame)
        logo_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(logo_frame, text="Instagram Bot", style='Heading.TLabel')
        title_label.pack()
        
        version_label = ttk.Label(logo_frame, text="v2.0 Pro", style='Subheading.TLabel')
        version_label.pack()
        
        # Навігаційні кнопки
        nav_frame = ttk.LabelFrame(sidebar_frame, text="📋 Навігація")
        nav_frame.pack(fill='x', pady=(0, 10))
        
        self.nav_buttons = {}
        nav_items = [
            ("🏠 Dashboard", "dashboard"),
            ("👥 Акаунти", "accounts"),
            ("🎯 Цілі", "targets"),
            ("🤖 Автоматизація", "automation"),
            ("⚙️ Налаштування", "settings"),
            ("📊 Статистика", "statistics"),
            ("📋 Логи", "logs")
        ]
        
        for text, key in nav_items:
            btn = ttk.Button(
                nav_frame, 
                text=text, 
                command=lambda k=key: self.show_page(k),
                style='Primary.TButton'
            )
            btn.pack(fill='x', pady=2, padx=5)
            self.nav_buttons[key] = btn
        
        # Швидкі дії
        quick_frame = ttk.LabelFrame(sidebar_frame, text="⚡ Швидкі дії")
        quick_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(quick_frame, text="▶️ Швидкий старт", 
                  command=self.quick_start, style='Success.TButton').pack(fill='x', pady=2, padx=5)
        ttk.Button(quick_frame, text="⏹️ Стоп", 
                  command=self.emergency_stop, style='Danger.TButton').pack(fill='x', pady=2, padx=5)
        ttk.Button(quick_frame, text="📊 Звіт", 
                  command=self.generate_quick_report).pack(fill='x', pady=2, padx=5)
        
        # Індикатори статусу
        status_frame = ttk.LabelFrame(sidebar_frame, text="📈 Статус")
        status_frame.pack(fill='x', pady=(0, 10))
        
        self.status_indicators = {}
        status_items = [
            ("Бот", "bot_status"),
            ("Акаунти", "accounts_status"),
            ("Проксі", "proxy_status")
        ]
        
        for text, key in status_items:
            frame = ttk.Frame(status_frame)
            frame.pack(fill='x', padx=5, pady=2)
            
            ttk.Label(frame, text=f"{text}:").pack(side='left')
            
            indicator = ttk.Label(frame, text="●", foreground='gray')
            indicator.pack(side='right')
            
            self.status_indicators[key] = indicator
    
    def create_main_area(self, parent):
        """Створення основної області"""
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(side='left', fill='both', expand=True)
        
        # Контейнер для сторінок
        self.pages_container = ttk.Frame(self.main_frame)
        self.pages_container.pack(fill='both', expand=True)
        
        # Створення всіх сторінок
        self.pages = {}
        self.create_all_pages()
        
        # Показ початкової сторінки
        self.show_page('dashboard')
    
    def create_all_pages(self):
        """Створення всіх сторінок"""
        self.create_dashboard_page()
        self.create_accounts_page()
        self.create_targets_page()
        self.create_automation_page()
        self.create_settings_page()
        self.create_statistics_page()
        self.create_logs_page()
    
    def create_dashboard_page(self):
        """Створення Dashboard сторінки"""
        page = ttk.Frame(self.pages_container)
        self.pages['dashboard'] = page
        
        # Заголовок
        header_frame = ttk.Frame(page)
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="📊 Dashboard", style='Heading.TLabel').pack(side='left')
        
        # Швидкі статистики
        stats_frame = ttk.Frame(page)
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Картки статистики
        self.create_stats_cards(stats_frame)
        
        # Графіки та діаграми
        charts_frame = ttk.LabelFrame(page, text="📈 Аналітика")
        charts_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Тут буде графік активності
        self.create_activity_chart(charts_frame)
        
        # Останні дії
        recent_frame = ttk.LabelFrame(page, text="🕒 Останні дії")
        recent_frame.pack(fill='x', pady=(0, 10))
        
        self.recent_actions_tree = ttk.Treeview(
            recent_frame, 
            columns=('time', 'account', 'action', 'target', 'status'),
            show='headings',
            height=8
        )
        
        # Налаштування колонок
        columns = [
            ('time', 'Час', 80),
            ('account', 'Акаунт', 100),
            ('action', 'Дія', 100),
            ('target', 'Ціль', 100),
            ('status', 'Статус', 80)
        ]
        
        for col_id, heading, width in columns:
            self.recent_actions_tree.heading(col_id, text=heading)
            self.recent_actions_tree.column(col_id, width=width)
        
        self.recent_actions_tree.pack(fill='x', padx=10, pady=10)
        
        # Scrollbar для таблиці
        scrollbar = ttk.Scrollbar(recent_frame, orient='vertical', command=self.recent_actions_tree.yview)
        self.recent_actions_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
    
    def create_stats_cards(self, parent):
        """Створення карток статистики"""
        cards_data = [
            ("👥", "Акаунти", "0", "active"),
            ("🎯", "Цілі", "0", "primary"),
            ("❤️", "Лайки сьогодні", "0", "success"),
            ("💬", "Повідомлення", "0", "info")
        ]
        
        self.stats_cards = {}
        
        for i, (icon, title, value, color) in enumerate(cards_data):
            card_frame = ttk.Frame(parent, relief='raised', borderwidth=1)
            card_frame.grid(row=0, column=i, padx=10, pady=5, sticky='ew')
            
            parent.grid_columnconfigure(i, weight=1)
            
            # Іконка
            icon_label = ttk.Label(card_frame, text=icon, font=('Segoe UI', 20))
            icon_label.pack(pady=(10, 5))
            
            # Значення
            value_var = tk.StringVar(value=value)
            value_label = ttk.Label(card_frame, textvariable=value_var, 
                                   font=ModernStyle.FONTS['heading'])
            value_label.pack()
            
            # Назва
            title_label = ttk.Label(card_frame, text=title, 
                                   style='Subheading.TLabel')
            title_label.pack(pady=(0, 10))
            
            self.stats_cards[title.lower().replace(' ', '_')] = value_var
    
    def create_activity_chart(self, parent):
        """Створення графіку активності"""
        # Заглушка для графіку
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        chart_label = ttk.Label(chart_frame, 
                               text="📊 Графік активності\n(Буде реалізовано в наступній версії)",
                               style='Subheading.TLabel')
        chart_label.pack(expand=True)
    
    def create_accounts_page(self):
        """Створення сторінки акаунтів"""
        page = ttk.Frame(self.pages_container)
        self.pages['accounts'] = page
        
        # Заголовок
        header_frame = ttk.Frame(page)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="👥 Управління акаунтами", 
                 style='Heading.TLabel').pack(side='left')
        
        # Панель додавання
        add_frame = ttk.LabelFrame(page, text="➕ Додати новий акаунт")
        add_frame.pack(fill='x', pady=(0, 10))
        
        # Форма додавання
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        # Поля введення
        fields = [
            ("Логін:", "username"),
            ("Пароль:", "password"),
            ("Проксі:", "proxy")
        ]
        
        self.account_entries = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(row=0, column=i*2, sticky='w', padx=(0, 5))
            
            entry = ttk.Entry(form_frame, width=20)
            if field_name == "password":
                entry.configure(show='*')
            
            entry.grid(row=0, column=i*2+1, padx=(0, 20))
            self.account_entries[field_name] = entry
        
        # Кнопки
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=0, column=6, padx=10)
        
        ttk.Button(btn_frame, text="➕ Додати", command=self.add_account).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="📂 Імпорт", command=self.import_accounts).pack(side='left', padx=2)
        
        # Список акаунтів
        list_frame = ttk.LabelFrame(page, text="📋 Список акаунтів")
        list_frame.pack(fill='both', expand=True)
        
        # Таблиця акаунтів
        columns = ('username', 'status', 'actions_today', 'total_actions', 'last_activity', 'proxy')
        self.accounts_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Налаштування колонок
        column_configs = [
            ('username', 'Логін', 120),
            ('status', 'Статус', 100),
            ('actions_today', 'Дій сьогодні', 100),
            ('total_actions', 'Всього дій', 100),
            ('last_activity', 'Остання активність', 150),
            ('proxy', 'Проксі', 200)
        ]
        
        for col_id, heading, width in column_configs:
            self.accounts_tree.heading(col_id, text=heading)
            self.accounts_tree.column(col_id, width=width)
        
        # Контейнер для таблиці та скролбара
        table_frame = ttk.Frame(list_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.accounts_tree.pack(side='left', fill='both', expand=True)
        
        accounts_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.accounts_tree.yview)
        self.accounts_tree.configure(yscrollcommand=accounts_scrollbar.set)
        accounts_scrollbar.pack(side='right', fill='y')
        
        # Кнопки управління
        controls_frame = ttk.Frame(list_frame)
        controls_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        control_buttons = [
            ("🔄 Оновити", self.refresh_accounts),
            ("🗑️ Видалити", self.remove_account),
            ("🔐 Тест входу", self.test_account_login),
            ("📊 Статистика", self.show_account_stats),
            ("⚙️ Налаштування", self.edit_account_settings)
        ]
        
        for text, command in control_buttons:
            ttk.Button(controls_frame, text=text, command=command).pack(side='left', padx=5)
    
    def create_targets_page(self):
        """Створення сторінки цілей"""
        page = ttk.Frame(self.pages_container)
        self.pages['targets'] = page
        
        # Заголовок
        header_frame = ttk.Frame(page)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="🎯 Управління цілями", 
                 style='Heading.TLabel').pack(side='left')
        
        # Панель додавання
        add_frame = ttk.LabelFrame(page, text="➕ Додати нову ціль")
        add_frame.pack(fill='x', pady=(0, 10))
        
        entry_frame = ttk.Frame(add_frame)
        entry_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(entry_frame, text="Ім'я користувача:").pack(side='left')
        self.target_entry = ttk.Entry(entry_frame, width=25)
        self.target_entry.pack(side='left', padx=10)
        self.target_entry.bind('<Return>', lambda e: self.add_target())
        
        ttk.Button(entry_frame, text="➕ Додати", command=self.add_target).pack(side='left', padx=5)
        ttk.Button(entry_frame, text="📂 Імпорт з файлу", command=self.import_targets).pack(side='left', padx=5)
        ttk.Button(entry_frame, text="🔍 Пошук схожих", command=self.find_similar_accounts).pack(side='left', padx=5)
        
        # Основний контент - розділений на дві частини
        content_frame = ttk.Frame(page)
        content_frame.pack(fill='both', expand=True)
        
        # Ліва частина - список цілей
        left_frame = ttk.LabelFrame(content_frame, text="📋 Список цілей")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Контейнер для списку
        list_container = ttk.Frame(left_frame)
        list_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.targets_listbox = tk.Listbox(list_container, height=20, font=ModernStyle.FONTS['body'])
        targets_scrollbar = ttk.Scrollbar(list_container, orient='vertical', command=self.targets_listbox.yview)
        self.targets_listbox.configure(yscrollcommand=targets_scrollbar.set)
        
        self.targets_listbox.pack(side='left', fill='both', expand=True)
        targets_scrollbar.pack(side='right', fill='y')
        
        # Права частина - попередній перегляд профілю
        right_frame = ttk.LabelFrame(content_frame, text="👁️ Попередній перегляд")
        right_frame.pack(side='right', fill='y', width=300)
        right_frame.pack_propagate(False)
        
        # Інформація про профіль
        self.profile_info_frame = ttk.Frame(right_frame)
        self.profile_info_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_profile_preview()
        
        # Кнопки управління цілями
        targets_controls = ttk.Frame(left_frame)
        targets_controls.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(targets_controls, text="🗑️ Видалити", command=self.remove_target).pack(side='left', padx=5)
        ttk.Button(targets_controls, text="🗑️ Очистити все", command=self.clear_targets).pack(side='left', padx=5)
        ttk.Button(targets_controls, text="📤 Експорт", command=self.export_targets).pack(side='left', padx=5)
        
        # Лічильник
        self.targets_counter = ttk.Label(targets_controls, text="Цілей: 0", style='Subheading.TLabel')
        self.targets_counter.pack(side='right', padx=5)
        
        # Bind для оновлення попереднього перегляду
        self.targets_listbox.bind('<<ListboxSelect>>', self.on_target_select)
    
    def create_profile_preview(self):
        """Створення області попереднього перегляду профілю"""
        # Заглушка аватара
        avatar_frame = ttk.Frame(self.profile_info_frame)
        avatar_frame.pack(pady=10)
        
        self.avatar_label = ttk.Label(avatar_frame, text="👤", font=('Segoe UI', 48))
        self.avatar_label.pack()
        
        # Інформація про профіль
        self.profile_username = ttk.Label(self.profile_info_frame, text="Виберіть ціль", 
                                         style='Heading.TLabel')
        self.profile_username.pack(pady=5)
        
        self.profile_stats = ttk.Label(self.profile_info_frame, text="", 
                                      style='Subheading.TLabel')
        self.profile_stats.pack(pady=5)
        
        # Кнопки дій
        actions_frame = ttk.Frame(self.profile_info_frame)
        actions_frame.pack(pady=10)
        
        ttk.Button(actions_frame, text="🔍 Переглянути профіль", 
                  command=self.view_profile_in_browser).pack(fill='x', pady=2)
        ttk.Button(actions_frame, text="📊 Аналіз профілю", 
                  command=self.analyze_profile).pack(fill='x', pady=2)
        ttk.Button(actions_frame, text="🎯 Запустити автоматизацію", 
                  command=self.run_single_target).pack(fill='x', pady=2)
    
    def create_automation_page(self):
        """Створення сторінки автоматизації"""
        page = ttk.Frame(self.pages_container)
        self.pages['automation'] = page
        
        # Заголовок
        header_frame = ttk.Frame(page)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="🤖 Автоматизація", 
                 style='Heading.TLabel').pack(side='left')
        
        # Налаштування дій
        actions_frame = ttk.LabelFrame(page, text="⚙️ Налаштування дій")
        actions_frame.pack(fill='x', pady=(0, 10))
        
        # Чекбокси для дій
        checkboxes_frame = ttk.Frame(actions_frame)
        checkboxes_frame.pack(fill='x', padx=10, pady=10)
        
        self.action_vars = {}
        actions = [
            ("like_posts", "❤️ Лайкати останні 2 пости", True),
            ("like_stories", "📖 Лайкати сторіс", True),
            ("reply_stories", "💬 Відповідати на сторіс", True),
            ("send_dm_if_no_stories", "📩 Писати в DM якщо немає сторіс", False)
        ]
        
        for i, (key, text, default) in enumerate(actions):
            var = tk.BooleanVar(value=default)
            self.action_vars[key] = var
            
            cb = ttk.Checkbutton(checkboxes_frame, text=text, variable=var)
            cb.grid(row=i//2, column=i%2, sticky='w', padx=20, pady=5)
        
        # Повідомлення
        messages_frame = ttk.LabelFrame(page, text="💬 Повідомлення")
        messages_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Вкладки для різних типів повідомлень
        messages_notebook = ttk.Notebook(messages_frame)
        messages_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка сторіс
        stories_frame = ttk.Frame(messages_notebook)
        messages_notebook.add(stories_frame, text="📖 Для сторіс")
        
        self.create_messages_tab(stories_frame, "stories")
        
        # Вкладка директ
        direct_frame = ttk.Frame(messages_notebook)
        messages_notebook.add(direct_frame, text="📩 Для директ")
        
        self.create_messages_tab(direct_frame, "direct")
        
        # Панель управління
        control_frame = ttk.LabelFrame(page, text="🎮 Управління")
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Основні кнопки
        main_controls = ttk.Frame(control_frame)
        main_controls.pack(fill='x', padx=10, pady=10)
        
        self.start_button = ttk.Button(main_controls, text="▶️ Запустити автоматизацію", 
                                      command=self.start_automation, style='Success.TButton')
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(main_controls, text="⏹️ Зупинити", 
                                     command=self.stop_automation, style='Danger.TButton',
                                     state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        self.pause_button = ttk.Button(main_controls, text="⏸️ Пауза", 
                                      command=self.pause_automation, state='disabled')
        self.pause_button.pack(side='left', padx=5)
        
        # Прогрес
        progress_frame = ttk.Frame(control_frame)
        progress_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Label(progress_frame, text="Прогрес:").pack(side='left')
        
        self.automation_progress = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.automation_progress.pack(side='left', padx=10, fill='x', expand=True)
        
        self.progress_label = ttk.Label(progress_frame, text="0/0")
        self.progress_label.pack(side='right')
        
        # Статус автоматизації
        self.automation_status = ttk.Label(control_frame, text="Статус: Очікування", 
                                          style='Subheading.TLabel')
        self.automation_status.pack(padx=10, pady=(0, 10))
    
    def create_messages_tab(self, parent, message_type):
        """Створення вкладки повідомлень"""
        # Кнопки швидкого додавання
        quick_frame = ttk.Frame(parent)
        quick_frame.pack(fill='x', pady=(0, 10))
        
        if message_type == "stories":
            quick_buttons = [
                ("🔥 Емодзі", self.add_emoji_messages),
                ("👍 Позитивні", self.add_positive_messages),
                ("🌟 Вау-фактор", self.add_wow_messages)
            ]
        else:
            quick_buttons = [
                ("👋 Привітання", self.add_greeting_messages),
                ("💭 Компліменти", self.add_compliment_messages),
                ("🤝 Знайомство", self.add_introduction_messages)
            ]
        
        for text, command in quick_buttons:
            ttk.Button(quick_frame, text=text, command=lambda c=command, t=message_type: c(t)).pack(side='left', padx=5)
        
        ttk.Button(quick_frame, text="🗑️ Очистити", 
                  command=lambda: self.clear_messages(message_type)).pack(side='right', padx=5)
        
        # Текстове поле
        if message_type == "stories":
            self.stories_text = scrolledtext.ScrolledText(parent, height=12, wrap='word')
            self.stories_text.pack(fill='both', expand=True)
            
            # Стандартні повідомлення для сторіс
            default_stories = "\n".join(self.config.get_story_replies())
            self.stories_text.insert('1.0', default_stories)
        else:
            self.direct_text = scrolledtext.ScrolledText(parent, height=12, wrap='word')
            self.direct_text.pack(fill='both', expand=True)
            
            # Стандартні повідомлення для директ
            default_direct = "\n".join(self.config.get_direct_messages())
            self.direct_text.insert('1.0', default_direct)
    
    def create_settings_page(self):
        """Створення сторінки налаштувань"""
        page = ttk.Frame(self.pages_container)
        self.pages['settings'] = page
        
        # Заголовок
        header_frame = ttk.Frame(page)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="⚙️ Налаштування", 
                 style='Heading.TLabel').pack(side='left')
        
        # Створення вкладок для налаштувань
        settings_notebook = ttk.Notebook(page)
        settings_notebook.pack(fill='both', expand=True)
        
        # Основні налаштування
        general_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(general_frame, text="🔧 Основні")
        self.create_general_settings(general_frame)
        
        # Налаштування безпеки
        security_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(security_frame, text="🛡️ Безпека")
        self.create_security_settings(security_frame)
        
        # Проксі налаштування
        proxy_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(proxy_frame, text="🌐 Проксі")
        self.create_proxy_settings(proxy_frame)
        
        # Капча налаштування
        captcha_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(captcha_frame, text="🤖 Капча")
        self.create_captcha_settings(captcha_frame)
    
    def create_general_settings(self, parent):
        """Створення основних налаштувань"""
        # Скролабельна область
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Затримки
        delays_frame = ttk.LabelFrame(scrollable_frame, text="⏱️ Затримки (секунди)")
        delays_frame.pack(fill='x', padx=10, pady=10)
        
        self.delay_entries = {}
        delay_configs = [
            ("Лайки", "like", "2-5"),
            ("Сторіс", "story_reply", "2-6"),
            ("Між діями", "between_actions", "8-15"),
            ("Між цілями", "between_targets", "15-45")
        ]
        
        delays_grid = ttk.Frame(delays_frame)
        delays_grid.pack(fill='x', padx=10, pady=10)
        
        for i, (label, key, default) in enumerate(delay_configs):
            row, col = i // 2, (i % 2) * 2
            
            ttk.Label(delays_grid, text=f"{label}:").grid(row=row, column=col, sticky='w', padx=(0, 5))
            
            entry = ttk.Entry(delays_grid, width=15)
            entry.insert(0, default)
            entry.grid(row=row, column=col+1, padx=(0, 20))
            
            self.delay_entries[key] = entry
        
        # Ліміти
        limits_frame = ttk.LabelFrame(scrollable_frame, text="📊 Ліміти")
        limits_frame.pack(fill='x', padx=10, pady=10)
        
        limits_grid = ttk.Frame(limits_frame)
        limits_grid.pack(fill='x', padx=10, pady=10)
        
        self.limit_entries = {}
        limit_configs = [
            ("Дій на день", "daily_limit", "80"),
            ("Дій на годину", "hourly_limit", "15"),
            ("Помилок підряд", "max_errors", "3"),
            ("Кулдаун (хв)", "cooldown", "30")
        ]
        
        for i, (label, key, default) in enumerate(limit_configs):
            row, col = i // 2, (i % 2) * 2
            
            ttk.Label(limits_grid, text=f"{label}:").grid(row=row, column=col, sticky='w', padx=(0, 5))
            
            entry = ttk.Entry(limits_grid, width=10)
            entry.insert(0, default)
            entry.grid(row=row, column=col+1, padx=(0, 20))
            
            self.limit_entries[key] = entry
        
        # Кнопки збереження
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(fill='x', padx=10, pady=20)
        
        ttk.Button(buttons_frame, text="💾 Зберегти", 
                  command=self.save_general_settings).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="🔄 Скинути", 
                  command=self.reset_general_settings).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="📂 Завантажити", 
                  command=self.load_general_settings).pack(side='left', padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_security_settings(self, parent):
        """Створення налаштувань безпеки"""
        # Скролабельна область
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Основні налаштування безпеки
        main_security_frame = ttk.LabelFrame(scrollable_frame, text="🛡️ Основні налаштування безпеки")
        main_security_frame.pack(fill='x', padx=10, pady=10)
        
        security_grid = ttk.Frame(main_security_frame)
        security_grid.pack(fill='x', padx=10, pady=10)
        
        self.security_vars = {}
        security_options = [
            ("check_shadowban", "Перевіряти shadowban", True),
            ("avoid_suspicious", "Уникати підозрілої поведінки", True),
            ("randomize_actions", "Рандомізувати дії", True),
            ("human_like_delays", "Людські затримки", True),
            ("monitor_health", "Моніторити здоров'я акаунтів", True),
            ("auto_pause_errors", "Автопауза при помилках", True)
        ]
        
        for i, (key, text, default) in enumerate(security_options):
            var = tk.BooleanVar(value=default)
            self.security_vars[key] = var
            
            cb = ttk.Checkbutton(security_grid, text=text, variable=var)
            cb.grid(row=i//2, column=i%2, sticky='w', padx=10, pady=5)
        
        # Ліміти безпеки
        security_limits_frame = ttk.LabelFrame(scrollable_frame, text="📊 Ліміти безпеки")
        security_limits_frame.pack(fill='x', padx=10, pady=10)
        
        limits_grid = ttk.Frame(security_limits_frame)
        limits_grid.pack(fill='x', padx=10, pady=10)
        
        self.security_limit_entries = {}
        security_limit_configs = [
            ("Макс лайків на день", "max_daily_likes", "300"),
            ("Макс коментарів на день", "max_daily_comments", "50"),
            ("Макс сторіс на день", "max_daily_stories", "100"),
            ("Макс DM на день", "max_daily_dms", "20")
        ]
        
        for i, (label, key, default) in enumerate(security_limit_configs):
            row, col = i // 2, (i % 2) * 2
            
            ttk.Label(limits_grid, text=f"{label}:").grid(row=row, column=col, sticky='w', padx=(0, 5))
            
            entry = ttk.Entry(limits_grid, width=10)
            entry.insert(0, default)
            entry.grid(row=row, column=col+1, padx=(0, 20))
            
            self.security_limit_entries[key] = entry
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_proxy_settings(self, parent):
        """Створення налаштувань проксі"""
        # Заголовок
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="🌐 Налаштування проксі серверів", 
                 style='Heading.TLabel').pack(side='left')
        
        # Інструкції
        info_frame = ttk.LabelFrame(parent, text="ℹ️ Інформація")
        info_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        info_text = """
Формати проксі:
• ip:port (для безкоштовних проксі)
• ip:port:username:password (для приватних проксі)
• domain.com:port:username:password

Рекомендації:
• Використовуйте приватні проксі для кращої безпеки
• Один проксі на один акаунт
• Регулярно змінюйте проксі
        """
        
        info_label = ttk.Label(info_frame, text=info_text, justify='left')
        info_label.pack(padx=10, pady=10)
        
        # Поле для введення проксі
        proxy_frame = ttk.LabelFrame(parent, text="📝 Список проксі")
        proxy_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Кнопки управління
        proxy_buttons = ttk.Frame(proxy_frame)
        proxy_buttons.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(proxy_buttons, text="📂 Завантажити з файлу", 
                  command=self.load_proxies_from_file).pack(side='left', padx=5)
        ttk.Button(proxy_buttons, text="💾 Зберегти у файл", 
                  command=self.save_proxies_to_file).pack(side='left', padx=5)
        ttk.Button(proxy_buttons, text="🧪 Тестувати всі", 
                  command=self.test_all_proxies).pack(side='left', padx=5)
        ttk.Button(proxy_buttons, text="🗑️ Очистити", 
                  command=self.clear_proxies).pack(side='right', padx=5)
        
        # Текстове поле для проксі
        self.proxy_text = scrolledtext.ScrolledText(proxy_frame, height=15, wrap='word')
        self.proxy_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Лічильник проксі
        self.proxy_counter = ttk.Label(proxy_frame, text="Проксі: 0", style='Subheading.TLabel')
        self.proxy_counter.pack(pady=5)
    
    def create_captcha_settings(self, parent):
        """Створення налаштувань капчі"""
        # Заголовок
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="🤖 Налаштування розв'язання капчі", 
                 style='Heading.TLabel').pack(side='left')
        
        # Основні налаштування
        main_frame = ttk.LabelFrame(parent, text="⚙️ Основні налаштування")
        main_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Вибір сервісу
        service_frame = ttk.Frame(main_frame)
        service_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(service_frame, text="Сервіс капчі:").pack(side='left')
        
        self.captcha_service_var = tk.StringVar(value="2captcha")
        service_combo = ttk.Combobox(service_frame, textvariable=self.captcha_service_var,
                                    values=["2captcha", "anticaptcha", "rucaptcha"], width=15)
        service_combo.pack(side='left', padx=10)
        
        # API ключ
        api_frame = ttk.Frame(main_frame)
        api_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(api_frame, text="API ключ:").pack(side='left')
        self.captcha_key_entry = ttk.Entry(api_frame, width=40, show='*')
        self.captcha_key_entry.pack(side='left', padx=10, fill='x', expand=True)
        
        # Кнопка тесту
        ttk.Button(api_frame, text="🧪 Тест", command=self.test_captcha_service).pack(side='right', padx=5)
        
        # Інформація про сервіси
        info_frame = ttk.LabelFrame(parent, text="ℹ️ Інформація про сервіси")
        info_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        services_info = """
2captcha.com:
• Популярний сервіс розв'язання капчі
• Підтримка reCAPTCHA v2/v3, hCaptcha
• Ціна: від $0.5 за 1000 капч
• Реєстрація: https://2captcha.com

anticaptcha.com:
• Професійний сервіс
• Швидке розв'язання
• Ціна: від $0.6 за 1000 капч
• Реєстрація: https://anti-captcha.com

rucaptcha.com:
• Російський сервіс
• Низькі ціни
• Ціна: від $0.3 за 1000 капч
• Реєстрація: https://rucaptcha.com
        """
        
        services_label = ttk.Label(info_frame, text=services_info, justify='left')
        services_label.pack(padx=10, pady=10)
    
    def create_statistics_page(self):
        """Створення сторінки статистики"""
        page = ttk.Frame(self.pages_container)
        self.pages['statistics'] = page
        
        # Заголовок
        header_frame = ttk.Frame(page)
        header_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(header_frame, text="📊 Статистика роботи", style='Heading.TLabel').pack(side='left')
        
        # Загальна статистика
        general_frame = ttk.LabelFrame(page, text="📈 Загальна статистика")
        general_frame.pack(fill='x', pady=(0, 10))
        
        stats_grid = ttk.Frame(general_frame)
        stats_grid.pack(fill='x', padx=10, pady=10)
        
        # Статистика по рядках
        self.total_actions_label = ttk.Label(stats_grid, text="Всього дій: 0")
        self.total_actions_label.grid(row=0, column=0, sticky='w', pady=2)
        
        self.successful_actions_label = ttk.Label(stats_grid, text="Успішних: 0")
        self.successful_actions_label.grid(row=0, column=1, sticky='w', pady=2)