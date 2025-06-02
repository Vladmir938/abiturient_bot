from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Callback data для кнопки отмены в этом модуле
CALLBACK_GEMINI_CANCEL_QUESTION = "gemini_cancel_q"

def gemini_cancel_question_keyboard():
    """
    Создает инлайн-клавиатуру с одной кнопкой "Отмена" для процесса задания вопроса ассистенту.
    """
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Отмена ❌", callback_data=CALLBACK_GEMINI_CANCEL_QUESTION))
    return markup