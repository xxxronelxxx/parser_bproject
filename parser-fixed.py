from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
import os

# Для красивого вывода в консоль
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel

console = Console()

# Функция для извлечения артикула из названия товара
def extract_article_from_name(product_name):
    match = re.search(r'\((.*?)\)', product_name)
    return match.group(1) if match else None


def setup_browser_simple():
    """Простая настройка браузера без сложных опций"""
    console.print("[blue]🔧 Простая настройка браузера...")
    
    # Пробуем Chrome с минимальными настройками
    try:
        console.print("[blue]🔄 Пробуем Chrome с минимальными настройками...")
        options = webdriver.ChromeOptions()
        # Только базовые настройки
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Ищем chromedriver.exe
        chrome_driver_path = "chromedriver.exe"
        if os.path.exists(chrome_driver_path):
            console.print(f"[green]✅ Найден chromedriver.exe")
            service = ChromeService(chrome_driver_path)
        else:
            console.print("[yellow]⚠️ Используем системный Chrome WebDriver")
            service = ChromeService()
        
        driver = webdriver.Chrome(service=service, options=options)
        console.print("[green]✅ Chrome успешно запущен")
        return driver
        
    except Exception as e:
        console.print(f"[yellow]⚠️ Chrome не удался: {e}")
        
        # Пробуем Edge с минимальными настройками
        try:
            console.print("[blue]🔄 Пробуем Edge с минимальными настройками...")
            options = webdriver.EdgeOptions()
            # Только базовые настройки
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Ищем msedgedriver.exe
            edge_driver_path = "msedgedriver.exe"
            if os.path.exists(edge_driver_path):
                console.print(f"[green]✅ Найден msedgedriver.exe")
                service = EdgeService(edge_driver_path)
            else:
                console.print("[yellow]⚠️ Используем системный Edge WebDriver")
                service = EdgeService()
            
            driver = webdriver.Edge(service=service, options=options)
            console.print("[green]✅ Edge успешно запущен")
            return driver
            
        except Exception as e2:
            console.print(f"[red]❌ Edge не удался: {e2}")
            raise Exception("Не удалось запустить ни один браузер")


