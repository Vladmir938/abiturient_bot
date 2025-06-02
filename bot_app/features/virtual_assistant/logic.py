import re
from telebot.types import Message
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from bot_app.config import GEMINI_API_KEY, GEMINI_MODEL_ID, GEMINI_MIN_QUESTION_LENGTH, GEMINI_MAX_QUESTION_LENGTH
from bot_app.states import GeminiAssistantStates
from bot_app.keyboards import main_menu_keyboard
from .keyboards import gemini_cancel_question_keyboard

# Инициализация клиента Gemini
if not GEMINI_API_KEY:
    print("ОШИБКА: API ключ для Gemini не установлен в config.py!")
    gemini_client = None
else:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        google_search_tool = Tool(
            google_search=GoogleSearch()
        )
    except Exception as e:
        print(f"Ошибка инициализации клиента Gemini: {e}")
        gemini_client = None


def request_gemini_question(bot, chat_id: int, user_id: int):
    """Запрашивает у пользователя вопрос для ассистента."""
    if not gemini_client:
        bot.send_message(chat_id, "Извините, виртуальный ассистент временно недоступен. Пожалуйста, попробуйте позже.")
        return

    bot.set_state(user_id, GeminiAssistantStates.waiting_for_question, chat_id)
    bot.send_message(chat_id,
                     "Пожалуйста, задайте ваш вопрос и я постараюсь найти на него ответ.",
                     reply_markup=gemini_cancel_question_keyboard())


def is_text_safe(text: str) -> bool:
    """Проверяет текст на наличие только разрешенных символов (буквы, цифры, пробелы, знаки препинания)."""
    # Разрешаем русские, английские буквы, цифры, пробелы и основные знаки препинания.
    # Запрещаем смайлики, спецсимволы, которые могут сломать Markdown или быть нежелательными.
    # Этот паттерн можно усложнить при необходимости.
    # \w эквивалентно [a-zA-Z0-9_], добавим русские буквы и знаки.
    # Паттерн для разрешенных символов: буквы (русские и английские), цифры, пробелы, и некоторые знаки препинания.
    # Важно: этот паттерн НЕ идеален и может требовать доработки.
    allowed_pattern = re.compile(r"^[а-яА-ЯёЁa-zA-Z0-9\s.,!?;:'\"()\-–—]+$")
    return bool(allowed_pattern.match(text))


def process_gemini_question(bot, message: Message):
    """Обрабатывает вопрос пользователя, отправляет его в Gemini и возвращает ответ."""
    if not gemini_client:
        bot.send_message(message.chat.id, "Извините, виртуальный ассистент временно недоступен.",
                               reply_markup=main_menu_keyboard())
        bot.delete_state(message.from_user.id, message.chat.id)
        return

    question = message.text.strip()

    # 1. Проверка на тип контента (только текст)
    if message.content_type != 'text':
        bot.reply_to(message, "Пожалуйста, отправьте ваш вопрос в виде текстового сообщения.",
                     reply_markup=main_menu_keyboard())
        bot.delete_state(message.from_user.id, message.chat.id)
        return

    # 2. Проверка на длину сообщения
    if not (GEMINI_MIN_QUESTION_LENGTH <= len(question) <= GEMINI_MAX_QUESTION_LENGTH):
        bot.reply_to(message,
                     f"Ваш вопрос слишком короткий или слишком длинный. "
                     f"Допустимая длина: от {GEMINI_MIN_QUESTION_LENGTH} до {GEMINI_MAX_QUESTION_LENGTH} символов.",
                     reply_markup=main_menu_keyboard())
        bot.delete_state(message.from_user.id, message.chat.id)  # Сбрасываем состояние
        return

    # 3. Проверка на запрещенные символы (базовая)
    if not is_text_safe(question):
        bot.reply_to(message,
                     "Ваш вопрос содержит недопустимые символы (например, эмодзи или специальные знаки). "
                     "Пожалуйста, используйте только буквы, цифры и стандартные знаки препинания.",
                     reply_markup=main_menu_keyboard())
        bot.delete_state(message.from_user.id, message.chat.id)
        return

    # Добавляем контекст к вопросу пользователя
    # "Забгу. Ответ выводи в markdown разметке" - это хороший системный промпт
    full_prompt = f"{question}\n\n(Информация касается ЗабГУ. Ответ верни текстом в удобном читаемом формате."

    processing_msg = bot.reply_to(message,
                                        "🤖 Думаю над вашим вопросом...")

    try:
        # Для genai.GenerativeModel().generate_content_async()
        # response = await gemini_client.generate_content_async(full_prompt) # Асинхронный вызов

        # Для синхронного genai.GenerativeModel().generate_content()
        # (pyTelegramBotAPI обычно работает синхронно в обработчиках, если не использовать asyncio специфично)

        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL_ID,
            contents=full_prompt,
            config=GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            )
        )

        ai_response_text = ""
        if response.candidates[0].content.parts:
            for each in response.candidates[0].content.parts:
                ai_response_text += each.text
        else:
            ai_response_text = "Не удалось получить внятный ответ от ассистента. Попробуйте переформулировать вопрос."
            print(f"Я сломался: {response}")

        # Удаляем сообщение "Думаю..."
        bot.delete_message(message.chat.id, processing_msg.message_id)

        # Отправляем ответ пользователю
        # parse_mode='MarkdownV2' если Gemini возвращает MarkdownV2, или 'Markdown' если старый Markdown.
        # Если Gemini возвращает простой текст, parse_mode можно убрать или использовать HTML для своего форматирования.
        # Для безопасности, если не уверены в разметке от Gemini, лучше отправлять как простой текст
        # или очищать от потенциально опасной разметки.
        # Пока предполагаем, что Gemini вернет корректный Markdown (или мы его сами потом обработаем)
        bot.send_message(message.chat.id, ai_response_text, parse_mode='Markdown',
                               reply_markup=main_menu_keyboard())

    except Exception as e:
        print(f"Ошибка при обращении к Gemini API или обработке ответа: {e}")
        try:  # Пытаемся удалить сообщение "Думаю...", даже если была ошибка
            bot.delete_message(message.chat.id, processing_msg.message_id)
        except:
            pass
        bot.send_message(message.chat.id,
                               "Произошла ошибка при обработке вашего вопроса. Пожалуйста, попробуйте позже.",
                               reply_markup=main_menu_keyboard())
    finally:
        # Сбрасываем состояние пользователя в любом случае
        bot.delete_state(message.from_user.id, message.chat.id)


def cancel_gemini_question_process(bot, call):
    """Обрабатывает нажатие инлайн-кнопки 'Отмена'."""
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    bot.delete_state(user_id, chat_id)  # Сбрасываем состояние
    try:
        # Удаляем сообщение с кнопкой "Отмена"
        bot.delete_message(chat_id, call.message.message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения с кнопкой отмены Gemini: {e}")

    bot.send_message(chat_id, "Запрос к ассистенту отменен.", reply_markup=main_menu_keyboard())
    bot.answer_callback_query(call.id)  # Подтверждаем колбэк