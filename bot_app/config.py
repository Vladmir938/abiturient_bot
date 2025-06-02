# config.py
# Токен вашего Telegram бота
BOT_TOKEN = ""

# URL для API ЗабГУ
ZABGU_API_URL = "https://entrant.zabgu.ru/wp-content/themes/twentytwelve/page-templates/crudForCalc/crudForCalcAjax.php"

# Заголовки и cookies для запросов к API (как в вашем примере)
API_HEADERS = {
    "Accept": "application/json, text/javascript, /; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "X-KL-kfa-Ajax-Request": "Ajax_Request",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
    "Referer": "https://entrant.zabgu.ru/?page_id=4569",
}
API_COOKIES = {
    "agreement": "1"
}

# Количество предметов для выбора (первые N из JSON)
SUBJECT_COUNT_TO_OFFER = 11
MIN_SUBJECTS_TO_SELECT = 3

# Тексты кнопок (для удобства изменения)
BTN_EGE_CALCULATOR = "Калькулятор ЕГЭ 📐"
BTN_FAQ = "Часто задаваемые вопросы ❓"
BTN_ADMISSION_COMMITTEE = "Приёмная комиссия 🏛️"
BTN_GEMINI_ASSISTANT = "Спросить ассистента 🤖"

# Настройки для Gemini Assistant
GEMINI_API_KEY = ""
GEMINI_MODEL_ID = "gemini-2.0-flash"

# Тексты для подменю "Приёмная комиссия"
BTN_AC_CONTACTS = "Контакты 📞"
BTN_AC_DOCUMENTS = "Документы для поступления 📑"
BTN_AC_SUBMISSION_DATES = "Сроки подачи документов 🗓️"
BTN_BACK_TO_MAIN = "⬅️ В главное меню"

# Ограничения на длину сообщения для ассистента
GEMINI_MIN_QUESTION_LENGTH = 10  # Минимальная длина вопроса
GEMINI_MAX_QUESTION_LENGTH = 500 # Максимальная длина вопроса