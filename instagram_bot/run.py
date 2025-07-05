#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Bot v2.0 - Головний файл запуску
Професійна автоматизація Instagram з обходом всіх захистів
"""

import sys
import os
import argparse
import logging
import time
import json
from pathlib import Path
from typing import List, Dict, Any
import webbrowser

# Додавання поточної директорії до шляху
sys.path.append(str(Path(__file__).parent))

# Банер програми
BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🤖 INSTAGRAM AUTOMATION BOT v2.0 PRO 🤖               ║
║                                                              ║
║  ✨ Повна автоматизація Instagram з обходом захисту          ║
║  🛡️ Обхід капчі, popup'ів та систем детекції                ║
║  🎯 Лайки постів/сторіс, відповіді, DM повідомлення          ║
║  📊 Професійний GUI та CLI інтерфейс                         ║
║  🔒 Безпечні ліміти та розумні затримки                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

def print_banner():
    """Виведення банера програми"""
    print("\033[96m" + BANNER + "\033[0m")


def check_python_version():
    """Перевірка версії Python"""
    if sys.version_info < (3, 8):
        print("❌ Потрібна версія Python 3.8 або вища")
        print(f"📍 Поточна версія: {sys.version}")
        return False
    return True


def check_dependencies():
    """Перевірка залежностей"""
    print("🔍 Перевірка залежностей...")

    # Ключ — pip-пакет, Значення — ім'я для імпорту
    required_packages = {
        'selenium': 'selenium',
        'undetected-chromedriver': 'undetected_chromedriver',
        'requests': 'requests',
        'opencv-python': 'cv2',
        'Pillow': 'PIL',
        'numpy': 'numpy',
        'webdriver-manager': 'webdriver_manager'
    }

    missing_packages = []

    for pip_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {pip_name}")
        except ImportError:
            print(f"❌ {pip_name}")
            missing_packages.append(pip_name)

    if missing_packages:
        print(f"\n❌ Відсутні залежності: {', '.join(missing_packages)}")
        print("📦 Встановіть їх командою:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False

    print("✅ Всі залежності встановлені")
    return True



def setup_directories():
    """Створення необхідних директорій"""
    directories = [
        'logs',
        'data', 
        'backups',
        'exports',
        'config_backups',
        'assets'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("📁 Директорії створені")


def setup_logging():
    """Налаштування системи логування"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Основний логер
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('logs/instagram_bot.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Логер для помилок
    error_handler = logging.FileHandler('logs/errors.log', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format))
    
    logger = logging.getLogger()
    logger.addHandler(error_handler)
    
    print("📝 Логування налаштовано")


def create_sample_files():
    """Створення зразків файлів"""
    print("📄 Створення зразків файлів...")
    
    # Зразок акаунтів
    accounts_sample = """# Формат: username:password:proxy (proxy опціонально)
# Приклади:
# my_account:my_password
# account2:password2:127.0.0.1:8080
# account3:password3:proxy.example.com:3128:user:pass

# Ваші акаунти (розкоментуйте та замініть на реальні дані):
# your_username:your_password
# another_account:another_password:your.proxy.com:8080:proxyuser:proxypass
"""
    
    # Зразок цілей
    targets_sample = """# Список цільових користувачів Instagram (по одному на рядок)
# Приклади:
# target_user1
# target_user2
# famous_account
# competitor_page

# Ваші цілі (розкоментуйте та замініть):
# target1
# target2
# target3
"""
    
    # Зразок проксі
    proxies_sample = """# Список проксі серверів (по одному на рядок)
# Формати:
# ip:port
# ip:port:username:password
# domain.com:port
# domain.com:port:username:password

# Приклади:
# 127.0.0.1:8080
# proxy.example.com:3128:user:pass
# 192.168.1.1:1080

# Ваші проксі:
"""
    
    # Створення файлів
    samples = {
        'accounts_sample.txt': accounts_sample,
        'targets_sample.txt': targets_sample,
        'proxies_sample.txt': proxies_sample
    }
    
    for filename, content in samples.items():
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Створено {filename}")


def check_chrome_installation():
    """Перевірка встановлення Chrome"""
    print("🌐 Перевірка Chrome...")
    
    try:
        import subprocess
        
        if sys.platform.startswith('win'):
            # Windows
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ]
            
            for path in chrome_paths:
                if os.path.exists(path):
                    print("✅ Google Chrome знайдено")
                    return True
                    
        elif sys.platform.startswith('darwin'):
            # macOS
            result = subprocess.run(['which', 'google-chrome'], capture_output=True)
            if result.returncode == 0:
                print("✅ Google Chrome знайдено")
                return True
                
        else:
            # Linux
            result = subprocess.run(['which', 'google-chrome'], capture_output=True)
            if result.returncode == 0:
                print("✅ Google Chrome знайдено")
                return True
                
        print("⚠️ Google Chrome не знайдено")
        print("📦 Встановіть Chrome з https://www.google.com/chrome/")
        return False
        
    except Exception as e:
        print(f"⚠️ Помилка перевірки Chrome: {e}")
        return False


