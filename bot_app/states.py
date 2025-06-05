# states.py
from telebot.handler_backends import State, StatesGroup

# Определяем состояния для процесса калькулятора ЕГЭ
class EgeCalculatorStates(StatesGroup):
    choosing_subjects = State()  # Состояние выбора предметов
    entering_scores = State()    # Состояние ввода баллов