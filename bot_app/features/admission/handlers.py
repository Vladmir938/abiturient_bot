from telebot.types import Message
from bot_app.config import BTN_ADMISSION_COMMITTEE, BTN_AC_CONTACTS, BTN_AC_DOCUMENTS, BTN_BACK_TO_MAIN, \
    BTN_AC_SUBMISSION_DATES
from .logic import show_admission_committee_menu, show_contacts, show_documents_info, go_back_to_main_menu, \
    show_submission_dates_link

def register_admission_committee_handlers(bot):
    """Регистрирует обработчики для модуля 'Приёмная комиссия'."""

    # 1. Вход в меню "Приёмная комиссия"
    @bot.message_handler(func=lambda message: message.text == BTN_ADMISSION_COMMITTEE)
    def admission_committee_entry(message: Message):
        show_admission_committee_menu(bot, message.chat.id)

    # 2. Обработка кнопок внутри меню "Приёмная комиссия"
    # (Используем текстовые совпадения, так как это ReplyKeyboard)
    @bot.message_handler(func=lambda message: message.text == BTN_AC_CONTACTS)
    def ac_contacts_handler(message: Message):
        # Проверяем, чтобы этот хендлер не сработал случайно, если пользователь не в меню ПК
        # Это можно сделать через состояния (FSM), если меню становится сложнее.
        # Пока что, если пользователь нажал кнопку "Контакты", он, скорее всего, в нужном меню.
        show_contacts(bot, message.chat.id)
        # После показа информации, можно снова показать меню "Приёмная комиссия"
        # или оставить пользователя с текущей клавиатурой.
        # Для простоты, оставим текущую клавиатуру (меню Приёмной комиссии).
        # Если нужно вернуться или показать другое, добавьте:
        # show_admission_committee_menu(bot, message.chat.id)

    @bot.message_handler(func=lambda message: message.text == BTN_AC_DOCUMENTS)
    def ac_documents_handler(message: Message):
        show_documents_info(bot, message.chat.id)
        # Аналогично, можно снова показать меню или оставить так.

    # 3. Обработка кнопки "В главное меню" из подменю "Приёмная комиссия"
    @bot.message_handler(func=lambda message: message.text == BTN_BACK_TO_MAIN)
    def ac_back_to_main_handler(message: Message):
        # Здесь важно, чтобы эта кнопка обрабатывалась только когда мы ожидаем ее
        # (т.е. когда активна клавиатура admission_committee_menu_keyboard).
        # Если эта кнопка с таким же текстом может появиться в других контекстах,
        # нужно будет использовать состояния FSM для более точной маршрутизации.
        # Для простоты пока предполагаем, что текст уникален для этого меню
        # или пользователь явно находится в этом "режиме".
        go_back_to_main_menu(bot, message.chat.id)

    # Сроки подачи документов
    @bot.message_handler(func=lambda message: message.text == BTN_AC_SUBMISSION_DATES)
    def ac_submission_dates_handler(message: Message):
        show_submission_dates_link(bot, message.chat.id)