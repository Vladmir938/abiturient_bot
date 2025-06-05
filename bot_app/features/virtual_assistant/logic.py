import re
from telebot.types import Message
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from bot_app.config import GEMINI_API_KEY, GEMINI_MODEL_ID, GEMINI_MIN_QUESTION_LENGTH, GEMINI_MAX_QUESTION_LENGTH
from bot_app.keyboards import main_menu_keyboard

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


# Словарь для отслеживания, ожидает ли пользователь ответа от Gemini
# {user_id: True/False}
user_is_waiting_for_gemini = {}

def is_text_safe(text: str) -> bool:
    """Проверяет текст на наличие только разрешенных символов (буквы, цифры, пробелы, знаки препинания)."""
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

    if user_is_waiting_for_gemini.get(message.from_user.id, False):
        bot.send_message(message.from_user.id, "Пожалуйста, подождите ответа на предыдущий вопрос, прежде чем задавать новый.")
        return

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
    full_prompt = f"""
    {question}

    Информация должна касаться исключительно вопросов Забайкальского государственного университета (ЗабГУ) в городе Чита. 

    Строго соблюдай следующие правила:
    1. Отвечай ТОЛЬКО на вопросы, связанные с:
       - Темами, напрямую связанные с ЗАБГУ

    2. Если вопрос НЕ относится к ЗабГУ, отвечай строго:
       "Извините, я могу отвечать только на вопросы, связанные с Забайкальским государственным университетом."

    3. Формат ответа:
       - Четкий структурированный текст
       - Без лишних вступлений
       - С фактами и цифрами (если известны)
       - С указанием актуального учебного года
       - HTML разметка только:
        <b>жирный</b>
        <i>курсив</i>
        <u>подчёркнутый</u>
        <s>зачёркнутый</s>
        <code>моноширинный (для кода)</code>
        <a href="URL">гиперссылка</a>
    """

    user_is_waiting_for_gemini[message.chat.id] = True
    processing_msg = bot.send_message(message.chat.id, "🤖 Анализирую ваш запрос...")

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
        bot.send_message(message.chat.id, ai_response_text, parse_mode='HTML',
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
        user_is_waiting_for_gemini[message.chat.id] = False