def initialize_config():
    """Ініціалізація конфігурації"""
    try:
        from config import BotConfig
        config = BotConfig()
        
        # Перевірка валідності конфігурації
        validation = config.get_config_validation_report()
        
        if not validation['valid']:
            print("❌ Помилки в конфігурації:")
            for error in validation['errors']:
                print(f"   • {error}")
            return False
        
        if validation['warnings']:
            print("⚠️ Попередження конфігурації:")
            for warning in validation['warnings']:
                print(f"   • {warning}")
        
        print("✅ Конфігурація ініціалізована")
        return config
        
    except Exception as e:
        print(f"❌ Помилка ініціалізації конфігурації: {e}")
        return None


def run_gui_mode():
    """Запуск GUI режиму"""
    try:
        print("🖥️ Запуск графічного інтерфейсу...")
        
        import tkinter as tk
        from gui import InstagramBotGUI
        
        root = tk.Tk()
        app = InstagramBotGUI(root)
        
        # Обробка закриття
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        print("✅ GUI запущено успішно")
        print("💡 Підказка: Використовуйте Dashboard для швидкого старту")
        
        root.mainloop()
        return True
        
    except ImportError as e:
        print(f"❌ Помилка імпорту GUI: {e}")
        print("📦 Можливо потрібно встановити додаткові залежності:")
        print("   pip install sv-ttk")
        return False
    except Exception as e:
        print(f"❌ Помилка запуску GUI: {e}")
        return False


def run_cli_mode(args):
    """Запуск CLI режиму"""
    try:
        print("💻 Запуск CLI режиму...")
        
        from instagram_bot import InstagramBot
        from config import BotConfig
        
        # Завантаження конфігурації
        config = BotConfig(args.config)
        
        # Ініціалізація бота
        bot = InstagramBot(config.get('captcha_api_key'))
        
        # Завантаження акаунтів
        if args.accounts:
            accounts_loaded = load_accounts_from_file(bot, args.accounts)
            print(f"📥 Завантажено {accounts_loaded} акаунтів")
        
        if not bot.account_manager.accounts:
            print("❌ Немає акаунтів для роботи")
            print("💡 Додайте акаунти через --accounts файл або GUI режим")
            return False
        
        # Завантаження цілей
        targets = []
        if args.targets:
            targets = load_targets_from_file(args.targets)
            print(f"🎯 Завантажено {len(targets)} цілей")
        
        if not targets:
            print("❌ Немає цілей для автоматизації")
            print("💡 Додайте цілі через --targets файл або GUI режим")
            return False
        
        # Конфігурація автоматизації
        automation_config = {
            'accounts': [{'username': username} for username in bot.account_manager.accounts.keys()],
            'targets': targets,
            'actions': {
                'like_posts': getattr(args, 'like_posts', True),
                'like_stories': getattr(args, 'like_stories', True),
                'reply_stories': getattr(args, 'reply_stories', True),
                'send_dm_if_no_stories': getattr(args, 'send_dm', False)
            },
            'story_messages': config.get_story_replies(),
            'direct_messages': config.get_direct_messages()
        }
        
        print("🚀 Запуск автоматизації...")
        print(f"📊 Акаунтів: {len(automation_config['accounts'])}")
        print(f"🎯 Цілей: {len(automation_config['targets'])}")
        print(f"⚡ Дії: {', '.join([k for k, v in automation_config['actions'].items() if v])}")
        
        try:
            bot.run_automation(automation_config)
            print("✅ Автоматизація завершена успішно!")
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️ Автоматизація зупинена користувачем")
            return True
            
        except Exception as e:
            print(f"❌ Помилка автоматизації: {e}")
            logging.error(f"CLI automation error: {e}")
            return False
            
        finally:
            bot.close_all_drivers()
            
    except Exception as e:
        print(f"❌ Помилка CLI режиму: {e}")
        logging.error(f"CLI mode error: {e}")
        return False


