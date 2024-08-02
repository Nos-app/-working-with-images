import requests
from urllib.parse import urlencode
import os
import zipfile
import tifffile
import numpy as np
from PIL import Image

base_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download?"
public_key = "https://disk.yandex.ru/d/V47MEP5hZ3U1kg"

# Получаем список файлов в папке
final_url = base_url + urlencode(dict(public_key=public_key))
response = requests.get(final_url)

# Проверяем ответ API
if response.status_code == 200:
    data = response.json()
    href = data["href"]

    # Загружаем архив
    response = requests.get(href, stream=True)

    # Создаем локальную папку для загрузки файлов, ну если её нет
    local_folder = "downloaded_files"
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    # Сохраняем загруженный архив
    filename = "archive.zip"
    local_path = os.path.join(local_folder, filename)
    with open(local_path, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    print(f"Архив загружен в {local_path}")
else:
    print(f"Ошибка при получении списка файлов: {response.status_code}")


archive_path = os.path.join(local_folder, "archive.zip")

# Распаковываем архив
with zipfile.ZipFile(archive_path, "r") as zip_ref:
    zip_ref.extractall(path="extracted_files")

print("Архив распакован в", local_folder)

# Создаем список файлов в папке
folder_path = "extracted_files"
files = []
for root, dirs, filenames in os.walk(folder_path):
    for filename in filenames:
        if filename.endswith(".png"):
            files.append(os.path.join(root, filename))

# Создаем список numpy массивов для каждого файла
arrays = []
for file in files:
    img = Image.open(file)
    arrays.append(np.asarray(img))

# Изменяем размеры массивов с помощью Pillow
common_shape = (800, 800)
resized_images = []
for array in arrays:
    img = Image.fromarray(array)
    resized_img = img.resize(common_shape)
    resized_images.append(resized_img)

# Создаем многослойный TIFF-файл
output_path = "output.tif"
tifffile.imwrite(output_path, np.stack(resized_images))

print(f"Многослойный TIFF-файл сохранен в {output_path}")
