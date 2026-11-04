from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import quote, unquote, urlparse

browser = webdriver.Firefox()

# Получаем первоначальный запрос.
query = input("Что найти в Википедии? ")

browser.get(
    "https://ru.wikipedia.org/w/index.php?search=" + quote(query)
)

# Если появился список результатов, открываем первый.
results = browser.find_elements(
    By.CSS_SELECTOR,
    ".mw-search-result-heading a"
)

if results:
    url = results[0].get_attribute("href")
    if url:
        browser.get(url)

# Главное меню.
while True:
    title = browser.find_element(By.ID, "firstHeading").text

    print(f"\nТекущая страница: {title}")
    print("1 — Читать абзацы статьи")
    print("2 — Перейти по ссылке из текста статьи")
    print("3 — Выйти")

    choice = input("Выберите действие: ").strip()

    if choice == "1":
        paragraphs = browser.find_elements(
            By.CSS_SELECTOR,
            "#mw-content-text .mw-parser-output p"
        )

        # Сохраняем только непустые тексты абзацев.
        texts = []

        for paragraph in paragraphs:
            text = paragraph.text.strip()

            if text:
                texts.append(text)

        if not texts:
            print("Абзацы не найдены.")
            continue

        for number, text in enumerate(texts, start=1):
            print(f"\n--- Абзац {number} из {len(texts)} ---")
            print(text)

            if number == len(texts):
                print("\nВсе абзацы прочитаны.")
                break

            answer = input(
                "\nEnter — следующий абзац, 0 — вернуться в меню: "
            ).strip()

            if answer == "0":
                break

    elif choice == "2":
        # Ищем ссылки только внутри абзацев.
        links = browser.find_elements(
            By.CSS_SELECTOR,
            "#mw-content-text .mw-parser-output p a[href]"
        )

        articles = []
        seen = set()

        current_path = unquote(
            urlparse(browser.current_url).path
        )

        for link in links:
            text = link.text.strip()
            url = link.get_attribute("href")

            if not text or not url:
                continue

            address = urlparse(url)
            path = unquote(address.path)

            # Оставляем внутренние ссылки на обычные статьи.
            if (
                address.netloc == "ru.wikipedia.org"
                and path.startswith("/wiki/")
                and ":" not in path
                and path != current_path
                and path != "/wiki/Заглавная_страница"
                and path not in seen
            ):
                seen.add(path)

                # Открываем статью целиком, без якоря и параметров.
                article_url = (
                    "https://ru.wikipedia.org" + address.path
                )

                articles.append((text, article_url))

        if not articles:
            print("В абзацах статьи подходящие ссылки не найдены.")
            continue

        print("\nСсылки из текста статьи:")

        for number, (text, url) in enumerate(articles, start=1):
            print(f"{number}. {text}")

        number = input(
            "\nВведите номер статьи или 0 для возврата: "
        ).strip()

        if number == "0":
            continue

        if number.isdigit() and 1 <= int(number) <= len(articles):
            text, url = articles[int(number) - 1]

            print(f"\nОткрываем: {text}")
            browser.get(url)
        else:
            print("Неверный номер статьи.")

    elif choice == "3":
        print("Программа завершена.")
        break

    else:
        print("Введите 1, 2 или 3.")

browser.quit()