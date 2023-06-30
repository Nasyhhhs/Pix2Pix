import requests
import numpy as np
from aiogram.types import Message
from aiogram.types import ContentType, BotCommand
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command, CommandStart
from lexicon import LEXICON_RU
from aiogram import Router
from PIL import Image
import torchvision.transforms.functional as TF
from data import generate_image, get_upscale_image
import io
from aiogram import Bot, Dispatcher
from config import load_config, Config

from super_image import ImageLoader

# Загружаем конфиг в переменную config
config: Config = load_config()

    # Инициализируем бот и диспетчер
bot: Bot = Bot(token=config.tg_bot.token)
dp: Dispatcher = Dispatcher()

API_TOKEN = config.tg_bot.token

URI_INFO = f'https://api.telegram.org/bot{API_TOKEN}/getFile?file_id='
URI = f'https://api.telegram.org/file/bot{API_TOKEN}/'

# Инициализируем роутер уровня модуля
router: Router = Router()


# Создаем асинхронную функцию



@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'])

@router.message(Command(commands='help'))
# Этот хэндлер будет срабатывать на команду "/help"
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])
#async def process_update_command(message: Message):    #просто
  #  await message.answer(message.json(indent=4, exclude_none=True))


# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help"
@router.message()
async def process_message(message: Message):
    if message.content_type == ContentType.PHOTO:  #, F.content_type == ContentType.PHOTO
        file_id = message.photo[-1].file_id
        width = message.photo[-1].width
        height = message.photo[-1].height
        print(width)
        print(height)

        resp = requests.get(URI_INFO + file_id)

        img_path = resp.json()['result']['file_path']
        img = requests.get(URI + img_path)
        img = Image.open(io.BytesIO(img.content))
        #new_img = img.filter(ImageFilter.GaussianBlur(radius=50))  # убрать
        new_img = generate_image(img).astype(np.uint8)
        new_img = TF.to_pil_image(new_img)

        #кормим еще модели апскейлеру
        preds = await get_upscale_image(new_img)
        # вернем исходный размер
        resized_img = TF.resize(preds, [height, width])
        ImageLoader.save_image(resized_img, 'files/scaled_2x.png')
        ImageLoader.save_compare(img, resized_img, 'files/scaled_2x_compare.png')
        photo = FSInputFile('files/scaled_2x.png')

        await bot.send_photo(chat_id=message.chat.id, photo=photo)

        #os.remove('files/scaled_2x.png')
        #return

    elif message.content_type == ContentType.TEXT:
        # Обрабатываем текстовые сообщения
        await message.reply(text=f'Я не отвечаю на "{message.text}" ( ͡❛ ͜ʖ ͡❛)🖕')
    else:
        await message.reply(text=LEXICON_RU['wtf'])
