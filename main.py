import asyncio  #чтобы иметь возможность добавить асинхронную функцию main в цикл событий.

from aiogram import Bot, Dispatcher
from config import Config, load_config
import user_handlers
from keyboard import set_main_menu

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