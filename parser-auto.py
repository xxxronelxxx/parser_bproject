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
import subprocess
import sys

# Для красивого вывода в консоль
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel

console = Console()

# Функция для извлечения артикула из названия товара
def extract_article_from_name(product_name):
    match = re.search(r'\((.*?)\)', product_name)
    return match.group(1) if match else None


def check_browser_versions():
    """Проверяем версии установленных браузеров"""
    console.print("[blue]🔍 Проверяем версии браузеров...")
    
    # Проверяем Edge
    try:
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        for path in edge_paths:
            if os.path.exists(path):
                try:
                    result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        console.print(f"[green]✅ Edge найден: {result.stdout.strip()}")
                        break
                except:
                    pass
    except Exception as e:
        console.print(f"[yellow]⚠️ Не удалось проверить Edge: {e}")
    
    # Проверяем Chrome
    try:
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                try:
                    result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        console.print(f"[green]✅ Chrome найден: {result.stdout.strip()}")
                        break
                except:
                    pass
    except Exception as e:
        console.print(f"[yellow]⚠️ Не удалось проверить Chrome: {e}")


def setup_browser_auto():
    """Автоматическая настройка браузера с несколькими попытками"""
    console.print("[blue]🔧 Автоматическая настройка браузера...")
    
    # Сначала пробуем Edge
    try:
        console.print("[blue]🔄 Пробуем Edge...")
        driver = setup_edge_browser()
        if driver:
            return driver
    except Exception as e:
        console.print(f"[yellow]⚠️ Edge не удался: {e}")
    
    # Затем пробуем Chrome
    try:
        console.print("[blue]🔄 Пробуем Chrome...")
        driver = setup_chrome_browser()
        if driver:
            return driver
    except Exception as e:
        console.print(f"[yellow]⚠️ Chrome не удался: {e}")
    
    # Пробуем автоматическую загрузку через webdriver-manager
    try:
        console.print("[blue]🔄 Пробуем автоматическую загрузку...")
        driver = setup_webdriver_manager()
        if driver:
            return driver
    except Exception as e:
        console.print(f"[yellow]⚠️ Автоматическая загрузка не удалась: {e}")
    
    raise Exception("Не удалось запустить ни один браузер")


def setup_edge_browser():
    """Настройка Edge браузера"""
    options = webdriver.EdgeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
    
    # Ищем msedgedriver.exe
    current_dir = os.getcwd()
    edge_driver_path = "msedgedriver.exe"
    
    if os.path.exists(edge_driver_path):
        console.print(f"[green]✅ Найден msedgedriver.exe в текущей папке")
        service = EdgeService(edge_driver_path)
    else:
        # Альтернативные пути
        possible_paths = [
            os.path.join(current_dir, "msedgedriver.exe"),
            os.path.join(current_dir, "driver", "msedgedriver.exe"),
            os.path.join(current_dir, "drivers", "msedgedriver.exe"),
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedgedriver.exe"
        ]
        
        edge_driver_path = None
        for path in possible_paths:
            if os.path.exists(path):
                edge_driver_path = path
                console.print(f"[green]✅ Найден msedgedriver.exe по пути: {path}")
                break
        
        if edge_driver_path:
            service = EdgeService(edge_driver_path)
        else:
            console.print("[yellow]⚠️ Локальный драйвер Edge не найден, используем системный путь")
            service = EdgeService()
    
    try:
        driver = webdriver.Edge(service=service, options=options)
        console.print("[green]✅ Edge успешно запущен")
        return driver
    except Exception as e:
        console.print(f"[red]❌ Edge не удался: {e}")
        return None


