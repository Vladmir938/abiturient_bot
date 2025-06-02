from telebot.types import Message, CallbackQuery
from bot_app.config import BTN_FAQ
from .logic import send_faq_page, send_faq_answer
from .keyboards import (
    CALLBACK_PREFIX_FAQ_QUESTION,
    CALLBACK_PREFIX_FAQ_PAGE,
    CALLBACK_BACK_TO_FAQ_LIST_FROM_ANSWER
)

# Для хранения текущей страницы пользователя при просмотре ответа
# Это простой способ, для более сложных сценариев лучше использовать FSM или user_data
user_current_faq_page = {}


def register_faq_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == BTN_FAQ)
    def faq_entry_handler(message: Message):
        # При первом входе показываем первую страницу (page_num=0)
        send_faq_page(bot, message.chat.id, page_num=0)
        user_current_faq_page[message.from_user.id] = 0  # Сохраняем текущую страницу

    # Обработчик нажатия на кнопку с вопросом
    @bot.callback_query_handler(func=lambda call: call.data.startswith(CALLBACK_PREFIX_FAQ_QUESTION))
    def faq_question_selected_handler(call: CallbackQuery):
        # Получаем текущую страницу из сохраненных данных или предполагаем 0
        current_page = user_current_faq_page.get(call.from_user.id, 0)
        send_faq_answer(bot, call, current_page_for_list=current_page)
        bot.answer_callback_query(
            call.id)  # Подтверждаем коллбек здесь, т.к. send_faq_answer может не всегда его отправлять сразу

    # Обработчик кнопок пагинации ("Вперед", "Назад")
    @bot.callback_query_handler(func=lambda call: call.data.startswith(CALLBACK_PREFIX_FAQ_PAGE))
    def faq_page_navigation_handler(call: CallbackQuery):
        try:
            page_num_str = call.data.replace(CALLBACK_PREFIX_FAQ_PAGE, "")
            page_num = int(page_num_str)

            # Редактируем текущее сообщение, чтобы показать новую страницу
            send_faq_page(bot, call.message.chat.id, page_num=page_num, message_id_to_edit=call.message.message_id)
            user_current_faq_page[call.from_user.id] = page_num  # Обновляем текущую страницу пользователя
            bot.answer_callback_query(call.id)
        except ValueError:
            bot.answer_callback_query(call.id, "Ошибка навигации.", show_alert=True)
            print(f"Ошибка разбора callback_data для пагинации FAQ: {call.data}")

    # Обработчик кнопки "К списку вопросов" (со страницы ответа)
    @bot.callback_query_handler(func=lambda call: call.data.startswith(CALLBACK_BACK_TO_FAQ_LIST_FROM_ANSWER))
    def faq_back_to_list_from_answer_handler(call: CallbackQuery):
        try:
            # Извлекаем номер страницы из callback_data
            page_num_str = call.data.replace(CALLBACK_BACK_TO_FAQ_LIST_FROM_ANSWER, "")
            page_num = int(page_num_str)

            # Редактируем текущее сообщение (ответ) обратно в список вопросов на нужной странице
            send_faq_page(bot, call.message.chat.id, page_num=page_num, message_id_to_edit=call.message.message_id)
            user_current_faq_page[call.from_user.id] = page_num  # Обновляем текущую страницу пользователя
            bot.answer_callback_query(call.id)
        except ValueError:
            bot.answer_callback_query(call.id, "Ошибка возврата к списку.", show_alert=True)
            print(f"Ошибка разбора callback_data для возврата к списку FAQ: {call.data}")
            # В случае ошибки, можно просто показать первую страницу
            send_faq_page(bot, call.message.chat.id, page_num=0, message_id_to_edit=call.message.message_id)