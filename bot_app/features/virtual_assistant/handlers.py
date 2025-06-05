from telebot.types import Message, CallbackQuery
from .logic import process_gemini_question
from bot_app.config import BTN_VIRTUAL_ASSISTANT


def register_gemini_assistant_handlers(bot):

    # Обработчик для других типов контента (не текст) в состоянии ожидания вопроса
    @bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document', 'location', 'contact', 'sticker'])
    def handle_unsupported_content_for_gemini(message: Message):
        bot.reply_to(message,
                     "Пожалуйста, задайте ваш вопрос текстом. Я не умею обрабатывать другие форматы.",
                     reply_markup=None)

    @bot.message_handler(func=lambda message: message.text == BTN_VIRTUAL_ASSISTANT)
    def handle_gemini_assistant_button(message: Message):
        # Формулировка сообщения:
        response_text = (
            "Чтобы задать мне вопрос, просто напишите его в этот чат. ✍️\n"
            "Я постараюсь предоставить самую актуальную информацию! 💡"
        )
        bot.send_message(message.chat.id, response_text)

    @bot.message_handler(content_types=['text'])
    def handle_user_question_for_gemini(message: Message):
        # Убедимся, что это не команда /cancel, если вдруг пользователь ее введет текстом
        if message.text.startswith('/'):
            # Можно добавить обработку /cancel здесь или положиться на глобальный
            if message.text == '/cancel':
                return
        process_gemini_question(bot, message)