from telebot.types import ReplyKeyboardMarkup, KeyboardButton  # Используем ReplyKeyboard для этого меню
from bot_app.config import BTN_AC_CONTACTS, BTN_AC_DOCUMENTS, BTN_BACK_TO_MAIN, BTN_AC_SUBMISSION_DATES
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# Callback data префиксы (если бы использовали InlineKeyboard)
CALLBACK_AC_CONTACTS = "ac_contacts"
CALLBACK_AC_DOCUMENTS = "ac_docs"
CALLBACK_AC_BACK_MAIN = "ac_back_main"

def admission_committee_menu_keyboard():
    """
    Создает ReplyKeyboard для подменю "Приёмная комиссия".
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 one_time_keyboard=False)  # one_time_keyboard=False для постоянного меню
    btn_contacts = KeyboardButton(BTN_AC_CONTACTS)
    btn_documents = KeyboardButton(BTN_AC_DOCUMENTS)
    btn_back = KeyboardButton(BTN_BACK_TO_MAIN)
    btn_submission_dates = KeyboardButton(BTN_AC_SUBMISSION_DATES)

    markup.row(btn_contacts, btn_documents)
    markup.row(btn_submission_dates)
    markup.row(btn_back)
    return markup


# # Если для ответов (контакты, документы) нужны будут инлайн-кнопки "Назад", можно их добавить здесь
# def back_to_admission_menu_inline_keyboard():
#     markup = InlineKeyboardMarkup()
#     markup.add(InlineKeyboardButton("⬅️ К меню 'Приёмная комиссия'", callback_data=CALLBACK_AC_BACK_MENU))
#     return markup