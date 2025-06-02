from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Префиксы и данные для callback_data
CALLBACK_PREFIX_FAQ_QUESTION = "faq_q_"
CALLBACK_PREFIX_FAQ_PAGE = "faq_page_"
CALLBACK_BACK_TO_FAQ_LIST_FROM_ANSWER = "faq_ans_back_list"  # Для возврата из ответа к текущей странице списка

# Количество вопросов на одной странице
QUESTIONS_PER_PAGE = 5


def faq_questions_paginated_keyboard(questions_indices_on_page, current_page: int, total_questions: int):
    """
    Создает инлайн-клавиатуру с НОМЕРАМИ вопросов для текущей страницы и кнопками пагинации.
    Текст вопросов будет в самом сообщении.
    :param questions_indices_on_page: Список ОРИГИНАЛЬНЫХ индексов вопросов (из FAQ_QUESTIONS_LIST), которые отображаются на текущей странице.
    :param current_page: Номер текущей страницы (начиная с 0).
    :param total_questions: Общее количество вопросов.
    """
    markup = InlineKeyboardMarkup()

    # Кнопки для выбора вопросов (по их порядковому номеру на странице или глобальному)
    # Для примера, будем использовать глобальный номер (индекс + 1) на кнопке
    question_buttons_row = []
    for i, original_index in enumerate(questions_indices_on_page):
        # На кнопке будет номер вопроса (глобальный)
        question_buttons_row.append(
            InlineKeyboardButton(str(original_index + 1),
                                 callback_data=f"{CALLBACK_PREFIX_FAQ_QUESTION}{original_index}")
        )
        # Создаем ряды по 5 кнопок с номерами (или сколько поместится/хочется)
        if len(question_buttons_row) == QUESTIONS_PER_PAGE or i == len(questions_indices_on_page) - 1:
            markup.row(*question_buttons_row)
            question_buttons_row = []

    # Кнопки пагинации
    pagination_buttons = []
    total_pages = (total_questions + QUESTIONS_PER_PAGE - 1) // QUESTIONS_PER_PAGE

    if current_page > 0:
        pagination_buttons.append(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"{CALLBACK_PREFIX_FAQ_PAGE}{current_page - 1}")
        )

    # Индикатор страницы (опционально, но полезно)
    if total_pages > 1:  # Показываем, только если страниц больше одной
        pagination_buttons.append(
            InlineKeyboardButton(f"Стр. {current_page + 1}/{total_pages}", callback_data="faq_page_indicator")  # no-op
        )

    if current_page < total_pages - 1:
        pagination_buttons.append(
            InlineKeyboardButton("Вперед ➡️", callback_data=f"{CALLBACK_PREFIX_FAQ_PAGE}{current_page + 1}")
        )

    if pagination_buttons:
        markup.row(*pagination_buttons)

    return markup


def faq_answer_keyboard(current_page_for_list: int):
    """
    Клавиатура под ответом, позволяет вернуться к СПИСКУ вопросов (на ту же страницу).
    :param current_page_for_list: Номер страницы списка вопросов, на которую нужно вернуться.
    """
    markup = InlineKeyboardMarkup()
    # Эта кнопка вернет пользователя на ту страницу списка вопросов, с которой он перешел к ответу
    markup.add(InlineKeyboardButton("⬅️ К списку вопросов",
                                    callback_data=f"{CALLBACK_BACK_TO_FAQ_LIST_FROM_ANSWER}{current_page_for_list}"))
    return markup