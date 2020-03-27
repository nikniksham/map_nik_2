from io import BytesIO
from WEB_requests import WebLoad
from Widget import *


def get(r):
    if r.status_code == 200:
        print(r.json())
        ll = ','.join(r.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split())
        params_image = {
            "ll": f'{ll}',
            'spn': '5,5',
            "l": 'map',
            "z": "10",
            "size": "400,400"
        }
        thread_2 = WebLoad('http://static-maps.yandex.ru/1.x/', params_image, get_image)
        app.add_thread(thread_2)
    else:
        raise Exception('ошибочка')


app = Application([400, 400])


def get_image(r):
    b = Widget(pygame.image.load(BytesIO(r.content)), [0, 0])
    app.add_widget(b)


params = {
            "apikey": '40d1649f-0493-4b70-98ba-98533de7710b',
            'format': 'json',
            "geocode": input(),
        }

thread = WebLoad(f"http://geocode-maps.yandex.ru/1.x/", params, get)
app.add_thread(thread)
app.run()
