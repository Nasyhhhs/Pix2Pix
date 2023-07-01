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


@router.message(Command(commands='start'))  #CommandStart() |
async def process_start_command(message: types.Message):
    await message.answer(text=LEXICON_RU['/start'])

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


input_image_data = InputImageData()


@router.message()
async def process_message(message: types.Message):
    if message.content_type == types.ContentType.PHOTO:
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


        input_image_data.input_path = 'files/input.jpg'
        #shared_data.img.save(shared_data.input_path)  # сохранить исходник
        #ImageLoader.save_image(img, input_path)

        # Отправляем сообщение с вопросом и кнопками
        await message.answer(text='Фото успешно загружено! Что делать будем?', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Neon', callback_data='neon')],
            [InlineKeyboardButton(text='Upscale', callback_data='upscale')]
        ]))

        #await bot.send_photo(chat_id=message.chat.id, photo=InputFile(new_img_path))

        # Удаляем временное изображение
        img.close()
        #os.remove(input_path)

    elif message.content_type == types.ContentType.TEXT:
        # Обрабатываем текстовые сообщения
        await message.reply(text=f'Я не отвечаю на "{message.text}" ( ͡❛ ͜ʖ ͡❛)🖕')
    else:
        await message.reply(text=LEXICON_RU['wtf'])

@router.callback_query(Text(text=['neon', 'upscale']))
async def process_button_press(callback: CallbackQuery):
    await callback.answer()

    if callback.data == 'neon':
        # Отправляем сообщение пользователю
        await callback.message.answer(text='Вызов Neon принят! Работаем, шеф!')
        # Обработка фото с помощью Neon
        new_img = generate_image(input_image_data.img).astype(np.uint8)
        new_img = TF.to_pil_image(new_img)

        # кормим еще модели апскейлеру
        preds = await get_upscale_image(new_img, scale=2)
        # вернем исходный размер
        resized_img = TF.resize(preds, [input_image_data.height, input_image_data.width])
        ImageLoader.save_image(resized_img, 'files/neon.png')
        photo = FSInputFile('files/neon.png')
        await bot.send_photo(chat_id=callback.message.chat.id, photo=photo)



    elif callback.data == 'upscale':
        # Отправляем сообщение пользователю
        await callback.message.answer(text='Вызов Upscale принят! Работаем, шеф!')
        # Обработка фото с помощью Upscale
        # кормим еще модели апскейлеру
        #img = Image.open('files/input.jpg')
        scale = 2
        preds = await get_upscale_image(input_image_data.img, scale=2)
        ImageLoader.save_image(preds, f'files/scaled_{scale}x.png')
        photo = FSInputFile(f'files/scaled_{scale}x.png')
        # Загружаем изображение с помощью PIL
        im = Image.open(f'files/scaled_{scale}x.png')

        # Получение размера изображения
        image_size = im.size
        print("Размер изображения после апскейла:", image_size)
        await bot.send_photo(chat_id=callback.message.chat.id, photo=photo)





