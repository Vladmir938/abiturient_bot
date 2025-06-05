from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from bot_app.config import (
    BTN_SP_BACHELOR, BTN_SP_MASTER,
    BTN_SP_POSTGRADUATE, BTN_SP_SPO,
    BTN_BACK_TO_MAIN
)


def study_programs_menu_keyboard():
    """
    Создает ReplyKeyboard для подменю "Программы обучения".
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn_bachelor = KeyboardButton(BTN_SP_BACHELOR)
    btn_master = KeyboardButton(BTN_SP_MASTER)
    btn_postgraduate = KeyboardButton(BTN_SP_POSTGRADUATE)
    btn_spo = KeyboardButton(BTN_SP_SPO)
    btn_back = KeyboardButton(BTN_BACK_TO_MAIN)

    markup.row(btn_bachelor, btn_master)
    markup.row(btn_postgraduate, btn_spo)
    markup.row(btn_back)
    return markup