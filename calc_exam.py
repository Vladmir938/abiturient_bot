import requests

url = "https://entrant.zabgu.ru/wp-content/themes/twentytwelve/page-templates/crudForCalc/crudForCalcAjax.php"

params = [
    ("arrayForSendingWithMinCount[]", "50"),
    ("arrayForSendingWithMinCount[]", "50"),
    ("arrayForSendingWithMinCount[]", "2"),
    ("arrayForSendingWithPredmet[]", "Русский язык"),
    ("arrayForSendingWithPredmet[]", "Математика профильного уровня"),
    ("arrayForSendingWithPredmet[]", "История"),
    ("spo", "0"),
    ("diplom", "0"),
    ("gto", "0"),
]

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "X-KL-kfa-Ajax-Request": "Ajax_Request",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
    "Referer": "https://entrant.zabgu.ru/?page_id=4569",
}

cookies = {
    "agreement": "1"
}

response = requests.get(url, headers=headers, params=params, cookies=cookies)

if response.ok:
    try:
        data = response.json()
        import json
        print(json.dumps(data, ensure_ascii=False, indent=4))
    except ValueError:
        print("Ответ не в формате JSON:")
        print(response.text)
else:
    print(f"Ошибка запроса: {response.status_code}")