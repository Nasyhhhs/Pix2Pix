from aiogram import Bot, types
from aiogram.types import BotCommand
from aiogram.types import (CallbackQuery,  ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)



async def set_main_menu(bot: Bot):

    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Начало работы'),
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/support',
                   description='Поддержка')
        ]

    await bot.set_my_commands(main_menu_commands)

# Создаем объекты инлайн-кнопок
big_button_1: InlineKeyboardButton = InlineKeyboardButton(
    text='Neon',
    callback_data='Neon')

big_button_2: InlineKeyboardButton = InlineKeyboardButton(
    text='Upscale',
    callback_data='Upscale')

# Создаем объект инлайн-клавиатуры
inline_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[big_button_1],
                     [big_button_2]])



start_button: KeyboardButton = KeyboardButton(text='🚀')

# Создаем объект клавиатуры, добавляя в него кнопки
start_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[start_button]],
    resize_keyboard=True,
    one_time_keyboard=True)

