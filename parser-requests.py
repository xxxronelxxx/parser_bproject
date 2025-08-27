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
from urllib.parse import urljoin, urlparse
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
        self.catalog_url = "https://novasklad.kz/catalog/kitchen-mixers/"
        
        # Заголовки для имитации браузера
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Применяем заголовки к сессии
        self.session.headers.update(self.headers)
        
        # Список для хранения товаров
        self.products = []
        
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
        
        for idx, product in enumerate(found_products):
            try:
                product_data = self.parse_product_element(product)
                if product_data:
                    products.append(product_data)
                    console.print(f"[green]✅ Товар {idx+1}: {product_data['name'][:50]}...")
                
            except Exception as e:
                console.print(f"[yellow]⚠️ Ошибка парсинга товара {idx+1}: {e}")
                continue
        
        return products
    
    def parse_product_element(self, product_elem):
        """Парсим отдельный товар"""
        try:
            # Название товара
            name = self.extract_text(product_elem, [
                '.title a',
                '.title',
                'h3',
                'h4',
                'a[href*="/catalog/"]'
            ])
            
            # Ссылка на товар
            link = self.extract_href(product_elem, [
                '.title a',
                'a[href*="/catalog/"]',
                'a'
            ])
            
            if link and not link.startswith('http'):
                link = urljoin(self.base_url, link)
            
            # Цена
            price = self.extract_text(product_elem, [
                '.price-line .price',
                '.price',
                '[class*="price"]',
                '.cost',
                '.price-value'
            ])
            
            # Статус
            status = self.extract_text(product_elem, [
                '.par.s .v',
                '.status',
                '[class*="status"]',
                '.availability',
                '.stock'
            ])
            
            # Бренд
            brand = self.extract_text(product_elem, [
                '.par.b .v',
                '.brand',
                '[class*="brand"]',
                '.brandLine',
                '.manufacturer'
            ])
            
            # Описание
            description = self.extract_text(product_elem, [
                '.description',
                '.desc',
                '.text',
                '[class*="description"]'
            ])
            
            # Артикул
            article = self.extract_text(product_elem, [
                '.article',
                '.articleLine',
                '.sku',
                '[class*="article"]',
                '.code'
            ])
            
            # Дополнительный артикул из названия
            additional_article = self.extract_article_from_name(name)
            
            # Если название не найдено, пропускаем товар
            if not name or name.strip() == "":
                return None
            
            return {
                'name': name.strip(),
                'link': link,
                'price': price.strip() if price else 'Не указана',
                'status': status.strip() if status else 'Не указан',
                'brand': brand.strip() if brand else 'Не указан',
                'description': description.strip() if description else 'Не указано',
                'article': article.strip() if article else 'Не указан',
                'additional_article': additional_article
            }
            
        except Exception as e:
            console.print(f"[yellow]⚠️ Ошибка парсинга элемента: {e}")
            return None
    
    def extract_text(self, element, selectors):
        """Извлекаем текст по разным селекторам"""
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found and found.get_text(strip=True):
                    return found.get_text(strip=True)
            except:
                continue
        return None
    
    def extract_href(self, element, selectors):
        """Извлекаем ссылку по разным селекторам"""
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found and found.get('href'):
                    return found.get('href')
            except:
                continue
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
        
        all_products = []
        page = 1
        max_pages = 50  # Ограничиваем количество страниц
        
        while page <= max_pages:
            try:
                # Формируем URL страницы
                if page == 1:
                    page_url = self.catalog_url
                else:
                    # Пробуем разные форматы пагинации
                    page_urls = [
                        f"{self.catalog_url}?page={page}",
                        f"{self.catalog_url}page/{page}/",
                        f"{self.catalog_url}?p={page}",
                        f"{self.catalog_url}?PAGEN_1={page}"
                    ]
                    
                    # Пробуем первый формат
                    page_url = page_urls[0]
                
                console.print(f"[blue]📄 Страница {page}: {page_url}")
                
                # Получаем содержимое страницы
                html_content = self.get_page_content(page_url, f"Страница {page}")
                
                if not html_content:
                    console.print(f"[yellow]⚠️ Не удалось загрузить страницу {page}")
                    break
                
                # Парсим товары на странице
                page_products = self.parse_catalog_page(html_content)
                
                if not page_products:
                    console.print(f"[yellow]⚠️ На странице {page} товары не найдены")
                    # Пробуем альтернативный формат URL
                    if page == 1:
                        break
                    else:
                        page += 1
                        continue
                
                all_products.extend(page_products)
                console.print(f"[green]✅ Страница {page}: найдено {len(page_products)} товаров")
                
                # Проверяем, есть ли следующая страница
                soup = BeautifulSoup(html_content, 'html.parser')
                next_page = soup.find('a', string=re.compile(r'следующая|next|>', re.I))
                
                if not next_page:
                    console.print(f"[green]✅ Достигнут конец каталога на странице {page}")
                    break
                
                page += 1
                time.sleep(1)  # Небольшая пауза между запросами
                
            except Exception as e:
                console.print(f"[red]❌ Ошибка на странице {page}: {e}")
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
                
                # Задача 1: Получение всех страниц
                task1 = progress.add_task("[green]Получение страниц каталога...", total=100)
                
                # Получаем все товары
                all_products = self.get_all_pages()
                
                if not all_products:
                    console.print("[red]❌ Не удалось получить товары!")
                    return
                
                progress.update(task1, completed=100)
                
                # Задача 2: Сохранение данных
                task2 = progress.add_task("[blue]Сохранение данных...", total=100)
                
                # Сохраняем в Excel
                success = self.save_to_excel(all_products)
                
                progress.update(task2, completed=100)
                
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
            console.print("3. Проверить, что все библиотеки установлены")


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