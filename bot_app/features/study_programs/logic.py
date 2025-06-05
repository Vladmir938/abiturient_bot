from .keyboards import study_programs_menu_keyboard  # Клавиатура подменю
from bot_app.keyboards import main_menu_keyboard  # Главное меню для возврата

# --- Данные о программах и ссылки ---
PROGRAM_LINKS = {
    "bachelor": {
        "title": "Бакалавриат и специалитет",
        "links": [
            ("Очная форма",
             "https://entrant.zabgu.ru/abitur/02%20-%20%D0%9A%D0%A6%D0%9F/%D0%9A%D0%A6%D0%9F%20%D0%B1%D0%B0%D0%BA%D0%B0%D0%BB%D0%B0%D0%B2%D1%80%D0%B8%D0%B0%D1%82%20%D0%BE%D1%87%D0%BD%D0%B0%D1%8F%20%D1%84%D0%BE%D1%80%D0%BC%D0%B0.pdf"),
            ("Очно-заочная форма",
             "https://entrant.zabgu.ru/abitur/02%20-%20%D0%9A%D0%A6%D0%9F/%D0%9A%D0%A6%D0%9F%20%D0%B1%D0%B0%D0%BA%D0%B0%D0%BB%D0%B0%D0%B2%D1%80%D0%B8%D0%B0%D1%82%20%D0%BE%D1%87%D0%BD%D0%BE-%D0%B7%D0%B0%D0%BE%D1%87%D0%BD%D0%B0%D1%8F%20%D1%84%D0%BE%D1%80%D0%BC%D0%B0.pdf"),
            ("Заочная форма",
             "https://entrant.zabgu.ru/abitur/02%20-%20%D0%9A%D0%A6%D0%9F/%D0%9A%D0%A6%D0%9F%20%D0%B1%D0%B0%D0%BA%D0%B0%D0%BB%D0%B0%D0%B2%D1%80%D0%B8%D0%B0%D1%82%20%D0%B7%D0%B0%D0%BE%D1%87%D0%BD%D0%B0%D1%8F%20%D1%84%D0%BE%D1%80%D0%BC%D0%B0.pdf")
        ]
    },
    "master": {
        "title": "Магистратура",
        "links": [
            ("Очная форма",
             "https://entrant.zabgu.ru/abitur/02%20-%20%D0%9A%D0%A6%D0%9F/%D0%9A%D0%A6%D0%9F%20%D0%BC%D0%B0%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%82%D1%83%D1%80%D0%B0%20%D0%BE%D1%87%D0%BD%D0%B0%D1%8F%20%D1%84%D0%BE%D1%80%D0%BC%D0%B0.pdf"),
            ("Очно-заочная форма",
             "https://entrant.zabgu.ru/abitur/02%20-%20%D0%9A%D0%A6%D0%9F/%D0%9A%D0%A6%D0%9F%20%D0%BC%D0%B0%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%82%D1%83%D1%80%D0%B0%20%D0%BE%D1%87%D0%BD%D0%BE-%D0%B7%D0%B0%D0%BE%D1%87%D0%BD%D0%B0%D1%8F%20%D1%84%D0%BE%D1%80%D0%BC%D0%B0.pdf"),
            ("Заочная форма",
             "https://entrant.zabgu.ru/abitur/02%20-%20%D0%9A%D0%A6%D0%9F/%D0%9A%D0%A6%D0%9F%20%D0%BC%D0%B0%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%82%D1%83%D1%80%D0%B0%20%D0%B7%D0%B0%D0%BE%D1%87%D0%BD%D0%B0%D1%8F%20%D1%84%D0%BE%D1%80%D0%BC%D0%B0.pdf")
        ]
    },
    "postgraduate": {
        "title": "Аспирантура",
        "links": [
            ("Очная форма",
             "https://entrant.zabgu.ru/abitur/02%20-%20%D0%9A%D0%A6%D0%9F/%D0%9A%D0%A6%D0%9F%20%D0%B0%D1%81%D0%BF%D0%B8%D1%80%D0%B0%D0%BD%D1%82%D1%83%D1%80%D0%B0%20%D0%BE%D1%87%D0%BD%D0%B0%D1%8F%20%D1%84%D0%BE%D1%80%D0%BC%D0%B0.pdf")
        ]
    },
    "spo": {
        "title": "Среднее профессиональное образование (СПО)",
        "links": [
            ("На базе 9 классов",
             "https://entrant.zabgu.ru/abitur/02%20-%20%D0%9A%D0%A6%D0%9F/%D0%9A%D0%A6%D0%9F%20%D0%A1%D0%9F%D0%9E%209.pdf"),
            ("На базе 11 классов",
             "https://entrant.zabgu.ru/abitur/02%20-%20%D0%9A%D0%A6%D0%9F/%D0%9A%D0%A6%D0%9F%20%D0%A1%D0%9F%D0%9E%2011.pdf")
        ]
    }
}


def show_study_programs_menu(bot, chat_id: int):
    """Показывает меню 'Программы обучения'."""
    bot.send_message(chat_id, "Выберите уровень образования:", reply_markup=study_programs_menu_keyboard())


def send_program_links(bot, chat_id: int, program_type_key: str):
    """Отправляет ссылки для выбранного типа программ."""
    program_data = PROGRAM_LINKS.get(program_type_key)

    if not program_data:
        bot.send_message(chat_id, "Информация по данному типу программ не найдена.")
        return

    title = program_data.get("title", "Программы обучения")
    links_list = program_data.get("links", [])

    if not links_list:
        bot.send_message(chat_id, f"Для '{title}' ссылки на программы не указаны.")
        return

    message_text = f"🔗 <b>{title}</b>\n\n"
    for link_name, link_url in links_list:
        # Используем HTML для ссылок, так как Markdown может конфликтовать с URL
        message_text += f'• <a href="{link_url}">{link_name}</a>\n'

    # Отправляем сообщение. Клавиатуру подменю "Программы обучения" оставляем активной.
    bot.send_message(chat_id, message_text, parse_mode='HTML', disable_web_page_preview=True)
    # Если нужно, можно снова показать меню после отправки ссылок:
    # show_study_programs_menu(bot, chat_id)


def go_back_to_main_menu_from_sp(bot, chat_id: int):  # sp - study programs
    """Возвращает пользователя в главное меню из раздела 'Программы обучения'."""
    bot.send_message(chat_id, "Вы вернулись в главное меню.", reply_markup=main_menu_keyboard())