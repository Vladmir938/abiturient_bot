from telebot.types import Message, CallbackQuery

from bot_app.config import BTN_GEMINI_ASSISTANT
from bot_app.states import GeminiAssistantStates
from .logic import request_gemini_question, process_gemini_question, cancel_gemini_question_process
from .keyboards import CALLBACK_GEMINI_CANCEL_QUESTION


def register_gemini_assistant_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == BTN_GEMINI_ASSISTANT)
    def gemini_assistant_entry(message: Message):
        request_gemini_question(bot, message.chat.id, message.from_user.id)

    # Обработчик текстового сообщения, когда ожидается вопрос к Gemini
    @bot.message_handler(state=GeminiAssistantStates.waiting_for_question, content_types=['text'])
    def handle_user_question_for_gemini(message: Message):
        # Убедимся, что это не команда /cancel, если вдруг пользователь ее введет текстом
        if message.text.startswith('/'):
            # Можно добавить обработку /cancel здесь или положиться на глобальный
            if message.text == '/cancel':
                return 
        process_gemini_question(bot, message)

    # Обработчик для других типов контента (не текст) в состоянии ожидания вопроса
    @bot.message_handler(state=GeminiAssistantStates.waiting_for_question,
                         content_types=['audio', 'photo', 'voice', 'video', 'document', 'location', 'contact', 'sticker'])
    def handle_unsupported_content_for_gemini(message: Message):
        bot.reply_to(message,
                     "Пожалуйста, задайте ваш вопрос текстом. Я не умею обрабатывать другие форматы.\n"
                     "Чтобы отменить, нажмите кнопку 'Отмена' ниже или введите /cancel.",
                     reply_markup=None) # Клавиатура "Отмена" должна быть уже у предыдущего сообщения бота

    # Обработчик нажатия инлайн-кнопки "Отмена"
    @bot.callback_query_handler(func=lambda call: call.data == CALLBACK_GEMINI_CANCEL_QUESTION,
                                state=GeminiAssistantStates.waiting_for_question)
    def gemini_cancel_button_handler(call: CallbackQuery):
        cancel_gemini_question_process(bot, call)