import requests
import numpy as np
from aiogram import types
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
from keyboard import keyboard

from aiogram.types import Message, ContentType, BotCommand, InlineKeyboardButton
from aiogram.filters import Text
from aiogram.types import CallbackQuery, InlineKeyboardButton,InlineKeyboardMarkup
# Инициализируем бот и диспетчер
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
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'])

@router.message(Command(commands='help'))
# Этот хэндлер будет срабатывать на команду "/help"
async def process_help_command(message: types.Message):
    await message.answer(text=LEXICON_RU['/help'])
#async def process_update_command(message: Message):    #просто
  #  await message.answer(message.json(indent=4, exclude_none=True))

@router.message(Command(commands='support'))
# Этот хэндлер будет срабатывать на команду "/help"
async def process_help_command(message: types.Message):
    await message.answer(text=LEXICON_RU['/support'])

# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help"

class SharedData:
    def __init__(self):
        self.width = None
        self.height = None
        self.img = None
        self.message = None

shared_data = SharedData()


@router.message()
async def process_message(message: types.Message):
    if message.content_type == types.ContentType.PHOTO:
        # Получаем информацию о фото
        photo = message.photo[-1]
        file_id = photo.file_id

        shared_data.width = photo.width

        shared_data.height = photo.height
        print(shared_data.width)
        print(shared_data.height)
        resp = requests.get(URI_INFO + file_id)

        img_path = resp.json()['result']['file_path']
        img = requests.get(URI + img_path)

        shared_data.img = Image.open(io.BytesIO(img.content))


        shared_data.input_path = 'files/input.jpg'
        #shared_data.img.save(shared_data.input_path)  # сохранить исходник
        #ImageLoader.save_image(img, input_path)

        # Отправляем сообщение с вопросом и кнопками
        await message.answer(text='Фото успешно загружено! Что делать будем?', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Neon', callback_data='neon')],
            [InlineKeyboardButton(text='Upscale', callback_data='upscale')]
        ]))

        #await bot.send_photo(chat_id=message.chat.id, photo=InputFile(new_img_path))

        # Удаляем временное изображение
        #img.close()
        #os.remove(input_path)

    elif message.content_type == types.ContentType.TEXT:
        # Обрабатываем текстовые сообщения
        await message.reply(text=f'Я не отвечаю на "{message.text}"')

@router.callback_query(Text(text=['neon', 'upscale']))
async def process_button_press(callback: CallbackQuery):
    await callback.answer()

    if callback.data == 'neon':
        # Отправляем сообщение пользователю
        await callback.message.answer(text='Вызов Neon принят! Работаем, шеф!')
        # Обработка фото с помощью Neon
        new_img = generate_image(shared_data.img).astype(np.uint8)
        new_img = TF.to_pil_image(new_img)

        # кормим еще модели апскейлеру
        preds = await get_upscale_image(new_img)
        # вернем исходный размер
        resized_img = TF.resize(preds, [shared_data.height, shared_data.width])
        ImageLoader.save_image(resized_img, 'files/neon.png')
        photo = FSInputFile('files/neon.png')
        await bot.send_photo(chat_id=callback.message.chat.id, photo=photo)



    elif callback.data == 'upscale':
        # Отправляем сообщение пользователю
        await callback.message.answer(text='Вызов Upscale принят! Работаем, шеф!')
        # Обработка фото с помощью Upscale
        # кормим еще модели апскейлеру
        #img = Image.open('files/input.jpg')
        preds = await get_upscale_image(shared_data.img)
        ImageLoader.save_image(preds, 'files/scaled_2x.png')
        photo = FSInputFile('files/scaled_3x.png')
        # Загружаем изображение с помощью PIL
        im = Image.open('files/scaled_3x.png')

        # Получение размера изображения
        image_size = im.size
        print("Размер изображения после апскейла:", image_size)
        await bot.send_photo(chat_id=callback.message.chat.id, photo=photo)





