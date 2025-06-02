import json
from telebot.types import Message, CallbackQuery
# Импортируем константы и клавиатуры
from .keyboards import (
    faq_questions_paginated_keyboard,
    faq_answer_keyboard,
    CALLBACK_PREFIX_FAQ_QUESTION,
    CALLBACK_PREFIX_FAQ_PAGE,
    CALLBACK_BACK_TO_FAQ_LIST_FROM_ANSWER,
    QUESTIONS_PER_PAGE
)
from bot_app.keyboards import main_menu_keyboard

FAQ_DATA_FILE = 'data/faq_questions.json'
FAQ_QUESTIONS_LIST = []
try:
    with open(FAQ_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if "часто_задаваемые_вопросы" in data and isinstance(data["часто_задаваемые_вопросы"], list):
            FAQ_QUESTIONS_LIST = data["часто_задаваемые_вопросы"]
        else:
            print(f"ОШИБКА: Ключ 'часто_задаваемые_вопросы' не найден или имеет неверный формат в {FAQ_DATA_FILE}")
except FileNotFoundError:
    print(f"ОШИБКА: Файл {FAQ_DATA_FILE} не найден.")
except json.JSONDecodeError:
    print(f"ОШИБКА: Некорректный формат JSON в {FAQ_DATA_FILE}.")


def send_faq_page(bot, chat_id: int, page_num: int = 0, message_id_to_edit=None):
    if not FAQ_QUESTIONS_LIST:
        text = "К сожалению, список часто задаваемых вопросов сейчас пуст."
        if message_id_to_edit:
            try:
                bot.edit_message_text(text, chat_id, message_id_to_edit, reply_markup=None)
            except:
                bot.send_message(chat_id, text)
        else:
            bot.send_message(chat_id, text)
        return

    start_index = page_num * QUESTIONS_PER_PAGE
    end_index = start_index + QUESTIONS_PER_PAGE

    questions_indices_on_page = []  # Список оригинальных индексов вопросов на этой странице

    # Формируем текст сообщения с вопросами текущей страницы
    page_text_content = ""

    has_questions_on_this_page = False
    for i in range(start_index, min(end_index, len(FAQ_QUESTIONS_LIST))):
        has_questions_on_this_page = True
        item = FAQ_QUESTIONS_LIST[i]
        question_text = item.get("вопрос", f"Текст вопроса {i + 1} отсутствует")
        # Добавляем вопрос в текст сообщения с его глобальным номером
        page_text_content += f"<b>{i + 1}.</b> {question_text}\n\n"
        questions_indices_on_page.append(i)  # Сохраняем оригинальный индекс для клавиатуры

    if not has_questions_on_this_page and page_num > 0:
        send_faq_page(bot, chat_id, page_num - 1, message_id_to_edit)
        return
    elif not has_questions_on_this_page and page_num == 0:  # Если вообще нет вопросов
        page_text_content = "Список вопросов пуст."
        markup = None
    else:
        page_text_content += "Выберите номер вопроса из кнопок ниже:"
        markup = faq_questions_paginated_keyboard(questions_indices_on_page, page_num, len(FAQ_QUESTIONS_LIST))

    # Ограничение длины сообщения
    if len(page_text_content) > 4096:
        # Это маловероятно для QUESTIONS_PER_PAGE = 5, но на всякий случай
        page_text_content = page_text_content[:4090] + "\n[...]"

    if message_id_to_edit:
        try:
            bot.edit_message_text(page_text_content, chat_id, message_id_to_edit,
                                  reply_markup=markup, parse_mode='HTML')
        except Exception as e:
            print(f"Ошибка при редактировании сообщения для страницы FAQ: {e}")
            try:
                bot.delete_message(chat_id, message_id_to_edit)
            except:
                pass
            bot.send_message(chat_id, page_text_content, reply_markup=markup, parse_mode='HTML')
    else:
        bot.send_message(chat_id, page_text_content, reply_markup=markup, parse_mode='HTML')


def send_faq_answer(bot, call: CallbackQuery, current_page_for_list: int):
    """
    Отправляет ответ на выбранный вопрос.
    :param current_page_for_list: Номер страницы списка, с которой был выбран вопрос (для кнопки "Назад").
    """
    try:
        # call.data будет вида "faq_q_ИНДЕКС"
        question_original_index_str = call.data.replace(CALLBACK_PREFIX_FAQ_QUESTION, "")
        question_original_index = int(question_original_index_str)

        if not (0 <= question_original_index < len(FAQ_QUESTIONS_LIST)):
            bot.answer_callback_query(call.id, "Ошибка: неверный вопрос.", show_alert=True)
            print(f"Ошибка: получен неверный индекс вопроса {question_original_index} из callback_data: {call.data}")
            # Возвращаем к списку вопросов (на ту же страницу)
            send_faq_page(bot, call.message.chat.id, page_num=current_page_for_list,
                          message_id_to_edit=call.message.message_id)
            return

        faq_item = FAQ_QUESTIONS_LIST[question_original_index]
        question_text = faq_item.get("вопрос", "Вопрос не найден")
        answer_text = faq_item.get("ответ", "Ответ на этот вопрос пока не добавлен.")
        full_message_text = f"<b>Вопрос:</b>\n{question_text}\n\n<b>Ответ:</b>\n{answer_text}"

        # Клавиатура для возврата на ТУ ЖЕ страницу списка вопросов
        markup = faq_answer_keyboard(current_page_for_list)

        if len(full_message_text) > 4096:
            # Обработка очень длинных ответов (разбивка)
            part1 = full_message_text[:4090] + "..."
            part2 = "... " + full_message_text[4090:]
            try:
                bot.edit_message_text(part1, call.message.chat.id, call.message.message_id, parse_mode='HTML',
                                      reply_markup=None)
                bot.send_message(call.message.chat.id, part2, reply_markup=markup, parse_mode='HTML')
            except Exception as e:
                print(f"Ошибка редактирования/отправки длинного ответа: {e}")
                # Если не удалось отредактировать, отправляем как новые
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except:
                    pass
                bot.send_message(call.message.chat.id, part1, parse_mode='HTML')
                bot.send_message(call.message.chat.id, part2, reply_markup=markup, parse_mode='HTML')
        else:
            try:
                bot.edit_message_text(full_message_text,
                                      call.message.chat.id,
                                      call.message.message_id,
                                      reply_markup=markup,
                                      parse_mode='HTML')
            except Exception as e:
                print(f"Ошибка редактирования сообщения с ответом: {e}")
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except:
                    pass
                bot.send_message(call.message.chat.id, full_message_text, reply_markup=markup, parse_mode='HTML')

        bot.answer_callback_query(call.id)

    except (ValueError, IndexError) as e:
        bot.answer_callback_query(call.id, "Ошибка обработки запроса.", show_alert=True)
        print(f"Ошибка разбора callback_data вопроса FAQ: {call.data}, {e}")
        send_faq_page(bot, call.message.chat.id, page_num=current_page_for_list,
                      message_id_to_edit=call.message.message_id)
