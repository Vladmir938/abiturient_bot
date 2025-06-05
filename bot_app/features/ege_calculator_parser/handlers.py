# zabgu_entrant_bot/features/ege_calculator_parser/handlers.py
from telebot.types import Message, CallbackQuery
from bot_app.states import EgeCalculatorStates
from bot_app.config import BTN_EGE_CALCULATOR
from .logic import (
    start_ege_calculator,
    handle_subject_toggle,
    proceed_to_score_input,
    handle_score_message,
    cancel_ege_process
)
# ИЗМЕНЕНО: импортируем правильный префикс для колбэков предметов
from .keyboards import CALLBACK_PREFIX_SUBJECT_IDX, CALLBACK_SUBJECTS_DONE, CALLBACK_CANCEL_EGE


def register_ege_calculator_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == BTN_EGE_CALCULATOR)
    def ege_calculator_entry_handler(message: Message):
        start_ege_calculator(bot, message.chat.id, message.from_user.id)

    # ИЗМЕНЕНО: используем CALLBACK_PREFIX_SUBJECT_IDX
    @bot.callback_query_handler(func=lambda call: call.data.startswith(CALLBACK_PREFIX_SUBJECT_IDX),
                                state=EgeCalculatorStates.choosing_subjects)
    def ege_subject_toggle_handler(call: CallbackQuery):
        handle_subject_toggle(bot, call)

    @bot.callback_query_handler(func=lambda call: call.data == CALLBACK_SUBJECTS_DONE,
                                state=EgeCalculatorStates.choosing_subjects)
    def ege_subjects_done_handler(call: CallbackQuery):
        proceed_to_score_input(bot, call)

    @bot.message_handler(state=EgeCalculatorStates.entering_scores, content_types=['text'])
    def ege_score_input_handler(message: Message):
        if message.text.startswith('/'):
            if message.text == '/cancel':
                cancel_ege_process(bot, message)
            return
        handle_score_message(bot, message)

    @bot.callback_query_handler(func=lambda call: call.data == CALLBACK_CANCEL_EGE,
                                state=[EgeCalculatorStates.choosing_subjects, EgeCalculatorStates.entering_scores])
    def ege_cancel_inline_handler(call: CallbackQuery):
        cancel_ege_process(bot, call)