import torch
from torchvision import transforms
import random
import numpy as np
from model import Generator
from super_image import EdsrModel, ImageLoader


# Преобразования для черно-белого изображения
transform_bw = transforms.Compose([
    transforms.Resize((256, 256), antialias=True),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])


#функция, чтобы ранее нормализованные изображения отображались корректно
def reverse_normalize(image, mean_=0.5, std_=0.5):
    if torch.is_tensor(image):
        image = image.detach()
    un_normalized_img = image * std_ + mean_
    un_normalized_img = un_normalized_img * 255
    return np.uint8(un_normalized_img)

weights_path = 'weights'
#Функции для загрузки весов генератора
def load_gen(path=weights_path, epoch=94):
    return torch.load(path+f'/Bgen_{epoch}.pth', map_location=torch.device('cpu'))

#функция загрузки и обработки фото генератором
def generate_image(img, path=weights_path):
    preprocess = transform_bw
    input_tensor = preprocess(img).unsqueeze(0)

    #создаем объект генератора и подгружаем веса
    gen = Generator(in_channels=3, features=64)
    generator_weights = load_gen(path)
    gen.load_state_dict(generator_weights)

    with torch.no_grad():
        output_tensor = gen(input_tensor)
        output_tensor = output_tensor.squeeze()
        output_image = reverse_normalize(output_tensor.permute(1, 2, 0))

    return output_image


#апскейлинг
async def get_upscale_image(img, scale=2):
    model = EdsrModel.from_pretrained('eugenesiow/edsr-base', scale=scale)
    inputs = ImageLoader.load_image(img)

    preds = model(inputs)
    return preds

#функция для генерации рандомных чисел определенной длины

def generate_random_number(length):
    min_value = 10**(length-1)  # Минимальное значение для заданной длины
    max_value = (10**length) - 1  # Максимальное значение для заданной длины
    return random.randrange(min_value, max_value)

