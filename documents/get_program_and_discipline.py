import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd

# URL страницы с таблицами программ обучения
TABLE_URL = "https://zabgu.ru/php/educational_programs_table.php"
DISCIPLINES_URL = "https://zabgu.ru/php/educational_parser_utilities.php"

HEADERS_TABLE = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://zabgu.ru",
    "Referer": TABLE_URL,
}

HEADERS_DISCIPLINE = {
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

session = requests.Session()
session.headers.update(HEADERS_TABLE)

def fetch_all_tables():
    response = session.get(TABLE_URL)
    response.raise_for_status()
    return pd.read_html(response.text)


def fetch_disciplines(year, speciality, profile):
    data = {
        "year": year,
        "speciality": speciality,
        "profile": profile,
    }
    try:
        response = requests.post(DISCIPLINES_URL, headers=HEADERS_DISCIPLINE, data=data)
        result = response.json()
        disciplines = []

        if result.get("answer") == "success" and result.get("links"):
            for sublist in result["links"]:
                if isinstance(sublist, list) and sublist:
                    for item in sublist:
                        disciplines.append({
                            "id": item.get("id"),
                            "label": item.get("label"),
                            "edu_form": item.get("edu_form"),
                        })

        return disciplines
    except Exception as e:
        print(f"Ошибка при получении дисциплин: {e}")
        return []


def parse_programs_from_table(df):
    programs = []
    for _, row in df.iterrows():
        program = {
            "Код": row.get("Код, шифр", ""),
            "Наименование": row.get("Наименование профессии, специальности, направления подготовки, наименование группы научных специальностей", ""),
            "Уровень образования": row.get("Уровень образования", ""),
            "Образовательная программа": row.get("Образовательная программа, направленность, профиль, шифр и наименование научной специальности", ""),
            "Форма обучения": row.get("Реализуемые формы обучения", ""),
        }

        code = str(program["Код"] or "").strip()
        profile = str(program["Образовательная программа"] or "").strip()
        disciplines = []

        if code and profile:
            for year in range(2025, 2019, -1):
                disciplines = fetch_disciplines(str(year), str(code), str(profile))
                if disciplines:
                    print(f"Найдены дисциплины для {code} {profile} за {year}")
                    break
                time.sleep(0.3)
            program["Дисциплины"] = disciplines
        else:
            program["Дисциплины"] = []

        programs.append(program)
    return programs


def main():
    tables = fetch_all_tables()
    all_programs = []

    for df in tables:
        programs = parse_programs_from_table(df)
        all_programs.extend(programs)

    with open("../bot_app/data/educational_programs.json", "w", encoding="utf-8") as f:
        json.dump(all_programs, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