def load_accounts_from_file(bot, file_path: str) -> int:
    """Завантаження акаунтів з файлу"""
    if not os.path.exists(file_path):
        print(f"❌ Файл акаунтів не знайдено: {file_path}")
        return 0
    
    count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(':')
                if len(parts) >= 2:
                    username = parts[0].strip()
                    password = parts[1].strip()
                    proxy = ':'.join(parts[2:]).strip() if len(parts) > 2 else None
                    
                    # Валідація
                    from utils import ValidationUtils
                    if not ValidationUtils.validate_username(username):
                        print(f"⚠️ Некоректний логін в рядку {line_num}: {username}")
                        continue
                    
                    if proxy and not ValidationUtils.validate_proxy(proxy):
                        print(f"⚠️ Некоректний проксі в рядку {line_num}: {proxy}")
                        proxy = None
                    
                    bot.account_manager.add_account(username, password, proxy)
                    count += 1
                else:
                    print(f"⚠️ Некоректний формат в рядку {line_num}: {line}")
        
        logging.info(f"Завантажено {count} акаунтів з файлу {file_path}")
        
    except Exception as e:
        print(f"❌ Помилка завантаження акаунтів: {e}")
        logging.error(f"Error loading accounts: {e}")
    
    return count


def load_targets_from_file(file_path: str) -> List[str]:
    """Завантаження цілей з файлу"""
    if not os.path.exists(file_path):
        print(f"❌ Файл цілей не знайдено: {file_path}")
        return []
    
    targets = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                target = line.strip()
                if target and not target.startswith('#'):
                    # Валідація
                    from utils import ValidationUtils
                    if ValidationUtils.validate_username(target):
                        targets.append(target)
                    else:
                        print(f"⚠️ Некоректна ціль в рядку {line_num}: {target}")
        
        logging.info(f"Завантажено {len(targets)} цілей з файлу {file_path}")
        
    except Exception as e:
        print(f"❌ Помилка завантаження цілей: {e}")
        logging.error(f"Error loading targets: {e}")
    
    return targets


def run_setup_wizard():
    """Майстер початкового налаштування"""
    print("\n🧙‍♂️ Майстер початкового налаштування")
    print("=" * 50)
    
    # Крок 1: Створення зразків файлів
    print("\n📄 Крок 1: Створення зразків файлів")
    create_sample_files()
    
    # Крок 2: Налаштування конфігурації
    print("\n⚙️ Крок 2: Базова конфігурація")
    config = initialize_config()
    
    if not config:
        return False
    
    # Крок 3: Рекомендації
    print("\n💡 Крок 3: Рекомендації для безпечного використання")
    print("""
    🛡️ ВАЖЛИВІ РЕКОМЕНДАЦІЇ:
    
    1. 📊 Ліміти безпеки:
       • Не більше 80-100 дій на день на акаунт
       • Не більше 15-20 дій на годину
       • Робіть перерви між сесіями
    
    2. 🌐 Проксі:
       • Використовуйте якісні приватні проксі
       • Один проксі на один акаунт
       • Регулярно змінюйте проксі
    
    3. 🔒 Безпека акаунтів:
       • Використовуйте різні паролі
       • Не запускайте багато акаунтів одночасно
       • Моніторьте стан акаунтів
    
    4. 📝 Контент:
       • Використовуйте різноманітні повідомлення
       • Уникайте спаму та повторень
       • Будьте природними у взаємодії
    """)
    
    # Крок 4: Запуск
    print("\n🚀 Крок 4: Готовність до запуску")
    print("""
    ✅ Налаштування завершено!
    
    📋 Наступні кроки:
    1. Відредагуйте файли accounts_sample.txt та targets_sample.txt
    2. Додайте свої акаунти та цілі
    3. Запустіть програму в GUI режимі: python run.py
    4. Або використовуйте CLI: python run.py --mode cli --accounts accounts.txt --targets targets.txt
    """)
    
    return True


