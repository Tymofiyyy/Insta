
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Bot GUI - Сучасний професійний інтерфейс
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import webbrowser
from pathlib import Path

# Імпорти внутрішніх модулів
try:
    from config import BotConfig
    from instagram_bot import InstagramBot
    from utils import DatabaseManager, StatisticsManager, ValidationUtils, SystemUtils
except ImportError as e:
    print(f"Помилка імпорту: {e}")
    sys.exit(1)


class ModernStyle:
    """Сучасний стиль інтерфейсу"""
    
    # Кольорова схема
    COLORS = {
        'primary': '#2563eb',      # Синій
        'primary_dark': '#1d4ed8',
        'primary_light': '#3b82f6',
        'secondary': '#6366f1',    # Індиго
        'success': '#10b981',      # Зелений
        'warning': '#f59e0b',      # Жовтий
        'error': '#ef4444',        # Червоний
        'info': '#06b6d4',         # Блакитний
        
        'background': '#ffffff',   # Білий
        'surface': '#f8fafc',      # Світло-сірий
        'card': '#ffffff',         # Білий
        'border': '#e2e8f0',       # Сірий
        'text': '#1e293b',         # Темно-сірий
        'text_secondary': '#64748b', # Середньо-сірий
        'text_light': '#94a3b8',   # Світло-сірий
        
        'sidebar': '#1e293b',      # Темно-сірий
        'sidebar_hover': '#334155',
        'sidebar_text': '#f1f5f9',
        'sidebar_active': '#3b82f6'
    }
    
    # Шрифти
    FONTS = {
        'title': ('Segoe UI', 24, 'bold'),
        'subtitle': ('Segoe UI', 18, 'bold'),
        'heading': ('Segoe UI', 14, 'bold'),
        'body': ('Segoe UI', 11),
        'small': ('Segoe UI', 9),
        'code': ('Consolas', 10)
    }
    
    # Розміри
    SIZES = {
        'window_width': 1400,
        'window_height': 900,
        'sidebar_width': 280,
        'padding': 20,
        'margin': 10,
        'border_radius': 8,
        'button_height': 36,
        'input_height': 32
    }


class AnimatedButton(tk.Button):
    """Анімована кнопка з hover ефектом"""
    
    def __init__(self, parent, hover_bg=None, **kwargs):
        # Витягуємо hover_bg з kwargs перед передачею в Button
        self.default_bg = kwargs.get('bg', ModernStyle.COLORS['primary'])
        self.hover_bg = hover_bg or ModernStyle.COLORS['primary_dark']
        
        # Видаляємо hover_bg з kwargs, щоб не передавати в Button
        if 'hover_bg' in kwargs:
            del kwargs['hover_bg']
        
        super().__init__(parent, **kwargs)
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
        # Стиль кнопки
        self.configure(
            relief='flat',
            borderwidth=0,
            font=ModernStyle.FONTS['body'],
            fg='white',
            bg=self.default_bg,
            height=2,
            cursor='hand2'
        )
    
    def on_enter(self, event):
        self.configure(bg=self.hover_bg)
    
    def on_leave(self, event):
        self.configure(bg=self.default_bg)

