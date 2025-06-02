# zabgu_entrant_bot/features/ege_calculator/logic.py
# import logging # Убрали
from telebot.types import Message, CallbackQuery

from bot_app.states import EgeCalculatorStates
from bot_app.core_utils.utils_ege import (
    get_subject_min_score,
    OFFERED_SUBJECTS,
    fetch_programs_from_zabgu,
    format_programs_for_sending
)

from .keyboards import ege_subject_selection_keyboard, CALLBACK_PREFIX_SUBJECT_IDX, CALLBACK_CANCEL_EGE
from bot_app.keyboards import cancel_inline_keyboard, main_menu_keyboard
from bot_app.config import MIN_SUBJECTS_TO_SELECT


# logger = logging.getLogger(__name__) # Убрали

# --- Логика самого калькулятора ---
def start_ege_calculator(bot, chat_id: int, user_id: int):
    bot.set_state(user_id, EgeCalculatorStates.choosing_subjects, chat_id)
    with bot.retrieve_data(user_id, chat_id) as data:
        data['selected_subjects'] = []
        data['subject_scores'] = {}
        data['current_subject_index_for_score'] = 0
    bot.send_message(chat_id,
                     f"Пожалуйста, выберите от {MIN_SUBJECTS_TO_SELECT} предметов, которые вы сдавали.\n"
                     "Нажмите на предмет, чтобы выбрать или отменить выбор.",
                     reply_markup=ege_subject_selection_keyboard([]))


def handle_subject_toggle(bot, call: CallbackQuery):
    try:
        subject_index_str = call.data.replace(CALLBACK_PREFIX_SUBJECT_IDX, "")
        subject_index = int(subject_index_str)
        if not (0 <= subject_index < len(OFFERED_SUBJECTS)):
            bot.answer_callback_query(call.id, "Ошибка: неверный предмет.", show_alert=True)
            # print(f"EGE: Неверный индекс предмета: {subject_index} из callback_data: {call.data}") # Убрал
            return
        subject_name = OFFERED_SUBJECTS[subject_index]['name']
    except (ValueError, IndexError) as e:
        bot.answer_callback_query(call.id, "Ошибка обработки выбора.", show_alert=True)
        print(f"EGE: Ошибка разбора callback_data предмета: {call.data}, {e}")  # Оставил print для ошибок парсинга
        return
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        selected_subjects = data.get('selected_subjects', [])
        if subject_name in selected_subjects:
            selected_subjects.remove(subject_name)
            bot.answer_callback_query(call.id, f"Предмет '{subject_name}' убран.")
        else:
            selected_subjects.append(subject_name)
            bot.answer_callback_query(call.id, f"Предмет '{subject_name}' выбран.")
        data['selected_subjects'] = selected_subjects
        try:
            bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=ege_subject_selection_keyboard(selected_subjects))
        except Exception as e:
            print(f"EGE: Ошибка при обновлении клавиатуры выбора предметов: {e}")  # Оставил print


def proceed_to_score_input(bot, call: CallbackQuery):
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        selected_subjects = data.get('selected_subjects', [])
    if len(selected_subjects) < MIN_SUBJECTS_TO_SELECT:
        bot.answer_callback_query(call.id, f"Нужно выбрать минимум {MIN_SUBJECTS_TO_SELECT} предмета!", show_alert=True)
        return
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(f"EGE: Не удалось удалить сообщение с кнопками выбора предметов: {e}")  # Оставил print
    _ask_for_next_score(bot, call.message.chat.id, call.from_user.id)


def _ask_for_next_score(bot, chat_id: int, user_id: int):
    with bot.retrieve_data(user_id, chat_id) as data:
        selected_subjects = data.get('selected_subjects', [])
        current_idx = data.get('current_subject_index_for_score', 0)
        if current_idx < len(selected_subjects):
            current_subject_name = selected_subjects[current_idx]
            min_score = get_subject_min_score(current_subject_name)
            bot.set_state(user_id, EgeCalculatorStates.entering_scores, chat_id)
            prompt_text = (f"Введите ваш балл по предмету: <b>{current_subject_name}</b>\n"
                           f"(Минимальный допустимый балл: {min_score})")
            msg = bot.send_message(chat_id, prompt_text,
                                   reply_markup=cancel_inline_keyboard(CALLBACK_CANCEL_EGE),
                                   parse_mode='HTML')
            data['last_prompt_message_id'] = msg.message_id
        else:
            _finalize_ege_calculation(bot, chat_id, user_id)


