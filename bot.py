from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import ContentType
from PIL import Image
from io import BytesIO
import io
import os
from aiogram.types.input_file import FSInputFile

from data import generate_image
import requests
import numpy as np
import torchvision.transforms.functional as TF
from super_image import EdsrModel, ImageLoader

from environs import Env

from config import load_config, Config


config: Config = load_config()  # Сохраняем значение переменной окружения в переменную bot_token
  # Преобразуем значение переменной окружения к типу int
# и сохраняем в переменной admin_id

API_TOKEN = config.tg_bot.token
# Создаем объекты бота и диспетчера

bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher()

URI_INFO = f'https://api.telegram.org/bot{API_TOKEN}/getFile?file_id='
URI = f'https://api.telegram.org/file/bot{API_TOKEN}/'

# Этот хэндлер будет срабатывать на команду "/start"
async def process_start_command(message: Message):
    await message.answer('Ну что ж, заливай свою картинку и я превращу ее в неоновый шедевр! (Но это не точно) 👾 ')


# Этот хэндлер будет срабатывать на команду "/help"
async def process_help_command(message: Message):
    await message.answer('Просто отправь мне картинку и может быть что-то получишь в ответ ( ͡❛ ͜ʖ ͡❛)')
#async def process_update_command(message: Message):    #просто
  #  await message.answer(message.json(indent=4, exclude_none=True))


# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help"

async def process_message(message: Message):
    if message.content_type == ContentType.PHOTO:  #, F.content_type == ContentType.PHOTO
        file_id = message.photo[-1].file_id
        width = message.photo[-1].width
        height = message.photo[-1].height

        resp = requests.get(URI_INFO + file_id)

        img_path = resp.json()['result']['file_path']
        img = requests.get(URI + img_path)
        img = Image.open(io.BytesIO(img.content))
        #new_img = img.filter(ImageFilter.GaussianBlur(radius=50))  # убрать
        new_img = generate_image(img).astype(np.uint8)
        new_img = TF.to_pil_image(new_img)
        #возвращаем исходный размер
        new_img.save("files/gen_.jpg")
        #photo =open('files/gen_.jpg', 'rb')

        #апскейлинг
        model = EdsrModel.from_pretrained('eugenesiow/edsr-base', scale=2)
        #image = Image.open("files/gen_.jpg")
        inputs = ImageLoader.load_image(new_img)
        preds = model(inputs)

        #вернем исходный размер

        resized_img  = TF.resize(preds, (height, width))
        ImageLoader.save_image(resized_img, 'files/scaled_2x.png')
        ImageLoader.save_compare(inputs, resized_img, 'files/scaled_2x_compare.png')
        photo = FSInputFile('files/scaled_2x.png')
        #with open('files/gen_.jpg', 'rb') as photo:
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
        #cyber_photo =  process_photo(message.photo[1].file_id)
        #await message.reply_photo(photo = open(f'files/gen_{epoch}.jpg','rb'))
        #os.remove('files/gen_.jpg')
        #return

    elif message.content_type == ContentType.TEXT:
        # Обрабатываем текстовые сообщения
        await message.answer(text=f'Я не отвечаю на "{message.text}" ( ͡❛ ͜ʖ ͡❛)🖕')
    else:
        await message.reply(text='Ну и что за туфту ты прислал на этот раз? Давай фото!')



# Регистрируем хэндлеры
dp.message.register(process_start_command, Command(commands=['start']))
dp.message.register(process_help_command, Command(commands=['help']))


dp.message.register(process_message)


#запускает пуллинг, то есть постоянный опрос сервера Telegram на наличие апдейтов для бота. В качестве аргумента в метод диспетчера run_polling нужно передать объект бота
if __name__ == '__main__':
    dp.run_polling(bot)