def setup_chrome_browser():
    """Настройка Chrome браузера"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Ищем chromedriver.exe
    current_dir = os.getcwd()
    chrome_driver_path = "chromedriver.exe"
    
    if os.path.exists(chrome_driver_path):
        console.print(f"[green]✅ Найден chromedriver.exe в текущей папке")
        service = ChromeService(chrome_driver_path)
    else:
        # Альтернативные пути
        possible_paths = [
            os.path.join(current_dir, "chromedriver.exe"),
            os.path.join(current_dir, "driver", "chromedriver.exe"),
            os.path.join(current_dir, "drivers", "chromedriver.exe"),
            r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
        ]
        
        chrome_driver_path = None
        for path in possible_paths:
            if os.path.exists(path):
                chrome_driver_path = path
                console.print(f"[green]✅ Найден chromedriver.exe по пути: {path}")
                break
        
        if chrome_driver_path:
            service = ChromeService(chrome_driver_path)
        else:
            console.print("[yellow]⚠️ Локальный драйвер Chrome не найден, используем системный путь")
            service = ChromeService()
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        console.print("[green]✅ Chrome успешно запущен")
        return driver
    except Exception as e:
        console.print(f"[red]❌ Chrome не удался: {e}")
        return None


def setup_webdriver_manager():
    """Настройка через webdriver-manager"""
    try:
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        from webdriver_manager.chrome import ChromeDriverManager
        
        console.print("[blue]🔄 Пробуем Edge через webdriver-manager...")
        try:
            edge_driver_path = EdgeChromiumDriverManager().install()
            service = EdgeService(edge_driver_path)
            options = webdriver.EdgeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Edge(service=service, options=options)
            console.print("[green]✅ Edge через webdriver-manager успешно запущен")
            return driver
        except Exception as e:
            console.print(f"[yellow]⚠️ Edge через webdriver-manager не удался: {e}")
        
        console.print("[blue]🔄 Пробуем Chrome через webdriver-manager...")
        try:
            chrome_driver_path = ChromeDriverManager().install()
            service = ChromeService(chrome_driver_path)
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(service=service, options=options)
            console.print("[green]✅ Chrome через webdriver-manager успешно запущен")
            return driver
        except Exception as e:
            console.print(f"[yellow]⚠️ Chrome через webdriver-manager не удался: {e}")
        
    except ImportError:
        console.print("[yellow]⚠️ webdriver-manager не установлен")
    except Exception as e:
        console.print(f"[yellow]⚠️ Ошибка webdriver-manager: {e}")
    
    return None


# Основная функция парсинга
def main():
    console.print(Panel("[bold blue]Начало работы парсера (автоматическая версия)", expand=False))
    
    # Проверяем версии браузеров
    check_browser_versions()

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
            driver = setup_browser_auto()
            if not driver:
                raise Exception("Не удалось запустить браузер")
            
            progress.update(task1, completed=100)
            console.print("[green]✔️ Браузер успешно настроен")
            
            # Этап 1: Авторизация
            task2 = progress.add_task("[green]Авторизация на сайте...", total=100)
            driver.get("https://www.novasklad.kz ")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "login")))
            login_field = driver.find_element(By.NAME, "login")
            login_field.send_keys("+77025757606")
            pass_field = driver.find_element(By.NAME, "pass")
            pass_field.send_keys("681660")
            pass_field.send_keys(Keys.RETURN)
            time.sleep(5)
            progress.update(task2, completed=100)
            console.print(f"[green]✔️ Авторизация успешна → {driver.current_url}")

            # Этап 2: Переход в категорию
            task3 = progress.add_task("[cyan]Переход в категорию...", total=100)
            driver.get("https://www.novasklad.kz/catalog/sinks-and-blanco-mixers/ ")
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "v259"))
            )
            progress.update(task3, completed=100)
            console.print("[green]✔️ Переход в категорию завершён")

            # Этап 3: Простановка фильтров
            task4 = progress.add_task("[yellow]Простановка фильтров...", total=100)
            checkbox_259 = driver.find_element(By.ID, "v259")
            checkbox_481 = driver.find_element(By.ID, "v481")
            if not checkbox_259.is_selected():
                driver.execute_script("arguments[0].click();", checkbox_259)
            if not checkbox_481.is_selected():
                driver.execute_script("arguments[0].click();", checkbox_481)
            progress.update(task4, completed=100)
            console.print("[green]✔️ Фильтры установлены")

            time.sleep(3)

            # Этап 4: Прокрутка страницы
            task5 = progress.add_task("[blue]Подгрузка товаров...", total=100)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            progress.update(task5, completed=100)
            console.print("[green]✔️ Все товары подгружены")

            # Этап 5: Парсинг товаров
            task6 = progress.add_task("[red]Парсинг товаров...", total=100)
            # Обновляем селектор для карточек товаров
            product_elements = driver.find_elements(By.CSS_SELECTOR, ".product")
            total_products = len(product_elements)
            console.print(f"[green]📊 Найдено товаров: [bold]{total_products}[/bold]")

            products = []

            for idx, product in enumerate(product_elements):
                try:
                    # Обновленный парсинг названия товара - убираем ссылку
                    name_elem = product.find_element(By.CSS_SELECTOR, ".title a")
                    name = name_elem.text.strip()  # Только текст без ссылки
                    link = name_elem.get_attribute("href")

                    try:
                        description = product.find_element(By.CLASS_NAME, "description").text
                    except:
                        description = "Не указан"

                    try:
                        article = product.find_element(By.CLASS_NAME, "articleLine").text
                    except:
                        article = "Не указан"

                    # Обновленный парсинг цены
                    try:
                        price_elem = product.find_element(By.CSS_SELECTOR, ".price-line .price")
                        price = price_elem.text.strip()
                    except:
                        price = "Не указана"

                    # Обновленный парсинг статуса
                    try:
                        status_elem = product.find_element(By.CSS_SELECTOR, ".par.s .v")
                        status = status_elem.text.strip()
                    except:
                        status = "Не указан"

                    # Обновленный парсинг бренда
                    try:
                        brand_elem = product.find_element(By.CSS_SELECTOR, ".par.b .v")
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
                    continue  # Пропускаем товар, если не получилось спарсить

                progress.update(task6, advance=100 / total_products)

            # Этап 6: Сохранение данных
            task7 = progress.add_task("[purple]Сохранение данных...", total=100)
            df = pd.DataFrame(products)
            df.to_excel("products_with_status_auto.xlsx", index=False)
            progress.update(task7, completed=100)
            console.print("[green]✔️ Данные успешно сохранены в Excel")

        except Exception as e:
            console.print(f"[red]❌ Ошибка: {e}")
            console.print("[yellow]Попробуйте:")
            console.print("1. Установить Microsoft Edge или Google Chrome")
            console.print("2. Установить webdriver-manager: pip install webdriver-manager")
            console.print("3. Проверить, что WebDriver файлы не заблокированы")
        finally:
            if 'driver' in locals():
                driver.quit()
                console.print("[green]✔️ Браузер закрыт")
            console.print(Panel("[bold green]Готово! Все данные сохранены в 'products_with_status_auto.xlsx'", expand=False))


if __name__ == "__main__":
    main()