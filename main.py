import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api import VkUpload
import requests
from io import BytesIO

#Ваш токен тут
token = 'vk1.a.g6xsx5S3DmK6Oe0c1DQKoSFKtEiS666KqYWpZirwN2J7BdJ6UscyQaZHa3ftNcH19Mm2XnwxJF9nMxbKyfdD6u-oNAPjqj0EGNibrL4md_y_Z2kRX2HJHPHHpR-qhc83eSfh9aeCv8fFHebgZz-TYx8q3RgtVeMaT6IWjxuqARKCmedApQ7hNh2nNA_N5ZQboOBB2K3Gm7Ogm6ZN0t810Q'


auth = vk_api.VkApi(token=token)
api = auth.get_api()
longpoll = VkLongPoll(auth)
upload = VkUpload(auth)


def write_message(user_id, message, attachment):
    """
    Отпралвяет пользователю сообщение

    :param user_id: id пользователя
    :param message: сообщение для отправки
    :param attachment: вложения для отправки
    """

    auth.method('messages.send',
                {
                    'user_id':user_id,
                    'message':message,
                    'random_id':get_random_id(),
                    'attachment': attachment})

def upload_photo(upload, url):

    """
    Загружает картинку в память

    :param upload: объект VkUpload
    :param url: ссылка на картинку
    :return: параметры картинки для отправки
    """

    img = requests.get(url).content
    f = BytesIO(img)

    response = upload.photo_messages(f)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return [owner_id, photo_id, access_key]

def main():
    #Слушаем события чата
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:

            user_id = event.user_id #id отправителя

            #Получает последние два сообщения из истории сообщений. Если Пользователь только начал диалог с ботом, то выведется приветственное сообщение
            history = auth.method('messages.getHistory', {'peer_id': event.peer_id, 'count': 2})['items']
            if len(history) <= 1:
                write_message(user_id, "Привет! Это сообщество отправки вам ваших же изображений! Отправляйте мне фото и я отправлю вам их же в ответ!", ','.join([]))

            #Получаем последнее сообщение пользователя
            last_item = history[0]
            print(last_item)
            photos = []
            #Проходимся по всем вложениям
            for attachment in last_item['attachments']:
                if attachment['type'] == 'photo':
                    #Берем оригинальное изображение
                    url =  attachment['photo']['orig_photo']['url']
                    res = upload_photo(upload, url)
                    photos.append(f'photo{res[0]}_{res[1]}_{res[2]}')

            if photos:
                write_message(user_id, f'Взгляните еще раз на {'вашу прекрасную картинку' if len(photos) == 1 else 'ваши прекрасные картинки'}!', ','.join(photos))

main()