# Основная функция парсинга
def main():
    console.print(Panel("[bold blue]Начало работы парсера (исправленная версия)", expand=False))
    console.print("[yellow]⚠️ ВНИМАНИЕ: Браузер будет открыт в видимом режиме!")
    console.print("[yellow]⚠️ НЕ ЗАКРЫВАЙТЕ окно браузера во время работы!")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True
    ) as progress:
        task1 = progress.add_task("[green]Настройка браузера...", total=100)
        
        try:
            driver = setup_browser_simple()
            if not driver:
                raise Exception("Не удалось запустить браузер")
            
            progress.update(task1, completed=100)
            console.print("[green]✔️ Браузер успешно настроен")
            
            # Этап 1: Авторизация
            task2 = progress.add_task("[green]Авторизация на сайте...", total=100)
            console.print("[blue]🌐 Открываем страницу авторизации...")
            
            # Используем правильный URL для авторизации
            driver.get("https://novasklad.kz/sign/")
            console.print("[green]✅ Страница авторизации открыта")
            
            # Ждем загрузки страницы
            console.print("[blue]⏳ Ждем загрузки страницы...")
            time.sleep(5)
            
            # Ищем поля для ввода с правильными селекторами
            try:
                console.print("[blue]🔍 Ищем поле логина...")
                login_field = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.NAME, "login"))
                )
                console.print("[green]✅ Поле логина найдено")
                
                console.print("[blue]🔍 Ищем поле пароля...")
                pass_field = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.NAME, "password"))
                )
                console.print("[green]✅ Поле пароля найдено")
                
            except Exception as e:
                console.print(f"[yellow]⚠️ Не удалось найти поля для ввода: {e}")
                console.print("[blue]🔍 Проверяем текущий URL и содержимое страницы...")
                console.print(f"[blue]URL: {driver.current_url}")
                console.print(f"[blue]Заголовок: {driver.title}")
                
                # Показываем текущий HTML для отладки
                page_source = driver.page_source[:2000]  # Первые 2000 символов
                console.print(f"[blue]HTML (начало): {page_source}")
                
                # Пробуем найти любые поля ввода
                input_fields = driver.find_elements(By.TAG_NAME, "input")
                console.print(f"[blue]Найдено полей ввода: {len(input_fields)}")
                for i, field in enumerate(input_fields):
                    try:
                        field_type = field.get_attribute("type")
                        field_name = field.get_attribute("name")
                        field_id = field.get_attribute("id")
                        field_class = field.get_attribute("class")
                        console.print(f"[blue]Поле {i+1}: type={field_type}, name={field_name}, id={field_id}, class={field_class}")
                    except:
                        pass
                
                raise Exception("Не удалось найти поля для авторизации")
            
            # Вводим логин и пароль
            console.print("[blue]🔑 Вводим логин и пароль...")
            login_field.clear()
            login_field.send_keys("+77025757606")
            pass_field.clear()
            pass_field.send_keys("681660")
            
            console.print("[blue]📤 Ищем кнопку входа...")
            try:
                # Ищем кнопку входа по правильному селектору
                submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Войти']")
                console.print("[green]✅ Кнопка входа найдена")
                
                console.print("[blue]📤 Нажимаем кнопку входа...")
                submit_button.click()
                
            except Exception as e:
                console.print(f"[yellow]⚠️ Не удалось найти кнопку входа: {e}")
                console.print("[blue]🔍 Пробуем альтернативные способы...")
                
                # Пробуем найти кнопку по классу
                try:
                    submit_button = driver.find_element(By.CLASS_NAME, "btn")
                    console.print("[green]✅ Кнопка найдена по классу")
                    submit_button.click()
                except:
                    # Пробуем отправить форму через Enter
                    console.print("[blue]📤 Отправляем форму через Enter...")
                    pass_field.send_keys(Keys.RETURN)
            
            # Ждем авторизации
            console.print("[blue]⏳ Ждем завершения авторизации...")
            time.sleep(8)
            
            progress.update(task2, completed=100)
            console.print(f"[green]✔️ Авторизация завершена → {driver.current_url}")

            # Этап 2: Переход в категорию
            task3 = progress.add_task("[cyan]Переход в категорию...", total=100)
            console.print("[blue]📁 Переходим в категорию...")
            
            try:
                driver.get("https://www.novasklad.kz/catalog/sinks-and-blanco-mixers/")
                console.print("[green]✅ Перешли в категорию")
            except Exception as e:
                console.print(f"[yellow]⚠️ Ошибка при переходе в категорию: {e}")
                # Пробуем альтернативный способ
                driver.get("https://www.novasklad.kz/catalog/sinks-and-blanco-mixers/")
            
            # Ждем загрузки страницы категории
            time.sleep(8)
            
            try:
                console.print("[blue]🔍 Ищем фильтры на странице...")
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "v259"))
                )
                console.print("[green]✅ Страница категории загружена")
            except Exception as e:
                console.print(f"[yellow]⚠️ Не удалось найти фильтры: {e}")
                console.print("[blue]🔍 Проверяем содержимое страницы категории...")
                console.print(f"[blue]URL: {driver.current_url}")
                console.print(f"[blue]Заголовок: {driver.title}")
                
                # Ищем любые элементы на странице
                all_elements = driver.find_elements(By.TAG_NAME, "*")
                console.print(f"[blue]Всего элементов на странице: {len(all_elements)}")
                
                # Ищем элементы с ID
                elements_with_id = driver.find_elements(By.CSS_SELECTOR, "[id]")
                console.print(f"[blue]Элементы с ID: {len(elements_with_id)}")
                for elem in elements_with_id[:15]:  # Показываем первые 15
                    try:
                        elem_id = elem.get_attribute("id")
                        elem_tag = elem.tag_name
                        console.print(f"[blue]ID: {elem_id}, Tag: {elem_tag}")
                    except:
                        pass
                
                # Пробуем продолжить без фильтров
                console.print("[yellow]⚠️ Продолжаем без фильтров...")
            
            progress.update(task3, completed=100)
            console.print("[green]✔️ Переход в категорию завершён")

            # Этап 3: Простановка фильтров (если найдены)
            task4 = progress.add_task("[yellow]Простановка фильтров...", total=100)
            console.print("[blue]🔧 Устанавливаем фильтры...")
            
            try:
                checkbox_259 = driver.find_element(By.ID, "v259")
                checkbox_481 = driver.find_element(By.ID, "v481")
                
                if not checkbox_259.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox_259)
                    console.print("[green]✅ Фильтр v259 установлен")
                else:
                    console.print("[blue]ℹ️ Фильтр v259 уже установлен")
                    
                if not checkbox_481.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox_481)
                    console.print("[green]✅ Фильтр v481 установлен")
                else:
                    console.print("[blue]ℹ️ Фильтр v481 уже установлен")
                    
            except Exception as e:
                console.print(f"[yellow]⚠️ Фильтры не найдены, продолжаем без них: {e}")
            
            progress.update(task4, completed=100)
            console.print("[green]✔️ Фильтры обработаны")

            time.sleep(3)

            # Этап 4: Прокрутка страницы
            task5 = progress.add_task("[blue]Подгрузка товаров...", total=100)
            console.print("[blue]📜 Прокручиваем страницу для загрузки всех товаров...")
            
            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0
            max_scrolls = 15  # Увеличиваем количество прокруток
            
            while scroll_count < max_scrolls:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  # Увеличиваем время ожидания
                new_height = driver.execute_script("return document.body.scrollHeight")
                scroll_count += 1
                console.print(f"[blue]📜 Прокрутка {scroll_count}/{max_scrolls}")
                
                if new_height == last_height:
                    console.print("[green]✅ Достигнут конец страницы")
                    break
                last_height = new_height
            
            progress.update(task5, completed=100)
            console.print("[green]✔️ Все товары подгружены")

            # Этап 5: Парсинг товаров
            task6 = progress.add_task("[red]Парсинг товаров...", total=100)
            console.print("[blue]🔍 Ищем товары на странице...")
            
            # Пробуем разные селекторы для товаров
            product_selectors = [
                ".product",
                ".line .product", 
                ".item",
                ".product-item",
                "[class*='product']",
                ".catalog-item",
                ".goods-item"
            ]
            
            product_elements = []
            for selector in product_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        console.print(f"[green]✅ Найдено товаров с селектором '{selector}': {len(elements)}")
                        product_elements = elements
                        break
                except:
                    continue
            
            if not product_elements:
                console.print("[yellow]⚠️ Товары не найдены, показываем структуру страницы...")
                
                # Показываем структуру страницы для отладки
                body = driver.find_element(By.TAG_NAME, "body")
                classes = body.get_attribute("class")
                console.print(f"[blue]Классы body: {classes}")
                
                # Ищем любые div элементы
                divs = driver.find_elements(By.TAG_NAME, "div")
                console.print(f"[blue]Всего div элементов: {len(divs)}")
                
                # Показываем классы первых div элементов
                for i, div in enumerate(divs[:30]):
                    try:
                        div_class = div.get_attribute("class")
                        if div_class:
                            console.print(f"[blue]Div {i+1}: class='{div_class}'")
                    except:
                        pass
                
                # Пробуем найти любые элементы с классом, содержащим 'product'
                try:
                    product_like = driver.find_elements(By.CSS_SELECTOR, "[class*='product']")
                    console.print(f"[blue]Элементы с 'product' в классе: {len(product_like)}")
                    for i, elem in enumerate(product_like[:10]):
                        try:
                            elem_class = elem.get_attribute("class")
                            elem_tag = elem.tag_name
                            console.print(f"[blue]Product-like {i+1}: {elem_tag}.{elem_class}")
                        except:
                            pass
                except:
                    pass
                
                raise Exception("Товары не найдены на странице")
            
            total_products = len(product_elements)
            console.print(f"[green]📊 Найдено товаров: [bold]{total_products}[/bold]")

            products = []

            for idx, product in enumerate(product_elements):
                try:
                    console.print(f"[blue]🔍 Парсим товар {idx+1}/{total_products}")
                    
                    # Парсинг названия товара
                    name = "Не указан"
                    link = ""
                    try:
                        name_elem = product.find_element(By.CSS_SELECTOR, ".title a")
                        name = name_elem.text.strip()
                        link = name_elem.get_attribute("href")
                        console.print(f"[green]✅ Название: {name[:50]}...")
                    except:
                        # Пробуем альтернативные селекторы
                        try:
                            name_elem = product.find_element(By.CSS_SELECTOR, ".title")
                            name = name_elem.text.strip()
                        except:
                            try:
                                name_elem = product.find_element(By.CSS_SELECTOR, "h3")
                                name = name_elem.text.strip()
                            except:
                                try:
                                    name_elem = product.find_element(By.CSS_SELECTOR, "h4")
                                    name = name_elem.text.strip()
                                except:
                                    name = "Не указан"
                    
                    # Парсинг описания
                    description = "Не указан"
                    try:
                        description = product.find_element(By.CLASS_NAME, "description").text
                    except:
                        try:
                            description = product.find_element(By.CSS_SELECTOR, ".desc").text
                        except:
                            description = "Не указан"

                    # Парсинг артикула
                    article = "Не указан"
                    try:
                        article = product.find_element(By.CLASS_NAME, "articleLine").text
                    except:
                        try:
                            article = product.find_element(By.CSS_SELECTOR, ".article").text
                        except:
                            article = "Не указан"

                    # Парсинг цены
                    price = "Не указана"
                    try:
                        price_elem = product.find_element(By.CSS_SELECTOR, ".price-line .price")
                        price = price_elem.text.strip()
                    except:
                        try:
                            price_elem = product.find_element(By.CSS_SELECTOR, ".price")
                            price = price_elem.text.strip()
                        except:
                            try:
                                price_elem = product.find_element(By.CSS_SELECTOR, "[class*='price']")
                                price = price_elem.text.strip()
                            except:
                                price = "Не указана"

                    # Парсинг статуса
                    status = "Не указан"
                    try:
                        status_elem = product.find_element(By.CSS_SELECTOR, ".par.s .v")
                        status = status_elem.text.strip()
                    except:
                        try:
                            status_elem = product.find_element(By.CSS_SELECTOR, ".status")
                            status = status_elem.text.strip()
                        except:
                            try:
                                status_elem = product.find_element(By.CSS_SELECTOR, "[class*='status']")
                                status = status_elem.text.strip()
                            except:
                                status = "Не указан"

                    # Парсинг бренда
                    brand = "Не указан"
                    try:
                        brand_elem = product.find_element(By.CSS_SELECTOR, ".par.b .v")
                        brand = brand_elem.text.strip()
                    except:
                        try:
                            brand_elem = product.find_element(By.CLASS_NAME, "brandLine")
                            brand = brand_elem.text.strip()
                        except:
                            try:
                                brand_elem = product.find_element(By.CSS_SELECTOR, "[class*='brand']")
                                brand = brand_elem.text.strip()
                            except:
                                brand = "Не указан"

                    additional_article = extract_article_from_name(name)

                    products.append({
                        "Brand": brand,
                        "Name": name,
                        "Link": link,
                        "Description": description,
                        "Article": article,
                        "Additional Article": additional_article,
                        "Price": price,
                        "Status": status
                    })

                except Exception as e:
                    console.print(f"[yellow]⚠️ Ошибка при парсинге товара {idx+1}: {e}")
                    continue

                progress.update(task6, advance=100 / total_products)

            # Этап 6: Сохранение данных
            task7 = progress.add_task("[purple]Сохранение данных...", total=100)
            console.print(f"[blue]💾 Сохраняем {len(products)} товаров...")
            
            df = pd.DataFrame(products)
            filename = "products_with_status_fixed.xlsx"
            df.to_excel(filename, index=False)
            
            progress.update(task7, completed=100)
            console.print(f"[green]✔️ Данные успешно сохранены в {filename}")
            console.print(f"[green]📊 Всего спарсено товаров: {len(products)}")

        except Exception as e:
            console.print(f"[red]❌ Ошибка: {e}")
            console.print("[yellow]Попробуйте:")
            console.print("1. Проверить интернет-соединение")
            console.print("2. Убедиться, что сайт доступен")
            console.print("3. Проверить логин и пароль")
        finally:
            if 'driver' in locals():
                console.print("[blue]⏳ Закрываем браузер через 15 секунд...")
                console.print("[yellow]⚠️ Вы можете закрыть браузер вручную или подождать автоматического закрытия")
                time.sleep(15)
                driver.quit()
                console.print("[green]✔️ Браузер закрыт")
            console.print(Panel("[bold green]Готово! Все данные сохранены в 'products_with_status_fixed.xlsx'", expand=False))


if __name__ == "__main__":
    main()