class IconButton(tk.Button):
    """Кнопка з іконкою"""
    
    def __init__(self, parent, icon, text="", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.icon = icon
        self.text_content = text
        
        self.configure(
            text=f"{icon} {text}" if text else icon,
            relief='flat',
            borderwidth=0,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            cursor='hand2',
            padx=12,
            pady=8
        )
        
        self.bind('<Enter>', self.on_hover)
        self.bind('<Leave>', self.on_leave)
    
    def on_hover(self, event):
        self.configure(bg=ModernStyle.COLORS['border'])
    
    def on_leave(self, event):
        self.configure(bg=ModernStyle.COLORS['surface'])


class Card(tk.Frame):
    """Картка з тінню та закругленими краями"""
    
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(
            bg=ModernStyle.COLORS['card'],
            relief='flat',
            bd=1,
            highlightbackground=ModernStyle.COLORS['border'],
            highlightthickness=1
        )
        
        if title:
            title_label = tk.Label(
                self,
                text=title,
                font=ModernStyle.FONTS['heading'],
                bg=ModernStyle.COLORS['card'],
                fg=ModernStyle.COLORS['text']
            )
            title_label.pack(anchor='w', padx=20, pady=(20, 10))


class StatusIndicator(tk.Frame):
    """Індикатор статусу"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(bg=ModernStyle.COLORS['background'])
        
        self.dot = tk.Label(
            self,
            text="●",
            font=('Arial', 12),
            bg=ModernStyle.COLORS['background']
        )
        self.dot.pack(side='left')
        
        self.label = tk.Label(
            self,
            font=ModernStyle.FONTS['small'],
            bg=ModernStyle.COLORS['background']
        )
        self.label.pack(side='left', padx=(5, 0))
    
    def set_status(self, status: str, text: str):
        colors = {
            'success': ModernStyle.COLORS['success'],
            'warning': ModernStyle.COLORS['warning'],
            'error': ModernStyle.COLORS['error'],
            'info': ModernStyle.COLORS['info'],
            'inactive': ModernStyle.COLORS['text_light']
        }
        
        self.dot.configure(fg=colors.get(status, colors['inactive']))
        self.label.configure(text=text, fg=ModernStyle.COLORS['text'])


class ProgressCard(Card):
    """Картка з прогрес-баром"""
    
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, title, **kwargs)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.pack(padx=20, pady=10, fill='x')
        
        self.status_label = tk.Label(
            self,
            text="Готовий до роботи",
            font=ModernStyle.FONTS['small'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text_secondary']
        )
        self.status_label.pack(padx=20, pady=(0, 20))
    
    def update_progress(self, value: float, status: str = ""):
        self.progress_var.set(value)
        if status:
            self.status_label.configure(text=status)


class SidebarButton(tk.Button):
    """Кнопка бічної панелі"""
    
    def __init__(self, parent, icon, text, command=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(
            text=f"  {icon}  {text}",
            command=command,
            relief='flat',
            borderwidth=0,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['sidebar'],
            fg=ModernStyle.COLORS['sidebar_text'],
            anchor='w',
            padx=20,
            pady=12,
            cursor='hand2'
        )
        
        self.bind('<Enter>', self.on_hover)
        self.bind('<Leave>', self.on_leave)
        
        self.is_active = False
    
    def on_hover(self, event):
        if not self.is_active:
            self.configure(bg=ModernStyle.COLORS['sidebar_hover'])
    
    def on_leave(self, event):
        if not self.is_active:
            self.configure(bg=ModernStyle.COLORS['sidebar'])
    
    def set_active(self, active=True):
        self.is_active = active
        if active:
            self.configure(bg=ModernStyle.COLORS['sidebar_active'])
        else:
            self.configure(bg=ModernStyle.COLORS['sidebar'])


class InstagramBotGUI:
    """Основний клас GUI"""
    
    def __init__(self, root):
        self.root = root
        self.config_manager = BotConfig()
        self.bot = None
        self.db_manager = DatabaseManager()
        self.stats_manager = StatisticsManager(self.db_manager)
        
        self.current_page = "dashboard"
        self.is_running = False
        self.automation_thread = None
        
        self.setup_window()
        self.create_widgets()
        self.load_initial_data()
        
        # Періодичне оновлення статистики
        self.update_statistics()
        
    def setup_window(self):
        """Налаштування головного вікна"""
        self.root.title("Instagram Bot Pro v2.0 - Професійна автоматизація")
        
        # Розмір та позиція вікна
        width = ModernStyle.SIZES['window_width']
        height = ModernStyle.SIZES['window_height']
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(1200, 700)
        
        # Налаштування стилю
        self.root.configure(bg=ModernStyle.COLORS['background'])
        
        # Іконка (якщо є)
        try:
            self.root.iconbitmap('assets/icon.ico')
        except:
            pass
        
        # Обробка закриття
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Стиль ttk
        self.setup_ttk_style()
    
    def setup_ttk_style(self):
        """Налаштування стилю ttk віджетів"""
        style = ttk.Style()
        
        # Прогрес-бар
        style.configure(
            "Modern.Horizontal.TProgressbar",
            background=ModernStyle.COLORS['primary'],
            troughcolor=ModernStyle.COLORS['border'],
            borderwidth=0,
            lightcolor=ModernStyle.COLORS['primary'],
            darkcolor=ModernStyle.COLORS['primary']
        )
        
        # Combobox
        style.configure(
            "Modern.TCombobox",
            fieldbackground=ModernStyle.COLORS['surface'],
            background=ModernStyle.COLORS['surface'],
            bordercolor=ModernStyle.COLORS['border'],
            arrowcolor=ModernStyle.COLORS['text'],
            selectbackground=ModernStyle.COLORS['primary'],
            selectforeground='white'
        )
        
        # Notebook (вкладки)
        style.configure(
            "Modern.TNotebook",
            background=ModernStyle.COLORS['background'],
            borderwidth=0
        )
        
        style.configure(
            "Modern.TNotebook.Tab",
            background=ModernStyle.COLORS['surface'],
            foreground=ModernStyle.COLORS['text'],
            padding=[20, 10],
            borderwidth=0
        )
        
        style.map(
            "Modern.TNotebook.Tab",
            background=[('selected', ModernStyle.COLORS['primary'])],
            foreground=[('selected', 'white')]
        )
    
    def create_widgets(self):
        """Створення віджетів інтерфейсу"""
        # Основний контейнер
        self.main_container = tk.Frame(self.root, bg=ModernStyle.COLORS['background'])
        self.main_container.pack(fill='both', expand=True)
        
        # Бічна панель
        self.create_sidebar()
        
        # Основна область
        self.content_area = tk.Frame(
            self.main_container,
            bg=ModernStyle.COLORS['background']
        )
        self.content_area.pack(side='right', fill='both', expand=True)
        
        # Заголовок
        self.create_header()
        
        # Область вмісту
        self.content_frame = tk.Frame(
            self.content_area,
            bg=ModernStyle.COLORS['background']
        )
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Створення сторінок
        self.create_pages()
        
        # Показ початкової сторінки
        self.show_page("dashboard")
    
    def create_sidebar(self):
        """Створення бічної панелі"""
        self.sidebar = tk.Frame(
            self.main_container,
            bg=ModernStyle.COLORS['sidebar'],
            width=ModernStyle.SIZES['sidebar_width']
        )
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        
        # Логотип/заголовок
        logo_frame = tk.Frame(self.sidebar, bg=ModernStyle.COLORS['sidebar'])
        logo_frame.pack(fill='x', pady=20)
        
        logo_label = tk.Label(
            logo_frame,
            text="🤖 Instagram Bot Pro",
            font=ModernStyle.FONTS['subtitle'],
            bg=ModernStyle.COLORS['sidebar'],
            fg=ModernStyle.COLORS['sidebar_text']
        )
        logo_label.pack()
        
        version_label = tk.Label(
            logo_frame,
            text="v2.0 Professional",
            font=ModernStyle.FONTS['small'],
            bg=ModernStyle.COLORS['sidebar'],
            fg=ModernStyle.COLORS['text_light']
        )
        version_label.pack()
        
        # Розділювач
        separator = tk.Frame(
            self.sidebar,
            bg=ModernStyle.COLORS['border'],
            height=1
        )
        separator.pack(fill='x', padx=20, pady=10)
        
        # Кнопки навігації
        self.nav_buttons = {}
        navigation_items = [
            ("📊", "Dashboard", "dashboard"),
            ("👥", "Акаунти", "accounts"),
            ("🎯", "Цілі", "targets"),
            ("⚙️", "Автоматизація", "automation"),
            ("📈", "Статистика", "statistics"),
            ("🔧", "Налаштування", "settings"),
            ("📚", "Довідка", "help")
        ]
        
        for icon, text, page in navigation_items:
            btn = SidebarButton(
                self.sidebar,
                icon=icon,
                text=text,
                command=lambda p=page: self.show_page(p)
            )
            btn.pack(fill='x')
            self.nav_buttons[page] = btn
        
        # Статус внизу
        self.create_sidebar_status()
    
    def create_sidebar_status(self):
        """Створення статусу в бічній панелі"""
        status_frame = tk.Frame(self.sidebar, bg=ModernStyle.COLORS['sidebar'])
        status_frame.pack(side='bottom', fill='x', padx=20, pady=20)
        
        # Статус системи
        self.system_status = StatusIndicator(status_frame)
        self.system_status.pack(anchor='w', pady=2)
        self.system_status.set_status('success', 'Система готова')
        
        # Статус автоматизації
        self.automation_status = StatusIndicator(status_frame)
        self.automation_status.pack(anchor='w', pady=2)
        self.automation_status.set_status('inactive', 'Автоматизація зупинена')
        
        # Кількість активних акаунтів
        self.accounts_status = StatusIndicator(status_frame)
        self.accounts_status.pack(anchor='w', pady=2)
        self.accounts_status.set_status('info', '0 активних акаунтів')
    
    def create_header(self):
        """Створення заголовка"""
        self.header = tk.Frame(
            self.content_area,
            bg=ModernStyle.COLORS['background'],
            height=80
        )
        self.header.pack(fill='x', padx=20, pady=(20, 0))
        self.header.pack_propagate(False)
        
        # Заголовок сторінки
        self.page_title = tk.Label(
            self.header,
            text="Dashboard",
            font=ModernStyle.FONTS['title'],
            bg=ModernStyle.COLORS['background'],
            fg=ModernStyle.COLORS['text']
        )
        self.page_title.pack(side='left', anchor='w')
        
        # Кнопки управління
        control_frame = tk.Frame(self.header, bg=ModernStyle.COLORS['background'])
        control_frame.pack(side='right', anchor='e')
        
        # Кнопка швидкого старту
        self.quick_start_btn = AnimatedButton(
            control_frame,
            text="🚀 Швидкий старт",
            command=self.quick_start,
            bg=ModernStyle.COLORS['success'],
            hover_bg='#059669'
        )
        self.quick_start_btn.pack(side='right', padx=(10, 0))
        
        # Кнопка стоп
        self.stop_btn = AnimatedButton(
            control_frame,
            text="⏹️ Зупинити",
            command=self.stop_automation,
            bg=ModernStyle.COLORS['error'],
            hover_bg='#dc2626',
            state='disabled'
        )
        self.stop_btn.pack(side='right', padx=(10, 0))
        
        # Кнопка налаштувань
        settings_btn = IconButton(
            control_frame,
            icon="⚙️",
            text="",
            command=lambda: self.show_page("settings")
        )
        settings_btn.pack(side='right')
    
    def create_pages(self):
        """Створення всіх сторінок"""
        self.pages = {}
        
        # Dashboard
        self.pages["dashboard"] = self.create_dashboard_page()
        
        # Акаунти
        self.pages["accounts"] = self.create_accounts_page()
        
        # Цілі
        self.pages["targets"] = self.create_targets_page()
        
        # Автоматизація
        self.pages["automation"] = self.create_automation_page()
        
        # Статистика
        self.pages["statistics"] = self.create_statistics_page()
        
        # Налаштування
        self.pages["settings"] = self.create_settings_page()
        
        # Довідка
        self.pages["help"] = self.create_help_page()
    
    def create_dashboard_page(self):
        """Створення головної сторінки"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.COLORS['background'])
        
        # Верхня панель з метриками
        metrics_frame = tk.Frame(page, bg=ModernStyle.COLORS['background'])
        metrics_frame.pack(fill='x', pady=(0, 20))
        
        # Картки метрик
        self.create_metric_cards(metrics_frame)
        
        # Основна область з двома колонками
        main_frame = tk.Frame(page, bg=ModernStyle.COLORS['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Ліва колонка
        left_column = tk.Frame(main_frame, bg=ModernStyle.COLORS['background'])
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Права колонка
        right_column = tk.Frame(main_frame, bg=ModernStyle.COLORS['background'])
        right_column.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Швидкі дії
        self.create_quick_actions(left_column)
        
        # Останні дії
        self.create_recent_activities(right_column)
        
        # Прогрес автоматизації
        self.automation_progress = ProgressCard(
            left_column,
            title="Прогрес автоматизації"
        )
        self.automation_progress.pack(fill='x', pady=(20, 0))
        
        return page
    
    def create_metric_cards(self, parent):
        """Створення карток метрик"""
        metrics = [
            ("📊", "Всього дій", "0", "today"),
            ("✅", "Успішних", "0", "success"),
            ("👥", "Акаунтів", "0", "accounts"),
            ("🎯", "Цілей", "0", "targets")
        ]
        
        self.metric_cards = {}
        
        for i, (icon, title, value, key) in enumerate(metrics):
            card = Card(parent)
            card.pack(side='left', fill='x', expand=True, padx=(0, 15 if i < 3 else 0))
            
            # Іконка
            icon_label = tk.Label(
                card,
                text=icon,
                font=('Arial', 24),
                bg=ModernStyle.COLORS['card'],
                fg=ModernStyle.COLORS['primary']
            )
            icon_label.pack(pady=(20, 5))
            
            # Значення
            value_label = tk.Label(
                card,
                text=value,
                font=ModernStyle.FONTS['title'],
                bg=ModernStyle.COLORS['card'],
                fg=ModernStyle.COLORS['text']
            )
            value_label.pack()
            
            # Заголовок
            title_label = tk.Label(
                card,
                text=title,
                font=ModernStyle.FONTS['small'],
                bg=ModernStyle.COLORS['card'],
                fg=ModernStyle.COLORS['text_secondary']
            )
            title_label.pack(pady=(0, 20))
            
            self.metric_cards[key] = value_label
    
    def create_quick_actions(self, parent):
        """Створення швидких дій"""
        card = Card(parent, title="Швидкі дії")
        card.pack(fill='x', pady=(0, 20))
        
        actions_frame = tk.Frame(card, bg=ModernStyle.COLORS['card'])
        actions_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        actions = [
            ("➕ Додати акаунт", lambda: self.show_page("accounts")),
            ("🎯 Додати цілі", lambda: self.show_page("targets")),
            ("⚙️ Налаштувати автоматизацію", lambda: self.show_page("automation")),
            ("📈 Переглянути статистику", lambda: self.show_page("statistics"))
        ]
        
        for i, (text, command) in enumerate(actions):
            if i % 2 == 0:
                row_frame = tk.Frame(actions_frame, bg=ModernStyle.COLORS['card'])
                row_frame.pack(fill='x', pady=5)
            
            btn = AnimatedButton(
                row_frame,
                text=text,
                command=command,
                bg=ModernStyle.COLORS['surface'],
                hover_bg=ModernStyle.COLORS['border'],
                fg=ModernStyle.COLORS['text']
            )
            btn.pack(side='left', fill='x', expand=True, padx=(0, 10 if i % 2 == 0 else 0))
    
    def create_recent_activities(self, parent):
        """Створення списку останніх дій"""
        card = Card(parent, title="Останні дії")
        card.pack(fill='both', expand=True)
        
        # Список активностей
        self.activity_listbox = tk.Listbox(
            card,
            font=ModernStyle.FONTS['small'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text'],
            selectbackground=ModernStyle.COLORS['primary'],
            selectforeground='white',
            relief='flat',
            borderwidth=0,
            highlightthickness=0
        )
        self.activity_listbox.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Заглушка
        activities = [
            "🕐 Запуск програми - щойно",
            "📊 Завантажено конфігурацію - щойно",
            "💾 Ініціалізовано базу даних - щойно"
        ]
        
        for activity in activities:
            self.activity_listbox.insert(tk.END, activity)
    
    def create_accounts_page(self):
        """Створення сторінки акаунтів"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.COLORS['background'])
        
        # Панель управління
        control_panel = Card(page, title="Управління акаунтами")
        control_panel.pack(fill='x', pady=(0, 20))
        
        btn_frame = tk.Frame(control_panel, bg=ModernStyle.COLORS['card'])
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Кнопки
        add_btn = AnimatedButton(
            btn_frame,
            text="➕ Додати акаунт",
            command=self.add_account_dialog,
            bg=ModernStyle.COLORS['success']
        )
        add_btn.pack(side='left', padx=(0, 10))
        
        import_btn = AnimatedButton(
            btn_frame,
            text="📂 Імпорт з файлу",
            command=self.import_accounts,
            bg=ModernStyle.COLORS['info']
        )
        import_btn.pack(side='left', padx=(0, 10))
        
        test_btn = AnimatedButton(
            btn_frame,
            text="🧪 Тестувати акаунти",
            command=self.test_accounts,
            bg=ModernStyle.COLORS['warning']
        )
        test_btn.pack(side='left')
        
        # Таблиця акаунтів
        accounts_card = Card(page, title="Список акаунтів")
        accounts_card.pack(fill='both', expand=True)
        
        # Створення Treeview
        columns = ('username', 'status', 'actions_today', 'total_actions', 'last_activity')
        self.accounts_tree = ttk.Treeview(
            accounts_card,
            columns=columns,
            show='headings',
            height=15
        )
        
        # Заголовки колонок
        self.accounts_tree.heading('username', text='Користувач')
        self.accounts_tree.heading('status', text='Статус')
        self.accounts_tree.heading('actions_today', text='Дій сьогодні')
        self.accounts_tree.heading('total_actions', text='Всього дій')
        self.accounts_tree.heading('last_activity', text='Остання активність')
        
        # Ширина колонок
        self.accounts_tree.column('username', width=150)
        self.accounts_tree.column('status', width=100)
        self.accounts_tree.column('actions_today', width=120)
        self.accounts_tree.column('total_actions', width=120)
        self.accounts_tree.column('last_activity', width=150)
        
        # Скролбар
        scrollbar = ttk.Scrollbar(accounts_card, orient='vertical', command=self.accounts_tree.yview)
        self.accounts_tree.configure(yscroll=scrollbar.set)
        
        # Упакування
        self.accounts_tree.pack(side='left', fill='both', expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side='right', fill='y', padx=(0, 20), pady=(0, 20))
        
        # Контекстне меню
        self.create_accounts_context_menu()
        
        return page
    
    def create_accounts_context_menu(self):
        """Створення контекстного меню для акаунтів"""
        self.accounts_context_menu = tk.Menu(self.root, tearoff=0)
        self.accounts_context_menu.add_command(label="✏️ Редагувати", command=self.edit_account)
        self.accounts_context_menu.add_command(label="🧪 Тестувати", command=self.test_selected_account)
        self.accounts_context_menu.add_command(label="📊 Статистика", command=self.show_account_stats)
        self.accounts_context_menu.add_separator()
        self.accounts_context_menu.add_command(label="🗑️ Видалити", command=self.delete_account)
        
        self.accounts_tree.bind("<Button-3>", self.show_accounts_context_menu)
    
    def create_targets_page(self):
        """Створення сторінки цілей"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.COLORS['background'])
        
        # Панель управління
        control_panel = Card(page, title="Управління цілями")
        control_panel.pack(fill='x', pady=(0, 20))
        
        btn_frame = tk.Frame(control_panel, bg=ModernStyle.COLORS['card'])
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Поле для додавання цілі
        input_frame = tk.Frame(btn_frame, bg=ModernStyle.COLORS['card'])
        input_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            input_frame,
            text="Ім'я користувача:",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text']
        ).pack(side='left')
        
        self.target_entry = tk.Entry(
            input_frame,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            relief='flat',
            bd=5
        )
        self.target_entry.pack(side='left', fill='x', expand=True, padx=(10, 10))
        self.target_entry.bind('<Return>', lambda e: self.add_target())
        
        add_target_btn = AnimatedButton(
            input_frame,
            text="➕ Додати",
            command=self.add_target,
            bg=ModernStyle.COLORS['success']
        )
        add_target_btn.pack(side='right')
        
        # Кнопки управління
        btn_control_frame = tk.Frame(btn_frame, bg=ModernStyle.COLORS['card'])
        btn_control_frame.pack(fill='x')
        
        import_targets_btn = AnimatedButton(
            btn_control_frame,
            text="📂 Імпорт з файлу",
            command=self.import_targets,
            bg=ModernStyle.COLORS['info']
        )
        import_targets_btn.pack(side='left', padx=(0, 10))
        
        export_targets_btn = AnimatedButton(
            btn_control_frame,
            text="💾 Експорт",
            command=self.export_targets,
            bg=ModernStyle.COLORS['secondary']
        )
        export_targets_btn.pack(side='left', padx=(0, 10))
        
        clear_targets_btn = AnimatedButton(
            btn_control_frame,
            text="🗑️ Очистити все",
            command=self.clear_targets,
            bg=ModernStyle.COLORS['error']
        )
        clear_targets_btn.pack(side='left')
        
        # Список цілей
        targets_card = Card(page, title="Список цілей")
        targets_card.pack(fill='both', expand=True)
        
        # Frame для списку
        list_frame = tk.Frame(targets_card, bg=ModernStyle.COLORS['card'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Listbox з scrollbar
        scrollbar_targets = ttk.Scrollbar(list_frame)
        scrollbar_targets.pack(side='right', fill='y')
        
        self.targets_listbox = tk.Listbox(
            list_frame,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            selectbackground=ModernStyle.COLORS['primary'],
            selectforeground='white',
            relief='flat',
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=scrollbar_targets.set
        )
        self.targets_listbox.pack(side='left', fill='both', expand=True)
        scrollbar_targets.config(command=self.targets_listbox.yview)
        
        # Контекстне меню для цілей
        self.create_targets_context_menu()
        
        return page
    
    def create_targets_context_menu(self):
        """Створення контекстного меню для цілей"""
        self.targets_context_menu = tk.Menu(self.root, tearoff=0)
        self.targets_context_menu.add_command(label="🔗 Відкрити в браузері", command=self.open_target_profile)
        self.targets_context_menu.add_command(label="📊 Показати статистику", command=self.show_target_stats)
        self.targets_context_menu.add_separator()
        self.targets_context_menu.add_command(label="🗑️ Видалити", command=self.delete_target)
        
        self.targets_listbox.bind("<Button-3>", self.show_targets_context_menu)
        self.targets_listbox.bind("<Double-Button-1>", lambda e: self.open_target_profile())
    
    def create_automation_page(self):
        """Створення сторінки автоматизації"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.COLORS['background'])
        
        # Дві колонки
        left_column = tk.Frame(page, bg=ModernStyle.COLORS['background'])
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_column = tk.Frame(page, bg=ModernStyle.COLORS['background'])
        right_column.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Налаштування дій
        actions_card = Card(left_column, title="Налаштування дій")
        actions_card.pack(fill='x', pady=(0, 20))
        
        actions_frame = tk.Frame(actions_card, bg=ModernStyle.COLORS['card'])
        actions_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Чекбокси для дій
        self.action_vars = {}
        actions = [
            ("like_posts", "❤️ Лайкати пости", True),
            ("like_stories", "📖 Лайкати сторіс", True),
            ("reply_stories", "💬 Відповідати на сторіс", False),
            ("send_dm", "📩 Відправляти DM", False)
        ]
        
        for var_name, text, default in actions:
            var = tk.BooleanVar(value=default)
            self.action_vars[var_name] = var
            
            check = tk.Checkbutton(
                actions_frame,
                text=text,
                variable=var,
                font=ModernStyle.FONTS['body'],
                bg=ModernStyle.COLORS['card'],
                fg=ModernStyle.COLORS['text'],
                selectcolor=ModernStyle.COLORS['surface'],
                relief='flat',
                borderwidth=0
            )
            check.pack(anchor='w', pady=5)
        
        # Налаштування планувальника
        scheduler_card = Card(left_column, title="Планувальник")
        scheduler_card.pack(fill='x', pady=(0, 20))
        
        scheduler_frame = tk.Frame(scheduler_card, bg=ModernStyle.COLORS['card'])
        scheduler_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Час роботи
        time_frame = tk.Frame(scheduler_frame, bg=ModernStyle.COLORS['card'])
        time_frame.pack(fill='x', pady=5)
        
        tk.Label(
            time_frame,
            text="Час роботи:",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text']
        ).pack(side='left')
        
        self.start_time_var = tk.StringVar(value="09:00")
        start_time_combo = ttk.Combobox(
            time_frame,
            textvariable=self.start_time_var,
            values=[f"{h:02d}:00" for h in range(24)],
            width=8,
            state='readonly'
        )
        start_time_combo.pack(side='left', padx=(10, 5))
        
        tk.Label(
            time_frame,
            text="до",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text']
        ).pack(side='left', padx=5)
        
        self.end_time_var = tk.StringVar(value="22:00")
        end_time_combo = ttk.Combobox(
            time_frame,
            textvariable=self.end_time_var,
            values=[f"{h:02d}:00" for h in range(24)],
            width=8,
            state='readonly'
        )
        end_time_combo.pack(side='left', padx=5)
        
        # Інтервал роботи
        interval_frame = tk.Frame(scheduler_frame, bg=ModernStyle.COLORS['card'])
        interval_frame.pack(fill='x', pady=5)
        
        tk.Label(
            interval_frame,
            text="Інтервал (хв):",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text']
        ).pack(side='left')
        
        self.interval_var = tk.StringVar(value="30")
        interval_entry = tk.Entry(
            interval_frame,
            textvariable=self.interval_var,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            width=10,
            relief='flat',
            bd=5
        )
        interval_entry.pack(side='left', padx=(10, 0))
        
        # Ліміти безпеки
        limits_card = Card(left_column, title="Ліміти безпеки")
        limits_card.pack(fill='x')
        
        limits_frame = tk.Frame(limits_card, bg=ModernStyle.COLORS['card'])
        limits_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Дії на день
        daily_frame = tk.Frame(limits_frame, bg=ModernStyle.COLORS['card'])
        daily_frame.pack(fill='x', pady=5)
        
        tk.Label(
            daily_frame,
            text="Дій на день:",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text']
        ).pack(side='left')
        
        self.daily_limit_var = tk.StringVar(value="80")
        daily_entry = tk.Entry(
            daily_frame,
            textvariable=self.daily_limit_var,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            width=10,
            relief='flat',
            bd=5
        )
        daily_entry.pack(side='left', padx=(10, 0))
        
        # Дії на годину
        hourly_frame = tk.Frame(limits_frame, bg=ModernStyle.COLORS['card'])
        hourly_frame.pack(fill='x', pady=5)
        
        tk.Label(
            hourly_frame,
            text="Дій на годину:",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text']
        ).pack(side='left')
        
        self.hourly_limit_var = tk.StringVar(value="15")
        hourly_entry = tk.Entry(
            hourly_frame,
            textvariable=self.hourly_limit_var,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            width=10,
            relief='flat',
            bd=5
        )
        hourly_entry.pack(side='left', padx=(10, 0))
        
        # Права колонка - Управління і лог
        control_card = Card(right_column, title="Управління автоматизацією")
        control_card.pack(fill='x', pady=(0, 20))
        
        control_frame = tk.Frame(control_card, bg=ModernStyle.COLORS['card'])
        control_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Великі кнопки управління
        self.start_automation_btn = AnimatedButton(
            control_frame,
            text="🚀 Запустити автоматизацію",
            command=self.start_automation,
            bg=ModernStyle.COLORS['success']
        )
        self.start_automation_btn.pack(fill='x', pady=(0, 10))
        
        self.pause_automation_btn = AnimatedButton(
            control_frame,
            text="⏸️ Призупинити",
            command=self.pause_automation,
            bg=ModernStyle.COLORS['warning'],
            state='disabled'
        )
        self.pause_automation_btn.pack(fill='x', pady=(0, 10))
        
        self.stop_automation_btn = AnimatedButton(
            control_frame,
            text="⏹️ Зупинити",
            command=self.stop_automation,
            bg=ModernStyle.COLORS['error'],
            state='disabled'
        )
        self.stop_automation_btn.pack(fill='x')
        
        # Лог автоматизації
        log_card = Card(right_column, title="Лог автоматизації")
        log_card.pack(fill='both', expand=True)
        
        self.automation_log = scrolledtext.ScrolledText(
            log_card,
            font=ModernStyle.FONTS['code'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            relief='flat',
            borderwidth=0,
            wrap=tk.WORD,
            state='disabled'
        )
        self.automation_log.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        return page
    
    def create_statistics_page(self):
        """Створення сторінки статистики"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.COLORS['background'])
        
        # Панель фільтрів
        filter_card = Card(page, title="Фільтри")
        filter_card.pack(fill='x', pady=(0, 20))
        
        filter_frame = tk.Frame(filter_card, bg=ModernStyle.COLORS['card'])
        filter_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Період
        period_frame = tk.Frame(filter_frame, bg=ModernStyle.COLORS['card'])
        period_frame.pack(side='left')
        
        tk.Label(
            period_frame,
            text="Період:",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text']
        ).pack(side='left')
        
        self.period_var = tk.StringVar(value="7 днів")
        period_combo = ttk.Combobox(
            period_frame,
            textvariable=self.period_var,
            values=["1 день", "7 днів", "30 днів", "Весь час"],
            width=10,
            state='readonly'
        )
        period_combo.pack(side='left', padx=(10, 0))
        
        # Кнопка оновлення
        refresh_btn = AnimatedButton(
            filter_frame,
            text="🔄 Оновити",
            command=self.refresh_statistics,
            bg=ModernStyle.COLORS['info']
        )
        refresh_btn.pack(side='right')
        
        # Основна область з графіками
        charts_frame = tk.Frame(page, bg=ModernStyle.COLORS['background'])
        charts_frame.pack(fill='both', expand=True)
        
        # Дві колонки для графіків
        left_charts = tk.Frame(charts_frame, bg=ModernStyle.COLORS['background'])
        left_charts.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_charts = tk.Frame(charts_frame, bg=ModernStyle.COLORS['background'])
        right_charts.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Графік дій по днях
        daily_stats_card = Card(left_charts, title="Дії по днях")
        daily_stats_card.pack(fill='both', expand=True, pady=(0, 20))
        
        # Заглушка для графіка
        chart_frame = tk.Frame(daily_stats_card, bg=ModernStyle.COLORS['surface'], height=200)
        chart_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        chart_frame.pack_propagate(False)
        
        chart_label = tk.Label(
            chart_frame,
            text="📈 Графік дій по днях\n(інтеграція з matplotlib)",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text_secondary']
        )
        chart_label.pack(expand=True)
        
        # Топ цілей
        top_targets_card = Card(left_charts, title="Топ цілей")
        top_targets_card.pack(fill='both', expand=True)
        
        self.top_targets_listbox = tk.Listbox(
            top_targets_card,
            font=ModernStyle.FONTS['small'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            relief='flat',
            borderwidth=0,
            highlightthickness=0
        )
        self.top_targets_listbox.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Статистика по акаунтах
        accounts_stats_card = Card(right_charts, title="Статистика по акаунтах")
        accounts_stats_card.pack(fill='both', expand=True, pady=(0, 20))
        
        # Таблиця статистики акаунтів
        accounts_stats_frame = tk.Frame(accounts_stats_card, bg=ModernStyle.COLORS['card'])
        accounts_stats_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        columns = ('account', 'actions', 'success_rate')
        self.stats_tree = ttk.Treeview(
            accounts_stats_frame,
            columns=columns,
            show='headings',
            height=8
        )
        
        self.stats_tree.heading('account', text='Акаунт')
        self.stats_tree.heading('actions', text='Дії')
        self.stats_tree.heading('success_rate', text='% успіху')
        
        self.stats_tree.column('account', width=120)
        self.stats_tree.column('actions', width=80)
        self.stats_tree.column('success_rate', width=100)
        
        self.stats_tree.pack(fill='both', expand=True)
        
        # Загальна статистика
        summary_card = Card(right_charts, title="Загальна статистика")
        summary_card.pack(fill='both', expand=True)
        
        summary_frame = tk.Frame(summary_card, bg=ModernStyle.COLORS['card'])
        summary_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Статистичні дані
        stats_data = [
            "Всього дій: 0",
            "Успішних дій: 0",
            "Процент успіху: 0%",
            "Середня швидкість: 0 дій/год",
            "Найактивніший акаунт: -",
            "Найпопулярніша ціль: -"
        ]
        
        for stat in stats_data:
            stat_label = tk.Label(
                summary_frame,
                text=stat,
                font=ModernStyle.FONTS['body'],
                bg=ModernStyle.COLORS['card'],
                fg=ModernStyle.COLORS['text'],
                anchor='w'
            )
            stat_label.pack(fill='x', pady=2)
        
        return page
    
    def create_settings_page(self):
        """Створення сторінки налаштувань"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.COLORS['background'])
        
        # Notebook для вкладок
        notebook = ttk.Notebook(page, style="Modern.TNotebook")
        notebook.pack(fill='both', expand=True)
        
        # Вкладка "Загальні"
        general_tab = tk.Frame(notebook, bg=ModernStyle.COLORS['background'])
        notebook.add(general_tab, text="Загальні")
        
        # Вкладка "Затримки"
        delays_tab = tk.Frame(notebook, bg=ModernStyle.COLORS['background'])
        notebook.add(delays_tab, text="Затримки")
        
        # Вкладка "Проксі"
        proxy_tab = tk.Frame(notebook, bg=ModernStyle.COLORS['background'])
        notebook.add(proxy_tab, text="Проксі")
        
        # Вкладка "Повідомлення"
        messages_tab = tk.Frame(notebook, bg=ModernStyle.COLORS['background'])
        notebook.add(messages_tab, text="Повідомлення")
        
        # Заповнення вкладок
        self.create_general_settings(general_tab)
        self.create_delays_settings(delays_tab)
        self.create_proxy_settings(proxy_tab)
        self.create_messages_settings(messages_tab)
        
        return page
    
    def create_general_settings(self, parent):
        """Створення загальних налаштувань"""
        # API налаштування
        api_card = Card(parent, title="API налаштування")
        api_card.pack(fill='x', padx=20, pady=20)
        
        api_frame = tk.Frame(api_card, bg=ModernStyle.COLORS['card'])
        api_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Капча API
        captcha_frame = tk.Frame(api_frame, bg=ModernStyle.COLORS['card'])
        captcha_frame.pack(fill='x', pady=10)
        
        tk.Label(
            captcha_frame,
            text="2captcha API ключ:",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text']
        ).pack(anchor='w')
        
        self.captcha_api_var = tk.StringVar(value=self.config_manager.get('captcha_api_key', ''))
        captcha_entry = tk.Entry(
            captcha_frame,
            textvariable=self.captcha_api_var,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            relief='flat',
            bd=5,
            show='*'
        )
        captcha_entry.pack(fill='x', pady=(5, 0))
        
        # Безпека
        security_card = Card(parent, title="Налаштування безпеки")
        security_card.pack(fill='x', padx=20, pady=(0, 20))
        
        security_frame = tk.Frame(security_card, bg=ModernStyle.COLORS['card'])
        security_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.safety_vars = {}
        safety_options = [
            ("check_shadowban", "Перевіряти shadowban"),
            ("avoid_suspicious_behavior", "Уникати підозрілої поведінки"),
            ("randomize_actions", "Рандомізувати дії"),
            ("human_like_delays", "Людські затримки"),
            ("monitor_account_health", "Моніторити здоров'я акаунтів")
        ]
        
        for var_name, text in safety_options:
            var = tk.BooleanVar(value=self.config_manager.get(f'safety_settings.{var_name}', True))
            self.safety_vars[var_name] = var
            
            check = tk.Checkbutton(
                security_frame,
                text=text,
                variable=var,
                font=ModernStyle.FONTS['body'],
                bg=ModernStyle.COLORS['card'],
                fg=ModernStyle.COLORS['text'],
                selectcolor=ModernStyle.COLORS['surface'],
                relief='flat'
            )
            check.pack(anchor='w', pady=2)
        
        # Кнопки
        buttons_frame = tk.Frame(parent, bg=ModernStyle.COLORS['background'])
        buttons_frame.pack(fill='x', padx=20, pady=20)
        
        save_btn = AnimatedButton(
            buttons_frame,
            text="💾 Зберегти налаштування",
            command=self.save_settings,
            bg=ModernStyle.COLORS['success']
        )
        save_btn.pack(side='left', padx=(0, 10))
        
        reset_btn = AnimatedButton(
            buttons_frame,
            text="🔄 Скинути до стандартних",
            command=self.reset_settings,
            bg=ModernStyle.COLORS['warning']
        )
        reset_btn.pack(side='left')
    
    def create_delays_settings(self, parent):
     """Створення налаштувань затримок"""
     delays_card = Card(parent, title="Налаштування затримок (секунди)")
     delays_card.pack(fill='both', expand=True, padx=20, pady=20)
    
     delays_frame = tk.Frame(delays_card, bg=ModernStyle.COLORS['card'])
     delays_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
     self.delay_vars = {}
     delay_settings = [
        ("like", "Лайки", [2, 5]),
        ("comment", "Коментарі", [3, 8]),
        ("story_view", "Перегляд сторіс", [1, 3]),
        ("story_reply", "Відповіді на сторіс", [2, 6]),
        ("direct_message", "Прямі повідомлення", [5, 12]),
        ("between_actions", "Між діями", [8, 15]),
        ("between_targets", "Між цілями", [15, 45])
    ]
    
     for action, label, default_range in delay_settings:
        frame = tk.Frame(delays_frame, bg=ModernStyle.COLORS['card'])
        frame.pack(fill='x', pady=5)
        
        # Мітка з назвою дії
        tk.Label(
            frame,
            text=f"{label}:",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text'],
            width=20,
            anchor='w'
        ).pack(side='left')
        
        # Мітка "від"
        tk.Label(
            frame,
            text="від",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text']
        ).pack(side='left', padx=(10, 5))
        
        # Створення змінних для мін/макс значень
        min_var = tk.StringVar(value=str(default_range[0]))
        max_var = tk.StringVar(value=str(default_range[1]))
        
        # Поле для мінімального значення
        min_entry = tk.Entry(
            frame,
            textvariable=min_var,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            width=8,
            relief='flat',
            bd=5
        )
        min_entry.pack(side='left', padx=2)
        
        # Мітка "до"
        tk.Label(
            frame,
            text="до",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text']
        ).pack(side='left', padx=5)
        
        # Поле для максимального значення
        max_entry = tk.Entry(
            frame,
            textvariable=max_var,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            width=8,
            relief='flat',
            bd=5
        )
        max_entry.pack(side='left', padx=2)
        
        # Мітка "сек"
        tk.Label(
            frame,
            text="сек",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text']
        ).pack(side='left', padx=(5, 0))
        
        # Збереження змінних для подальшого використання
        self.delay_vars[action] = (min_var, max_var)

    
    def create_proxy_settings(self, parent):
        """Створення налаштувань проксі"""
        # Управління проксі
        control_card = Card(parent, title="Управління проксі")
        control_card.pack(fill='x', padx=20, pady=20)
        
        control_frame = tk.Frame(control_card, bg=ModernStyle.COLORS['card'])
        control_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Додавання проксі
        add_frame = tk.Frame(control_frame, bg=ModernStyle.COLORS['card'])
        add_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            add_frame,
            text="Формат: ip:port або ip:port:user:pass",
            font=ModernStyle.FONTS['small'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text_secondary']
        ).pack(anchor='w')
        
        proxy_input_frame = tk.Frame(add_frame, bg=ModernStyle.COLORS['card'])
        proxy_input_frame.pack(fill='x', pady=(5, 0))
        
        self.proxy_entry = tk.Entry(
            proxy_input_frame,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            relief='flat',
            bd=5
        )
        self.proxy_entry.pack(side='left', fill='x', expand=True)
        self.proxy_entry.bind('<Return>', lambda e: self.add_proxy())
        
        add_proxy_btn = AnimatedButton(
            proxy_input_frame,
            text="➕ Додати",
            command=self.add_proxy,
            bg=ModernStyle.COLORS['success']
        )
        add_proxy_btn.pack(side='right', padx=(10, 0))
        
        # Кнопки управління
        btn_frame = tk.Frame(control_frame, bg=ModernStyle.COLORS['card'])
        btn_frame.pack(fill='x')
        
        import_proxy_btn = AnimatedButton(
            btn_frame,
            text="📂 Імпорт з файлу",
            command=self.import_proxies,
            bg=ModernStyle.COLORS['info']
        )
        import_proxy_btn.pack(side='left', padx=(0, 10))
        
        test_proxies_btn = AnimatedButton(
            btn_frame,
            text="🧪 Тестувати всі",
            command=self.test_proxies,
            bg=ModernStyle.COLORS['warning']
        )
        test_proxies_btn.pack(side='left', padx=(0, 10))
        
        clear_proxies_btn = AnimatedButton(
            btn_frame,
            text="🗑️ Очистити все",
            command=self.clear_proxies,
            bg=ModernStyle.COLORS['error']
        )
        clear_proxies_btn.pack(side='left')
        
        # Список проксі
        proxy_list_card = Card(parent, title="Список проксі")
        proxy_list_card.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Treeview для проксі
        proxy_frame = tk.Frame(proxy_list_card, bg=ModernStyle.COLORS['card'])
        proxy_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        proxy_columns = ('proxy', 'status', 'response_time', 'last_check')
        self.proxy_tree = ttk.Treeview(
            proxy_frame,
            columns=proxy_columns,
            show='headings',
            height=10
        )
        
        self.proxy_tree.heading('proxy', text='Проксі')
        self.proxy_tree.heading('status', text='Статус')
        self.proxy_tree.heading('response_time', text='Час відповіді')
        self.proxy_tree.heading('last_check', text='Остання перевірка')
        
        self.proxy_tree.column('proxy', width=200)
        self.proxy_tree.column('status', width=100)
        self.proxy_tree.column('response_time', width=120)
        self.proxy_tree.column('last_check', width=150)
        
        # Scrollbar для проксі
        proxy_scrollbar = ttk.Scrollbar(proxy_frame, orient='vertical', command=self.proxy_tree.yview)
        self.proxy_tree.configure(yscroll=proxy_scrollbar.set)
        
        self.proxy_tree.pack(side='left', fill='both', expand=True)
        proxy_scrollbar.pack(side='right', fill='y')
        
        # Контекстне меню для проксі
        self.create_proxy_context_menu()
    
    def create_proxy_context_menu(self):
        """Створення контекстного меню для проксі"""
        self.proxy_context_menu = tk.Menu(self.root, tearoff=0)
        self.proxy_context_menu.add_command(label="🧪 Тестувати", command=self.test_selected_proxy)
        self.proxy_context_menu.add_command(label="📋 Копіювати", command=self.copy_proxy)
        self.proxy_context_menu.add_separator()
        self.proxy_context_menu.add_command(label="🗑️ Видалити", command=self.delete_proxy)
        
        self.proxy_tree.bind("<Button-3>", self.show_proxy_context_menu)
    
    def create_messages_settings(self, parent):
        """Створення налаштувань повідомлень"""
        # Повідомлення для сторіс
        stories_card = Card(parent, title="Відповіді на сторіс")
        stories_card.pack(fill='both', expand=True, padx=20, pady=20)
        
        stories_frame = tk.Frame(stories_card, bg=ModernStyle.COLORS['card'])
        stories_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Додавання повідомлення
        add_story_frame = tk.Frame(stories_frame, bg=ModernStyle.COLORS['card'])
        add_story_frame.pack(fill='x', pady=(0, 10))
        
        self.story_message_entry = tk.Entry(
            add_story_frame,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            relief='flat',
            bd=5
        )
        self.story_message_entry.pack(side='left', fill='x', expand=True)
        self.story_message_entry.bind('<Return>', lambda e: self.add_story_message())
        
        add_story_btn = AnimatedButton(
            add_story_frame,
            text="➕ Додати",
            command=self.add_story_message,
            bg=ModernStyle.COLORS['success']
        )
        add_story_btn.pack(side='right', padx=(10, 0))
        
        # Список повідомлень для сторіс
        self.story_messages_listbox = tk.Listbox(
            stories_frame,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            selectbackground=ModernStyle.COLORS['primary'],
            selectforeground='white',
            relief='flat',
            borderwidth=0,
            highlightthickness=0,
            height=8
        )
        self.story_messages_listbox.pack(fill='both', expand=True, pady=(0, 10))
        
        # Кнопки управління повідомленнями сторіс
        story_btn_frame = tk.Frame(stories_frame, bg=ModernStyle.COLORS['card'])
        story_btn_frame.pack(fill='x')
        
        delete_story_btn = AnimatedButton(
            story_btn_frame,
            text="🗑️ Видалити вибране",
            command=self.delete_story_message,
            bg=ModernStyle.COLORS['error']
        )
        delete_story_btn.pack(side='left', padx=(0, 10))
        
        load_default_stories_btn = AnimatedButton(
            story_btn_frame,
            text="🔄 Завантажити стандартні",
            command=self.load_default_story_messages,
            bg=ModernStyle.COLORS['info']
        )
        load_default_stories_btn.pack(side='left')
        
        # Прямі повідомлення
        dm_card = Card(parent, title="Прямі повідомлення")
        dm_card.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        dm_frame = tk.Frame(dm_card, bg=ModernStyle.COLORS['card'])
        dm_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Додавання DM
        add_dm_frame = tk.Frame(dm_frame, bg=ModernStyle.COLORS['card'])
        add_dm_frame.pack(fill='x', pady=(0, 10))
        
        self.dm_message_entry = tk.Entry(
            add_dm_frame,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            relief='flat',
            bd=5
        )
        self.dm_message_entry.pack(side='left', fill='x', expand=True)
        self.dm_message_entry.bind('<Return>', lambda e: self.add_dm_message())
        
        add_dm_btn = AnimatedButton(
            add_dm_frame,
            text="➕ Додати",
            command=self.add_dm_message,
            bg=ModernStyle.COLORS['success']
        )
        add_dm_btn.pack(side='right', padx=(10, 0))
        
        # Список DM
        self.dm_messages_listbox = tk.Listbox(
            dm_frame,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            selectbackground=ModernStyle.COLORS['primary'],
            selectforeground='white',
            relief='flat',
            borderwidth=0,
            highlightthickness=0,
            height=6
        )
        self.dm_messages_listbox.pack(fill='both', expand=True, pady=(0, 10))
        
        # Кнопки управління DM
        dm_btn_frame = tk.Frame(dm_frame, bg=ModernStyle.COLORS['card'])
        dm_btn_frame.pack(fill='x')
        
        delete_dm_btn = AnimatedButton(
            dm_btn_frame,
            text="🗑️ Видалити вибране",
            command=self.delete_dm_message,
            bg=ModernStyle.COLORS['error']
        )
        delete_dm_btn.pack(side='left', padx=(0, 10))
        
        load_default_dm_btn = AnimatedButton(
            dm_btn_frame,
            text="🔄 Завантажити стандартні",
            command=self.load_default_dm_messages,
            bg=ModernStyle.COLORS['info']
        )
        load_default_dm_btn.pack(side='left')
    
    def create_help_page(self):
        """Створення сторінки довідки"""
        page = tk.Frame(self.content_frame, bg=ModernStyle.COLORS['background'])
        
        # Notebook для розділів довідки
        help_notebook = ttk.Notebook(page, style="Modern.TNotebook")
        help_notebook.pack(fill='both', expand=True)
        
        # Початок роботи
        getting_started_tab = tk.Frame(help_notebook, bg=ModernStyle.COLORS['background'])
        help_notebook.add(getting_started_tab, text="Початок роботи")
        
        # FAQ
        faq_tab = tk.Frame(help_notebook, bg=ModernStyle.COLORS['background'])
        help_notebook.add(faq_tab, text="FAQ")
        
        # Про програму
        about_tab = tk.Frame(help_notebook, bg=ModernStyle.COLORS['background'])
        help_notebook.add(about_tab, text="Про програму")
        
        # Заповнення розділів
        self.create_getting_started_help(getting_started_tab)
        self.create_faq_help(faq_tab)
        self.create_about_help(about_tab)
        
        return page
    
    def create_getting_started_help(self, parent):
        """Створення розділу "Початок роботи" """
        help_text = """
🚀 ШВИДКИЙ СТАРТ

1. Додайте акаунти Instagram:
   • Перейдіть на вкладку "Акаунти"
   • Натисніть "Додати акаунт"
   • Введіть логін та пароль

2. Додайте цілі:
   • Перейдіть на вкладку "Цілі"
   • Введіть імена користувачів Instagram
   • Можете імпортувати список з файлу

3. Налаштуйте автоматизацію:
   • Оберіть необхідні дії (лайки, коментарі, тощо)
   • Встановіть безпечні ліміти
   • Налаштуйте розклад роботи

4. Запустіть автоматизацію:
   • Натисніть "Швидкий старт" або
   • Перейдіть на "Автоматизація" і натисніть "Запустити"

⚠️ ВАЖЛИВО:
• Використовуйте якісні проксі для кожного акаунту
• Не перевищуйте рекомендовані ліміти
• Регулярно перевіряйте стан акаунтів
        """
        
        text_widget = scrolledtext.ScrolledText(
            parent,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['background'],
            fg=ModernStyle.COLORS['text'],
            relief='flat',
            borderwidth=0,
            wrap=tk.WORD,
            state='normal'
        )
        text_widget.pack(fill='both', expand=True, padx=20, pady=20)
        text_widget.insert('1.0', help_text)
        text_widget.configure(state='disabled')
    
    def create_faq_help(self, parent):
        """Створення розділу FAQ"""
        faq_text = """
❓ ЧАСТІ ПИТАННЯ

Q: Чому акаунт заблокований?
A: Можливі причини:
   • Перевищено ліміти дій
   • Використання неякісних проксі
   • Підозріла активність
   
   Рішення: Зменшіть ліміти, змініть проксі, зробіть паузу

Q: Як налаштувати проксі?
A: Формати проксі:
   • ip:port
   • ip:port:username:password
   • domain.com:port:username:password

Q: Які ліміти безпечні?
A: Рекомендації:
   • 50-80 дій на день на акаунт
   • 10-15 дій на годину
   • Затримки 2-5 секунд між діями

Q: Програма не запускається
A: Перевірте:
   • Встановлений Google Chrome
   • Встановлені всі залежності (pip install -r requirements.txt)
   • Права доступу до файлів

Q: Як оновити програму?
A: Завантажте нову версію з офіційного сайту
   або використайте git pull (якщо встановлено через git)

Q: Підтримка капчі
A: Програма підтримує автоматичне розв'язання капчі
   через сервіс 2captcha.com. Додайте API ключ в налаштуваннях.
        """
        
        faq_widget = scrolledtext.ScrolledText(
            parent,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['background'],
            fg=ModernStyle.COLORS['text'],
            relief='flat',
            borderwidth=0,
            wrap=tk.WORD,
            state='normal'
        )
        faq_widget.pack(fill='both', expand=True, padx=20, pady=20)
        faq_widget.insert('1.0', faq_text)
        faq_widget.configure(state='disabled')
    
    def create_about_help(self, parent):
        """Створення розділу "Про програму" """
        about_frame = tk.Frame(parent, bg=ModernStyle.COLORS['background'])
        about_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Логотип та назва
        title_frame = tk.Frame(about_frame, bg=ModernStyle.COLORS['background'])
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="🤖 Instagram Bot Pro v2.0",
            font=ModernStyle.FONTS['title'],
            bg=ModernStyle.COLORS['background'],
            fg=ModernStyle.COLORS['primary']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Професійна автоматизація Instagram",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['background'],
            fg=ModernStyle.COLORS['text_secondary']
        )
        subtitle_label.pack()
        
        # Інформація
        info_card = Card(about_frame, title="Інформація про програму")
        info_card.pack(fill='x', pady=(0, 20))
        
        info_text = """
📋 Версія: 2.0.0 Professional
🗓️ Дата релізу: 2024
👨‍💻 Розробник: Instagram Bot Team
🌐 Сайт: https://instagrambot.pro
📧 Підтримка: support@instagrambot.pro

✨ ОСОБЛИВОСТІ:
• Повний обхід систем захисту Instagram
• Підтримка капчі та 2FA
• Розумні затримки та обмеження
• Мультиакаунтна робота
• Детальна статистика
• Сучасний інтерфейс

🛡️ БЕЗПЕКА:
Програма розроблена з урахуванням усіх вимог безпеки
та використовує найсучасніші методи обходу детекції.
        """
        
        info_label = tk.Label(
            info_card,
            text=info_text,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['card'],
            fg=ModernStyle.COLORS['text'],
            justify='left',
            anchor='nw'
        )
        info_label.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Кнопки
        buttons_frame = tk.Frame(about_frame, bg=ModernStyle.COLORS['background'])
        buttons_frame.pack(fill='x')
        
        website_btn = AnimatedButton(
            buttons_frame,
            text="🌐 Відвідати сайт",
            command=lambda: webbrowser.open("https://instagrambot.pro"),
            bg=ModernStyle.COLORS['info']
        )
        website_btn.pack(side='left', padx=(0, 10))
        
        support_btn = AnimatedButton(
            buttons_frame,
            text="📧 Техпідтримка",
            command=lambda: webbrowser.open("mailto:support@instagrambot.pro"),
            bg=ModernStyle.COLORS['secondary']
        )
        support_btn.pack(side='left', padx=(0, 10))
        
        donate_btn = AnimatedButton(
            buttons_frame,
            text="☕ Подякувати розробнику",
            command=lambda: messagebox.showinfo("Подяка", "Дякуємо за підтримку! 🙏"),
            bg=ModernStyle.COLORS['warning']
        )
        donate_btn.pack(side='left')
    
    # Методи управління сторінками
    def show_page(self, page_name):
        """Показ сторінки"""
        # Приховування всіх сторінок
        for page in self.pages.values():
            page.pack_forget()
        
        # Показ вибраної сторінки
        if page_name in self.pages:
            self.pages[page_name].pack(fill='both', expand=True)
            
            # Оновлення заголовка
            titles = {
                "dashboard": "📊 Dashboard",
                "accounts": "👥 Управління акаунтами",
                "targets": "🎯 Управління цілями",
                "automation": "⚙️ Автоматизація",
                "statistics": "📈 Статистика",
                "settings": "🔧 Налаштування",
                "help": "📚 Довідка"
            }
            
            self.page_title.configure(text=titles.get(page_name, page_name))
            
            # Оновлення активної кнопки в сайдбарі
            for btn_name, btn in self.nav_buttons.items():
                btn.set_active(btn_name == page_name)
            
            self.current_page = page_name
            
            # Оновлення даних сторінки
            if page_name == "dashboard":
                self.update_dashboard()
            elif page_name == "accounts":
                self.update_accounts_list()
            elif page_name == "targets":
                self.update_targets_list()
            elif page_name == "statistics":
                self.update_statistics_page()
    
    # Методи функціоналу
    def load_initial_data(self):
        """Завантаження початкових даних"""
        try:
            # Завантаження акаунтів
            self.update_accounts_list()
            
            # Завантаження цілей
            self.update_targets_list()
            
            # Завантаження налаштувань
            self.load_settings()
            
            # Завантаження повідомлень
            self.load_messages()
            
            # Оновлення статистики
            self.update_dashboard()
            
        except Exception as e:
            self.log_message(f"Помилка завантаження даних: {e}", "error")
    
    def update_dashboard(self):
        """Оновлення Dashboard"""
        try:
            # Отримання статистики з бази даних
            stats = self.db_manager.get_statistics()
            
            # Оновлення карток метрик
            self.metric_cards["today"].configure(text=str(stats.get("today_actions", 0)))
            self.metric_cards["success"].configure(text=str(stats.get("successful_actions", 0)))
            self.metric_cards["accounts"].configure(text=str(stats.get("active_accounts", 0)))
            
            # Підрахунок цілей
            targets_count = self.targets_listbox.size() if hasattr(self, 'targets_listbox') else 0
            self.metric_cards["targets"].configure(text=str(targets_count))
            
            # Оновлення статусу акаунтів
            self.accounts_status.set_status('info', f'{stats.get("active_accounts", 0)} активних акаунтів')
            
        except Exception as e:
            self.log_message(f"Помилка оновлення dashboard: {e}", "error")
    
    def update_accounts_list(self):
        """Оновлення списку акаунтів"""
        try:
            # Очищення списку
            for item in self.accounts_tree.get_children():
                self.accounts_tree.delete(item)
            
            # Додавання акаунтів з бази даних
            if hasattr(self, 'bot') and self.bot:
                accounts = self.bot.account_manager.accounts
                for username, account_data in accounts.items():
                    stats = self.db_manager.get_account_stats(username)
                    
                    self.accounts_tree.insert('', 'end', values=(
                        username,
                        account_data.get('status', 'active'),
                        stats.get('daily_actions', 0),
                        stats.get('total_actions', 0),
                        account_data.get('last_activity', 'Ніколи')
                    ))
            
        except Exception as e:
            self.log_message(f"Помилка оновлення списку акаунтів: {e}", "error")
    
    def update_targets_list(self):
        """Оновлення списку цілей"""
        try:
            # Очищення списку
            self.targets_listbox.delete(0, tk.END)
            
            # Завантаження цілей з файлу
            targets_file = "targets.txt"
            if os.path.exists(targets_file):
                with open(targets_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        target = line.strip()
                        if target and not target.startswith('#'):
                            self.targets_listbox.insert(tk.END, target)
            
        except Exception as e:
            self.log_message(f"Помилка завантаження цілей: {e}", "error")
    
    def load_settings(self):
        """Завантаження налаштувань"""
        try:
            # Завантаження API ключа
            if hasattr(self, 'captcha_api_var'):
                self.captcha_api_var.set(self.config_manager.get('captcha_api_key', ''))
            
            # Завантаження налаштувань безпеки
            if hasattr(self, 'safety_vars'):
                safety_settings = self.config_manager.get('safety_settings', {})
                for var_name, var in self.safety_vars.items():
                    var.set(safety_settings.get(var_name, True))
            
            # Завантаження затримок
            if hasattr(self, 'delay_vars'):
                delays = self.config_manager.get('action_delays', {})
                for action, (min_var, max_var) in self.delay_vars.items():
                    if action in delays:
                        min_var.set(str(delays[action][0]))
                        max_var.set(str(delays[action][1]))
            
        except Exception as e:
            self.log_message(f"Помилка завантаження налаштувань: {e}", "error")
    
    def load_messages(self):
        """Завантаження повідомлень"""
        try:
            # Завантаження повідомлень для сторіс
            if hasattr(self, 'story_messages_listbox'):
                self.story_messages_listbox.delete(0, tk.END)
                story_replies = self.config_manager.get_story_replies()
                for reply in story_replies:
                    self.story_messages_listbox.insert(tk.END, reply)
            
            # Завантаження прямих повідомлень
            if hasattr(self, 'dm_messages_listbox'):
                self.dm_messages_listbox.delete(0, tk.END)
                dm_messages = self.config_manager.get_direct_messages()
                for message in dm_messages:
                    self.dm_messages_listbox.insert(tk.END, message)
            
        except Exception as e:
            self.log_message(f"Помилка завантаження повідомлень: {e}", "error")
    
    def log_message(self, message: str, level: str = "info"):
        """Додавання повідомлення до логу"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Додавання до automation log
        if hasattr(self, 'automation_log'):
            self.automation_log.configure(state='normal')
            self.automation_log.insert(tk.END, formatted_message + "\n")
            self.automation_log.see(tk.END)
            self.automation_log.configure(state='disabled')
        
        # Додавання до списку активностей
        if hasattr(self, 'activity_listbox'):
            icons = {
                'info': 'ℹ️',
                'success': '✅',
                'warning': '⚠️',
                'error': '❌'
            }
            icon = icons.get(level, 'ℹ️')
            activity_message = f"{icon} {message} - {timestamp}"
            
            self.activity_listbox.insert(0, activity_message)
            
            # Обмеження кількості повідомлень
            if self.activity_listbox.size() > 50:
                self.activity_listbox.delete(tk.END)
    
    # Методи для роботи з акаунтами
    def add_account_dialog(self):
        """Діалог додавання акаунту"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Додавання акаунту")
        dialog.geometry("400x300")
        dialog.configure(bg=ModernStyle.COLORS['background'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрування діалогу
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Заголовок
        title_label = tk.Label(
            dialog,
            text="➕ Додати новий акаунт",
            font=ModernStyle.FONTS['heading'],
            bg=ModernStyle.COLORS['background'],
            fg=ModernStyle.COLORS['text']
        )
        title_label.pack(pady=20)
        
        # Форма
        form_frame = tk.Frame(dialog, bg=ModernStyle.COLORS['background'])
        form_frame.pack(fill='both', expand=True, padx=20)
        
        # Логін
        tk.Label(
            form_frame,
            text="Логін Instagram:",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['background'],
            fg=ModernStyle.COLORS['text']
        ).pack(anchor='w', pady=(0, 5))
        
        username_entry = tk.Entry(
            form_frame,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            relief='flat',
            bd=5
        )
        username_entry.pack(fill='x', pady=(0, 15))
        username_entry.focus()
        
        # Пароль
        tk.Label(
            form_frame,
            text="Пароль:",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['background'],
            fg=ModernStyle.COLORS['text']
        ).pack(anchor='w', pady=(0, 5))
        
        password_entry = tk.Entry(
            form_frame,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            relief='flat',
            bd=5,
            show='*'
        )
        password_entry.pack(fill='x', pady=(0, 15))
        
        # Проксі (опціонально)
        tk.Label(
            form_frame,
            text="Проксі (опціонально):",
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['background'],
            fg=ModernStyle.COLORS['text']
        ).pack(anchor='w', pady=(0, 5))
        
        proxy_entry = tk.Entry(
            form_frame,
            font=ModernStyle.FONTS['body'],
            bg=ModernStyle.COLORS['surface'],
            fg=ModernStyle.COLORS['text'],
            relief='flat',
            bd=5
        )
        proxy_entry.pack(fill='x', pady=(0, 5))
        
        # Підказка
        hint_label = tk.Label(
            form_frame,
            text="Формат: ip:port або ip:port:user:pass",
            font=ModernStyle.FONTS['small'],
            bg=ModernStyle.COLORS['background'],
            fg=ModernStyle.COLORS['text_secondary']
        )
        hint_label.pack(anchor='w', pady=(0, 20))
        
        # Кнопки
        buttons_frame = tk.Frame(form_frame, bg=ModernStyle.COLORS['background'])
        buttons_frame.pack(fill='x', pady=(0, 20))
        
        def add_account():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            proxy = proxy_entry.get().strip() or None
            
            if not username or not password:
                messagebox.showerror("Помилка", "Заповніть всі обов'язкові поля!")
                return
            
            if not ValidationUtils.validate_username(username):
                messagebox.showerror("Помилка", "Некоректний формат логіну!")
                return
            
            if proxy and not ValidationUtils.validate_proxy(proxy):
                messagebox.showerror("Помилка", "Некоректний формат проксі!")
                return
            
            try:
                # Ініціалізація бота якщо потрібно
                if not self.bot:
                    self.bot = InstagramBot(self.config_manager.get('captcha_api_key'))
                
                # Додавання акаунту
                self.bot.account_manager.add_account(username, password, proxy)
                self.db_manager.add_account(username, password, proxy)
                
                self.log_message(f"Акаунт {username} додано успішно", "success")
                self.update_accounts_list()
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося додати акаунт: {e}")
        
        add_btn = AnimatedButton(
            buttons_frame,
            text="✅ Додати",
            command=add_account,
            bg=ModernStyle.COLORS['success']
        )
        add_btn.pack(side='right', padx=(10, 0))
        
        cancel_btn = AnimatedButton(
            buttons_frame,
            text="❌ Скасувати",
            command=dialog.destroy,
            bg=ModernStyle.COLORS['error']
        )
        cancel_btn.pack(side='right')
        
        # Enter для додавання
        dialog.bind('<Return>', lambda e: add_account())
    
    def import_accounts(self):
        """Імпорт акаунтів з файлу"""
        file_path = filedialog.askopenfilename(
            title="Вибрати файл з акаунтами",
            filetypes=[("Текстові файли", "*.txt"), ("Всі файли", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            imported_count = 0
            errors = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split(':')
                    if len(parts) < 2:
                        errors.append(f"Рядок {line_num}: некоректний формат")
                        continue
                    
                    username = parts[0].strip()
                    password = parts[1].strip()
                    proxy = ':'.join(parts[2:]).strip() if len(parts) > 2 else None
                    
                    if not ValidationUtils.validate_username(username):
                        errors.append(f"Рядок {line_num}: некоректний логін")
                        continue
                    
                    if proxy and not ValidationUtils.validate_proxy(proxy):
                        errors.append(f"Рядок {line_num}: некоректний проксі")
                        proxy = None
                    
                    # Ініціалізація бота якщо потрібно
                    if not self.bot:
                        self.bot = InstagramBot(self.config_manager.get('captcha_api_key'))
                    
                    # Додавання акаунту
                    self.bot.account_manager.add_account(username, password, proxy)
                    self.db_manager.add_account(username, password, proxy)
                    imported_count += 1
            
            # Повідомлення про результат
            message = f"Імпортовано {imported_count} акаунтів"
            if errors:
                message += f"\nПомилки: {len(errors)}"
                if len(errors) <= 5:
                    message += "\n" + "\n".join(errors)
                else:
                    message += f"\nПерші 5 помилок:\n" + "\n".join(errors[:5])
            
            messagebox.showinfo("Результат імпорту", message)
            self.log_message(f"Імпортовано {imported_count} акаунтів", "success")
            self.update_accounts_list()
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка імпорту: {e}")
    
    def test_accounts(self):
        """Тестування всіх акаунтів"""
        if not self.bot or not self.bot.account_manager.accounts:
            messagebox.showwarning("Попередження", "Немає акаунтів для тестування")
            return
        
        def test_worker():
            tested = 0
            successful = 0
            
            for username in self.bot.account_manager.accounts.keys():
                try:
                    self.log_message(f"Тестування акаунту {username}...", "info")
                    
                    if self.bot.login_account(username):
                        self.log_message(f"✅ {username} - успішно", "success")
                        successful += 1
                    else:
                        self.log_message(f"❌ {username} - помилка входу", "error")
                    
                    tested += 1
                    
                    # Закриття драйвера після тесту
                    self.bot.close_driver(username)
                    
                except Exception as e:
                    self.log_message(f"❌ {username} - помилка: {e}", "error")
                    tested += 1
            
            self.log_message(f"Тестування завершено: {successful}/{tested} успішних", "info")
            self.update_accounts_list()
        
        # Запуск в окремому потоці
        thread = threading.Thread(target=test_worker, daemon=True)
        thread.start()
        
        self.log_message("Запуск тестування акаунтів...", "info")
    
    # Методи для роботи з цілями
    def add_target(self):
        """Додавання цілі"""
        target = self.target_entry.get().strip()
        
        if not target:
            messagebox.showwarning("Попередження", "Введіть ім'я користувача")
            return
        
        if not ValidationUtils.validate_username(target):
            messagebox.showerror("Помилка", "Некоректний формат імені користувача")
            return
        
        # Перевірка дублікатів
        existing_targets = [self.targets_listbox.get(i) for i in range(self.targets_listbox.size())]
        if target in existing_targets:
            messagebox.showwarning("Попередження", "Ця ціль вже додана")
            return
        
        # Додавання до списку
        self.targets_listbox.insert(tk.END, target)
        self.target_entry.delete(0, tk.END)
        
        # Збереження в файл
        self.save_targets_to_file()
        
        self.log_message(f"Додано ціль: {target}", "success")
        self.update_dashboard()
    
    def import_targets(self):
        """Імпорт цілей з файлу"""
        file_path = filedialog.askopenfilename(
            title="Вибрати файл з цілями",
            filetypes=[("Текстові файли", "*.txt"), ("Всі файли", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            imported_count = 0
            existing_targets = [self.targets_listbox.get(i) for i in range(self.targets_listbox.size())]
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    target = line.strip()
                    if target and not target.startswith('#'):
                        if ValidationUtils.validate_username(target) and target not in existing_targets:
                            self.targets_listbox.insert(tk.END, target)
                            existing_targets.append(target)
                            imported_count += 1
            
            # Збереження
            self.save_targets_to_file()
            
            messagebox.showinfo("Успіх", f"Імпортовано {imported_count} цілей")
            self.log_message(f"Імпортовано {imported_count} цілей", "success")
            self.update_dashboard()
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка імпорту: {e}")
    
    def export_targets(self):
        """Експорт цілей у файл"""
        if self.targets_listbox.size() == 0:
            messagebox.showwarning("Попередження", "Немає цілей для експорту")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Зберегти цілі",
            defaultextension=".txt",
            filetypes=[("Текстові файли", "*.txt"), ("Всі файли", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# Список цілей Instagram Bot\n")
                f.write(f"# Експортовано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for i in range(self.targets_listbox.size()):
                    f.write(f"{self.targets_listbox.get(i)}\n")
            
            messagebox.showinfo("Успіх", f"Цілі експортовано в {file_path}")
            self.log_message(f"Експортовано {self.targets_listbox.size()} цілей", "success")
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка експорту: {e}")
    
    def save_targets_to_file(self):
        """Збереження цілей у файл"""
        try:
            with open("targets.txt", 'w', encoding='utf-8') as f:
                for i in range(self.targets_listbox.size()):
                    f.write(f"{self.targets_listbox.get(i)}\n")
        except Exception as e:
            self.log_message(f"Помилка збереження цілей: {e}", "error")
    
    def clear_targets(self):
        """Очищення всіх цілей"""
        if self.targets_listbox.size() == 0:
            return
        
        if messagebox.askyesno("Підтвердження", "Видалити всі цілі?"):
            self.targets_listbox.delete(0, tk.END)
            self.save_targets_to_file()
            self.log_message("Всі цілі видалено", "warning")
            self.update_dashboard()
    
    # Методи автоматизації
    def quick_start(self):
        """Швидкий старт автоматизації"""
        # Перевірка готовності
        if not self.bot or not self.bot.account_manager.accounts:
            messagebox.showwarning("Попередження", "Спочатку додайте акаунти")
            self.show_page("accounts")
            return
        
        if self.targets_listbox.size() == 0:
            messagebox.showwarning("Попередження", "Спочатку додайте цілі")
            self.show_page("targets")
            return
        
        # Перехід на сторінку автоматизації
        self.show_page("automation")
        
        # Автоматичний запуск через секунду
        self.root.after(1000, self.start_automation)
    
    def start_automation(self):
        """Запуск автоматизації"""
        if self.is_running:
            messagebox.showwarning("Попередження", "Автоматизація вже запущена")
            return
        
        # Перевірки
        if not self.bot:
            self.bot = InstagramBot(self.config_manager.get('captcha_api_key'))
        
        if not self.bot.account_manager.accounts:
            messagebox.showwarning("Попередження", "Немає акаунтів для роботи")
            return
        
        if self.targets_listbox.size() == 0:
            messagebox.showwarning("Попередження", "Немає цілей для автоматизації")
            return
        
        # Отримання цілей
        targets = [self.targets_listbox.get(i) for i in range(self.targets_listbox.size())]
        
        # Конфігурація автоматизації
        automation_config = {
            'accounts': [{'username': username} for username in self.bot.account_manager.accounts.keys()],
            'targets': targets,
            'actions': {
                'like_posts': self.action_vars.get('like_posts', tk.BooleanVar(value=True)).get(),
                'like_stories': self.action_vars.get('like_stories', tk.BooleanVar(value=True)).get(),
                'reply_stories': self.action_vars.get('reply_stories', tk.BooleanVar(value=False)).get(),
                'send_dm_if_no_stories': self.action_vars.get('send_dm', tk.BooleanVar(value=False)).get()
            },
            'story_messages': self.config_manager.get_story_replies(),
            'direct_messages': self.config_manager.get_direct_messages()
        }
        
        # Запуск в окремому потоці
        def automation_worker():
            try:
                self.is_running = True
                self.update_automation_buttons()
                
                self.log_message("🚀 Запуск автоматизації...", "info")
                self.automation_status.set_status('success', 'Автоматизація активна')
                
                # Запуск бота
                self.bot.run_automation(automation_config)
                
            except Exception as e:
                self.log_message(f"❌ Помилка автоматизації: {e}", "error")
            finally:
                self.is_running = False
                self.update_automation_buttons()
                self.automation_status.set_status('inactive', 'Автоматизація зупинена')
                self.log_message("⏹️ Автоматизація завершена", "info")
        
        self.automation_thread = threading.Thread(target=automation_worker, daemon=True)
        self.automation_thread.start()
    
    def pause_automation(self):
        """Призупинення автоматизації"""
        # TODO: Реалізувати призупинення
        self.log_message("⏸️ Автоматизація призупинена", "warning")
    
    def stop_automation(self):
        """Зупинка автоматизації"""
        if not self.is_running:
            return
        
        if messagebox.askyesno("Підтвердження", "Зупинити автоматизацію?"):
            try:
                if self.bot:
                    self.bot.close_all_drivers()
                
                self.is_running = False
                self.update_automation_buttons()
                self.automation_status.set_status('inactive', 'Автоматизація зупинена')
                self.log_message("⏹️ Автоматизація зупинена користувачем", "warning")
                
            except Exception as e:
                self.log_message(f"Помилка зупинки: {e}", "error")
    
    def update_automation_buttons(self):
        """Оновлення стану кнопок автоматизації"""
        if hasattr(self, 'start_automation_btn'):
            if self.is_running:
                self.start_automation_btn.configure(state='disabled')
                self.pause_automation_btn.configure(state='normal')
                self.stop_automation_btn.configure(state='normal')
                self.quick_start_btn.configure(state='disabled')
                self.stop_btn.configure(state='normal')
            else:
                self.start_automation_btn.configure(state='normal')
                self.pause_automation_btn.configure(state='disabled')
                self.stop_automation_btn.configure(state='disabled')
                self.quick_start_btn.configure(state='normal')
                self.stop_btn.configure(state='disabled')
    
    # Методи налаштувань
    def save_settings(self):
        """Збереження налаштувань"""
        try:
            # Збереження API ключа
            if hasattr(self, 'captcha_api_var'):
                self.config_manager.set('captcha_api_key', self.captcha_api_var.get())
            
            # Збереження налаштувань безпеки
            if hasattr(self, 'safety_vars'):
                for var_name, var in self.safety_vars.items():
                    self.config_manager.set(f'safety_settings.{var_name}', var.get())
            
            # Збереження затримок
            if hasattr(self, 'delay_vars'):
                for action, (min_var, max_var) in self.delay_vars.items():
                    try:
                        min_val = float(min_var.get())
                        max_val = float(max_var.get())
                        if min_val >= 0 and max_val >= min_val:
                            self.config_manager.set(f'action_delays.{action}', [min_val, max_val])
                    except ValueError:
                        pass
            
            # Збереження лімітів
            if hasattr(self, 'daily_limit_var'):
                try:
                    daily_limit = int(self.daily_limit_var.get())
                    if daily_limit > 0:
                        self.config_manager.set('daily_action_limit', daily_limit)
                except ValueError:
                    pass
            
            if hasattr(self, 'hourly_limit_var'):
                try:
                    hourly_limit = int(self.hourly_limit_var.get())
                    if hourly_limit > 0:
                        self.config_manager.set('hourly_action_limit', hourly_limit)
                except ValueError:
                    pass
            
            messagebox.showinfo("Успіх", "Налаштування збережені")
            self.log_message("Налаштування збережені", "success")
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка збереження: {e}")
    
    def reset_settings(self):
        """Скидання налаштувань до стандартних"""
        if messagebox.askyesno("Підтвердження", "Скинути всі налаштування до стандартних?"):
            try:
                self.config_manager.reset_to_defaults()
                self.load_settings()
                messagebox.showinfo("Успіх", "Налаштування скинуті")
                self.log_message("Налаштування скинуті до стандартних", "warning")
            except Exception as e:
                messagebox.showerror("Помилка", f"Помилка скидання: {e}")
    
    # Методи для повідомлень
    def add_story_message(self):
        """Додавання повідомлення для сторіс"""
        message = self.story_message_entry.get().strip()
        if not message:
            return
        
        # Перевірка дублікатів
        existing = [self.story_messages_listbox.get(i) for i in range(self.story_messages_listbox.size())]
        if message in existing:
            messagebox.showwarning("Попередження", "Це повідомлення вже додано")
            return
        
        self.story_messages_listbox.insert(tk.END, message)
        self.story_message_entry.delete(0, tk.END)
        
        # Збереження в конфігурацію
        self.config_manager.add_story_reply(message)
        self.log_message(f"Додано відповідь для сторіс: {message}", "success")
    
    def delete_story_message(self):
        """Видалення повідомлення для сторіс"""
        selection = self.story_messages_listbox.curselection()
        if not selection:
            messagebox.showwarning("Попередження", "Виберіть повідомлення для видалення")
            return
        
        message = self.story_messages_listbox.get(selection[0])
        self.story_messages_listbox.delete(selection[0])
        
        # Оновлення конфігурації
        story_replies = [self.story_messages_listbox.get(i) for i in range(self.story_messages_listbox.size())]
        self.config_manager.set('story_replies', story_replies)
        
        self.log_message(f"Видалено відповідь: {message}", "warning")
    
    def add_dm_message(self):
        """Додавання прямого повідомлення"""
        message = self.dm_message_entry.get().strip()
        if not message:
            return
        
        # Перевірка дублікатів
        existing = [self.dm_messages_listbox.get(i) for i in range(self.dm_messages_listbox.size())]
        if message in existing:
            messagebox.showwarning("Попередження", "Це повідомлення вже додано")
            return
        
        self.dm_messages_listbox.insert(tk.END, message)
        self.dm_message_entry.delete(0, tk.END)
        
        # Збереження в конфігурацію
        self.config_manager.add_direct_message(message)
        self.log_message(f"Додано DM повідомлення: {message}", "success")
    
    def delete_dm_message(self):
        """Видалення прямого повідомлення"""
        selection = self.dm_messages_listbox.curselection()
        if not selection:
            messagebox.showwarning("Попередження", "Виберіть повідомлення для видалення")
            return
        
        message = self.dm_messages_listbox.get(selection[0])
        self.dm_messages_listbox.delete(selection[0])
        
        # Оновлення конфігурації
        dm_messages = [self.dm_messages_listbox.get(i) for i in range(self.dm_messages_listbox.size())]
        self.config_manager.set('direct_messages', dm_messages)
        
        self.log_message(f"Видалено DM: {message}", "warning")
    
    def load_default_story_messages(self):
        """Завантаження стандартних повідомлень для сторіс"""
        if messagebox.askyesno("Підтвердження", "Завантажити стандартні повідомлення для сторіс?"):
            self.story_messages_listbox.delete(0, tk.END)
            
            default_messages = [
                "🔥🔥🔥", "❤️", "Круто!", "👍", "Супер!", "💯", "🙌", 
                "Класно!", "👏", "Wow!", "Дуже цікаво!", "Топ контент!", 
                "Красиво!", "😍", "🤩", "💪", "✨", "🎉", "👌"
            ]
            
            for message in default_messages:
                self.story_messages_listbox.insert(tk.END, message)
            
            # Збереження
            self.config_manager.set('story_replies', default_messages)
            self.log_message("Завантажено стандартні повідомлення для сторіс", "info")
    
    def load_default_dm_messages(self):
        """Завантаження стандартних прямих повідомлень"""
        if messagebox.askyesno("Підтвердження", "Завантажити стандартні прямі повідомлення?"):
            self.dm_messages_listbox.delete(0, tk.END)
            
            default_messages = [
                "Привіт! Як справи? 😊",
                "Вітаю! Сподобався ваш контент 👍",
                "Доброго дня! Цікавий профіль ✨",
                "Привіт! Круті пости у вас ❤️",
                "Вітаю! Дякую за натхнення 🙌"
            ]
            
            for message in default_messages:
                self.dm_messages_listbox.insert(tk.END, message)
            
            # Збереження
            self.config_manager.set('direct_messages', default_messages)
            self.log_message("Завантажено стандартні прямі повідомлення", "info")
    
    # Методи для проксі
    def add_proxy(self):
        """Додавання проксі"""
        proxy = self.proxy_entry.get().strip()
        if not proxy:
            return
        
        if not ValidationUtils.validate_proxy(proxy):
            messagebox.showerror("Помилка", "Некоректний формат проксі")
            return
        
        # Перевірка дублікатів
        for item in self.proxy_tree.get_children():
            if self.proxy_tree.item(item)['values'][0] == proxy:
                messagebox.showwarning("Попередження", "Цей проксі вже додано")
                return
        
        # Додавання до списку
        self.proxy_tree.insert('', 'end', values=(proxy, 'Не перевірено', '-', '-'))
        self.proxy_entry.delete(0, tk.END)
        
        # Збереження в конфігурацію
        self.config_manager.add_proxy(proxy)
        self.log_message(f"Додано проксі: {proxy}", "success")
    
    def import_proxies(self):
        """Імпорт проксі з файлу"""
        file_path = filedialog.askopenfilename(
            title="Вибрати файл з проксі",
            filetypes=[("Текстові файли", "*.txt"), ("Всі файли", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            imported_count = 0
            existing_proxies = [self.proxy_tree.item(item)['values'][0] 
                             for item in self.proxy_tree.get_children()]
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    proxy = line.strip()
                    if proxy and not proxy.startswith('#'):
                        if ValidationUtils.validate_proxy(proxy) and proxy not in existing_proxies:
                            self.proxy_tree.insert('', 'end', values=(proxy, 'Не перевірено', '-', '-'))
                            self.config_manager.add_proxy(proxy)
                            existing_proxies.append(proxy)
                            imported_count += 1
            
            messagebox.showinfo("Успіх", f"Імпортовано {imported_count} проксі")
            self.log_message(f"Імпортовано {imported_count} проксі", "success")
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка імпорту: {e}")
    
    def test_proxies(self):
        """Тестування всіх проксі"""
        proxies = [self.proxy_tree.item(item)['values'][0] 
                  for item in self.proxy_tree.get_children()]
        
        if not proxies:
            messagebox.showwarning("Попередження", "Немає проксі для тестування")
            return
        
        def test_worker():
            from utils import ProxyManager
            proxy_manager = ProxyManager()
            
            for item in self.proxy_tree.get_children():
                proxy = self.proxy_tree.item(item)['values'][0]
                self.log_message(f"Тестування проксі {proxy}...", "info")
                
                # Оновлення статусу
                self.proxy_tree.item(item, values=(proxy, 'Тестування...', '-', '-'))
                
                try:
                    import time
                    start_time = time.time()
                    
                    if proxy_manager.test_proxy(proxy):
                        response_time = f"{(time.time() - start_time) * 1000:.0f}ms"
                        self.proxy_tree.item(item, values=(
                            proxy, 'Працює', response_time, 
                            datetime.now().strftime('%H:%M:%S')
                        ))
                        self.log_message(f"✅ {proxy} - працює", "success")
                    else:
                        self.proxy_tree.item(item, values=(
                            proxy, 'Не працює', '-', 
                            datetime.now().strftime('%H:%M:%S')
                        ))
                        self.log_message(f"❌ {proxy} - не працює", "error")
                        
                except Exception as e:
                    self.proxy_tree.item(item, values=(
                        proxy, 'Помилка', '-', 
                        datetime.now().strftime('%H:%M:%S')
                    ))
                    self.log_message(f"❌ {proxy} - помилка: {e}", "error")
            
            self.log_message("Тестування проксі завершено", "info")
        
        # Запуск в окремому потоці
        thread = threading.Thread(target=test_worker, daemon=True)
        thread.start()
    
    def clear_proxies(self):
        """Очищення всіх проксі"""
        if not self.proxy_tree.get_children():
            return
        
        if messagebox.askyesno("Підтвердження", "Видалити всі проксі?"):
            for item in self.proxy_tree.get_children():
                self.proxy_tree.delete(item)
            
            # Очищення в конфігурації
            self.config_manager.set('proxy_list', [])
            self.log_message("Всі проксі видалено", "warning")
    
    # Статистика
    def update_statistics(self):
        """Періодичне оновлення статистики"""
        try:
            self.update_dashboard()
            self.update_sidebar_status()
            
            # Запланувати наступне оновлення через 30 секунд
            self.root.after(30000, self.update_statistics)
            
        except Exception as e:
            self.log_message(f"Помилка оновлення статистики: {e}", "error")
            # Все одно запланувати наступне оновлення
            self.root.after(30000, self.update_statistics)
    
    def update_sidebar_status(self):
        """Оновлення статусу в бічній панелі"""
        try:
            # Статус системи
            system_info = SystemUtils.get_system_info()
            memory_percent = (system_info['memory_total'] - system_info['memory_available']) / system_info['memory_total'] * 100
            
            if memory_percent > 90:
                self.system_status.set_status('error', 'Мало пам\'яті')
            elif memory_percent > 70:
                self.system_status.set_status('warning', 'Багато пам\'яті')
            else:
                self.system_status.set_status('success', 'Система готова')
            
            # Кількість акаунтів
            account_count = len(self.bot.account_manager.accounts) if self.bot else 0
            self.accounts_status.set_status('info', f'{account_count} акаунтів')
            
        except Exception as e:
            pass  # Ігноруємо помилки статусу
    
    def update_statistics_page(self):
        """Оновлення сторінки статистики"""
        try:
            # Очищення існуючих даних
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)
            
            self.top_targets_listbox.delete(0, tk.END)
            
            # Отримання статистики з бази даних
            if hasattr(self, 'bot') and self.bot:
                accounts = self.bot.account_manager.accounts
                for username in accounts.keys():
                    stats = self.db_manager.get_account_stats(username)
                    total_actions = stats.get('total_actions', 0)
                    success_rate = 95 if total_actions > 0 else 0  # Приклад
                    
                    self.stats_tree.insert('', 'end', values=(
                        username,
                        total_actions,
                        f"{success_rate}%"
                    ))
            
            # Топ цілей (приклад)
            targets = [self.targets_listbox.get(i) for i in range(min(10, self.targets_listbox.size()))]
            for i, target in enumerate(targets, 1):
                self.top_targets_listbox.insert(tk.END, f"{i}. {target}")
            
        except Exception as e:
            self.log_message(f"Помилка оновлення статистики: {e}", "error")
    
    def refresh_statistics(self):
        """Оновлення статистики вручну"""
        self.update_statistics_page()
        self.log_message("Статистика оновлена", "info")
    
    # Контекстні меню
    def show_accounts_context_menu(self, event):
        """Показ контекстного меню для акаунтів"""
        selection = self.accounts_tree.selection()
        if selection:
            self.accounts_context_menu.post(event.x_root, event.y_root)
    
    def show_targets_context_menu(self, event):
        """Показ контекстного меню для цілей"""
        selection = self.targets_listbox.curselection()
        if selection:
            self.targets_context_menu.post(event.x_root, event.y_root)
    
    def show_proxy_context_menu(self, event):
        """Показ контекстного меню для проксі"""
        selection = self.proxy_tree.selection()
        if selection:
            self.proxy_context_menu.post(event.x_root, event.y_root)
    
    # Методи контекстних меню
    def edit_account(self):
        """Редагування акаунту"""
        selection = self.accounts_tree.selection()
        if not selection:
            return
        
        username = self.accounts_tree.item(selection[0])['values'][0]
        messagebox.showinfo("Інформація", f"Редагування акаунту {username}\n(Функція буде додана)")
    
    def test_selected_account(self):
        """Тестування вибраного акаунту"""
        selection = self.accounts_tree.selection()
        if not selection:
            return
        
        username = self.accounts_tree.item(selection[0])['values'][0]
        
        def test_worker():
            try:
                if not self.bot:
                    self.bot = InstagramBot(self.config_manager.get('captcha_api_key'))
                
                self.log_message(f"Тестування акаунту {username}...", "info")
                
                if self.bot.login_account(username):
                    self.log_message(f"✅ {username} - успішно", "success")
                else:
                    self.log_message(f"❌ {username} - помилка входу", "error")
                
                self.bot.close_driver(username)
                self.update_accounts_list()
                
            except Exception as e:
                self.log_message(f"❌ {username} - помилка: {e}", "error")
        
        thread = threading.Thread(target=test_worker, daemon=True)
        thread.start()
    
    def show_account_stats(self):
        """Показ статистики акаунту"""
        selection = self.accounts_tree.selection()
        if not selection:
            return
        
        username = self.accounts_tree.item(selection[0])['values'][0]
        stats = self.db_manager.get_account_stats(username)
        
        stats_text = f"""
Статистика акаунту: {username}

Всього дій: {stats.get('total_actions', 0)}
Дій сьогодні: {stats.get('daily_actions', 0)}
Остання активність: {stats.get('last_activity', 'Ніколи')}
Статус: {stats.get('status', 'Невідомо')}
        """
        
        messagebox.showinfo(f"Статистика {username}", stats_text)
    
    def delete_account(self):
        """Видалення акаунту"""
        selection = self.accounts_tree.selection()
        if not selection:
            return
        
        username = self.accounts_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Підтвердження", f"Видалити акаунт {username}?"):
            try:
                if self.bot and username in self.bot.account_manager.accounts:
                    del self.bot.account_manager.accounts[username]
                    self.bot.account_manager.save_accounts()
                
                self.log_message(f"Акаунт {username} видалено", "warning")
                self.update_accounts_list()
                
            except Exception as e:
                messagebox.showerror("Помилка", f"Помилка видалення: {e}")
    
    def open_target_profile(self):
        """Відкриття профілю цілі в браузері"""
        selection = self.targets_listbox.curselection()
        if not selection:
            return
        
        target = self.targets_listbox.get(selection[0])
        url = f"https://www.instagram.com/{target}/"
        webbrowser.open(url)
    
    def show_target_stats(self):
        """Показ статистики цілі"""
        selection = self.targets_listbox.curselection()
        if not selection:
            return
        
        target = self.targets_listbox.get(selection[0])
        messagebox.showinfo("Статистика", f"Статистика для {target}\n(Функція буде додана)")
    
    def delete_target(self):
        """Видалення цілі"""
        selection = self.targets_listbox.curselection()
        if not selection:
            return
        
        target = self.targets_listbox.get(selection[0])
        
        if messagebox.askyesno("Підтвердження", f"Видалити ціль {target}?"):
            self.targets_listbox.delete(selection[0])
            self.save_targets_to_file()
            self.log_message(f"Ціль {target} видалено", "warning")
            self.update_dashboard()
    
    def test_selected_proxy(self):
        """Тестування вибраного проксі"""
        selection = self.proxy_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        proxy = self.proxy_tree.item(item)['values'][0]
        
        def test_worker():
            from utils import ProxyManager
            proxy_manager = ProxyManager()
            
            self.log_message(f"Тестування проксі {proxy}...", "info")
            self.proxy_tree.item(item, values=(proxy, 'Тестування...', '-', '-'))
            
            try:
                import time
                start_time = time.time()
                
                if proxy_manager.test_proxy(proxy):
                    response_time = f"{(time.time() - start_time) * 1000:.0f}ms"
                    self.proxy_tree.item(item, values=(
                        proxy, 'Працює', response_time, 
                        datetime.now().strftime('%H:%M:%S')
                    ))
                    self.log_message(f"✅ {proxy} - працює", "success")
                else:
                    self.proxy_tree.item(item, values=(
                        proxy, 'Не працює', '-', 
                        datetime.now().strftime('%H:%M:%S')
                    ))
                    self.log_message(f"❌ {proxy} - не працює", "error")
                    
            except Exception as e:
                self.proxy_tree.item(item, values=(
                    proxy, 'Помилка', '-', 
                    datetime.now().strftime('%H:%M:%S')
                ))
                self.log_message(f"❌ {proxy} - помилка: {e}", "error")
        
        thread = threading.Thread(target=test_worker, daemon=True)
        thread.start()
    
    def copy_proxy(self):
        """Копіювання проксі в буфер обміну"""
        selection = self.proxy_tree.selection()
        if not selection:
            return
        
        proxy = self.proxy_tree.item(selection[0])['values'][0]
        self.root.clipboard_clear()
        self.root.clipboard_append(proxy)
        self.log_message(f"Проксі {proxy} скопійовано", "info")
    
    def delete_proxy(self):
        """Видалення проксі"""
        selection = self.proxy_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        proxy = self.proxy_tree.item(item)['values'][0]
        
        if messagebox.askyesno("Підтвердження", f"Видалити проксі {proxy}?"):
            self.proxy_tree.delete(item)
            self.config_manager.remove_proxy(proxy)
            self.log_message(f"Проксі {proxy} видалено", "warning")
    
    def on_closing(self):
        """Обробка закриття програми"""
        if self.is_running:
            if messagebox.askyesno("Підтвердження", "Автоматизація активна. Зупинити і вийти?"):
                try:
                    if self.bot:
                        self.bot.close_all_drivers()
                except:
                    pass
                self.root.destroy()
        else:
            if messagebox.askyesno("Підтвердження", "Закрити програму?"):
                try:
                    if self.bot:
                        self.bot.close_all_drivers()
                except:
                    pass
                self.root.destroy()


def main():
    """Запуск GUI"""
    try:
        # Перевірка залежностей
        print("🔍 Перевірка залежностей...")
        
        missing_deps = []
        required_modules = ['tkinter', 'threading', 'json', 'os', 'sys', 'datetime', 'webbrowser']
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                missing_deps.append(module)
                print(f"❌ {module}")
        
        if missing_deps:
            print(f"\n❌ Відсутні залежності: {', '.join(missing_deps)}")
            print("📦 Встановіть їх командою: pip install -r requirements.txt")
            return False
        
        print("✅ Всі залежності встановлені")
        
        # Створення головного вікна
        print("🖥️ Запуск GUI...")
        root = tk.Tk()
        
        # Налаштування для Windows
        try:
            root.iconbitmap('assets/icon.ico')
        except:
            pass
        
        # Запуск програми
        app = InstagramBotGUI(root)
        
        print("✅ GUI запущено успішно!")
        print("💡 Використовуйте Dashboard для швидкого старту")
        
        # Основний цикл
        root.mainloop()
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ Програма зупинена користувачем")
        return True
    except Exception as e:
        print(f"❌ Критична помилка GUI: {e}")
        import traceback
        traceback.print_exc()
        
        # Спроба запуску без GUI (fallback)
        print("\n💡 Спробуйте запустити через командний рядок:")
        print("   python run.py --mode cli --help")
        
        return False


def build_delay_range_input(self, parent, action, label, default_range=(1, 3)):
    frame = tk.Frame(parent, bg=ModernStyle.COLORS['card'])
    frame.pack(anchor='w', pady=5)

    tk.Label(
        frame,
        text=f"{label}:",
        font=ModernStyle.FONTS['body'],
        bg=ModernStyle.COLORS['card'],
        fg=ModernStyle.COLORS['text'],
        width=20,
        anchor='w'
    ).pack(side='left')

    tk.Label(
        frame,
        text="від",
        font=ModernStyle.FONTS['body'],
        bg=ModernStyle.COLORS['card'],
        fg=ModernStyle.COLORS['text']
    ).pack(side='left', padx=(10, 5))

    min_var = tk.StringVar(value=str(default_range[0]))
    max_var = tk.StringVar(value=str(default_range[1]))

    min_entry = tk.Entry(
        frame,
        textvariable=min_var,
        font=ModernStyle.FONTS['body'],
        bg=ModernStyle.COLORS['surface'],
        fg=ModernStyle.COLORS['text'],
        width=8,
        relief='flat',
        bd=5
    )
    min_entry.pack(side='left', padx=2)

    tk.Label(
        frame,
        text="до",
        font=ModernStyle.FONTS['body'],
        bg=ModernStyle.COLORS['card'],
        fg=ModernStyle.COLORS['text']
    ).pack(side='left', padx=5)

    max_entry = tk.Entry(
        frame,
        textvariable=max_var,
        font=ModernStyle.FONTS['body'],
        bg=ModernStyle.COLORS['surface'],
        fg=ModernStyle.COLORS['text'],
        width=8,
        relief='flat',
        bd=5
    )
    max_entry.pack(side='left', padx=2)

    tk.Label(
        frame,
        text="сек",
        font=ModernStyle.FONTS['body'],
        bg=ModernStyle.COLORS['card'],
        fg=ModernStyle.COLORS['text']
    ).pack(side='left', padx=(5, 0))

    self.delay_vars[action] = (min_var, max_var)
