#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утиліти та допоміжні функції для Instagram Bot
"""

import logging
import json
import os
import re
import time
import random
import sqlite3
import requests
import psutil
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import base64


def setup_logging(log_file: str = 'instagram_bot.log', level=logging.INFO):
    """Налаштування системи логування"""
    # Створення директорії для логів
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Конфігурація логування
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Створення ротації логів
    import logging.handlers
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    logger = logging.getLogger()
    logger.addHandler(file_handler)


class ProxyManager:
    """Менеджер проксі серверів"""
    
    def __init__(self):
        self.proxy_list = []
        self.working_proxies = []
        self.current_index = 0
        
    def add_proxy(self, proxy: str):
        """Додавання проксі"""
        if self.validate_proxy_format(proxy):
            self.proxy_list.append(proxy)
        else:
            logging.warning(f"Некоректний формат проксі: {proxy}")
    
    def validate_proxy_format(self, proxy: str) -> bool:
        """Валідація формату проксі"""
        patterns = [
            r'^(\d{1,3}\.){3}\d{1,3}:\d{1,5}$',  # ip:port
            r'^(\d{1,3}\.){3}\d{1,3}:\d{1,5}:\w+:\w+$',  # ip:port:user:pass
            r'^[\w\.-]+:\d{1,5}$',  # domain:port
            r'^[\w\.-]+:\d{1,5}:\w+:\w+$'  # domain:port:user:pass
        ]
        return any(re.match(pattern, proxy) for pattern in patterns)
    
    def test_proxy(self, proxy: str, timeout: int = 10) -> bool:
        """Тестування проксі"""
        try:
            proxy_dict = self.parse_proxy(proxy)
            
            response = requests.get(
                'https://httpbin.org/ip',
                proxies=proxy_dict,
                timeout=timeout
            )
            
            if response.status_code == 200:
                self.working_proxies.append(proxy)
                logging.info(f"Проксі працює: {proxy}")
                return True
            else:
                logging.warning(f"Проксі не відповідає: {proxy}")
                return False
                
        except Exception as e:
            logging.error(f"Помилка тестування проксі {proxy}: {e}")
            return False
    
    def parse_proxy(self, proxy: str) -> Dict[str, str]:
        """Парсинг проксі для requests"""
        parts = proxy.split(':')
        
        if len(parts) == 2:
            # ip:port
            return {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
        elif len(parts) == 4:
            # ip:port:user:pass
            ip, port, user, password = parts
            auth_proxy = f'http://{user}:{password}@{ip}:{port}'
            return {
                'http': auth_proxy,
                'https': auth_proxy
            }
        else:
            raise ValueError(f"Некоректний формат проксі: {proxy}")
    
    def get_random_proxy(self) -> Optional[str]:
        """Отримання випадкового робочого проксі"""
        if self.working_proxies:
            return random.choice(self.working_proxies)
        return None
    
    def get_next_proxy(self) -> Optional[str]:
        """Отримання наступного проксі по черзі"""
        if not self.working_proxies:
            return None
        
        proxy = self.working_proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.working_proxies)
        return proxy


class DatabaseManager:
    """Менеджер бази даних для зберігання статистики"""
    
    def __init__(self, db_path: str = 'data/instagram_bot.db'):
        self.db_path = db_path
        self.ensure_directory()
        self.init_database()
    
    def ensure_directory(self):
        """Створення директорії для БД"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def init_database(self):
        """Ініціалізація бази даних"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблиця акаунтів
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    proxy TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP,
                    total_actions INTEGER DEFAULT 0,
                    daily_actions INTEGER DEFAULT 0,
                    last_reset DATE DEFAULT CURRENT_DATE
                )
            ''')
            
            # Таблиця дій
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_username TEXT,
                    target_username TEXT,
                    action_type TEXT,
                    success BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT,
                    FOREIGN KEY (account_username) REFERENCES accounts (username)
                )
            ''')
            
            # Таблиця сесій
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_username TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    actions_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0,
                    FOREIGN KEY (account_username) REFERENCES accounts (username)
                )
            ''')
            
            conn.commit()
    
    def add_account(self, username: str, password: str, proxy: str = None):
        """Додавання акаунту до БД"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO accounts (username, password, proxy)
                VALUES (?, ?, ?)
            ''', (username, password, proxy))
            conn.commit()
    
    def log_action(self, account_username: str, target_username: str, 
                   action_type: str, success: bool, details: str = None):
        """Логування дії"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO actions (account_username, target_username, action_type, success, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (account_username, target_username, action_type, success, details))
            
            # Оновлення лічильників акаунту
            cursor.execute('''
                UPDATE accounts 
                SET total_actions = total_actions + 1,
                    daily_actions = daily_actions + 1,
                    last_activity = CURRENT_TIMESTAMP
                WHERE username = ?
            ''', (account_username,))
            
            conn.commit()
    
    def get_account_stats(self, username: str) -> Dict:
        """Отримання статистики акаунту"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT total_actions, daily_actions, last_activity, status
                FROM accounts WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'total_actions': result[0],
                    'daily_actions': result[1],
                    'last_activity': result[2],
                    'status': result[3]
                }
            return {}
    
    def reset_daily_limits(self):
        """Скидання денних лімітів"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE accounts 
                SET daily_actions = 0, last_reset = CURRENT_DATE
                WHERE last_reset < CURRENT_DATE
            ''')
            conn.commit()
    
    def get_statistics(self) -> Dict:
        """Отримання загальної статистики"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Загальна кількість дій
            cursor.execute('SELECT COUNT(*) FROM actions')
            total_actions = cursor.fetchone()[0]
            
            # Успішні дії
            cursor.execute('SELECT COUNT(*) FROM actions WHERE success = 1')
            successful_actions = cursor.fetchone()[0]
            
            # Активні акаунти
            cursor.execute('SELECT COUNT(*) FROM accounts WHERE status = "active"')
            active_accounts = cursor.fetchone()[0]
            
            # Дії за сьогодні
            cursor.execute('''
                SELECT COUNT(*) FROM actions 
                WHERE DATE(timestamp) = CURRENT_DATE
            ''')
            today_actions = cursor.fetchone()[0]
            
            return {
                'total_actions': total_actions,
                'successful_actions': successful_actions,
                'active_accounts': active_accounts,
                'today_actions': today_actions,
                'success_rate': (successful_actions / total_actions * 100) if total_actions > 0 else 0
            }


class StatisticsManager:
    """Менеджер статистики"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.stats_file = 'data/statistics.json'
        self.ensure_directory()
    
    def ensure_directory(self):
        """Створення директорії для статистики"""
        stats_dir = os.path.dirname(self.stats_file)
        if stats_dir and not os.path.exists(stats_dir):
            os.makedirs(stats_dir)
    
    def generate_report(self) -> Dict:
        """Генерація звіту"""
        stats = self.db.get_statistics()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': stats,
            'accounts': self.get_accounts_report(),
            'daily_breakdown': self.get_daily_breakdown(),
            'action_breakdown': self.get_action_breakdown()
        }
        
        # Збереження звіту
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def get_accounts_report(self) -> List[Dict]:
        """Звіт по акаунтах"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, total_actions, daily_actions, status, last_activity
                FROM accounts
            ''')
            
            accounts = []
            for row in cursor.fetchall():
                accounts.append({
                    'username': row[0],
                    'total_actions': row[1],
                    'daily_actions': row[2],
                    'status': row[3],
                    'last_activity': row[4]
                })
            
            return accounts
    
    def get_daily_breakdown(self) -> List[Dict]:
        """Розбивка по днях"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DATE(timestamp) as date, 
                       COUNT(*) as total,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM actions
                WHERE DATE(timestamp) >= DATE('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            ''')
            
            breakdown = []
            for row in cursor.fetchall():
                total = row[1]
                successful = row[2]
                breakdown.append({
                    'date': row[0],
                    'total_actions': total,
                    'successful_actions': successful,
                    'success_rate': (successful / total * 100) if total > 0 else 0
                })
            
            return breakdown
    
    def get_action_breakdown(self) -> Dict:
        """Розбивка по типах дій"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT action_type, 
                       COUNT(*) as total,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM actions
                GROUP BY action_type
            ''')
            
            breakdown = {}
            for row in cursor.fetchall():
                action_type = row[0]
                total = row[1]
                successful = row[2]
                breakdown[action_type] = {
                    'total': total,
                    'successful': successful,
                    'success_rate': (successful / total * 100) if total > 0 else 0
                }
            
            return breakdown


class FileManager:
    """Менеджер файлів та бекапів"""
    
    def __init__(self):
        self.backup_dir = 'backups'
        self.ensure_directories()
    
    def ensure_directories(self):
        """Створення необхідних директорій"""
        directories = [self.backup_dir, 'exports', 'data', 'logs']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def create_backup(self, source_file: str) -> str:
        """Створення бекапу файлу"""
        if not os.path.exists(source_file):
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(source_file)
        backup_path = os.path.join(self.backup_dir, f"{timestamp}_{filename}")
        
        try:
            import shutil
            shutil.copy2(source_file, backup_path)
            logging.info(f"Створено бекап: {backup_path}")
            return backup_path
        except Exception as e:
            logging.error(f"Помилка створення бекапу: {e}")
            return None
    
    def export_data(self, data: Dict, filename: str, format_type: str = 'json'):
        """Експорт даних"""
        export_path = os.path.join('exports', filename)
        
        try:
            if format_type == 'json':
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format_type == 'csv':
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    if isinstance(data, list) and data:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
            
            logging.info(f"Дані експортовано: {export_path}")
            return export_path
            
        except Exception as e:
            logging.error(f"Помилка експорту: {e}")
            return None
    
    def cleanup_old_files(self, directory: str, days: int = 30):
        """Очищення старих файлів"""
        if not os.path.exists(directory):
            return
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        logging.info(f"Видалено старий файл: {file_path}")
                    except Exception as e:
                        logging.error(f"Помилка видалення файлу {file_path}: {e}")


class SystemUtils:
    """Системні утиліти"""
    
    @staticmethod
    def check_dependencies() -> Dict[str, bool]:
        """Перевірка наявності залежностей"""
        dependencies = {
            'selenium': False,
            'opencv-python': False,
            'Pillow': False,
            'requests': False,
            'numpy': False,
            'psutil': False
        }
        
        for package in dependencies:
            try:
                if package == 'opencv-python':
                    import cv2
                elif package == 'Pillow':
                    import PIL
                else:
                    __import__(package)
                dependencies[package] = True
            except ImportError:
                pass
        
        return dependencies
    
    @staticmethod
    def get_system_info() -> Dict:
        """Отримання інформації про систему"""
        import platform
        
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_free': psutil.disk_usage('/').free if os.name != 'nt' else psutil.disk_usage('C:').free
        }
    
    @staticmethod
    def get_chrome_version() -> str:
        """Отримання версії Chrome"""
        try:
            if os.name == 'nt':  # Windows
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                return version
            else:  # Linux/Mac
                result = subprocess.run(['google-chrome', '--version'], 
                                      capture_output=True, text=True)
                return result.stdout.strip().split()[-1]
        except:
            return "Unknown"
    
    @staticmethod
    def monitor_resources() -> Dict:
        """Моніторинг ресурсів системи"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
            'network_sent': psutil.net_io_counters().bytes_sent,
            'network_recv': psutil.net_io_counters().bytes_recv
        }


