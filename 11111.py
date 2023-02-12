import time
import math
import os
import csv
from bs4 import BeautifulSoup
import time
from datetime import datetime
import requests
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_all_pages():
    headers = {
        "Accept":"image / avif, image / webp, image / apng, image / svg + xml, image / *, * / *;q = 0.8",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}

    options = webdriver.ChromeOptions()
    options.add_argument(headers)
    # options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(r'C:\Windows\chromedriver.exe'))  # , options=options)
    url = 'http://volgainfo.net/togliatti/search/kvartiryi/SEARCH_BEGINPOS=0'
    try:
        driver.get(url)
        if not os.path.exists(
                "1111"):  # Напишем условие для создания директорий, в которых будем сохраниять html файл, Чтобы не засорять дерево проекта
            os.mkdir("1111")
        with open("1111/page_0.html", 'w', encoding='utf-8') as file:
            file.write(driver.page_source)

        with open("1111/page_0.html", encoding='utf-8') as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        digs = []
        for word in soup.find("div", class_="podstxt").string.split():
            if word.isdigit():
                digs.append(int(word))
        pages_count = math.ceil(digs[0]//digs[1])*digs[1]
        print(pages_count)
        for i in range(digs[1], pages_count + 1, digs[1]):
            url = f"http://volgainfo.net/togliatti/search/kvartiryi/SEARCH_BEGINPOS={i}"
            print(url)
            driver.get(url)  # отправляем запрос в цикле к каждой из страниц
            with open(f"1111/page_{i}.html", "w", encoding='utf-8') as file:   # сохраняем запросы под разными именами. Имя будет отличаться цифрой в соответствии с номером итерации
                file.write(driver.page_source)

            time.sleep(1)    # поставим небольшую паузу между каждой итерацией, чтобы запрос успел подгрузить данные

        return pages_count + 1   # функция возвращает кол-во страниц


        # time.sleep(10)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def main():
    get_all_pages()


if __name__ == '__main__':
    main()

def collect_data(pages_count):  # новая функция принимает кол-во страниц из предыдущей ф-ции
    cur_date = datetime.now().strftime("%d_%m_%Y")

    with open(f"data_{cur_date}.csv", "w", encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(  # указываем заголовки столбцов
            (
                "Кол-во комнат",
                "Район",
                "Этажность",
                "Общая площадь",
                "Жилая площадь",
                "Площадь кухни",
                "Планировка",
                "Цена"

            )
        )

    data = []
    for page in range(0, pages_count+1, 20):  # в цикле читаем полученные ранее страницы
        with open(f"1111/page_{page}.html", encoding='utf-8') as file:  # открываем файл и сохраняем содержимое в переменную src
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        items_cards = soup.find_all('tr', valign="top")  # получаем список из нужных карточек
        # print(items_cards)

        for item in items_cards[0:(len(items_cards)-2)]:
            rooms = item.find('center').text  # заберем количество комнат
            location = item.find(id="s-city").text
            specs = item.find_all('td')#, 'td')#.text  # заберем этаж

            floor = specs[2].text
            area = specs[3].text.split(sep='/')
            total = area[0]
            living = area[1]
            kitchen = area[2].split(sep="\n")[0]
            walls = area[2].split(sep="\n")[1] + "/" + area[3]
            price = specs[4].text

            data.append(
                {
                    "rooms": rooms,
                    "location": location,
                    "floor": floor,
                    "total": total,
                    "living": living,
                    "kitchen": kitchen,
                    "walls": walls,
                    "price": price
                }
            )
        #
            with open(f"data_{cur_date}.csv", "a", encoding='utf-8') as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        rooms,
                        location,
                        floor,
                        total,
                        living,
                        kitchen,
                        walls,
                        price
                    )
                )

        print(f"[INFO] Обработана страница {page}/20")


def main():
    pages_count = get_all_pages()
    collect_data(pages_count=pages_count)


if __name__ == '__main__':
    main()