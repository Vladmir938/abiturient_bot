from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import BTN_EGE_CALCULATOR, BTN_FAQ, BTN_ADMISSION_COMMITTEE, BTN_GEMINI_ASSISTANT


def main_menu_keyboard():
    """Создает клавиатуру главного меню."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn_calculator = KeyboardButton(BTN_EGE_CALCULATOR)
    btn_faq = KeyboardButton(BTN_FAQ)
    btn_admission = KeyboardButton(BTN_ADMISSION_COMMITTEE)
    btn_bot = KeyboardButton(BTN_GEMINI_ASSISTANT)

    markup.add(btn_calculator, btn_faq)
    markup.row(btn_admission, btn_bot)

    # Сюда можно будет добавлять другие кнопки главных функций
    return markup


def cancel_inline_keyboard(callback_data_prefix="cancel_action"):
    """
    Создает инлайн-клавиатуру с кнопкой "Отмена".
    callback_data_prefix используется для создания уникального callback_data, если нужно.
    Например, для калькулятора это будет "ege_cancel".
    """
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Отмена ❌", callback_data=f"{callback_data_prefix}"))
    return markup