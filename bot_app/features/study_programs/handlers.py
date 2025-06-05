from telebot.types import Message
from bot_app.config import (
    BTN_STUDY_PROGRAMS,
    BTN_SP_BACHELOR, BTN_SP_MASTER,
    BTN_SP_POSTGRADUATE, BTN_SP_SPO,
    BTN_BACK_TO_MAIN  # Общая кнопка "Назад"
)
from .logic import (
    show_study_programs_menu,
    send_program_links,
    go_back_to_main_menu_from_sp
)


def register_study_programs_handlers(bot):
    """Регистрирует обработчики для модуля 'Программы обучения'."""

    # 1. Вход в меню "Программы обучения"
    @bot.message_handler(func=lambda message: message.text == BTN_STUDY_PROGRAMS)
    def study_programs_entry(message: Message):
        show_study_programs_menu(bot, message.chat.id)

    # 2. Обработка кнопок подменю
    @bot.message_handler(func=lambda message: message.text == BTN_SP_BACHELOR)
    def sp_bachelor_handler(message: Message):
        send_program_links(bot, message.chat.id, "bachelor")

    @bot.message_handler(func=lambda message: message.text == BTN_SP_MASTER)
    def sp_master_handler(message: Message):
        send_program_links(bot, message.chat.id, "master")

    @bot.message_handler(func=lambda message: message.text == BTN_SP_POSTGRADUATE)
    def sp_postgraduate_handler(message: Message):
        send_program_links(bot, message.chat.id, "postgraduate")

    @bot.message_handler(func=lambda message: message.text == BTN_SP_SPO)
    def sp_spo_handler(message: Message):
        send_program_links(bot, message.chat.id, "spo")

    # 3. Обработка кнопки "В главное меню" из подменю "Программы обучения"
    @bot.message_handler(func=lambda message: message.text == BTN_BACK_TO_MAIN)
    def sp_back_to_main_handler(message: Message):
        go_back_to_main_menu_from_sp(bot, message.chat.id)