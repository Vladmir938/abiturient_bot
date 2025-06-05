import telebot
from telebot import custom_filters # Для StateFilter
from telebot.storage import StateMemoryStorage # Для хранения состояний в памяти
from telebot.types import Message

from config import BOT_TOKEN
from keyboards import main_menu_keyboard
from states import EgeCalculatorStates # Импортируем, чтобы /cancel мог проверить это состояние

# Импортируем ФИЧИ
from features.ege_calculator_parser.handlers import register_ege_calculator_handlers
from features.faq.handlers import register_faq_handlers
from features.admission.handlers import register_admission_committee_handlers
from features.virtual_assistant.handlers import register_gemini_assistant_handlers
from features.study_programs.handlers import register_study_programs_handlers
from features.ege_calculator_local.handlers import register_ege_calculator_local_handlers

# Инициализация хранилища состояний
state_storage = StateMemoryStorage()

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage, parse_mode='HTML')


# --- ОБЩИЕ ОБРАБОТЧИКИ ---
@bot.message_handler(commands=['start', 'help'])
def command_start_help(message: Message):
    """Обработчик команд /start и /help."""
    user_name = message.from_user.first_name
    bot.reply_to(message,
                 f"👋 Привет, {user_name}!\n"
                 f"Я бот-помощник для абитуриентов ЗабГУ.\n"
                 f"Используйте кнопки меню для навигации.",
                 reply_markup=main_menu_keyboard())
    # Сбрасываем состояние пользователя, если оно было
    bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(commands=['cancel'])
def command_cancel(message: Message):
    """Обработчик команды /cancel для отмены текущего действия."""
    current_state = bot.get_state(message.from_user.id, message.chat.id)
    if current_state is None:
        bot.send_message(message.chat.id, "Нет активных действий для отмены.", reply_markup=main_menu_keyboard())
        return

    # Если мы в процессе калькулятора, вызываем его специфическую отмену
    # Это более явная обработка, но можно и просто bot.delete_state
    if str(current_state).startswith(EgeCalculatorStates.group_name): # Проверяем, что состояние из группы EgeCalculatorStates
        from features.ege_calculator_parser.logic import cancel_ege_process # Локальный импорт, чтобы избежать циклов
        cancel_ege_process(bot, message) # Передаем message, т.к. это команда
    else:
        # Общая отмена для других возможных состояний
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, "Действие отменено.", reply_markup=main_menu_keyboard())


# --- РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ ИЗ МОДУЛЕЙ ФИЧ ---
# register_ege_calculator_handlers(bot)
register_faq_handlers(bot)
register_admission_committee_handlers(bot)
register_study_programs_handlers(bot)
register_ege_calculator_local_handlers(bot)
register_gemini_assistant_handlers(bot)

# Сюда можно будет добавлять регистрацию обработчиков для других фич:
# from features.admission_info.handlers import register_admission_info_handlers
# register_admission_info_handlers(bot)


# --- ЗАПУСК БОТА ---
if __name__ == '__main__':
    print("Запуск бота...")
    # Добавляем фильтр состояний для корректной работы хендлеров с состояниями
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    # Запуск бесконечного опроса Telegram API
    bot.infinity_polling(skip_pending=True) # skip_pending=True чтобы не обрабатывать старые сообщения при перезапуске
    print("Бот остановлен.")