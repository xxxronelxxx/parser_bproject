from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
import pandas as pd
import re

# Для красивого вывода в консоль
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel

console = Console()

# Функция для извлечения артикула из названия товара
def extract_article_from_name(product_name):
    match = re.search(r'\((.*?)\)', product_name)
    return match.group(1) if match else None


# Настройка Microsoft Edge в headless-режиме
def setup_browser():
    options = webdriver.EdgeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)
    return driver


# Основная функция парсинга
def main():
    console.print(Panel("[bold blue]Начало работы парсера", expand=False))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True
    ) as progress:
        task1 = progress.add_task("[green]Авторизация на сайте...", total=100)
        driver = setup_browser()

        try:
            # Этап 1: Авторизация
            driver.get("https://www.novasklad.kz ")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "login")))
            login_field = driver.find_element(By.NAME, "login")
            login_field.send_keys("+77025757606")
            pass_field = driver.find_element(By.NAME, "pass")
            pass_field.send_keys("681660")
            pass_field.send_keys(Keys.RETURN)
            time.sleep(5)
            progress.update(task1, completed=100)
            console.print(f"[green]✔️ Авторизация успешна → {driver.current_url}")

            # Этап 2: Переход в категорию
            task2 = progress.add_task("[cyan]Переход в категорию...", total=100)
            driver.get("https://www.novasklad.kz/catalog/sinks-and-blanco-mixers/ ")
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "v259"))
            )
            progress.update(task2, completed=100)
            console.print("[green]✔️ Переход в категорию завершён")

            # Этап 3: Простановка фильтров
            task3 = progress.add_task("[yellow]Простановка фильтров...", total=100)
            checkbox_259 = driver.find_element(By.ID, "v259")
            checkbox_481 = driver.find_element(By.ID, "v481")
            if not checkbox_259.is_selected():
                driver.execute_script("arguments[0].click();", checkbox_259)
            if not checkbox_481.is_selected():
                driver.execute_script("arguments[0].click();", checkbox_481)
            progress.update(task3, completed=100)
            console.print("[green]✔️ Фильтры установлены")

            time.sleep(3)

            # Этап 4: Прокрутка страницы
            task4 = progress.add_task("[blue]Подгрузка товаров...", total=100)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            progress.update(task4, completed=100)
            console.print("[green]✔️ Все товары подгружены")

            # Этап 5: Парсинг товаров
            task5 = progress.add_task("[red]Парсинг товаров...", total=100)
            product_elements = driver.find_elements(By.CSS_SELECTOR, ".line .product")
            total_products = len(product_elements)
            console.print(f"[green]📊 Найдено товаров: [bold]{total_products}[/bold]")

            products = []

            for idx, product in enumerate(product_elements):
                try:
                    name_elem = product.find_element(By.CSS_SELECTOR, ".title a")
                    name = name_elem.text
                    link = name_elem.get_attribute("href")

                    try:
                        description = product.find_element(By.CLASS_NAME, "description").text
                    except:
                        description = "Не указан"

                    try:
                        article = product.find_element(By.CLASS_NAME, "articleLine").text
                    except:
                        article = "Не указан"

                    try:
                        price = product.find_element(By.CSS_SELECTOR, ".price").text
                    except:
                        price = "Не указана"

                    try:
                        status = product.find_element(By.CSS_SELECTOR, ".status").text
                    except:
                        status = "Не указан"

                    try:
                        brand = product.find_element(By.CLASS_NAME, "brandLine").text
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
                    continue  # Пропускаем товар, если не получилось спарсить

                progress.update(task5, advance=100 / total_products)

            # Этап 6: Сохранение данных
            task6 = progress.add_task("[purple]Сохранение данных...", total=100)
            df = pd.DataFrame(products)
            df.to_excel("products_with_status.xlsx", index=False)
            progress.update(task6, completed=100)
            console.print("[green]✔️ Данные успешно сохранены в Excel")

        except Exception as e:
            console.print(f"[red]❌ Ошибка: {e}")
        finally:
            driver.quit()
            console.print("[green]✔️ Браузер закрыт")
            console.print(Panel("[bold green]Готово! Все данные сохранены в 'products_with_status.xlsx'", expand=False))


if __name__ == "__main__":
    main()