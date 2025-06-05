from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_app.config import MIN_SUBJECTS_TO_SELECT
from bot_app.core_utils.utils_ege import OFFERED_SUBJECTS  # Данные о предметах для выбора

# Префиксы для callback_data, чтобы они были уникальны для этого модуля
CALLBACK_PREFIX_SUBJECT_IDX = "ege_idx_"  # ИЗМЕНЕНО: префикс для индекса предмета
CALLBACK_SUBJECTS_DONE = "ege_subj_done"
CALLBACK_CANCEL_EGE = "ege_cancel"


def ege_subject_selection_keyboard(selected_subjects_names):
    """
    Создает инлайн-клавиатуру для выбора предметов ЕГЭ.
    :param selected_subjects_names: Список названий уже выбранных предметов.
    """
    markup = InlineKeyboardMarkup(row_width=1)
    buttons = []

    # ИЗМЕНЕНО: используем enumerate для получения индекса каждого предмета
    for index, subject_info in enumerate(OFFERED_SUBJECTS):
        subject_name = subject_info['name']
        button_text = f"✅ {subject_name}" if subject_name in selected_subjects_names else subject_name
        # ИЗМЕНЕНО: в callback_data передаем индекс предмета
        buttons.append(InlineKeyboardButton(button_text, callback_data=f"{CALLBACK_PREFIX_SUBJECT_IDX}{index}"))

    markup.add(*buttons)

    if len(selected_subjects_names) >= MIN_SUBJECTS_TO_SELECT:
        markup.add(InlineKeyboardButton("Готово 👍", callback_data=CALLBACK_SUBJECTS_DONE))

    markup.add(InlineKeyboardButton("Отмена ❌", callback_data=CALLBACK_CANCEL_EGE))
    return markup