def show_help():
    """Показ детальної довідки"""
    help_text = """
🤖 INSTAGRAM AUTOMATION BOT v2.0 - ДЕТАЛЬНА ДОВІДКА

📖 ОГЛЯД:
   Професійний бот для автоматизації дій в Instagram з повним обходом
   систем захисту, включаючи капчу, popup'и та детекцію ботів.

🔧 ОСНОВНІ ФУНКЦІЇ:
   ❤️  Лайки постів (останні 2 пости користувача)
   📖 Лайки та перегляд сторіс
   💬 Відповіді на сторіс
   📩 Відправка прямих повідомлень (якщо немає сторіс)
   🛡️  Обхід капчі та popup'ів
   🔒 Безпечні ліміти та затримки

🚀 РЕЖИМИ ЗАПУСКУ:
   
   🖥️  GUI режим (рекомендований):
       python run.py
       python run.py --mode gui
   
   💻 CLI режим:
       python run.py --mode cli --accounts accounts.txt --targets targets.txt
   
   📅 Планувальник:
       python run.py --mode scheduler --start-time 09:00

📋 ПАРАМЕТРИ КОМАНДНОГО РЯДКА:
   
   --mode {gui,cli,scheduler}     Режим роботи
   --config FILE                  Файл конфігурації (за замовчуванням: bot_config.json)
   --accounts FILE                Файл з акаунтами (username:password:proxy)
   --targets FILE                 Файл з цілями (по одному на рядок)
   --like-posts                   Лайкати пости
   --like-stories                 Лайкати сторіс
   --reply-stories                Відповідати на сторіс
   --send-dm                      Відправляти DM якщо немає сторіс
   --start-time TIME              Час запуску планувальника (HH:MM)

📁 СТРУКТУРА ФАЙЛІВ:
   
   bot_config.json                Основна конфігурація
   accounts.txt                   Акаунти Instagram
   targets.txt                    Цільові користувачі
   proxies.txt                    Список проксі серверів
   
   logs/                          Логи програми
   ├── instagram_bot.log          Основний лог
   └── errors.log                 Логи помилок
   
   data/                          Дані програми
   ├── instagram_bot.db           База даних
   └── statistics.json            Статистика
   
   backups/                       Backup файли
   exports/                       Експортовані дані

📄 ФОРМАТИ ФАЙЛІВ:
   
   📝 accounts.txt:
      username1:password1
      username2:password2:proxy.com:8080
      username3:password3:proxy.com:8080:user:pass
   
   🎯 targets.txt:
      target_user1
      target_user2
      target_user3
   
   🌐 proxies.txt:
      127.0.0.1:8080
      proxy.example.com:3128:username:password

🛡️ НАЛАШТУВАННЯ БЕЗПЕКИ:
   
   📊 Рекомендовані ліміти:
   • 50-80 дій на день на акаунт
   • 10-15 дій на годину
   • 2-5 секунд між діями
   • 15-45 секунд між цілями
   • 2-5 хвилин між акаунтами
   
   🔒 Обов'язкові заходи:
   • Використовуйте якісні проксі
   • Різні User-Agent для кожного акаунту
   • Випадкові затримки між діями
   • Моніторинг стану акаунтів

⚙️ РОЗШИРЕНІ НАЛАШТУВАННЯ:
   
   🤖 Капча:
   • Підтримка 2captcha.com
   • Автоматичне розв'язання reCAPTCHA
   • Розпізнавання FunCAPTCHA
   
   🌐 Проксі:
   • HTTP/HTTPS проксі
   • SOCKS4/SOCKS5 проксі  
   • Автоматична ротація
   • Тестування швидкості
   
   📱 Емуляція пристроїв:
   • Випадкові User-Agent
   • Мобільні роздільності екрану
   • Емуляція touch подій

🔧 УСУНЕННЯ ПРОБЛЕМ:
   
   ❌ Проблема: "Chrome not found"
   ✅ Рішення: Встановіть Google Chrome
   
   ❌ Проблема: "Captcha not solved"
   ✅ Рішення: Додайте API ключ 2captcha
   
   ❌ Проблема: "Account restricted"
   ✅ Рішення: Зменшіть ліміти, змініть проксі
   
   ❌ Проблема: "Proxy error"
   ✅ Рішення: Перевірте формат та працездатність проксі

📞 ПІДТРИМКА:
   
   📧 Email: support@instagrambot.pro
   💬 Telegram: @instagrambot_support
   🌐 Сайт: https://instagrambot.pro
   📚 Документація: https://docs.instagrambot.pro

🔄 ОНОВЛЕННЯ:
   
   Для отримання оновлень виконайте:
   git pull origin main
   pip install -r requirements.txt --upgrade
"""
    
    print(help_text)


