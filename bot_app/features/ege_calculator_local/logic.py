from bot_app.config import EGE_CALCULATOR_URL, SUBJECT_COUNT_TO_OFFER
# Предполагаем, что у вас есть модуль для загрузки данных о предметах,
# например, core_utils/utils_ege.py или core_utils/data_loader.py
# Если вы используете ваш utils_ege.py:
from bot_app.core_utils.utils_ege import OFFERED_SUBJECTS

# Если вы использовали data_loader.py из моих предыдущих примеров:
# from bot_app.core_utils.data_loader import OFFERED_EGE_SUBJECTS as OFFERED_SUBJECTS

def send_ege_calculator_link_and_scores(bot, chat_id: int):
    """
    Отправляет ссылку на калькулятор ЕГЭ и список первых 11 предметов с минимальными баллами.
    """

    message_text = (
        f"🔗 Калькулятор ЕГЭ ЗабГУ\n\n"
        f"Вы можете воспользоваться официальным калькулятором на сайте университета:\n"
        f"{EGE_CALCULATOR_URL}\n\n"
        f"ℹ Минимальные баллы для поступления (ЕГЭ):\n\n"
    )

    if not OFFERED_SUBJECTS:  # Проверка, что предметы загрузились
        message_text += "Не удалось загрузить информацию о минимальных баллах. Попробуйте позже."
    else:
        # Используем первые COUNT_SUBJECTS_TO_DISPLAY предметов из OFFERED_SUBJECTS
        # OFFERED_SUBJECTS уже содержит первые N предметов, согласно SUBJECT_COUNT_TO_OFFER в config
        # Убедимся, что мы берем не больше, чем доступно и не больше COUNT_SUBJECTS_TO_DISPLAY
        subjects_to_show = OFFERED_SUBJECTS[:SUBJECT_COUNT_TO_OFFER]

        if not subjects_to_show:
            message_text += "Список предметов для отображения пуст."
        else:
            for subject_data in subjects_to_show:
                name = subject_data.get("name", "Неизвестный предмет")
                min_score = subject_data.get("min_score", "н/д")
                message_text += f"• {name}: <b>{min_score}</b>\n"

    message_text += "\nУдачи с выбором!"

    # Отправляем сообщение. parse_mode='HTML' для жирного шрифта и ссылок.
    # disable_web_page_preview=False чтобы ссылка на калькулятор могла сгенерировать превью.
    bot.send_message(chat_id, message_text, parse_mode='HTML', disable_web_page_preview=False)