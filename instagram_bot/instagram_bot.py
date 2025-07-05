#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Bot - Розширена автоматизація з обходом захисту
Функції: лайки постів/сторіс, відповіді на сторіс, директ повідомлення
"""

import random
import time
import json
import logging
import re
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException,
    StaleElementReferenceException, WebDriverException
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc


class AntiDetectionManager:
    """Менеджер для обходу систем детекції ботів"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        ]
        
        self.screen_resolutions = [
            (375, 812), (414, 896), (390, 844), (360, 640), (375, 667)
        ]
        
    def get_random_user_agent(self) -> str:
        return random.choice(self.user_agents)
    
    def get_random_resolution(self) -> tuple:
        return random.choice(self.screen_resolutions)
    
    def human_like_delay(self, min_delay: float = 1.0, max_delay: float = 4.0):
        """Затримка, що імітує людську поведінку"""
        delay = random.uniform(min_delay, max_delay)
        # Додавання випадкових мікро-пауз
        for _ in range(random.randint(1, 3)):
            time.sleep(delay / 10)
            delay *= 0.9
        time.sleep(delay)
    
    def random_scroll(self, driver, direction='down', distance=None):
        """Випадкове прокручування"""
        if distance is None:
            distance = random.randint(100, 500)
        
        if direction == 'down':
            distance = abs(distance)
        else:
            distance = -abs(distance)
        
        actions = ActionChains(driver)
        actions.scroll_by_amount(0, distance).perform()
        time.sleep(random.uniform(0.5, 2.0))
    
    def human_mouse_movement(self, driver, element):
        """Імітація людського руху миші"""
        actions = ActionChains(driver)
        
        # Випадковий рух до елемента
        for _ in range(random.randint(1, 3)):
            x_offset = random.randint(-50, 50)
            y_offset = random.randint(-20, 20)
            actions.move_by_offset(x_offset, y_offset)
            time.sleep(random.uniform(0.1, 0.3))
        
        actions.move_to_element(element).perform()
        time.sleep(random.uniform(0.2, 0.8))


