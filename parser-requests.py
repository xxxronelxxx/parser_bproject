#!/usr/bin/env python3
"""
Парсер для novasklad.kz - версия без браузера
Использует requests + BeautifulSoup для парсинга товаров
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json
from urllib.parse import urljoin, urlparse, urlencode, parse_qsl, urlunparse
import os

# Для красивого вывода
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table

console = Console()

class NovaskladParser:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://novasklad.kz"
        
        # Загружаем ссылку на категорию из файла cat.txt
        self.catalog_url = self.load_catalog_url()
        
        # Заголовки для имитации браузера
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://novasklad.kz/sign/'
        }
        
        # Применяем заголовки к сессии
        self.session.headers.update(self.headers)
        
        # Список для хранения товаров
        self.products = []
        
        # Множества и параметры фильтров
        self.visited_pages = set()
        self.seen_product_links = set()
        self.filter_params = {}
        
        # Данные для авторизации
        self.login = "+77025757606"
        self.password = "681660"
    
    def load_catalog_url(self):
        """Загружаем ссылку на категорию из файла cat.txt"""
        try:
            if os.path.exists('cat.txt'):
                with open('cat.txt', 'r', encoding='utf-8') as f:
                    url = f.read().strip()
                    if url:
                        console.print(f"[green]✅ Загружена ссылка на категорию: {url}")
                        return url
                    else:
                        console.print("[yellow]⚠️ Файл cat.txt пустой, используем ссылку по умолчанию")
            else:
                console.print("[yellow]⚠️ Файл cat.txt не найден, создаем с ссылкой по умолчанию")
                # Создаем файл с ссылкой по умолчанию
                default_url = "https://novasklad.kz/catalog/kitchen-mixers/"
                with open('cat.txt', 'w', encoding='utf-8') as f:
                    f.write(default_url)
                console.print(f"[blue]📝 Создан файл cat.txt с ссылкой: {default_url}")
                return default_url
        except Exception as e:
            console.print(f"[red]❌ Ошибка при загрузке cat.txt: {e}")
            # Возвращаем ссылку по умолчанию
            default_url = "https://novasklad.kz/catalog/kitchen-mixers/"
            console.print(f"[blue]📝 Используем ссылку по умолчанию: {default_url}")
            return default_url
        
        # Если что-то пошло не так, возвращаем ссылку по умолчанию
        return "https://novasklad.kz/catalog/kitchen-mixers/"
    
    def test_connection(self):
        """Тестируем подключение к сайту"""
        console.print("[blue]🔍 Тестируем подключение к сайту...")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            if response.status_code == 200:
                console.print(f"[green]✅ Подключение успешно! Статус: {response.status_code}")
                console.print(f"[green]✅ URL: {response.url}")
                return True
            else:
                console.print(f"[yellow]⚠️ Статус ответа: {response.status_code}")
                return False
        except Exception as e:
            console.print(f"[red]❌ Ошибка подключения: {e}")
            return False
    

    
    def get_page_content(self, url, description=""):
        """Получаем содержимое страницы"""
        try:
            console.print(f"[blue]📄 Загружаем страницу: {description}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Проверяем кодировку
            if response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            
            console.print(f"[green]✅ Страница загружена: {len(response.text)} символов")
            

            
            return response.text
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]❌ Ошибка загрузки страницы: {e}")
            return None
    
    def parse_catalog_page(self, html_content):
        """Парсим страницу каталога"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        console.print("[blue]🔍 Ищем товары на странице...")
        
        # Пробуем разные селекторы для товаров
        product_selectors = [
            '.product',
            '.line .product',
            '.item',
            '.product-item',
            '.catalog-item',
            '.goods-item',
            '[class*="product"]',
            '.line'
        ]
        
        found_products = []
        used_selector = None
        
        for selector in product_selectors:
            try:
                elements = soup.select(selector)
                if elements and len(elements) > 0:
                    console.print(f"[green]✅ Найдено товаров с селектором '{selector}': {len(elements)}")
                    found_products = elements
                    used_selector = selector
                    break
            except Exception as e:
                console.print(f"[yellow]⚠️ Ошибка с селектором '{selector}': {e}")
                continue
        
        if not found_products:
            console.print("[yellow]⚠️ Товары не найдены, показываем структуру страницы...")
            
            # Показываем структуру для отладки
            body = soup.find('body')
            if body:
                body_classes = body.get('class', [])
                console.print(f"[blue]Классы body: {body_classes}")
            
            # Ищем все div элементы
            divs = soup.find_all('div')
            console.print(f"[blue]Всего div элементов: {len(divs)}")
            
            # Показываем классы первых div элементов
            for i, div in enumerate(divs[:20]):
                div_class = div.get('class', [])
                if div_class:
                    console.print(f"[blue]Div {i+1}: class='{' '.join(div_class)}'")
            
            return []
        
        console.print(f"[green]📊 Парсим {len(found_products)} товаров...")
        
        # Показываем структуру первого найденного элемента для отладки
        if found_products:
            first_product = found_products[0]
            console.print(f"[blue]🔍 Структура первого элемента '{used_selector}':")
            console.print(f"[blue]   Tag: {first_product.name}")
            console.print(f"[blue]   Classes: {first_product.get('class', [])}")
            console.print(f"[blue]   ID: {first_product.get('id', 'Нет')}")
            
            # Показываем дочерние элементы
            children = first_product.find_all(recursive=False)
            console.print(f"[blue]   Дочерние элементы: {len(children)}")
            for i, child in enumerate(children[:10]):
                console.print(f"[blue]     {i+1}. {child.name}.{' '.join(child.get('class', []))}")
        
        # Локальная дедупликация в пределах одной страницы (по ссылке)
        local_seen_links = set()
        
        for idx, product in enumerate(found_products):
            try:
                console.print(f"[blue]🔍 Парсим товар {idx+1}...")
                product_data = self.parse_product_element(product)
                if product_data:
                    product_link = product_data.get('link')
                    if product_link and product_link in local_seen_links:
                        console.print(f"[yellow]⚠️ Дубликат в рамках страницы пропущен: {product_link}")
                    else:
                        if product_link:
                            local_seen_links.add(product_link)
                        products.append(product_data)
                        console.print(f"[green]✅ Товар {idx+1}: {product_data['name'][:50]}...")
                else:
                    console.print(f"[yellow]⚠️ Товар {idx+1}: не удалось извлечь данные")
                
            except Exception as e:
                console.print(f"[yellow]⚠️ Ошибка парсинга товара {idx+1}: {e}")
                continue
        
        return products
    
    def parse_product_element(self, product_elem):
        """Парсим отдельный товар"""
        try:
            console.print(f"[blue]     🔍 Анализируем структуру товара...")
            
            # Показываем HTML структуру элемента для отладки
            html_preview = str(product_elem)[:500]
            console.print(f"[blue]     HTML (начало): {html_preview}...")
            
            # Название товара
            name = self.extract_text(product_elem, [
                '.title a',
                '.title',
                'h3',
                'h4',
                'a[href*="/catalog/"]',
                'a',
                '.name',
                '.product-name'
            ])
            
            if name:
                console.print(f"[green]     ✅ Название найдено: {name[:50]}...")
            else:
                console.print(f"[yellow]     ⚠️ Название не найдено")
            
            # Ссылка на товар
            link = self.extract_href(product_elem, [
                '.title a',
                'a[href*="/catalog/"]',
                'a'
            ])
            
            if link and not link.startswith('http'):
                link = urljoin(self.base_url, link)
            
            if link:
                console.print(f"[green]     ✅ Ссылка найдена: {link}")
            else:
                console.print(f"[yellow]     ⚠️ Ссылка не найдена")
            
            # Цена
            price = self.extract_text(product_elem, [
                '.price-line .price',
                '.price',
                '[class*="price"]',
                '.cost',
                '.price-value',
                '.price-amount'
            ])
            
            if price:
                console.print(f"[green]     ✅ Цена найдена: {price}")
            else:
                console.print(f"[yellow]     ⚠️ Цена не найдена")
            
            # Статус
            status = self.extract_text(product_elem, [
                '.par.s .v',
                '.status',
                '[class*="status"]',
                '.availability',
                '.stock',
                '.in-stock'
            ])
            
            if status:
                console.print(f"[green]     ✅ Статус найден: {status}")
            else:
                console.print(f"[yellow]     ⚠️ Статус не найден")
            
            # Бренд
            brand = self.extract_text(product_elem, [
                '.par.b .v',
                '.brand',
                '[class*="brand"]',
                '.brandLine',
                '.manufacturer',
                '.vendor'
            ])
            
            if brand:
                console.print(f"[green]     ✅ Бренд найден: {brand}")
            else:
                console.print(f"[yellow]     ⚠️ Бренд не найден")
            
            # Описание
            description = self.extract_text(product_elem, [
                '.description',
                '.desc',
                '.text',
                '[class*="description"]',
                '.product-desc'
            ])
            
            if description:
                console.print(f"[green]     ✅ Описание найдено: {description[:50]}...")
            else:
                console.print(f"[yellow]     ⚠️ Описание не найдено")
            
            # Артикул
            article = self.extract_text(product_elem, [
                '.article',
                '.articleLine',
                '.sku',
                '[class*="article"]',
                '.code',
                '.product-code'
            ])
            
            if article:
                console.print(f"[green]     ✅ Артикул найден: {article}")
            else:
                console.print(f"[yellow]     ⚠️ Артикул не найден")
            
            # Дополнительный артикул из названия
            additional_article = self.extract_article_from_name(name)
            
            # Если название не найдено, пропускаем товар
            if not name or name.strip() == "":
                console.print(f"[red]     ❌ Товар пропущен: нет названия")
                return None
            
            # Создаем словарь с данными
            product_data = {
                'name': name.strip(),
                'link': link,
                'price': price.strip() if price else 'Не указана',
                'status': status.strip() if status else 'Не указан',
                'brand': brand.strip() if brand else 'Не указан',
                'description': description.strip() if description else 'Не указано',
                'article': article.strip() if article else 'Не указан',
                'additional_article': additional_article
            }
            
            console.print(f"[green]     ✅ Товар успешно обработан")
            return product_data
            
        except Exception as e:
            console.print(f"[red]     ❌ Ошибка парсинга элемента: {e}")
            return None
    
    def extract_text(self, element, selectors):
        """Извлекаем текст по разным селекторам"""
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found and found.get_text(strip=True):
                    text = found.get_text(strip=True)
                    if text and len(text) > 0:
                        return text
            except Exception as e:
                console.print(f"[yellow]       ⚠️ Ошибка с селектором '{selector}': {e}")
                continue
        
        # Если селекторы не сработали, пробуем найти любой текст в элементе
        try:
            # Ищем все ссылки
            links = element.find_all('a')
            for link in links:
                text = link.get_text(strip=True)
                if text and len(text) > 0:
                    return text
            
            # Ищем заголовки
            headers = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for header in headers:
                text = header.get_text(strip=True)
                if text and len(text) > 0:
                    return text
            
            # Ищем любой текст в элементе
            text = element.get_text(strip=True)
            if text and len(text) > 0:
                # Убираем лишние пробелы и переносы
                text = ' '.join(text.split())
                if len(text) > 0:
                    return text
                    
        except Exception as e:
            console.print(f"[yellow]       ⚠️ Ошибка при поиске текста: {e}")
        
        return None
    
    def extract_href(self, element, selectors):
        """Извлекаем ссылку по разным селекторам"""
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found and found.get('href'):
                    href = found.get('href')
                    if href and href != '#':
                        return href
            except Exception as e:
                console.print(f"[yellow]       ⚠️ Ошибка с селектором '{selector}': {e}")
                continue
        
        # Если селекторы не сработали, пробуем найти любую ссылку
        try:
            # Ищем все ссылки в элементе
            links = element.find_all('a')
            for link in links:
                href = link.get('href')
                if href and href != '#' and href.startswith('/'):
                    return href
                elif href and href != '#' and 'catalog' in href:
                    return href
                    
        except Exception as e:
            console.print(f"[yellow]       ⚠️ Ошибка при поиске ссылок: {e}")
        
        return None
    
    def extract_article_from_name(self, name):
        """Извлекаем артикул из названия товара"""
        if not name:
            return None
        
        # Ищем артикул в скобках
        match = re.search(r'\((.*?)\)', name)
        if match:
            return match.group(1)
        
        # Ищем артикул в конце названия
        match = re.search(r'(\d{4,})$', name)
        if match:
            return match.group(1)
        
        return None
    
    def get_all_pages(self):
        """Получаем все страницы каталога"""
        console.print("[blue]📚 Получаем все страницы каталога...")
        
        # Проверяем, что мы авторизованы
        console.print("[blue]🔍 Проверяем статус авторизации...")
        try:
            # Пробуем получить главную страницу
            main_page = self.session.get(self.base_url, timeout=30)
            if "Войти" in main_page.text or "login" in main_page.text.lower():
                console.print("[red]❌ Не авторизованы! Нужно сначала войти в систему.")
                return []
            else:
                console.print("[green]✅ Авторизация подтверждена")
        except Exception as e:
            console.print(f"[yellow]⚠️ Не удалось проверить авторизацию: {e}")
        
        # Включаем фильтры 'В пути' и 'Под заказ'
        self.enable_status_filters()
        
        all_products = []
        current_url = self.catalog_url
        max_pages = 100  # Жёсткий предел на всякий случай
        page_number = 1
        
        while current_url and page_number <= max_pages:
            try:
                # Защита от циклов по страницам
                if current_url in self.visited_pages:
                    console.print(f"[yellow]⚠️ Страница уже посещена, останавливаемся: {current_url}")
                    break
                self.visited_pages.add(current_url)
                
                console.print(f"[blue]📄 Страница {page_number}: {current_url}")
                
                # Получаем содержимое страницы
                html_content = self.get_page_content(current_url, f"Страница {page_number}")
                
                if not html_content:
                    console.print(f"[yellow]⚠️ Не удалось загрузить страницу {page_number}")
                    break
                
                # Парсим товары на странице
                page_products = self.parse_catalog_page(html_content)
                
                # Подсчитываем сколько новых добавим
                new_count = 0
                for p in page_products:
                    link = p.get('link')
                    if link and link in self.seen_product_links:
                        continue
                    if link:
                        self.seen_product_links.add(link)
                    all_products.append(p)
                    new_count += 1
                
                console.print(f"[green]✅ Страница {page_number}: добавлено новых {new_count} товаров, всего {len(all_products)}")
                
                # Если на странице не появилось новых товаров, выходим чтобы не зациклиться
                if new_count == 0:
                    console.print("[yellow]⚠️ Нет новых товаров на странице, останавливаемся")
                    break
                
                # Пытаемся определить реальную ссылку на следующую страницу из HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                next_url = self.extract_next_page_url(soup, current_url)
                
                if not next_url:
                    console.print(f"[green]✅ Достигнут конец каталога на странице {page_number}")
                    break
                
                # Гарантируем сохранение параметров фильтров в ссылке
                next_url = self._merge_filter_params(next_url)
                
                # Если next ведет на уже посещенную страницу, прерываем
                if next_url in self.visited_pages:
                    console.print(f"[yellow]⚠️ Следующая страница уже посещена ({next_url}), останавливаемся")
                    break
                
                current_url = next_url
                page_number += 1
                time.sleep(1)  # Небольшая пауза между запросами
                
            except Exception as e:
                console.print(f"[red]❌ Ошибка на странице {page_number}: {e}")
                break
        
        return all_products
    
    def save_to_excel(self, products, filename="products_novasklad.xlsx"):
        """Сохраняем товары в Excel файл"""
        if not products:
            console.print("[red]❌ Нет товаров для сохранения!")
            return False
        
        try:
            df = pd.DataFrame(products)
            
            # Сортируем по названию
            df = df.sort_values('name')
            
            # Сохраняем в Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            
            console.print(f"[green]✅ Данные сохранены в файл: {filename}")
            console.print(f"[green]📊 Всего товаров: {len(products)}")
            
            # Показываем статистику
            self.show_statistics(products)
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Ошибка сохранения: {e}")
            return False
    
    def show_statistics(self, products):
        """Показываем статистику по товарам"""
        console.print("\n[bold blue]📊 Статистика по товарам:")
        
        # Создаем таблицу
        table = Table(title="Статистика")
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="green")
        
        table.add_row("Всего товаров", str(len(products)))
        
        # Статистика по брендам
        brands = [p['brand'] for p in products if p['brand'] != 'Не указан']
        if brands:
            brand_counts = pd.Series(brands).value_counts()
            top_brands = brand_counts.head(5)
            table.add_row("Топ-5 брендов", ", ".join([f"{brand} ({count})" for brand, count in top_brands.items()]))
        
        # Статистика по статусам
        statuses = [p['status'] for p in products if p['status'] != 'Не указан']
        if statuses:
            status_counts = pd.Series(statuses).value_counts()
            table.add_row("Статусы", ", ".join([f"{status} ({count})" for status, count in status_counts.items()]))
        
        # Товары с ценами
        prices = [p for p in products if p['price'] != 'Не указана']
        table.add_row("Товары с ценами", str(len(prices)))
        
        console.print(table)
    
    def run(self):
        """Основной метод запуска парсера"""
        console.print(Panel("[bold blue]🚀 Запуск парсера novasklad.kz (версия без браузера)", expand=False))
        console.print("[yellow]ℹ️ Используется requests + BeautifulSoup для парсинга")
        
        # Тестируем подключение
        if not self.test_connection():
            console.print("[red]❌ Не удалось подключиться к сайту!")
            return
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console,
                transient=True
            ) as progress:
                
                # Задача 1: Авторизация
                task1 = progress.add_task("[green]Авторизация на сайте...", total=100)
                
                # Выполняем авторизацию
                if not self.authenticate():
                    console.print("[red]❌ Авторизация не удалась! Парсинг невозможен.")
                    return
                
                progress.update(task1, completed=100)
                console.print("[green]✔️ Авторизация завершена")
                
                # Задача 2: Получение всех страниц
                task2 = progress.add_task("[blue]Получение страниц каталога...", total=100)
                
                # Получаем все товары
                all_products = self.get_all_pages()
                
                if not all_products:
                    console.print("[red]❌ Не удалось получить товары!")
                    return
                
                progress.update(task2, completed=100)
                
                # Задача 3: Сохранение данных
                task3 = progress.add_task("[purple]Сохранение данных...", total=100)
                
                # Сохраняем в Excel
                success = self.save_to_excel(all_products)
                
                progress.update(task3, completed=100)
                
                if success:
                    console.print(Panel(f"[bold green]✅ Парсинг завершен успешно! Спарсено {len(all_products)} товаров", expand=False))
                else:
                    console.print(Panel("[bold red]❌ Ошибка при сохранении данных", expand=False))
        
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️ Парсинг прерван пользователем")
        except Exception as e:
            console.print(f"[red]❌ Критическая ошибка: {e}")
            console.print("[yellow]Попробуйте:")
            console.print("1. Проверить интернет-соединение")
            console.print("2. Убедиться, что сайт доступен")
            console.print("3. Проверить логин и пароль")
            console.print("4. Проверить, что все библиотеки установлены")

    def authenticate(self):
        """Авторизация на сайте"""
        console.print("[blue]🔐 Выполняем авторизацию...")
        
        try:
            # Сначала получаем страницу авторизации для получения CSRF токена
            console.print("[blue]📄 Получаем страницу авторизации...")
            login_page = self.session.get("https://novasklad.kz/sign/", timeout=30)
            login_page.raise_for_status()
            

            
            # Парсим страницу для поиска CSRF токена и формы
            soup = BeautifulSoup(login_page.text, 'html.parser')
            
            # Ищем форму авторизации
            form = soup.find('form')
            if form:
                form_action = form.get('action', '')
                form_method = form.get('method', 'post')
                console.print(f"[green]✅ Форма найдена: action='{form_action}', method='{form_method}'")
                
                # Ищем все поля формы
                form_inputs = form.find_all('input')
                console.print(f"[blue]🔍 Найдено полей в форме: {len(form_inputs)}")
                for i, inp in enumerate(form_inputs):
                    inp_type = inp.get('type', 'text')
                    inp_name = inp.get('name', 'Нет')
                    inp_value = inp.get('value', 'Нет')
                    inp_id = inp.get('id', 'Нет')
                    console.print(f"[blue]   {i+1}. type='{inp_type}', name='{inp_name}', value='{inp_value}', id='{inp_id}'")
            else:
                console.print("[yellow]⚠️ Форма не найдена")
                return False
            
            # Формируем данные для авторизации
            auth_data = {
                'login': self.login,
                'password': self.password
            }
            
            console.print("[blue]📤 Отправляем данные авторизации...")
            console.print(f"[blue]   Логин: {self.login}")
            console.print(f"[blue]   Пароль: {'*' * len(self.password)}")
            console.print(f"[blue]   Данные: {auth_data}")
            
            # Обновляем заголовки для авторизации
            auth_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://novasklad.kz',
                'Referer': 'https://novasklad.kz/sign/',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Пробуем разные методы авторизации с правильным action
            auth_methods = [
                # Метод 1: POST на /sign/?in (правильный action формы)
                ("https://novasklad.kz/sign/?in", auth_data),
                # Метод 2: POST на /sign/ с параметром в data
                ("https://novasklad.kz/sign/", {**auth_data, 'action': 'in'}),
                # Метод 3: POST на /sign/ с параметром в URL
                ("https://novasklad.kz/sign/", auth_data),
                # Метод 4: POST на корневой URL с параметром
                ("https://novasklad.kz/?in", auth_data)
            ]
            
            auth_success = False
            
            for i, (auth_url, data) in enumerate(auth_methods):
                try:
                    console.print(f"[blue]🔄 Метод {i+1}: POST на {auth_url}")
                    console.print(f"[blue]   Данные: {data}")
                    
                    auth_response = self.session.post(
                        auth_url,
                        data=data,
                        headers=auth_headers,
                        timeout=30,
                        allow_redirects=True
                    )
                    
                    console.print(f"[blue]📥 Ответ: статус {auth_response.status_code}, URL: {auth_response.url}")
                    

                    
                    # Проверяем успешность
                    if auth_response.status_code in [301, 302, 303, 307, 308]:
                        console.print(f"[green]✅ Получен редирект - авторизация возможна")
                        auth_success = True
                        break
                    elif auth_response.status_code == 200:
                        # Проверяем, что мы больше не на странице входа
                        if "Войти" not in auth_response.text and "Авторизоваться" not in auth_response.text:
                            console.print(f"[green]✅ Авторизация успешна!")
                            auth_success = True
                            break
                        else:
                            console.print(f"[yellow]⚠️ Все еще на странице входа")
                    
                    # Пауза между попытками
                    time.sleep(1)
                    
                except Exception as e:
                    console.print(f"[yellow]⚠️ Ошибка метода {i+1}: {e}")
                    continue
            
            if not auth_success:
                # Пробуем альтернативный подход - ищем кнопку submit
                console.print("[blue]🔄 Пробуем альтернативный подход...")
                
                submit_button = soup.find('input', {'type': 'submit'})
                if submit_button:
                    submit_name = submit_button.get('name', '')
                    submit_value = submit_button.get('value', '')
                    console.print(f"[blue]🔍 Найдена кнопка submit: name='{submit_name}', value='{submit_value}'")
                    
                    # Добавляем данные кнопки если есть name
                    if submit_name:
                        auth_data[submit_name] = submit_value
                    
                    # Пробуем еще раз с правильным action
                    console.print("[blue]🔄 Пробуем повторную авторизацию с правильным action...")
                    try:
                        auth_response_final = self.session.post(
                            "https://novasklad.kz/sign/?in",  # Используем правильный action
                            data=auth_data,
                            headers=auth_headers,
                            timeout=30,
                            allow_redirects=True
                        )
                        
                        console.print(f"[blue]📥 Финальный ответ: статус {auth_response_final.status_code}")
                        console.print(f"[blue]📥 Финальный URL: {auth_response_final.url}")
                        

                        
                        if "Войти" not in auth_response_final.text and "Авторизоваться" not in auth_response_final.text:
                            console.print("[green]✅ Авторизация успешна при повторной попытке!")
                            auth_success = True
                        
                    except Exception as e:
                        console.print(f"[red]❌ Ошибка финальной попытки: {e}")
                
                if not auth_success:
                    console.print("[red]❌ Все методы авторизации не удались")
                    return False
            
            # Проверяем финальный статус авторизации
            console.print("[blue]🔍 Проверяем финальный статус авторизации...")
            
            try:
                # Пробуем получить главную страницу
                main_page = self.session.get(self.base_url, timeout=30)
                if "Войти" in main_page.text or "Авторизоваться" in main_page.text:
                    console.print("[yellow]⚠️ Авторизация не подтверждена - все еще есть ссылка входа")
                    return False
                else:
                    console.print("[green]✅ Авторизация подтверждена!")
                    return True
                    
            except Exception as e:
                console.print(f"[yellow]⚠️ Не удалось проверить статус: {e}")
                # Если не можем проверить, считаем что авторизация прошла
                return True
                
        except Exception as e:
            console.print(f"[red]❌ Ошибка авторизации: {e}")
            return False

    def extract_next_page_url(self, soup: BeautifulSoup, current_url: str):
        """Ищем реальную ссылку на следующую страницу каталога"""
        # 1) rel="next"
        link = soup.find('a', rel=lambda v: v and 'next' in v.lower())
        if link and link.get('href'):
            href = link.get('href')
            next_url = urljoin(self.base_url, href)
            if next_url != current_url:
                return next_url
        
        # 2) Кнопка со словом "Следующая" или стрелкой
        link = soup.find('a', string=re.compile(r'^(Следующая|Далее|Next|›|>>)$', re.I))
        if link and link.get('href'):
            href = link.get('href')
            next_url = urljoin(self.base_url, href)
            if next_url != current_url:
                return next_url
        
        # 3) Ссылки пагинации: ищем текущую активную и берём следующий элемент
        active = soup.select_one('.pagination .active, .pagination .current, .nav .active')
        if active:
            next_sibling = active.find_next('a')
            if next_sibling and next_sibling.get('href'):
                next_url = urljoin(self.base_url, next_sibling.get('href'))
                if next_url != current_url:
                    return next_url
        
        # 4) Фолбек: ищем параметр page/PAGEN_1 в ссылках
        for a in soup.find_all('a', href=True):
            href = a['href']
            if re.search(r'(page=\d+|PAGEN_1=\d+|/page/\d+/)', href, re.I):
                next_url = urljoin(self.base_url, href)
                if next_url != current_url:
                    return next_url
        
        return None

    def enable_status_filters(self):
        """Активируем фильтры 'В пути' (v481) и 'Под заказ' (v259) через параметры URL."""
        try:
            console.print("[blue]🔧 Включаем фильтры 'В пути' и 'Под заказ'")
            resp = self.session.get(self.catalog_url, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Ищем чекбоксы по id из label: v481, v259
            target_ids = {"v481", "v259"}
            found_params = []  # список кортежей (name, value)
            for input_tag in soup.find_all('input', {'type': 'checkbox'}):
                input_id = input_tag.get('id')
                if input_id in target_ids:
                    name = input_tag.get('name') or 'v[]'
                    value = input_tag.get('value') or re.sub(r'\D+', '', input_id or '')
                    if value:
                        found_params.append((name, value))
            
            # Если не нашли, используем типичный формат
            if not found_params:
                found_params = [("v[]", "481"), ("v[]", "259")]
            
            # Сливаем параметры с существующими
            self.catalog_url = self._merge_params_into_url(self.catalog_url, found_params)
            
            # Сохраняем плоский вид параметров для последующих страниц
            self.filter_params = {}
            for name, value in found_params:
                self.filter_params.setdefault(name, []).append(value)
            
            console.print(f"[green]✅ Фильтры активированы. URL: {self.catalog_url}")
        except Exception as e:
            console.print(f"[yellow]⚠️ Не удалось активировать фильтры: {e}")
            # продолжаем без ошибок
            
    def _merge_params_into_url(self, url: str, params_list: list):
        """Добавляет список (name,value) параметров в URL, сохраняя уже существующие значения."""
        parsed = urlparse(url)
        query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
        query_pairs.extend(params_list)
        new_query = urlencode(query_pairs, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    
    def _merge_filter_params(self, url: str):
        """Добавляет сохранённые параметры фильтров к URL при пагинации, если они отсутствуют."""
        if not self.filter_params:
            return url
        parsed = urlparse(url)
        existing = dict(parse_qsl(parsed.query, keep_blank_values=True))
        # Если уже есть хотя бы один фильтр по ключу, считаем что сохранены
        need_merge = True
        for key in self.filter_params.keys():
            if key in existing:
                need_merge = False
                break
        if not need_merge:
            return url
        # Мерджим
        query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
        for key, values in self.filter_params.items():
            for v in values:
                query_pairs.append((key, v))
        new_query = urlencode(query_pairs, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))


def main():
    """Главная функция"""
    try:
        # Создаем парсер
        parser = NovaskladParser()
        
        # Запускаем парсинг
        parser.run()
        
    except Exception as e:
        console.print(f"[red]❌ Ошибка запуска: {e}")
        console.print("[yellow]Убедитесь, что установлены все необходимые библиотеки:")
        console.print("pip install requests beautifulsoup4 pandas openpyxl rich")


if __name__ == "__main__":
    main()