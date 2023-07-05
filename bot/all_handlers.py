import requests
import os
import numpy as np
from aiogram import types
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command, CommandStart
from lexicon import LEXICON_RU
from aiogram import Router
from PIL import Image
import torchvision.transforms.functional as TF
from data import generate_image, get_upscale_image,  generate_random_number
import io
from aiogram import Bot, Dispatcher
from config import load_config, Config

from super_image import ImageLoader
from keyboard import inline_keyboard, start_keyboard
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

# Этот хэндлер будет срабатывать на команду "/start"
# и отправлять в чат клавиатуру
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text='Привет! Давай добавим неона в твои картинки!',
                         reply_markup=start_keyboard)


# Этот хэндлер будет срабатывать на ответ START и удалять клавиатуру

@router.message(Text(text='🚀') or Command(commands='/start'))
async def process_start(message: Message):
    await message.answer(text=LEXICON_RU['/start'])


#@router.message(Command(commands='start'))
#async def process_start_command(message: types.Message):
   # await message.answer(text=LEXICON_RU['/start'])

@router.message(Command(commands='help'))
async def process_help_command(message: types.Message):
    await message.answer(text=LEXICON_RU['/help'])

@router.message(Command(commands='support'))
async def process_support_command(message: types.Message):
    await message.answer(text=LEXICON_RU['/support'])


#отдельный класс для сохранения атрибутов полученнного изображения и использования в ассинхронных функциях
class InputImageData:
    def __init__(self):
        self.width = None
        self.height = None
        self.img = None
        self.num = None
        self.input_path = None

input_image_data = InputImageData()

@router.message()
async def process_message(message: types.Message):
    if message.content_type == types.ContentType.PHOTO:
        input_image_data.num = generate_random_number(5)
        print(input_image_data.num)

        # Получаем информацию о фото
        photo = message.photo[-1]
        file_id = photo.file_id
        input_image_data.width = photo.width
        input_image_data.height = photo.height

        print(input_image_data.width)
        print(input_image_data.height)

        resp = requests.get(URI_INFO + file_id)
        img_path = resp.json()['result']['file_path']
        img = requests.get(URI + img_path)
        input_image_data.img = Image.open(io.BytesIO(img.content))

        input_image_data.input_path = f'files/input/input_{input_image_data.num}.jpg'
        print(input_image_data.input_path)
        input_image_data.img.save(input_image_data.input_path)
        try:
            im = Image.open(input_image_data.input_path)
            image_size = im.size
            print(f'Файл {input_image_data.input_path} размером {image_size} успешно сохранен!')
            im.close()#ImageLoader.save_image(input_image_data.img, input_image_data.input_path)
        except:
            print('У нас проблема: не удалось сохранить исходник')
        # Отправляем сообщение с вопросом и кнопками
        await message.answer(text='Фото успешно загружено! Что делать будем?',
                             reply_markup=inline_keyboard)

        #input_image_data.img.close()


    elif message.content_type == types.ContentType.TEXT:
        # Обрабатываем текстовые сообщения
        await message.reply(text=f'Я не отвечаю на "{message.text}" ( ͡❛ ͜ʖ ͡❛)🖕')
    else:
        await message.reply(text=LEXICON_RU['wtf'])

@router.callback_query(Text(text=['Neon', 'Upscale']))
async def process_button_press(callback: CallbackQuery):
    await callback.answer()
    print(callback.data)
    if callback.data == 'Neon':
        print('Neon starting...')
        # Отправляем сообщение пользователю
        await callback.message.answer(text='👽')
        # Обработка фото с помощью Neon
        new_img = generate_image(input_image_data.img).astype(np.uint8)
        new_img = TF.to_pil_image(new_img)
        neon_path = f'files/neon/neon_{input_image_data.num}.png'
        print(neon_path)
        # кормим еще модели апскейлеру
        preds = await get_upscale_image(new_img, scale=2)
        # вернем исходный размер
        resized_img = TF.resize(preds, [input_image_data.height, input_image_data.width])
        ImageLoader.save_image(resized_img, neon_path)
        photo = FSInputFile(neon_path)
        await bot.send_photo(chat_id=callback.message.chat.id, photo=photo)
        os.remove(neon_path)
        os.remove(input_image_data.input_path)

    elif callback.data == 'Upscale':
        print('Upscale starting...')
        # Отправляем сообщение пользователю
        await callback.message.answer(text='👾')
        # Обработка фото с помощью Upscale
        # кормим еще модели апскейлеру
        #img = Image.open('files/input.jpg')
        scale = 2
        preds = await get_upscale_image(input_image_data.img, scale=2)
        scaled_path = f'files/upscaled/scaled_{scale}x_{input_image_data.num}.png'
        print(scaled_path)
        ImageLoader.save_image(preds, scaled_path)
        photo = FSInputFile(scaled_path)
        # Загружаем изображение с помощью PIL
        with Image.open(scaled_path) as im:
            # Получение размера изображения
            image_size = im.size
            print("Размер изображения после апскейла:", image_size)
        await bot.send_photo(chat_id=callback.message.chat.id, photo=photo)
        os.remove(scaled_path)
        os.remove(input_image_data.input_path)




