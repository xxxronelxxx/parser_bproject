#!/usr/bin/env python3
"""
Тестовый скрипт для проверки авторизации на novasklad.kz
"""

import requests
from bs4 import BeautifulSoup
import time

def test_auth():
    print("🔐 Тестируем авторизацию на novasklad.kz...")
    
    # Создаем сессию
    session = requests.Session()
    
    # Заголовки
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    session.headers.update(headers)
    
    try:
        # 1. Получаем страницу авторизации
        print("📄 Получаем страницу авторизации...")
        login_page = session.get("https://novasklad.kz/sign/", timeout=30)
        print(f"✅ Статус: {login_page.status_code}")
        print(f"✅ URL: {login_page.url}")
        
        # Сохраняем страницу
        with open("test_login.html", "w", encoding="utf-8") as f:
            f.write(login_page.text)
        print("💾 Страница сохранена в test_login.html")
        
        # 2. Парсим форму
        soup = BeautifulSoup(login_page.text, 'html.parser')
        
        # Ищем форму
        form = soup.find('form')
        if form:
            print(f"✅ Форма найдена: action='{form.get('action', 'Нет')}', method='{form.get('method', 'Нет')}'")
            
            # Поля формы
            inputs = form.find_all('input')
            print(f"🔍 Поля формы ({len(inputs)}):")
            for i, inp in enumerate(inputs):
                inp_type = inp.get('type', 'text')
                inp_name = inp.get('name', 'Нет')
                inp_value = inp.get('value', 'Нет')
                inp_id = inp.get('id', 'Нет')
                print(f"   {i+1}. type='{inp_type}', name='{inp_name}', value='{inp_value}', id='{inp_id}'")
        else:
            print("❌ Форма не найдена")
            return False
        
        # 3. Ищем CSRF токен
        csrf_token = None
        for inp in inputs:
            if inp.get('type') == 'hidden':
                csrf_token = inp.get('value')
                if csrf_token:
                    print(f"✅ CSRF токен найден: {csrf_token[:20]}...")
                    break
        
        # 4. Формируем данные для авторизации
        auth_data = {
            'login': '+77025757606',
            'password': '681660'
        }
        
        if csrf_token:
            auth_data['_token'] = csrf_token
        
        # Ищем кнопку submit
        submit_btn = soup.find('input', {'type': 'submit'})
        if submit_btn:
            submit_name = submit_btn.get('name')
            submit_value = submit_btn.get('value')
            if submit_name:
                auth_data[submit_name] = submit_value
            print(f"✅ Кнопка submit: name='{submit_name}', value='{submit_value}'")
        
        print(f"📤 Данные для авторизации: {auth_data}")
        
        # 5. Выполняем авторизацию
        print("📤 Отправляем запрос авторизации...")
        
        auth_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://novasklad.kz',
            'Referer': 'https://novasklad.kz/sign/'
        }
        
        auth_response = session.post(
            "https://novasklad.kz/sign/",
            data=auth_data,
            headers=auth_headers,
            timeout=30,
            allow_redirects=True
        )
        
        print(f"📥 Ответ авторизации: статус {auth_response.status_code}")
        print(f"📥 URL после авторизации: {auth_response.url}")
        
        # Сохраняем ответ
        with open("test_auth_response.html", "w", encoding="utf-8") as f:
            f.write(auth_response.text)
        print("💾 Ответ сохранен в test_auth_response.html")
        
        # 6. Проверяем результат
        if "Войти" in auth_response.text:
            print("❌ Авторизация не удалась - все еще на странице входа")
            return False
        else:
            print("✅ Авторизация успешна!")
            
            # 7. Пробуем получить каталог
            print("📚 Пробуем получить каталог...")
            catalog_response = session.get("https://novasklad.kz/catalog/kitchen-mixers/", timeout=30)
            print(f"📥 Каталог: статус {catalog_response.status_code}")
            
            if catalog_response.status_code == 200:
                with open("test_catalog.html", "w", encoding="utf-8") as f:
                    f.write(catalog_response.text)
                print("💾 Каталог сохранен в test_catalog.html")
                
                # Ищем товары
                catalog_soup = BeautifulSoup(catalog_response.text, 'html.parser')
                products = catalog_soup.find_all(['div', 'li'], class_=lambda x: x and 'product' in x.lower() if x else False)
                print(f"🔍 Найдено товаров: {len(products)}")
                
                if products:
                    print("✅ Товары найдены!")
                    return True
                else:
                    print("⚠️ Товары не найдены")
                    return False
            else:
                print(f"❌ Не удалось получить каталог: {catalog_response.status_code}")
                return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_auth()
    if success:
        print("\n🎉 Тест авторизации прошел успешно!")
    else:
        print("\n💥 Тест авторизации не прошел!")