def handle_score_message(bot, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    try:
        score_input = int(message.text)
    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите балл в виде числа (например, 75).")
        return
    with bot.retrieve_data(user_id, chat_id) as data:
        selected_subjects = data.get('selected_subjects', [])
        current_idx = data.get('current_subject_index_for_score', 0)
        subject_scores = data.get('subject_scores', {})
        last_prompt_msg_id = data.get('last_prompt_message_id')
    if current_idx >= len(selected_subjects):
        bot.send_message(chat_id, "Произошла ошибка в последовательности. Пожалуйста, начните калькулятор заново.",
                         reply_markup=main_menu_keyboard())
        bot.delete_state(user_id, chat_id)
        return
    current_subject_name = selected_subjects[current_idx]
    min_score = get_subject_min_score(current_subject_name)
    if score_input < min_score:
        bot.reply_to(message,
                     f"Балл по предмету '{current_subject_name}' должен быть не меньше {min_score}.\n"
                     f"Пожалуйста, введите корректный балл.")
        return
    subject_scores[current_subject_name] = score_input
    if last_prompt_msg_id:
        try:
            bot.delete_message(chat_id, last_prompt_msg_id)
        except Exception:
            pass
    try:
        bot.delete_message(chat_id, message.message_id)
    except Exception:
        pass
    with bot.retrieve_data(user_id, chat_id) as data:
        data['subject_scores'] = subject_scores
        data['current_subject_index_for_score'] = current_idx + 1
        data.pop('last_prompt_message_id', None)
    _ask_for_next_score(bot, chat_id, user_id)


def _finalize_ege_calculation(bot, chat_id: int, user_id: int):
    # print(f"EGE: Начало финализации расчета для пользователя {user_id} в чате {chat_id}") # Убрал
    loading_msg = bot.send_message(chat_id, "⏳ Подбираю программы, пожалуйста, подождите...")

    with bot.retrieve_data(user_id, chat_id) as data:
        subject_scores_dict = data.get('subject_scores', {})
        selected_subjects_ordered = data.get('selected_subjects', [])
        subjects_with_scores_for_api = []
        for subj_name in selected_subjects_ordered:
            if subj_name in subject_scores_dict:
                subjects_with_scores_for_api.append((subj_name, subject_scores_dict[subj_name]))

    # print(f"EGE: Предметы и баллы для API: {subjects_with_scores_for_api}") # Убрал

    if not subjects_with_scores_for_api:
        # print("EGE: Нет предметов и баллов для запроса к API.") # Убрал
        bot.delete_message(chat_id, loading_msg.message_id)
        bot.send_message(chat_id, "Произошла ошибка: не найдены предметы и баллы для запроса.",
                         reply_markup=main_menu_keyboard())
        bot.delete_state(user_id, chat_id)
        return

    api_response = fetch_programs_from_zabgu(subjects_with_scores_for_api)
    bot.delete_message(chat_id, loading_msg.message_id)
    # print(f"EGE: Ответ от API: {str(api_response)[:500]}...") # Убрал

    if api_response is None:
        # print("EGE: Ответ от API is None.") # Убрал
        bot.send_message(chat_id,
                         "Не удалось связаться с сервером ЗабГУ или произошла ошибка при получении данных. Попробуйте позже.",
                         reply_markup=main_menu_keyboard())
    else:
        # print("EGE: Ответ от API получен, форматирую и отправляю...") # Убрал
        list_of_messages_to_send = format_programs_for_sending(api_response)

        if not list_of_messages_to_send:
            # print("EGE: format_programs_for_sending вернул пустой список.") # Убрал
            bot.send_message(chat_id, "Не удалось отобразить программы.", reply_markup=main_menu_keyboard())
        else:
            for i, msg_text in enumerate(list_of_messages_to_send):
                reply_markup_for_msg = main_menu_keyboard() if i == len(list_of_messages_to_send) - 1 else None
                try:
                    bot.send_message(chat_id, msg_text, parse_mode='HTML', disable_web_page_preview=True,
                                     reply_markup=reply_markup_for_msg)
                except Exception as e:
                    print(
                        f"EGE: Ошибка при отправке части сообщения #{i + 1}: {e}\nТекст: {msg_text[:200]}...")  # Оставил print для ошибок отправки
                    if i == 0:
                        bot.send_message(chat_id, "Произошла ошибка при отображении результатов. Попробуйте позже.",
                                         reply_markup=main_menu_keyboard())
                        break
    bot.delete_state(user_id, chat_id)
    # print(f"EGE: Расчет для пользователя {user_id} завершен, состояние сброшено.") # Убрал


def cancel_ege_process(bot, call_or_message):
    user_id = call_or_message.from_user.id
    chat_id = call_or_message.chat.id if isinstance(call_or_message, Message) else call_or_message.message.chat.id
    bot.delete_state(user_id, chat_id)
    if isinstance(call_or_message, CallbackQuery):
        try:
            bot.delete_message(chat_id, call_or_message.message.message_id)
        except Exception as e:
            print(f"EGE: Ошибка при удалении сообщения при отмене калькулятора: {e}")  # Оставил print
        bot.answer_callback_query(call_or_message.id, "Калькулятор ЕГЭ отменен.")
    bot.send_message(chat_id, "Калькулятор ЕГЭ отменен. Выберите опцию в меню.", reply_markup=main_menu_keyboard())