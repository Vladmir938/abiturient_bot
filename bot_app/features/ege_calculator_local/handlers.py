from telebot.types import Message
from bot_app.config import BTN_EGE_CALCULATOR_LOCAL # Текст новой кнопки
from .logic import send_ege_calculator_link_and_scores

def register_ege_calculator_local_handlers(bot):
    """
    Регистрирует обработчики для модуля 'Локальный Калькулятор ЕГЭ (ссылка)'.
    """

    @bot.message_handler(func=lambda message: message.text == BTN_EGE_CALCULATOR_LOCAL)
    def ege_calculator_local_entry(message: Message):
        send_ege_calculator_link_and_scores(bot, message.chat.id)