class PopupHandler:
    """Обробник popup'ів та модальних вікон"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)
    
    def handle_all_popups(self):
        """Обробка всіх можливих popup'ів"""
        popups_handled = []
        
        # Обробка notification popup
        if self.handle_notification_popup():
            popups_handled.append("notification")
        
        # Обробка login suggestion
        if self.handle_login_suggestions():
            popups_handled.append("login_suggestions")
        
        # Обробка install app
        if self.handle_install_app():
            popups_handled.append("install_app")
        
        # Обробка cookies
        if self.handle_cookies():
            popups_handled.append("cookies")
        
        # Обробка location popup
        if self.handle_location_popup():
            popups_handled.append("location")
        
        # Обробка save login info
        if self.handle_save_login_info():
            popups_handled.append("save_login")
        
        return popups_handled
    
    def handle_notification_popup(self) -> bool:
        """Відхилення запиту на сповіщення"""
        selectors = [
            "button[class*='_a9--'][class*='_a9_1']",  # Not Now button
            "//button[contains(text(), 'Not Now')]",
            "//button[contains(text(), 'Не зараз')]",
            "[data-testid='turnOnNotifications'] button",
            "button[class*='_acan'][class*='_acap']"
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                element.click()
                time.sleep(1)
                return True
            except:
                continue
        return False
    
    def handle_login_suggestions(self) -> bool:
        """Закриття пропозицій входу"""
        selectors = [
            "svg[aria-label='Close']",
            "button[aria-label='Close']",
            "[role='button'][aria-label='Close']",
            "//button[contains(@aria-label, 'Close')]"
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                element.click()
                time.sleep(1)
                return True
            except:
                continue
        return False
    
    def handle_install_app(self) -> bool:
        """Відхилення пропозиції встановити застосунок"""
        selectors = [
            "//button[contains(text(), 'Not Now')]",
            "//button[contains(text(), 'Cancel')]",
            "//a[contains(text(), 'Not Now')]",
            "button[class*='_a9--'][class*='_a9_0']"
        ]
        
        for selector in selectors:
            try:
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                element.click()
                time.sleep(1)
                return True
            except:
                continue
        return False
    
    def handle_cookies(self) -> bool:
        """Прийняття cookies"""
        selectors = [
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Allow')]", 
            "//button[contains(text(), 'Accept All')]",
            "[data-cookiebanner='accept_button']"
        ]
        
        for selector in selectors:
            try:
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                element.click()
                time.sleep(1)
                return True
            except:
                continue
        return False
    
    def handle_location_popup(self) -> bool:
        """Відхилення запиту локації"""
        selectors = [
            "//button[contains(text(), 'Not Now')]",
            "//button[contains(text(), 'Block')]"
        ]
        
        for selector in selectors:
            try:
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                element.click()
                time.sleep(1)
                return True
            except:
                continue
        return False
    
    def handle_save_login_info(self) -> bool:
        """Відхилення збереження інформації для входу"""
        selectors = [
            "//button[contains(text(), 'Not Now')]",
            "//button[contains(text(), 'Save Info')]//following-sibling::button"
        ]
        
        for selector in selectors:
            try:
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                element.click()
                time.sleep(1)
                return True
            except:
                continue
        return False


class CaptchaSolver:
    """Розв'язувач капчі з підтримкою різних сервісів"""
    
    def __init__(self, api_key: str = None, service: str = "2captcha"):
        self.api_key = api_key
        self.service = service
        
        self.services = {
            '2captcha': {
                'submit_url': 'http://2captcha.com/in.php',
                'result_url': 'http://2captcha.com/res.php'
            },
            'anticaptcha': {
                'submit_url': 'https://api.anti-captcha.com/createTask',
                'result_url': 'https://api.anti-captcha.com/getTaskResult'
            }
        }
    
    def solve_recaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Розв'язання reCAPTCHA v2"""
        if not self.api_key:
            logging.warning("API ключ капчі не встановлено")
            return None
        
        try:
            if self.service == '2captcha':
                return self._solve_2captcha_recaptcha(site_key, page_url)
            elif self.service == 'anticaptcha':
                return self._solve_anticaptcha_recaptcha(site_key, page_url)
        except Exception as e:
            logging.error(f"Помилка розв'язання капчі: {e}")
        
        return None
    
    def _solve_2captcha_recaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Розв'язання через 2captcha"""
        # Відправка капчі
        submit_data = {
            'key': self.api_key,
            'method': 'userrecaptcha',
            'googlekey': site_key,
            'pageurl': page_url,
            'json': 1
        }
        
        response = requests.post(self.services['2captcha']['submit_url'], data=submit_data)
        result = response.json()
        
        if result.get('status') != 1:
            logging.error(f"Помилка відправки капчі: {result.get('error_text')}")
            return None
        
        captcha_id = result.get('request')
        
        # Очікування розв'язання
        for attempt in range(60):  # 5 хвилин максимум
            time.sleep(5)
            
            result_response = requests.get(self.services['2captcha']['result_url'], params={
                'key': self.api_key,
                'action': 'get',
                'id': captcha_id,
                'json': 1
            })
            
            result = result_response.json()
            
            if result.get('status') == 1:
                return result.get('request')
            elif result.get('error_text') == 'CAPCHA_NOT_READY':
                continue
            else:
                logging.error(f"Помилка отримання результату: {result.get('error_text')}")
                return None
        
        return None
    
    def solve_funcaptcha(self, public_key: str, page_url: str) -> Optional[str]:
        """Розв'язання FunCAPTCHA"""
        if not self.api_key:
            return None
        
        # Аналогічна логіка для FunCAPTCHA
        pass


class AccountManager:
    """Розширений менеджер акаунтів"""
    
    def __init__(self):
        self.accounts = {}
        self.session_data_file = 'account_sessions.json'
        self.load_accounts()
    
    def add_account(self, username: str, password: str, proxy: str = None):
        """Додавання акаунту з розширеними налаштуваннями"""
        self.accounts[username] = {
            'password': password,
            'proxy': proxy,
            'last_activity': None,
            'actions_count': 0,
            'daily_limit': 80,
            'status': 'active',
            'errors_count': 0,
            'last_error': None,
            'session_cookies': None,
            'user_agent': None,
            'created_at': datetime.now().isoformat(),
            'total_actions': 0,
            'shadowban_check': None,
            'rate_limit_reset': None,
            'last_successful_action': None
        }
        self.save_accounts()
    
    def update_account_activity(self, username: str, action_type: str, success: bool):
        """Оновлення активності акаунту"""
        if username not in self.accounts:
            return
        
        account = self.accounts[username]
        account['last_activity'] = datetime.now().isoformat()
        
        if success:
            account['actions_count'] += 1
            account['total_actions'] += 1
            account['last_successful_action'] = datetime.now().isoformat()
            account['errors_count'] = 0  # Скидання лічильника помилок
        else:
            account['errors_count'] += 1
            account['last_error'] = {
                'timestamp': datetime.now().isoformat(),
                'action_type': action_type
            }
        
        # Перевірка на необхідність блокування акаунту
        if account['errors_count'] >= 3:
            account['status'] = 'error_limit'
            logging.warning(f"Акаунт {username} заблоковано через кількість помилок")
        
        self.save_accounts()
    
    def is_account_available(self, username: str) -> bool:
        """Розширена перевірка доступності акаунту"""
        account = self.accounts.get(username)
        if not account:
            return False
        
        # Перевірка статусу
        if account['status'] in ['banned', 'shadowban', 'suspended', 'error_limit']:
            return False
        
        # Перевірка денних лімітів
        if account['actions_count'] >= account['daily_limit']:
            return False
        
        # Перевірка rate limit
        if account.get('rate_limit_reset'):
            reset_time = datetime.fromisoformat(account['rate_limit_reset'])
            if datetime.now() < reset_time:
                return False
        
        # Перевірка останньої помилки (кулдаун)
        if account.get('last_error'):
            last_error_time = datetime.fromisoformat(account['last_error']['timestamp'])
            if datetime.now() - last_error_time < timedelta(minutes=30):
                return False
        
        return True
    
    def set_rate_limit(self, username: str, duration_minutes: int = 60):
        """Встановлення rate limit для акаунту"""
        if username in self.accounts:
            reset_time = datetime.now() + timedelta(minutes=duration_minutes)
            self.accounts[username]['rate_limit_reset'] = reset_time.isoformat()
            self.save_accounts()
    
    def save_session_data(self, username: str, cookies: list, user_agent: str):
        """Збереження даних сесії"""
        if username in self.accounts:
            self.accounts[username]['session_cookies'] = cookies
            self.accounts[username]['user_agent'] = user_agent
            self.save_accounts()
    
    def get_session_data(self, username: str) -> Tuple[Optional[list], Optional[str]]:
        """Отримання даних сесії"""
        account = self.accounts.get(username, {})
        return account.get('session_cookies'), account.get('user_agent')
    
    def save_accounts(self):
        """Збереження акаунтів з backup"""
        try:
            # Створення backup
            if os.path.exists(self.session_data_file):
                backup_file = f"{self.session_data_file}.backup"
                with open(self.session_data_file, 'r') as f:
                    with open(backup_file, 'w') as bf:
                        bf.write(f.read())
            
            # Збереження нових даних
            with open(self.session_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Помилка збереження акаунтів: {e}")
    
    def load_accounts(self):
        """Завантаження акаунтів з відновленням"""
        try:
            if os.path.exists(self.session_data_file):
                with open(self.session_data_file, 'r', encoding='utf-8') as f:
                    self.accounts = json.load(f)
            else:
                self.accounts = {}
        except Exception as e:
            logging.error(f"Помилка завантаження акаунтів: {e}")
            # Спроба відновлення з backup
            backup_file = f"{self.session_data_file}.backup"
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        self.accounts = json.load(f)
                    logging.info("Акаунти відновлено з backup")
                except:
                    self.accounts = {}
            else:
                self.accounts = {}
    
    def reset_daily_limits(self):
        """Скидання денних лімітів для всіх акаунтів"""
        for username in self.accounts:
            self.accounts[username]['actions_count'] = 0
            # Скидання статусу error_limit якщо минув час
            if self.accounts[username]['status'] == 'error_limit':
                self.accounts[username]['status'] = 'active'
                self.accounts[username]['errors_count'] = 0
        self.save_accounts()


class InstagramBot:
    """Розширений Instagram Bot з повним обходом захисту"""
    
    def __init__(self, captcha_api_key: str = None):
        self.anti_detection = AntiDetectionManager()
        self.captcha_solver = CaptchaSolver(captcha_api_key)
        self.account_manager = AccountManager()
        self.drivers = {}
        self.popup_handlers = {}
        
        # Налаштування логування
        self.setup_logging()
        
        # Конфігурація затримок
        self.action_delays = {
            'like': (2, 5),
            'comment': (3, 8),
            'story_view': (1, 3),
            'story_reply': (2, 6),
            'direct_message': (5, 12),
            'page_load': (3, 7),
            'between_actions': (8, 15)
        }
        
        # Повідомлення
        self.story_replies = [
            "🔥🔥🔥", "❤️", "Круто!", "👍", "Супер!", "💯", "🙌", 
            "Класно!", "👏", "Wow!", "Дуже цікаво!", "Топ контент!", 
            "Красиво!", "😍", "🤩", "💪", "✨", "🎉", "👌"
        ]
        
        self.direct_messages = [
            "Привіт! Як справи? 😊",
            "Вітаю! Сподобався ваш контент 👍",
            "Доброго дня! Цікавий профіль ✨",
            "Привіт! Круті пости у вас ❤️",
            "Вітаю! Дякую за натхнення 🙌",
            "Привіт! Чудовий контент 🔥",
            "Вітаю! Дуже цікаво 💯"
        ]
    
    def setup_logging(self):
        """Налаштування логування"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('instagram_bot.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def create_driver(self, username: str) -> webdriver.Chrome:
        """Створення undetected Chrome driver"""
        try:
            # Отримання збережених налаштувань
            cookies, saved_user_agent = self.account_manager.get_session_data(username)
            
            # Налаштування Chrome
            options = uc.ChromeOptions()
            
            # Мобільна емуляція
            width, height = self.anti_detection.get_random_resolution()
            user_agent = saved_user_agent or self.anti_detection.get_random_user_agent()
            
            mobile_emulation = {
                "deviceMetrics": {
                    "width": width,
                    "height": height,
                    "pixelRatio": random.uniform(2.0, 3.0)
                },
                "userAgent": user_agent
            }
            
            options.add_experimental_option("mobileEmulation", mobile_emulation)
            
            # Додаткові налаштування для обходу детекції
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")  # Прискорення завантаження
            
            # Налаштування проксі
            account_info = self.account_manager.accounts.get(username, {})
            if account_info.get('proxy'):
                proxy = account_info['proxy']
                if ':' in proxy:
                    options.add_argument(f"--proxy-server={proxy}")
            
            # Створення драйвера
            driver = uc.Chrome(options=options, version_main=None)
            
            # Додаткові настройки для обходу детекції
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['uk-UA', 'uk', 'en-US', 'en']})")
            
            # Встановлення розміру вікна
            driver.set_window_size(width, height)
            
            # Відновлення cookies якщо є
            if cookies:
                driver.get("https://www.instagram.com")
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
            
            # Збереження user agent
            self.account_manager.save_session_data(username, [], user_agent)
            
            return driver
            
        except Exception as e:
            logging.error(f"Помилка створення драйвера для {username}: {e}")
            raise
    
    def login_account(self, username: str) -> bool:
        """Вхід в акаунт з обходом усіх захистів"""
        try:
            if username in self.drivers:
                return True
            
            account_info = self.account_manager.accounts.get(username)
            if not account_info:
                logging.error(f"Акаунт {username} не знайдено")
                return False
            
            if not self.account_manager.is_account_available(username):
                logging.warning(f"Акаунт {username} недоступний")
                return False
            
            logging.info(f"Початок входу в акаунт {username}")
            
            # Створення драйвера
            driver = self.create_driver(username)
            self.drivers[username] = driver
            
            # Створення обробника popup'ів
            popup_handler = PopupHandler(driver)
            self.popup_handlers[username] = popup_handler
            
            # Перехід на сторінку входу
            driver.get("https://www.instagram.com/accounts/login/")
            self.anti_detection.human_like_delay(3, 6)
            
            # Обробка popup'ів
            popup_handler.handle_all_popups()
            
            # Очікування форми входу
            wait = WebDriverWait(driver, 15)
            
            # Введення логіна
            username_field = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            self.human_type(username_field, username)
            
            # Введення пароля
            password_field = driver.find_element(By.NAME, "password")
            self.human_type(password_field, account_info['password'])
            
            # Випадкова затримка перед входом
            self.anti_detection.human_like_delay(1, 3)
            
            # Натискання кнопки входу
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            self.anti_detection.human_mouse_movement(driver, login_button)
            login_button.click()
            
            # Очікування результату входу
            self.anti_detection.human_like_delay(5, 8)
            
            # Обробка викликів після входу
            if self.handle_post_login_challenges(driver, username):
                # Збереження cookies
                cookies = driver.get_cookies()
                user_agent = driver.execute_script("return navigator.userAgent")
                self.account_manager.save_session_data(username, cookies, user_agent)
                
                logging.info(f"✅ Успішний вхід для {username}")
                self.account_manager.update_account_activity(username, 'login', True)
                return True
            else:
                logging.error(f"❌ Помилка входу для {username}")
                self.account_manager.update_account_activity(username, 'login', False)
                return False
                
        except Exception as e:
            logging.error(f"Критична помилка входу для {username}: {e}")
            self.account_manager.update_account_activity(username, 'login', False)
            return False
    
    def handle_post_login_challenges(self, driver, username: str) -> bool:
        """Обробка викликів після входу"""
        try:
            wait = WebDriverWait(driver, 10)
            popup_handler = self.popup_handlers[username]
            
            # Обробка всіх popup'ів
            popup_handler.handle_all_popups()
            
            # Перевірка на капчу
            if self.detect_and_solve_captcha(driver):
                logging.info(f"Капча розв'язана для {username}")
            
            # Перевірка на двофакторну аутентифікацію
            if self.detect_2fa(driver):
                logging.warning(f"Потрібна 2FA для {username}")
                return False
            
            # Перевірка на підозрілу активність
            if self.detect_suspicious_activity(driver):
                logging.warning(f"Підозріла активність для {username}")
                return False
            
            # Перевірка успішного входу
            try:
                # Очікування головної сторінки
                wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='mobile-nav-logged-in']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "nav[role='navigation']")),
                        EC.url_contains("instagram.com/")
                    )
                )
                return True
            except TimeoutException:
                return False
                
        except Exception as e:
            logging.error(f"Помилка обробки викликів для {username}: {e}")
            return False
    
    def detect_and_solve_captcha(self, driver) -> bool:
        """Детекція та розв'язання капчі"""
        try:
            # Пошук reCAPTCHA
            recaptcha_selectors = [
                "[data-sitekey]",
                ".g-recaptcha",
                "#recaptcha",
                "iframe[src*='recaptcha']"
            ]
            
            for selector in recaptcha_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    site_key = element.get_attribute("data-sitekey")
                    if site_key:
                        solution = self.captcha_solver.solve_recaptcha(site_key, driver.current_url)
                        if solution:
                            # Введення розв'язку
                            driver.execute_script(
                                f"document.getElementById('g-recaptcha-response').innerHTML='{solution}';"
                            )
                            return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception as e:
            logging.error(f"Помилка розв'язання капчі: {e}")
            return False
    
    def detect_2fa(self, driver) -> bool:
        """Детекція двофакторної аутентифікації"""
        selectors_2fa = [
            "input[name='verificationCode']",
            "input[placeholder*='security code']",
            "input[aria-label*='Security Code']",
            "[data-testid='login-form'] input[maxlength='6']"
        ]
        
        for selector in selectors_2fa:
            try:
                driver.find_element(By.CSS_SELECTOR, selector)
                return True
            except NoSuchElementException:
                continue
        
        return False
    
    def detect_suspicious_activity(self, driver) -> bool:
        """Детекція підозрілої активності"""
        suspicious_indicators = [
            "suspicious activity",
            "unusual activity", 
            "temporarily blocked",
            "account restricted",
            "verify your identity",
            "підозріла активність",
            "незвичайна активність"
        ]
        
        page_source = driver.page_source.lower()
        return any(indicator in page_source for indicator in suspicious_indicators)
    
    def human_type(self, element, text: str):
        """Імітація людського введення тексту"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.25))
        
        # Випадкове виправлення помилок
        if random.random() < 0.1:  # 10% шанс "помилки"
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.1, 0.3))
            element.send_keys(text[-1])
    
    def navigate_to_profile(self, driver, username: str, target_username: str) -> bool:
        """Навігація до профілю користувача"""
        try:
            url = f"https://www.instagram.com/{target_username}/"
            driver.get(url)
            
            # Очікування завантаження профілю
            wait = WebDriverWait(driver, 10)
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "main[role='main']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='user-avatar']"))
                )
            )
            
            # Обробка popup'ів
            self.popup_handlers[username].handle_all_popups()
            
            # Перевірка чи профіль існує
            if "page not found" in driver.page_source.lower() or "користувача не знайдено" in driver.page_source.lower():
                logging.warning(f"Профіль {target_username} не знайдено")
                return False
            
            # Перевірка чи профіль приватний
            if self.is_private_profile(driver):
                logging.info(f"Профіль {target_username} приватний")
                return False
            
            self.anti_detection.human_like_delay(2, 4)
            return True
            
        except Exception as e:
            logging.error(f"Помилка навігації до профілю {target_username}: {e}")
            return False
    
    def is_private_profile(self, driver) -> bool:
        """Перевірка чи профіль приватний"""
        private_indicators = [
            "This Account is Private",
            "Цей акаунт приватний",
            "[data-testid='private-account-icon']",
            "svg[aria-label*='private']"
        ]
        
        page_source = driver.page_source
        for indicator in private_indicators:
            if indicator.lower() in page_source.lower():
                return True
            
            try:
                driver.find_element(By.CSS_SELECTOR, indicator)
                return True
            except NoSuchElementException:
                continue
        
        return False
    
    def like_last_posts(self, username: str, target_username: str, count: int = 2) -> bool:
        """Лайк останніх постів користувача"""
        try:
            if not self.login_account(username):
                return False
            
            driver = self.drivers[username]
            logging.info(f"🔍 Лайк постів {target_username} від {username}")
            
            # Навігація до профілю
            if not self.navigate_to_profile(driver, username, target_username):
                return False
            
            # Пошук постів
            post_selectors = [
                "article a[href*='/p/']",
                "[data-testid='post-preview'] a",
                "a[role='link'][href*='/p/']"
            ]
            
            posts = []
            for selector in post_selectors:
                try:
                    posts = driver.find_elements(By.CSS_SELECTOR, selector)[:count]
                    if posts:
                        break
                except:
                    continue
            
            if not posts:
                logging.warning(f"Пости не знайдено у {target_username}")
                return False
            
            liked_count = 0
            for i, post in enumerate(posts):
                try:
                    # Випадкове прокручування
                    if i > 0:
                        self.anti_detection.random_scroll(driver)
                    
                    # Відкриття поста
                    self.anti_detection.human_mouse_movement(driver, post)
                    post.click()
                    
                    self.anti_detection.human_like_delay(2, 4)
                    
                    # Пошук кнопки лайка
                    like_selectors = [
                        "svg[aria-label='Like']",
                        "svg[aria-label='Уподобати']",
                        "[data-testid='like-button']",
                        "button svg[aria-label*='ike']"
                    ]
                    
                    like_button = None
                    for selector in like_selectors:
                        try:
                            like_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            break
                        except:
                            continue
                    
                    if like_button:
                        # Перевірка чи пост вже лайкнутий
                        if not self.is_post_already_liked(driver):
                            self.anti_detection.human_mouse_movement(driver, like_button)
                            like_button.click()
                            
                            liked_count += 1
                            logging.info(f"❤️ Лайк поста {i+1} у {target_username}")
                            self.account_manager.update_account_activity(username, 'like_post', True)
                            
                            # Затримка між лайками
                            delay = random.uniform(*self.action_delays['like'])
                            time.sleep(delay)
                        else:
                            logging.info(f"Post {i+1} already liked")
                    
                    # Закриття поста
                    close_selectors = [
                        "svg[aria-label='Close']",
                        "svg[aria-label='Закрити']",
                        "[data-testid='modal-close-button']"
                    ]
                    
                    for selector in close_selectors:
                        try:
                            close_button = driver.find_element(By.CSS_SELECTOR, selector)
                            close_button.click()
                            break
                        except:
                            continue
                    else:
                        # Якщо кнопка закриття не знайдена, використовуємо ESC
                        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    
                    self.anti_detection.human_like_delay(1, 3)
                    
                except Exception as e:
                    logging.error(f"Помилка лайка поста {i+1}: {e}")
                    self.account_manager.update_account_activity(username, 'like_post', False)
                    continue
            
            logging.info(f"✅ Лайкнуто {liked_count} постів у {target_username}")
            return liked_count > 0
            
        except Exception as e:
            logging.error(f"Помилка лайка постів {target_username}: {e}")
            return False
    
    def is_post_already_liked(self, driver) -> bool:
        """Перевірка чи пост вже лайкнутий"""
        liked_selectors = [
            "svg[aria-label='Unlike']",
            "svg[aria-label='Не вподобати']",
            "svg[fill='#ed4956']",  # Червоний колір лайка
        ]
        
        for selector in liked_selectors:
            try:
                driver.find_element(By.CSS_SELECTOR, selector)
                return True
            except NoSuchElementException:
                continue
        
        return False
    
    def view_and_like_stories(self, username: str, target_username: str) -> bool:
        """Перегляд та лайк сторіс"""
        try:
            if not self.login_account(username):
                return False
            
            driver = self.drivers[username]
            logging.info(f"📖 Перегляд сторіс {target_username} від {username}")
            
            # Перехід на головну сторінку для сторіс
            driver.get("https://www.instagram.com/")
            self.anti_detection.human_like_delay(3, 5)
            
            # Обробка popup'ів
            self.popup_handlers[username].handle_all_popups()
            
            # Пошук сторіс користувача
            story_selectors = [
                f"img[alt*='{target_username}']",
                f"canvas[aria-label*='{target_username}']",
                f"[data-testid='user-avatar'][alt*='{target_username}']"
            ]
            
            story_element = None
            for selector in story_selectors:
                try:
                    stories = driver.find_elements(By.CSS_SELECTOR, selector)
                    for story in stories:
                        if target_username.lower() in story.get_attribute('alt').lower():
                            story_element = story
                            break
                    if story_element:
                        break
                except:
                    continue
            
            if not story_element:
                logging.info(f"Сторіс {target_username} не знайдено")
                return False
            
            # Відкриття сторіс
            self.anti_detection.human_mouse_movement(driver, story_element)
            story_element.click()
            self.anti_detection.human_like_delay(2, 4)
            
            stories_viewed = 0
            max_stories = 5  # Максимум сторіс для перегляду
            
            for story_num in range(max_stories):
                try:
                    # Очікування завантаження сторіс
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "video, img"))
                    )
                    
                    # Лайк сторіс
                    like_selectors = [
                        "svg[aria-label='Like']",
                        "[data-testid='story-like-button']",
                        "button svg[aria-label*='ike']"
                    ]
                    
                    for selector in like_selectors:
                        try:
                            like_button = driver.find_element(By.CSS_SELECTOR, selector)
                            if like_button.is_displayed():
                                self.anti_detection.human_mouse_movement(driver, like_button)
                                like_button.click()
                                logging.info(f"❤️ Лайк сторіс {story_num + 1} у {target_username}")
                                self.account_manager.update_account_activity(username, 'like_story', True)
                                break
                        except:
                            continue
                    
                    stories_viewed += 1
                    
                    # Затримка перегляду сторіс
                    view_delay = random.uniform(*self.action_delays['story_view'])
                    time.sleep(view_delay)
                    
                    # Перехід до наступної сторіс або вихід
                    try:
                        # Пошук кнопки "Далі"
                        next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
                        next_button.click()
                        self.anti_detection.human_like_delay(1, 2)
                    except:
                        # Якщо кнопки немає, виходимо
                        break
                
                except Exception as e:
                    logging.error(f"Помилка перегляду сторіс {story_num + 1}: {e}")
                    break
            
            # Закриття сторіс
            try:
                close_selectors = [
                    "svg[aria-label='Close']",
                    "[data-testid='story-close-button']"
                ]
                
                for selector in close_selectors:
                    try:
                        close_button = driver.find_element(By.CSS_SELECTOR, selector)
                        close_button.click()
                        break
                    except:
                        continue
                else:
                    # ESC як fallback
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            except:
                pass
            
            logging.info(f"✅ Переглянуто {stories_viewed} сторіс у {target_username}")
            return stories_viewed > 0
            
        except Exception as e:
            logging.error(f"Помилка перегляду сторіс {target_username}: {e}")
            return False
    
    def reply_to_stories(self, username: str, target_username: str, messages: List[str] = None) -> bool:
        """Відповідь на сторіс"""
        try:
            if not self.login_account(username):
                return False
            
            driver = self.drivers[username]
            logging.info(f"💬 Відповідь на сторіс {target_username} від {username}")
            
            # Використання переданих повідомлень або стандартних
            reply_messages = messages or self.story_replies
            
            # Перехід на головну сторінку
            driver.get("https://www.instagram.com/")
            self.anti_detection.human_like_delay(3, 5)
            
            # Пошук сторіс
            story_selectors = [
                f"img[alt*='{target_username}']",
                f"canvas[aria-label*='{target_username}']"
            ]
            
            story_element = None
            for selector in story_selectors:
                try:
                    stories = driver.find_elements(By.CSS_SELECTOR, selector)
                    for story in stories:
                        if target_username.lower() in story.get_attribute('alt').lower():
                            story_element = story
                            break
                    if story_element:
                        break
                except:
                    continue
            
            if not story_element:
                logging.info(f"Сторіс {target_username} не знайдено для відповіді")
                return False
            
            # Відкриття сторіс
            story_element.click()
            self.anti_detection.human_like_delay(2, 4)
            
            # Пошук поля для відповіді
            reply_selectors = [
                "textarea[placeholder*='Send message']",
                "textarea[placeholder*='Reply']",
                "input[placeholder*='Send message']",
                "[data-testid='story-reply-input']"
            ]
            
            reply_field = None
            for selector in reply_selectors:
                try:
                    reply_field = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not reply_field:
                logging.warning(f"Поле для відповіді не знайдено у {target_username}")
                return False
            
            # Вибір випадкового повідомлення
            message = random.choice(reply_messages)
            
            # Введення повідомлення
            self.anti_detection.human_mouse_movement(driver, reply_field)
            reply_field.click()
            self.human_type(reply_field, message)
            
            # Затримка перед відправкою
            self.anti_detection.human_like_delay(1, 3)
            
            # Відправка повідомлення
            send_selectors = [
                "button[type='submit']",
                "button[aria-label='Send']",
                "[data-testid='story-reply-send-button']"
            ]
            
            for selector in send_selectors:
                try:
                    send_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if send_button.is_enabled():
                        send_button.click()
                        break
                except:
                    continue
            else:
                # Використання Enter як fallback
                reply_field.send_keys(Keys.RETURN)
            
            logging.info(f"💬 Відповідь на сторіс {target_username}: '{message}'")
            self.account_manager.update_account_activity(username, 'story_reply', True)
            
            # Закриття сторіс
            time.sleep(2)
            try:
                close_button = driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Close']")
                close_button.click()
            except:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            
            return True
            
        except Exception as e:
            logging.error(f"Помилка відповіді на сторіс {target_username}: {e}")
            self.account_manager.update_account_activity(username, 'story_reply', False)
            return False
    
    def send_direct_message(self, username: str, target_username: str, messages: List[str] = None) -> bool:
        """Відправка прямого повідомлення"""
        try:
            if not self.login_account(username):
                return False
            
            driver = self.drivers[username]
            logging.info(f"📩 Відправка DM {target_username} від {username}")
            
            # Використання переданих повідомлень або стандартних
            dm_messages = messages or self.direct_messages
            
            # Перехід до директ повідомлень
            driver.get("https://www.instagram.com/direct/inbox/")
            self.anti_detection.human_like_delay(3, 5)
            
            # Обробка popup'ів
            self.popup_handlers[username].handle_all_popups()
            
            # Пошук кнопки "New Message"
            new_message_selectors = [
                "svg[aria-label*='New message']",
                "[data-testid='new-message-button']",
                "a[href='/direct/new/']"
            ]
            
            new_message_button = None
            for selector in new_message_selectors:
                try:
                    new_message_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not new_message_button:
                logging.warning("Кнопка нового повідомлення не знайдена")
                return False
            
            # Відкриття нового повідомлення
            new_message_button.click()
            self.anti_detection.human_like_delay(2, 4)
            
            # Пошук поля для введення користувача
            search_selectors = [
                "input[placeholder*='Search']",
                "input[name='queryBox']",
                "[data-testid='user-search-input']"
            ]
            
            search_field = None
            for selector in search_selectors:
                try:
                    search_field = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not search_field:
                logging.warning("Поле пошуку користувача не знайдено")
                return False
            
            # Введення імені користувача
            self.human_type(search_field, target_username)
            self.anti_detection.human_like_delay(2, 4)
            
            # Вибір користувача зі списку
            user_selectors = [
                f"[title='{target_username}']",
                f"span:contains('{target_username}')",
                "[data-testid='user-search-result']"
            ]
            
            user_found = False
            for selector in user_selectors:
                try:
                    if "contains" in selector:
                        # XPath selector
                        user_element = driver.find_element(By.XPATH, f"//span[contains(text(), '{target_username}')]")
                    else:
                        user_element = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    user_element.click()
                    user_found = True
                    break
                except:
                    continue
            
            if not user_found:
                logging.warning(f"Користувач {target_username} не знайдений у пошуку")
                return False
            
            # Натискання "Next" або "Chat"
            next_selectors = [
                "button:contains('Next')",
                "button:contains('Chat')",
                "[data-testid='next-button']"
            ]
            
            for selector in next_selectors:
                try:
                    if "contains" in selector:
                        next_button = driver.find_element(By.XPATH, f"//button[contains(text(), 'Next') or contains(text(), 'Chat')]")
                    else:
                        next_button = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    next_button.click()
                    break
                except:
                    continue
            
            self.anti_detection.human_like_delay(2, 4)
            
            # Пошук поля для повідомлення
            message_selectors = [
                "textarea[placeholder*='Message']",
                "[data-testid='message-input']",
                "div[contenteditable='true']"
            ]
            
            message_field = None
            for selector in message_selectors:
                try:
                    message_field = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not message_field:
                logging.warning("Поле для повідомлення не знайдено")
                return False
            
            # Вибір та введення повідомлення
            message = random.choice(dm_messages)
            
            message_field.click()
            if message_field.tag_name == "div":
                # Для contenteditable div
                message_field.send_keys(message)
            else:
                # Для textarea
                self.human_type(message_field, message)
            
            # Затримка перед відправкою
            self.anti_detection.human_like_delay(2, 4)
            
            # Відправка повідомлення
            send_selectors = [
                "button[type='submit']",
                "button:contains('Send')",
                "[data-testid='send-button']"
            ]
            
            for selector in send_selectors:
                try:
                    if "contains" in selector:
                        send_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send')]")
                    else:
                        send_button = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if send_button.is_enabled():
                        send_button.click()
                        break
                except:
                    continue
            else:
                # Enter як fallback
                message_field.send_keys(Keys.RETURN)
            
            logging.info(f"📩 DM відправлено {target_username}: '{message}'")
            self.account_manager.update_account_activity(username, 'direct_message', True)
            
            return True
            
        except Exception as e:
            logging.error(f"Помилка відправки DM {target_username}: {e}")
            self.account_manager.update_account_activity(username, 'direct_message', False)
            return False
    
    def run_automation(self, config: Dict):
        """Запуск повної автоматизації"""
        try:
            accounts = config.get('accounts', [])
            targets = config.get('targets', [])
            actions = config.get('actions', {})
            story_messages = config.get('story_messages', [])
            direct_messages = config.get('direct_messages', [])
            
            logging.info(f"🚀 Запуск автоматизації: {len(accounts)} акаунтів, {len(targets)} цілей")
            
            total_actions = 0
            successful_actions = 0
            
            for account_info in accounts:
                username = account_info['username']
                
                if not self.account_manager.is_account_available(username):
                    logging.warning(f"⚠️ Акаунт {username} недоступний, пропускаємо")
                    continue
                
                logging.info(f"👤 Робота з акаунтом {username}")
                
                for target in targets:
                    try:
                        # Перевірка лімітів
                        account_data = self.account_manager.accounts.get(username, {})
                        if account_data.get('actions_count', 0) >= account_data.get('daily_limit', 80):
                            logging.warning(f"📊 Досягнуто денний ліміт для {username}")
                            break
                        
                        logging.info(f"🎯 Обробка цілі: {target}")
                        
                        # Лайк останніх постів
                        if actions.get('like_posts', False):
                            if self.like_last_posts(username, target, 2):
                                successful_actions += 1
                            total_actions += 1
                            
                            # Затримка між діями
                            delay = random.uniform(*self.action_delays['between_actions'])
                            time.sleep(delay)
                        
                        # Перегляд та лайк сторіс
                        if actions.get('like_stories', False):
                            if self.view_and_like_stories(username, target):
                                successful_actions += 1
                            total_actions += 1
                            
                            delay = random.uniform(*self.action_delays['between_actions'])
                            time.sleep(delay)
                        
                        # Відповідь на сторіс
                        if actions.get('reply_stories', False):
                            if self.reply_to_stories(username, target, story_messages):
                                successful_actions += 1
                            total_actions += 1
                            
                            delay = random.uniform(*self.action_delays['between_actions'])
                            time.sleep(delay)
                        
                        # Відправка DM якщо немає сторіс
                        if actions.get('send_dm_if_no_stories', False):
                            # Спочатку перевіряємо чи є сторіс
                            driver = self.drivers.get(username)
                            if driver:
                                driver.get("https://www.instagram.com/")
                                self.anti_detection.human_like_delay(2, 4)
                                
                                # Пошук сторіс
                                has_stories = False
                                try:
                                    story_elements = driver.find_elements(By.CSS_SELECTOR, f"img[alt*='{target}']")
                                    has_stories = len(story_elements) > 0
                                except:
                                    pass
                                
                                if not has_stories:
                                    if self.send_direct_message(username, target, direct_messages):
                                        successful_actions += 1
                                    total_actions += 1
                        
                        # Випадковий скрол та пауза
                        if username in self.drivers:
                            self.anti_detection.random_scroll(self.drivers[username])
                        
                        # Затримка між цілями
                        target_delay = random.uniform(15, 45)
                        logging.info(f"⏱️ Пауза {target_delay:.1f}с між цілями")
                        time.sleep(target_delay)
                        
                    except Exception as e:
                        logging.error(f"❌ Помилка обробки цілі {target}: {e}")
                        self.account_manager.update_account_activity(username, 'error', False)
                        continue
                
                # Затримка між акаунтами
                account_delay = random.uniform(120, 300)  # 2-5 хвилин
                logging.info(f"⏱️ Пауза {account_delay/60:.1f} хв між акаунтами")
                time.sleep(account_delay)
            
            # Підсумки
            success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0
            logging.info(f"✅ Автоматизація завершена: {successful_actions}/{total_actions} ({success_rate:.1f}%)")
            
        except Exception as e:
            logging.error(f"❌ Критична помилка автоматизації: {e}")
        finally:
            # Закриття всіх драйверів
            self.close_all_drivers()
    
    def monitor_account_health(self, username: str):
        """Моніторинг стану акаунту"""
        try:
            if username not in self.drivers:
                return
            
            driver = self.drivers[username]
            
            # Перевірка на повідомлення про обмеження
            restriction_indicators = [
                "your account has been restricted",
                "temporarily blocked",
                "unusual activity detected",
                "violating community guidelines",
                "action blocked",
                "try again later"
            ]
            
            page_source = driver.page_source.lower()
            for indicator in restriction_indicators:
                if indicator in page_source:
                    self.account_manager.accounts[username]['status'] = 'restricted'
                    logging.warning(f"⚠️ Акаунт {username} обмежений: {indicator}")
                    return
            
            # Перевірка shadowban
            if self.detect_shadowban(driver, username):
                self.account_manager.accounts[username]['status'] = 'shadowban'
                logging.warning(f"👻 Shadowban виявлено для {username}")
            
            # Перевірка rate limiting
            if self.detect_rate_limiting(driver):
                self.account_manager.set_rate_limit(username, 120)  # 2 години
                logging.warning(f"🚦 Rate limit для {username}")
            
        except Exception as e:
            logging.error(f"Помилка моніторингу {username}: {e}")
    
    def detect_shadowban(self, driver, username: str) -> bool:
        """Детекція shadowban"""
        try:
            # Перехід на власний профіль
            driver.get(f"https://www.instagram.com/{username}/")
            self.anti_detection.human_like_delay(3, 5)
            
            # Перевірка видимості постів у хештегах
            # Це спрощена перевірка, в реальності потрібна більш складна логіка
            return False
            
        except Exception as e:
            logging.error(f"Помилка детекції shadowban для {username}: {e}")
            return False
    
    def detect_rate_limiting(self, driver) -> bool:
        """Детекція rate limiting"""
        rate_limit_indicators = [
            "try again later",
            "action blocked",
            "we limit how often",
            "please wait a few minutes"
        ]
        
        page_source = driver.page_source.lower()
        return any(indicator in page_source for indicator in rate_limit_indicators)
    
    def close_driver(self, username: str):
        """Закриття драйвера для конкретного акаунту"""
        if username in self.drivers:
            try:
                self.drivers[username].quit()
                del self.drivers[username]
                if username in self.popup_handlers:
                    del self.popup_handlers[username]
                logging.info(f"🔒 Драйвер для {username} закрито")
            except Exception as e:
                logging.error(f"Помилка закриття драйвера {username}: {e}")
    
    def close_all_drivers(self):
        """Закриття всіх драйверів"""
        for username in list(self.drivers.keys()):
            self.close_driver(username)
        
        logging.info("🔒 Всі драйвери закрито")
    
    def get_account_statistics(self) -> Dict:
        """Отримання статистики всіх акаунтів"""
        stats = {
            'total_accounts': len(self.account_manager.accounts),
            'active_accounts': 0,
            'restricted_accounts': 0,
            'total_actions_today': 0,
            'accounts_details': []
        }
        
        for username, account in self.account_manager.accounts.items():
            if account['status'] == 'active':
                stats['active_accounts'] += 1
            elif account['status'] in ['restricted', 'shadowban', 'banned']:
                stats['restricted_accounts'] += 1
            
            stats['total_actions_today'] += account.get('actions_count', 0)
            
            stats['accounts_details'].append({
                'username': username,
                'status': account['status'],
                'actions_today': account.get('actions_count', 0),
                'total_actions': account.get('total_actions', 0),
                'last_activity': account.get('last_activity'),
                'errors_count': account.get('errors_count', 0)
            })
        
        return stats
    
    def export_session_data(self, username: str) -> Dict:
        """Експорт даних сесії для відновлення"""
        if username not in self.drivers:
            return {}
        
        try:
            driver = self.drivers[username]
            return {
                'cookies': driver.get_cookies(),
                'user_agent': driver.execute_script("return navigator.userAgent"),
                'local_storage': driver.execute_script("return localStorage"),
                'session_storage': driver.execute_script("return sessionStorage"),
                'current_url': driver.current_url
            }
        except Exception as e:
            logging.error(f"Помилка експорту сесії {username}: {e}")
            return {}
    
    def restore_session_data(self, username: str, session_data: Dict) -> bool:
        """Відновлення даних сесії"""
        try:
            if username not in self.drivers:
                return False
            
            driver = self.drivers[username]
            
            # Відновлення cookies
            if 'cookies' in session_data:
                driver.get("https://www.instagram.com")
                for cookie in session_data['cookies']:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
            
            # Відновлення local storage
            if 'local_storage' in session_data:
                for key, value in session_data['local_storage'].items():
                    try:
                        driver.execute_script(f"localStorage.setItem('{key}', '{value}')")
                    except:
                        pass
            
            # Відновлення session storage
            if 'session_storage' in session_data:
                for key, value in session_data['session_storage'].items():
                    try:
                        driver.execute_script(f"sessionStorage.setItem('{key}', '{value}')")
                    except:
                        pass
            
            return True
            
        except Exception as e:
            logging.error(f"Помилка відновлення сесії {username}: {e}")
            return False
    
    def __del__(self):
        """Деструктор - закриття всіх ресурсів"""
        try:
            self.close_all_drivers()
        except:
            pass