"""
Розширений менеджер конфігурації для Instagram Bot
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil


class BotConfig:
    """Розширений клас для управління конфігурацією бота"""
    
    def __init__(self, config_file: str = "bot_config.json"):
        self.config_file = config_file
        self.backup_dir = "config_backups"
        self.config = self.load_config()
        self.ensure_backup_directory()
    
    def ensure_backup_directory(self):
        """Створення директорії для backup'ів"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def load_config(self) -> Dict[str, Any]:
        """Завантаження конфігурації з файлу"""
        default_config = self.get_default_config()
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    
                # Злиття з дефолтними значеннями
                merged_config = self.merge_configs(default_config, loaded_config)
                
                # Валідація конфігурації
                if self.validate_config(merged_config):
                    return merged_config
                else:
                    logging.warning("Конфігурація не пройшла валідацію, використовуємо стандартну")
                    return default_config
            else:
                # Створення стандартного файлу конфігурації
                self.save_config(default_config)
                logging.info(f"Створено стандартний файл конфігурації: {self.config_file}")
                
        except Exception as e:
            logging.error(f"Помилка завантаження конфігурації: {e}")
            logging.info("Використовуємо стандартну конфігурацію")
        
        return default_config
    
    def get_default_config(self) -> Dict[str, Any]:
        """Стандартна конфігурація"""
        return {
            "version": "2.0.0",
            "created_at": datetime.now().isoformat(),
            
            # API налаштування
            "captcha_api_key": "",
            "captcha_service": "2captcha",  # 2captcha, anticaptcha
            
            # Проксі налаштування
            "proxy_list": [],
            "proxy_rotation": True,
            "proxy_timeout": 10,
            
            # Ліміти безпеки
            "max_accounts": 10,
            "daily_action_limit": 80,
            "hourly_action_limit": 15,
            "max_errors_per_account": 3,
            "cooldown_after_error": 1800,  # 30 хвилин
            
            # Затримки (секунди)
            "action_delays": {
                "like": [2, 5],
                "comment": [3, 8],
                "follow": [4, 10],
                "unfollow": [3, 7],
                "story_view": [1, 3],
                "story_reply": [2, 6],
                "direct_message": [5, 12],
                "page_load": [3, 7],
                "between_actions": [8, 15],
                "between_targets": [15, 45],
                "between_accounts": [120, 300]
            },
            
            # User Agents для обходу детекції
            "user_agents": [
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36"
            ],
            
            # Роздільна здатність екрану для емуляції мобільних пристроїв
            "screen_resolutions": [
                [375, 812],  # iPhone X/11/12/13
                [414, 896],  # iPhone XR/11/12/13 Pro Max
                [390, 844],  # iPhone 12/13 mini
                [360, 640],  # Samsung Galaxy S
                [375, 667],  # iPhone 6/7/8
                [412, 869],  # Pixel
                [414, 736]   # iPhone Plus
            ],
            
            # Повідомлення для сторіс
            "story_replies": [
                "🔥🔥🔥", "❤️", "Круто!", "👍", "Супер!", "💯", "🙌", 
                "Класно!", "👏", "Wow!", "Дуже цікаво!", "Топ контент!", 
                "Красиво!", "😍", "🤩", "💪", "✨", "🎉", "👌", "🔥",
                "Неймовірно!", "Вау!", "Шикарно!", "Бомба!", "👑", 
                "Обожнюю!", "Чудово!", "Натхнення!", "🚀", "💫"
            ],
            
            # Повідомлення для директ
            "direct_messages": [
                "Привіт! Як справи? 😊",
                "Вітаю! Сподобався ваш контент 👍",
                "Доброго дня! Цікавий профіль ✨",
                "Привіт! Круті пости у вас ❤️",
                "Вітаю! Дякую за натхнення 🙌",
                "Привіт! Чудовий контент 🔥",
                "Вітаю! Дуже цікаво 💯",
                "Доброго дня! Класний профіль 👌",
                "Привіт! Дуже круто виглядає 😍",
                "Вітаю! Продовжуйте в тому ж дусі 🚀"
            ],
            
            # Налаштування автоматизації
            "automation_settings": {
                "run_schedule": "09:00-22:00",
                "days_of_week": [1, 2, 3, 4, 5],  # Понеділок-П'ятниця
                "break_duration": [30, 120],  # хвилини
                "max_actions_per_session": 50,
                "session_duration": [60, 180],  # хвилини
                "rotate_accounts": True,
                "use_proxy_rotation": True,
                "randomize_order": True,
                "respect_rate_limits": True,
                "auto_retry_failed": True,
                "retry_count": 2,
                "retry_delay": [300, 600]  # секунди
            },
            
            # Налаштування безпеки
            "safety_settings": {
                "check_shadowban": True,
                "avoid_suspicious_behavior": True,
                "randomize_actions": True,
                "human_like_delays": True,
                "monitor_account_health": True,
                "auto_pause_on_errors": True,
                "max_daily_follows": 50,
                "max_daily_unfollows": 50,
                "max_daily_likes": 300,
                "max_daily_comments": 50,
                "max_daily_stories": 100,
                "max_daily_dms": 20
            },
            
            # Селектори для обходу детекції
            "selectors": {
                "login": {
                    "username_field": "input[name='username']",
                    "password_field": "input[name='password']",
                    "login_button": "button[type='submit']"
                },
                "posts": {
                    "post_links": "article a[href*='/p/']",
                    "like_button": "svg[aria-label='Like']",
                    "liked_button": "svg[aria-label='Unlike']",
                    "close_button": "svg[aria-label='Close']"
                },
                "stories": {
                    "story_avatar": "canvas",
                    "like_button": "svg[aria-label='Like']",
                    "reply_field": "textarea[placeholder*='Send message']",
                    "send_button": "button[type='submit']",
                    "next_button": "button[aria-label='Next']"
                },
                "direct": {
                    "new_message_button": "svg[aria-label*='New message']",
                    "search_field": "input[placeholder*='Search']",
                    "message_field": "textarea[placeholder*='Message']",
                    "send_button": "button[type='submit']"
                },
                "popups": {
                    "notification_not_now": "button:contains('Not Now')",
                    "save_info_not_now": "button:contains('Not Now')",
                    "install_app_cancel": "button:contains('Cancel')",
                    "close_buttons": "svg[aria-label='Close'], button[aria-label='Close']"
                }
            },
            
            # Налаштування логування
            "logging": {
                "level": "INFO",
                "file": "logs/instagram_bot.log",
                "max_file_size": 10485760,  # 10MB
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            
            # Налаштування GUI
            "gui_settings": {
                "theme": "modern",
                "window_size": [1200, 800],
                "auto_save": True,
                "auto_refresh": 30,  # секунди
                "show_notifications": True,
                "language": "uk"
            },
            
            # Розширені налаштування
            "advanced": {
                "use_undetected_chrome": True,
                "disable_images": True,
                "disable_css": False,
                "page_load_timeout": 30,
                "implicit_wait": 10,
                "retry_on_stale_element": True,
                "auto_accept_cookies": True,
                "clear_cache_interval": 24,  # годин
                "session_persistence": True
            }
        }
    
    def merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Злиття конфігурацій з пріоритетом завантаженої"""
        merged = default.copy()
        
        for key, value in loaded.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = self.merge_configs(merged[key], value)
                else:
                    merged[key] = value
            else:
                merged[key] = value
        
        return merged
    
    def validate_config(self, config: Dict) -> bool:
        """Валідація конфігурації"""
        try:
            # Перевірка обов'язкових полів
            required_fields = [
                'action_delays', 'daily_action_limit', 'automation_settings',
                'safety_settings', 'user_agents', 'story_replies'
            ]
            
            for field in required_fields:
                if field not in config:
                    logging.error(f"Відсутнє обов'язкове поле: {field}")
                    return False
            
            # Перевірка затримок
            delays = config.get('action_delays', {})
            for action, delay_range in delays.items():
                if not isinstance(delay_range, list) or len(delay_range) != 2:
                    logging.error(f"Некоректні затримки для {action}")
                    return False
                if delay_range[0] > delay_range[1]:
                    logging.error(f"Мінімальна затримка більша за максимальну для {action}")
                    return False
            
            # Перевірка лімітів
            daily_limit = config.get('daily_action_limit', 0)
            if not isinstance(daily_limit, int) or daily_limit <= 0:
                logging.error("Денний ліміт має бути позитивним числом")
                return False
            
            # Перевірка проксі
            proxy_list = config.get('proxy_list', [])
            for proxy in proxy_list:
                if not self.validate_proxy_format(proxy):
                    logging.warning(f"Некоректний формат проксі: {proxy}")
            
            return True
            
        except Exception as e:
            logging.error(f"Помилка валідації конфігурації: {e}")
            return False
    
    def validate_proxy_format(self, proxy: str) -> bool:
        """Валідація формату проксі"""
        import re
        patterns = [
            r'^(\d{1,3}\.){3}\d{1,3}:\d{1,5}$',  # ip:port
            r'^(\d{1,3}\.){3}\d{1,3}:\d{1,5}:\w+:\w+$',  # ip:port:user:pass
            r'^[\w\.-]+:\d{1,5}$',  # domain:port
            r'^[\w\.-]+:\d{1,5}:\w+:\w+$'  # domain:port:user:pass
        ]
        return any(re.match(pattern, proxy) for pattern in patterns)
    
    def save_config(self, config: Dict[str, Any] = None):
        """Збереження конфігурації з backup"""
        if config is None:
            config = self.config
        
        try:
            # Створення backup поточної конфігурації
            if os.path.exists(self.config_file):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = os.path.join(self.backup_dir, f"config_backup_{timestamp}.json")
                shutil.copy2(self.config_file, backup_file)
                logging.info(f"Створено backup конфігурації: {backup_file}")
            
            # Збереження нової конфігурації
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Конфігурація збережена: {self.config_file}")
            
        except Exception as e:
            logging.error(f"Помилка збереження конфігурації: {e}")
    
    def get(self, key: str, default=None):
        """Отримання значення з конфігурації"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Встановлення значення в конфігурації"""
        keys = key.split('.')
        config = self.config
        
        # Навігація до батьківського елемента
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Встановлення значення
        config[keys[-1]] = value
        self.save_config()
    
    def get_story_replies(self) -> List[str]:
        """Отримання шаблонів відповідей для сторіс"""
        return self.config.get('story_replies', [])
    
    def get_direct_messages(self) -> List[str]:
        """Отримання шаблонів прямих повідомлень"""
        return self.config.get('direct_messages', [])
    
    def get_automation_settings(self) -> Dict[str, Any]:
        """Отримання налаштувань автоматизації"""
        return self.config.get('automation_settings', {})
    
    def get_safety_settings(self) -> Dict[str, Any]:
        """Отримання налаштувань безпеки"""
        return self.config.get('safety_settings', {})
    
    def get_action_delays(self) -> Dict[str, List[int]]:
        """Отримання затримок для дій"""
        return self.config.get('action_delays', {})
    
    def get_user_agents(self) -> List[str]:
        """Отримання списку User-Agent'ів"""
        return self.config.get('user_agents', [])
    
    def get_screen_resolutions(self) -> List[List[int]]:
        """Отримання роздільних здатностей екрану"""
        return self.config.get('screen_resolutions', [])
    
    def get_selectors(self, category: str = None) -> Dict:
        """Отримання CSS селекторів"""
        selectors = self.config.get('selectors', {})
        if category:
            return selectors.get(category, {})
        return selectors
    
    def add_proxy(self, proxy: str):
        """Додавання проксі до списку"""
        if self.validate_proxy_format(proxy):
            if 'proxy_list' not in self.config:
                self.config['proxy_list'] = []
            
            if proxy not in self.config['proxy_list']:
                self.config['proxy_list'].append(proxy)
                self.save_config()
                return True
        return False
    
    def remove_proxy(self, proxy: str):
        """Видалення проксі зі списку"""
        if 'proxy_list' in self.config and proxy in self.config['proxy_list']:
            self.config['proxy_list'].remove(proxy)
            self.save_config()
            return True
        return False
    
    def add_story_reply(self, reply: str):
        """Додавання відповіді для сторіс"""
        if reply and reply not in self.config.get('story_replies', []):
            if 'story_replies' not in self.config:
                self.config['story_replies'] = []
            self.config['story_replies'].append(reply)
            self.save_config()
    
    def add_direct_message(self, message: str):
        """Додавання шаблону прямого повідомлення"""
        if message and message not in self.config.get('direct_messages', []):
            if 'direct_messages' not in self.config:
                self.config['direct_messages'] = []
            self.config['direct_messages'].append(message)
            self.save_config()
    
    def export_config(self, file_path: str) -> bool:
        """Експорт конфігурації у файл"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logging.info(f"Конфігурація експортована: {file_path}")
            return True
        except Exception as e:
            logging.error(f"Помилка експорту конфігурації: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """Імпорт конфігурації з файлу"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Валідація імпортованої конфігурації
            if self.validate_config(imported_config):
                # Злиття з поточною конфігурацією
                self.config = self.merge_configs(self.config, imported_config)
                self.save_config()
                logging.info(f"Конфігурація імпортована: {file_path}")
                return True
            else:
                logging.error("Імпортована конфігурація не пройшла валідацію")
                return False
                
        except Exception as e:
            logging.error(f"Помилка імпорту конфігурації: {e}")
            return False
    
    def reset_to_defaults(self):
        """Скидання до стандартних налаштувань"""
        self.config = self.get_default_config()
        self.save_config()
        logging.info("Конфігурація скинута до стандартних налаштувань")
    
    def get_config_summary(self) -> Dict:
        """Отримання короткого огляду конфігурації"""
        return {
            'version': self.config.get('version', 'Unknown'),
            'total_proxies': len(self.config.get('proxy_list', [])),
            'daily_action_limit': self.config.get('daily_action_limit', 0),
            'total_story_replies': len(self.config.get('story_replies', [])),
            'total_direct_messages': len(self.config.get('direct_messages', [])),
            'captcha_api_configured': bool(self.config.get('captcha_api_key', '')),
            'safety_mode': self.config.get('safety_settings', {}).get('avoid_suspicious_behavior', False),
            'auto_rotation': self.config.get('automation_settings', {}).get('rotate_accounts', False)
        }
    
    def cleanup_old_backups(self, max_backups: int = 10):
        """Очищення старих backup'ів"""
        try:
            if not os.path.exists(self.backup_dir):
                return
            
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('config_backup_') and filename.endswith('.json'):
                    file_path = os.path.join(self.backup_dir, filename)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # Сортування за часом модифікації
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Видалення старих backup'ів
            for file_path, _ in backup_files[max_backups:]:
                try:
                    os.remove(file_path)
                    logging.info(f"Видалено старий backup: {file_path}")
                except Exception as e:
                    logging.error(f"Помилка видалення backup {file_path}: {e}")
                    
        except Exception as e:
            logging.error(f"Помилка очищення backup'ів: {e}")
    
    def get_config_validation_report(self) -> Dict:
        """Отримання детального звіту валідації конфігурації"""
        report = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        try:
            # Перевірка безпеки
            daily_limit = self.config.get('daily_action_limit', 0)
            if daily_limit > 150:
                report['warnings'].append(f"Високий денний ліміт ({daily_limit}) може призвести до блокування")
            elif daily_limit > 200:
                report['errors'].append(f"Критично високий денний ліміт ({daily_limit})")
                report['valid'] = False
            
            # Перевірка затримок
            delays = self.config.get('action_delays', {})
            for action, delay_range in delays.items():
                if delay_range[0] < 1:
                    report['warnings'].append(f"Занадто короткі затримки для {action}")
                if delay_range[1] - delay_range[0] < 1:
                    report['recommendations'].append(f"Збільшіть розбіг затримок для {action}")
            
            # Перевірка проксі
            proxy_count = len(self.config.get('proxy_list', []))
            if proxy_count == 0:
                report['warnings'].append("Не налаштовано проксі серверів")
            elif proxy_count < 3:
                report['recommendations'].append("Рекомендується використовувати більше проксі серверів")
            
            # Перевірка API ключа капчі
            if not self.config.get('captcha_api_key'):
                report['warnings'].append("Не налаштовано API ключ для розв'язання капчі")
            
            # Перевірка повідомлень
            story_replies_count = len(self.config.get('story_replies', []))
            if story_replies_count < 10:
                report['recommendations'].append("Додайте більше варіантів відповідей для сторіс")
            
            dm_count = len(self.config.get('direct_messages', []))
            if dm_count < 5:
                report['recommendations'].append("Додайте більше шаблонів прямих повідомлень")
            
        except Exception as e:
            report['errors'].append(f"Помилка валідації: {e}")
            report['valid'] = False
        
        return report
