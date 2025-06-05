from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import BTN_EGE_CALCULATOR, BTN_FAQ, BTN_ADMISSION_COMMITTEE, BTN_VIRTUAL_ASSISTANT, BTN_STUDY_PROGRAMS, \
    BTN_EGE_CALCULATOR_LOCAL


def main_menu_keyboard():
    """Создает клавиатуру главного меню."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    # btn_calculator = KeyboardButton(BTN_EGE_CALCULATOR)
    btn_faq = KeyboardButton(BTN_FAQ)
    btn_admission = KeyboardButton(BTN_ADMISSION_COMMITTEE)
    btn_virtual_assistant = KeyboardButton(BTN_VIRTUAL_ASSISTANT)
    btn_study_programs = KeyboardButton(BTN_STUDY_PROGRAMS)
    btn_calculator_local = KeyboardButton(BTN_EGE_CALCULATOR_LOCAL)

    markup.add(btn_calculator_local, btn_study_programs)
    markup.row(btn_admission, btn_virtual_assistant)
    markup.add(btn_faq)

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