class ValidationUtils:
    """Утиліти для валідації даних"""
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Валідація імені користувача Instagram"""
        if not username:
            return False
        
        # Instagram username rules
        pattern = r'^[a-zA-Z0-9._]{1,30}$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_proxy(proxy: str) -> bool:
        """Валідація проксі"""
        if not proxy:
            return False
        
        patterns = [
            r'^(\d{1,3}\.){3}\d{1,3}:\d{1,5}$',  # ip:port
            r'^(\d{1,3}\.){3}\d{1,3}:\d{1,5}:\w+:\w+$',  # ip:port:user:pass
            r'^[\w\.-]+:\d{1,5}$',  # domain:port
            r'^[\w\.-]+:\d{1,5}:\w+:\w+$'  # domain:port:user:pass
        ]
        
        return any(re.match(pattern, proxy) for pattern in patterns)
    
    @staticmethod
    def validate_delay_range(delay_str: str) -> bool:
        """Валідація діапазону затримок"""
        try:
            if '-' not in delay_str:
                return False
            
            min_val, max_val = delay_str.split('-')
            min_val, max_val = float(min_val), float(max_val)
            
            return 0 <= min_val <= max_val <= 300  # Максимум 5 хвилин
        except:
            return False


class ConfigValidator:
    """Валідатор конфігурації"""
    
    @staticmethod
    def validate_config(config: Dict) -> Dict[str, Any]:
        """Валідація конфігурації"""
        errors = []
        warnings = []
        
        # Перевірка обов'язкових полів
        required_fields = ['action_delays', 'daily_action_limit']
        for field in required_fields:
            if field not in config:
                errors.append(f"Відсутнє обов'язкове поле: {field}")
        
        # Перевірка затримок
        if 'action_delays' in config:
            for action, delays in config['action_delays'].items():
                if not isinstance(delays, list) or len(delays) != 2:
                    errors.append(f"Некоректні затримки для {action}")
                elif delays[0] > delays[1]:
                    errors.append(f"Мінімальна затримка більша за максимальну для {action}")
        
        # Перевірка лімітів
        if 'daily_action_limit' in config:
            limit = config['daily_action_limit']
            if not isinstance(limit, int) or limit <= 0:
                errors.append("Денний ліміт має бути позитивним числом")
            elif limit > 200:
                warnings.append("Високий денний ліміт може призвести до блокування")
        
        # Перевірка проксі
        if 'proxy_list' in config and config['proxy_list']:
            for proxy in config['proxy_list']:
                if not ValidationUtils.validate_proxy(proxy):
                    warnings.append(f"Некоректний проксі: {proxy}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


class ImageProcessor:
    """Обробник зображень для розпізнавання капчі"""
    
    @staticmethod
    def preprocess_captcha_image(image_data: bytes) -> np.ndarray:
        """Попередня обробка зображення капчі"""
        # Конвертація в numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Конвертація в градації сірого
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Підвищення контрасту
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Зменшення шуму
        gray = cv2.medianBlur(gray, 3)
        
        # Бінаризація
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    @staticmethod
    def extract_text_from_image(image: np.ndarray) -> str:
        """Витягування тексту з зображення"""
        try:
            import pytesseract
            
            # Налаштування tesseract
            config = '--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            
            text = pytesseract.image_to_string(image, config=config)
            return text.strip()
            
        except ImportError:
            logging.error("pytesseract не встановлено")
            return ""
        except Exception as e:
            logging.error(f"Помилка OCR: {e}")
            return ""


def create_default_config() -> Dict:
    """Створення стандартної конфігурації"""
    return {
        "captcha_api_key": "",
        "proxy_list": [],
        "max_accounts": 10,
        "daily_action_limit": 80,
        "action_delays": {
            "like": [2, 5],
            "comment": [3, 8],
            "follow": [4, 10],
            "story_view": [1, 3],
            "story_reply": [2, 6],
            "direct_message": [5, 12]
        },
        "user_agents": [
            "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36"
        ],
        "story_replies": [
            "🔥🔥🔥", "❤️", "Круто!", "👍", "Супер!", 
            "💯", "🙌", "Класно!", "👏", "Wow!",
            "Дуже цікаво!", "Топ контент!", "Красиво!",
            "😍", "🤩", "💪", "✨", "🎉", "👌", "🔥"
        ],
        "direct_messages": [
            "Привіт! Як справи?",
            "Вітаю! Сподобався ваш контент 😊",
            "Доброго дня! Цікавий профіль 👍",
            "Привіт! Круті пости у вас ❤️",
            "Вітаю! Дякую за натхнення 🙌"
        ],
        "automation_settings": {
            "run_schedule": "09:00-22:00",
            "break_duration": [30, 120],
            "max_actions_per_hour": 15,
            "rotate_accounts": True,
            "use_proxy_rotation": True,
            "respect_rate_limits": True,
            "max_errors_per_account": 3,
            "cooldown_after_error": 300
        },
        "safety_settings": {
            "check_shadowban": True,
            "avoid_suspicious_behavior": True,
            "randomize_actions": True,
            "human_like_delays": True,
            "monitor_account_health": True
        }
    }


class SecurityManager:
    """Менеджер безпеки"""
    
    @staticmethod
    def encrypt_password(password: str) -> str:
        """Шифрування паролю (базове)"""
        import base64
        return base64.b64encode(password.encode()).decode()
    
    @staticmethod
    def decrypt_password(encrypted_password: str) -> str:
        """Розшифрування паролю"""
        import base64
        try:
            return base64.b64decode(encrypted_password.encode()).decode()
        except:
            return encrypted_password  # Якщо не зашифровано
    
    @staticmethod
    def generate_session_token() -> str:
        """Генерація токена сесії"""
        import secrets
        return secrets.token_hex(16)


# Експорт основних класів та функцій
__all__ = [
    'setup_logging', 'ProxyManager', 'DatabaseManager', 'StatisticsManager',
    'FileManager', 'SystemUtils', 'ValidationUtils', 'ConfigValidator',
    'ImageProcessor', 'create_default_config', 'SecurityManager'
]