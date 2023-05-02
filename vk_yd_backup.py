
''' !!!Перед стартом программы заполните информацию в файле personal!!! '''

import requests
from tqdm import tqdm
import json
import personal

class VK_photo:
    ''' В данном классе получаем фото VK '''

    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version,
        }
        self.images = []

    def get_photos(self, user_id=None):
        ''' Получаем фото по id пользователя '''

        get_photos_url = self.url + 'photos.get'
        get_photos_param = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
}
        response = requests.get(get_photos_url,params={**self.params, **get_photos_param},).json()

        # производим создание списка фото
        for i in response['response']['items']:
            likes_count = i['likes']['count']
            date = i['date']
            size = i['sizes'][-1]['height'] * i['sizes'][-1]['width']
            url = i['sizes'][-1]['url']
            self.images.append({
                'file_name': f"{likes_count}" if not self.is_filename_exist_in_imagelist(likes_count) else f"{likes_count}_{date}",
                'size': size,
                'url': url,
            })
        self.images = sorted(self.images, key=lambda x: x['size'], reverse=True)[:personal.yd_photo_count]


    def is_filename_exist_in_imagelist(self, fn):
        ''' Проверка наличия файла в списке изображений '''

        for i in self.images:
            if i['file_name'] == str(fn):
                return True
        return False


    def save_photo_info_to_file(self, filename='log.json'):
        ''' Запись информации о фото в файл '''

        json_object = json.dumps(self.images, indent=4)
        with open(filename, "w") as outfile:
            outfile.write(json_object)


class YaUploader:
    ''' Класс для работы с Яндекс диском '''

    host = 'https://cloud-api.yandex.net/'

    def __init__(self, token):
        self.token = token


    def get_headers(self):
        ''' Авторизация '''

        return {'Content_Type': 'application/json', 'Authorization': f'OAuth {self.token}'}


    def create_folder(self, folder_name):
        ''' Создание папки '''

        uri = 'v1/disk/resources/'
        url = self.host + uri
        params = {'path': f'/{folder_name}', 'overwrite': 'true'}
        requests.put(url, headers=self.get_headers(), params=params)


    def upload_from_VK(self, file_url, file_name, folder_name):
        ''' Загрузка файла на сервер '''

        uri = 'v1/disk/resources/upload'
        url = self.host+uri
        params = {'path': f'/{folder_name}/{file_name}',
                  'url': file_url, 'overwrite': 'true'}
        response = requests.post(url, headers=self.get_headers(), params=params)
        if response.status_code == 202:
            print(f'Загрузка файла {file_name} прошла успешно')


if __name__ == '__main__':
# подключение к vk
    user_vk = VK_photo(personal.vk_token, version='5.131')
# получение фото
    user_vk.get_photos(personal.owner_id)
# записываем лог в json
    user_vk.save_photo_info_to_file()

# подключение к яндекс-диску
    uploader = YaUploader(personal.yd_token)
    uploader.get_headers()

# создание папки с фото
    folder_photo = 'PhotoOfKurs'
    uploader.create_folder(folder_photo)

# загрузка фото
    for i in tqdm(range(len(user_vk.images))):
        el = user_vk.images[i]
        uploader.upload_from_VK(el['url'], el['file_name'], folder_photo)

    