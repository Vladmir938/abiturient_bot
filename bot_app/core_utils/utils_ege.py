import json
import requests

from bot_app.config import ZABGU_API_URL, API_HEADERS, API_COOKIES, SUBJECT_COUNT_TO_OFFER

# Максимальная длина сообщения в Telegram
MAX_MESSAGE_LENGTH = 4096

# --- Загрузка данных о предметах ---
ALL_SUBJECTS_DATA = []
try:
    with open('data/entrance_exam_scores.json', 'r', encoding='utf-8') as f:
        ALL_SUBJECTS_DATA = json.load(f)
except FileNotFoundError:
    print(
        "ОШИБКА: Файл data/entrance_exam_scores.json не найден. Проверьте путь!")
except json.JSONDecodeError:
    print("ОШИБКА: Некорректный формат JSON в data/entrance_exam_scores.json.")

OFFERED_SUBJECTS = ALL_SUBJECTS_DATA[:SUBJECT_COUNT_TO_OFFER]


def get_subject_min_score(subject_name):
    for subject_data in ALL_SUBJECTS_DATA:
        if subject_data.get('name') == subject_name:
            return subject_data.get('min_score', 0)
    return 0


def fetch_programs_from_zabgu(selected_subjects_with_scores):
    if not selected_subjects_with_scores:
        print("utils_ege: Нет выбранных предметов для запроса к API.")  # Оставил print
        return None
    params = []
    for subject_name, score in selected_subjects_with_scores:
        params.append(("arrayForSendingWithMinCount[]", str(score)))
        params.append(("arrayForSendingWithPredmet[]", subject_name))
    params.extend([("spo", "0"), ("diplom", "0"), ("gto", "0")])
    # print(f"utils_ege: Запрос к API с параметрами: {params}")
    try:
        response = requests.get(ZABGU_API_URL, headers=API_HEADERS, params=params, cookies=API_COOKIES, timeout=20)
        response.raise_for_status()
        # print(f"utils_ege: Ответ от API получен, статус {response.status_code}")
        return response.json()
    except requests.exceptions.Timeout:
        print(f"utils_ege: Таймаут запроса к {ZABGU_API_URL}")
        return None
    except requests.exceptions.HTTPError as http_err:
        print(f"utils_ege: HTTP ошибка: {http_err} - {response.text[:200]}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"utils_ege: Общая ошибка запроса: {e}")
        return None
    except ValueError:
        print(
            f"utils_ege: Ошибка декодирования JSON. Ответ: {response.text[:200] if 'response' in locals() and hasattr(response, 'text') else 'Ответ не получен или не содержит текст'}")  # Оставил print
        return None


def format_programs_for_sending(api_data):
    """
    Форматирует ответ от API и возвращает СПИСОК сообщений, готовых к отправке.
    Каждый элемент списка - это строка, не превышающая MAX_MESSAGE_LENGTH.
    Программы выводятся списком, БЕЗ явной группировки по формам обучения в виде заголовков.
    """
    # print(f"utils_ege: Форматирование данных API: {str(api_data)[:200]}...")
    if not api_data or not isinstance(api_data, dict):
        return [
            "По вашим предметам и баллам подходящих программ не найдено, или получен некорректный ответ от сервера."]

    messages_to_send = []
    current_message_text = "<b>✨ Найденные программы обучения:</b>\n\n"
    found_programs_at_all = False  # Флаг, что найдена хотя бы одна программа

    # Сначала собираем все программы в один "плоский" список, сохраняя форму обучения
    all_programs_flat_list = []
    for form_of_study, programs_dict in api_data.items():
        if not programs_dict or not isinstance(programs_dict, dict):
            continue
        for program_full_name_key, details in programs_dict.items():
            if not isinstance(details, dict):
                continue
            all_programs_flat_list.append({
                "form_of_study": form_of_study,  # Сохраняем форму обучения
                "program_key": program_full_name_key,  # "Код - Название направления"
                "details": details
            })
            found_programs_at_all = True

    if not found_programs_at_all:
        return ["По вашим предметам и баллам подходящих программ не найдено."]

    # Теперь итерируемся по этому плоскому списку и формируем сообщения
    is_first_program_in_current_message = True  # Для управления начальным заголовком в новых сообщениях

    for program_data in all_programs_flat_list:
        form_of_study = program_data["form_of_study"]
        details = program_data["details"]

        code = details.get('code', 'не указан')
        profile_name = details.get('profile', 'Название профиля не указано')
        program_title = f"{code} - {profile_name}"  # "Код - Название Профиля"
        budget_places = details.get('number_of_budget_places', 'н/д')
        passing_score = details.get('passing_score', 'н/д')

        # Формируем блок текста для одной программы
        program_block = (
            f"🔹 <b>{program_title}</b>\n"
            f"   Форма обучения: {form_of_study}\n"  # Указываем форму для каждой программы
            f"   Бюджетных мест: {budget_places}\n"
            f"   Проходной балл (ориентир): {passing_score}\n\n"
        )

        # Если текущее сообщение пустое (или содержит только начальный заголовок),
        # и мы начинаем новое сообщение, добавляем общий заголовок.
        if is_first_program_in_current_message and not current_message_text.startswith(
                "<b>✨ Найденные программы обучения:</b>"):
            current_message_text = "<b>✨ Найденные программы обучения:</b>\n\n" + current_message_text

        is_first_program_in_current_message = False  # Сбрасываем флаг после первой программы в сообщении

        # Проверяем, поместится ли блок в текущее сообщение
        if len(current_message_text) + len(program_block) > MAX_MESSAGE_LENGTH:
            # Завершаем текущее сообщение
            if current_message_text.strip() and current_message_text.strip() != "<b>✨ Найденные программы обучения:</b>":
                messages_to_send.append(current_message_text.strip())

            # Начинаем новое сообщение с общего заголовка и текущего блока программы
            current_message_text = "<b>✨ Найденные программы обучения:</b>\n\n" + program_block
            is_first_program_in_current_message = False  # Уже не первый блок
        else:
            current_message_text += program_block

    # Добавляем последнее собранное сообщение, если оно не пустое (и не только заголовок)
    if current_message_text.strip() and current_message_text.strip() != "<b>✨ Найденные программы обучения:</b>":
        messages_to_send.append(current_message_text.strip())

    if not messages_to_send:  # Если так и не собрали ни одного сообщения с программами
        return ["Не удалось сформировать список программ. Проверьте входные данные."]

    return messages_to_send