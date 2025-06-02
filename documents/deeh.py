import requests

url = "https://zabgu.ru/php/educational_parser_utilities.php"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
    "Accept": "*/*",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "X-KL-kfa-Ajax-Request": "Ajax_Request",
    "Origin": "https://zabgu.ru",
    "Referer": "https://zabgu.ru/php/educational_programs_table.php",
    "Connection": "keep-alive",
}

payload = {
    "year": "2024",
    "speciality": "09.03.03",
    "profile": "Прикладная информатика в цифровой экономике"
}

response = requests.post(url, headers=headers, data=payload)

# Проверка результата
print("Status code:", response.status_code)
try:
    data = response.json()
    print("Ответ JSON:", data)
except Exception as e:
    print("Ошибка парсинга JSON:", e)
    print("Ответ как текст:", response.text)
