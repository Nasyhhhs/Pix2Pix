import asyncio  #чтобы иметь возможность добавить асинхронную функцию main в цикл событий.
from aiogram.types import BotCommand
from aiogram import Bot, Dispatcher
from config import Config, load_config
import user_handlers

async def set_main_menu(bot: Bot):

    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/support',
                   description='Поддержка'),

        ]

    await bot.set_my_commands(main_menu_commands)

# Функция конфигурирования и запуска бота
async def main() -> None:

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot: Bot = Bot(token=config.tg_bot.token)
    dp: Dispatcher = Dispatcher()
    # Настраиваем кнопку Menu
    await set_main_menu(bot)
    # Регистриуем роутеры в диспетчере

    dp.startup.register(set_main_menu)
    dp.include_router(user_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    # Регистрируем асинхронную функцию в диспетчере,
    # которая будет выполняться на старте бота,

    asyncio.run(main())