def main():
    """Головна функція"""
    # Очищення екрану
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Банер
    print_banner()
    
    # Парсинг аргументів
    parser = argparse.ArgumentParser(
        description='Instagram Automation Bot v2.0 - Професійна автоматизація',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ПРИКЛАДИ ВИКОРИСТАННЯ:

  Запуск GUI (рекомендований):
    python run.py
    
  CLI з файлами:
    python run.py --mode cli --accounts accounts.txt --targets targets.txt
    
  CLI з усіма діями:
    python run.py --mode cli --accounts accounts.txt --targets targets.txt --like-posts --like-stories --reply-stories
    
  Планувальник:
    python run.py --mode scheduler --start-time 09:00 --accounts accounts.txt --targets targets.txt

ФАЙЛИ КОНФІГУРАЦІЇ:
  accounts.txt:     username:password:proxy
  targets.txt:      target_username (по одному на рядок)
  bot_config.json:  основна конфігурація програми
        """
    )
    
    parser.add_argument('--mode', 
                       choices=['gui', 'cli', 'scheduler'], 
                       default='gui', 
                       help='Режим роботи (за замовчуванням: gui)')
    
    parser.add_argument('--config', 
                       default='bot_config.json', 
                       help='Файл конфігурації')
    
    parser.add_argument('--accounts', 
                       help='Файл з акаунтами (username:password:proxy)')
    
    parser.add_argument('--targets', 
                       help='Файл з цілями')
    
    parser.add_argument('--like-posts', 
                       action='store_true',
                       help='Лайкати пости')
    
    parser.add_argument('--like-stories', 
                       action='store_true',
                       help='Лайкати сторіс')
    
    parser.add_argument('--reply-stories', 
                       action='store_true',
                       help='Відповідати на сторіс')
    
    parser.add_argument('--send-dm', 
                       action='store_true',
                       help='Відправляти DM якщо немає сторіс')
    
    parser.add_argument('--start-time', 
                       default='09:00',
                       help='Час запуску планувальника (HH:MM)')
    
    parser.add_argument('--setup', 
                       action='store_true',
                       help='Запустити майстер налаштування')
    
    parser.add_argument('--create-samples', 
                       action='store_true',
                       help='Створити зразки файлів')
    
    parser.add_argument('--check-system', 
                       action='store_true',
                       help='Перевірити системні вимоги')
    
    parser.add_argument('--help-detailed', 
                       action='store_true',
                       help='Показати детальну довідку')
    
    parser.add_argument('--version', 
                       action='store_true',
                       help='Показати версію')
    
    # Обробка аргументів
    try:
        args = parser.parse_args()
    except SystemExit:
        return 1
    
    # Спеціальні команди
    if args.version:
        print("📋 Instagram Bot v2.0.0 Professional")
        print(f"🐍 Python: {sys.version}")
        print("🏢 © 2024 Instagram Bot Pro")
        return 0
    
    if args.help_detailed:
        show_help()
        return 0
    
    if args.create_samples:
        create_sample_files()
        print("✅ Зразки файлів створені")
        return 0
    
    if args.setup:
        return 0 if run_setup_wizard() else 1
    
    if args.check_system:
        print("🔍 Перевірка системних вимог...\n")
        
        checks = [
            ("Python версія", check_python_version),
            ("Залежності", check_dependencies),
            ("Google Chrome", check_chrome_installation)
        ]
        
        all_passed = True
        for name, check_func in checks:
            print(f"🔍 {name}:")
            if not check_func():
                all_passed = False
            print()
        
        if all_passed:
            print("✅ Система готова до роботи!")
            return 0
        else:
            print("❌ Виявлені проблеми. Виправте їх перед запуском.")
            return 1
    
    # Основні перевірки
    print("🔍 Перевірка системи...")
    
    if not check_python_version():
        return 1
    
    if not check_dependencies():
        print("\n💡 Встановіть залежності командою:")
        print("   pip install -r requirements.txt")
        return 1
    
    # Налаштування середовища
    setup_directories()
    setup_logging()
    
    # Ініціалізація конфігурації
    config = initialize_config()
    if not config:
        return 1
    
    # Запуск відповідного режиму
    success = False
    
    try:
        print(f"\n🚀 Запуск режиму: {args.mode.upper()}")
        print("=" * 50)
        
        if args.mode == 'gui':
            success = run_gui_mode()
        elif args.mode == 'cli':
            success = run_cli_mode(args)
        elif args.mode == 'scheduler':
            # TODO: Реалізувати планувальник
            print("📅 Режим планувальника буде доступний в наступній версії")
            success = False
        
    except KeyboardInterrupt:
        print("\n⏹️ Програма зупинена користувачем")
        success = True
    except Exception as e:
        print(f"\n❌ Критична помилка: {e}")
        logging.error(f"Critical error: {e}")
        success = False
    
    # Завершення
    print("\n" + "=" * 50)
    if success:
        print("✅ Програма завершена успішно")
        print("📝 Логи збережені в папці logs/")
    else:
        print("❌ Програма завершена з помилками")
        print("🔍 Перевірте логи: logs/instagram_bot.log")
        print("💡 Спробуйте: python run.py --help-detailed")
    
    print("🙏 Дякуємо за використання Instagram Bot Pro!")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)