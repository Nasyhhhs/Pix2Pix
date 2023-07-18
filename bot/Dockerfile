# Указываем базовый образ
FROM python:3.10

WORKDIR /app

# Установка пакета libgl1-mesa-glx
RUN apt update && apt install -y libgl1-mesa-glx

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade setuptools -r requirements.txt

# Копируем все файлы проекта в рабочую директорию контейнера
#COPY . /app
COPY . .

# Устанавливаем зависимости проекта
#RUN pip install --no-cache-dir -r /app/requirements.txt

#задаем точку входа
#ENTRYPOINT ['python3', 'main.py']

# Запускаем файл бота
CMD python /app/main.py
