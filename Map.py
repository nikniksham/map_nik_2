import requests
from pygame import Surface, image, Rect
import pygame
from io import BytesIO
from Widget import Widget, Application
from WEB_requests import LoadChunk


class Map(Widget):
    def __init__(self, app):
        """Инициализация виджета"""
        super().__init__(Surface((100, 100)), (0, 0), size=(800, 600))
        self.app = app
        # координаты
        self._coord = [0, 0]
        # зум
        self._zoom = 10
        # тип карты
        self._type = "map"
        # список изображений
        self._images = {}
        # список загружаемых изображений
        self.loads = []
        # адресс апи сервиса
        self.api_server = "http://static-maps.yandex.ru/1.x/"
        # обновление и генерация карты
        self.update_map()

    def zoom_in(self):
        """Приблизить карту"""
        self._zoom += 1
        self.update_map()

    def zoom_out(self):
        """Отдалить карту"""
        self._zoom -= 1
        self.update_map()

    def move_left(self):
        """Сместить карту влево на зум"""
        self._coord[0] -= self._zoom
        self.update_map()

    def move_right(self):
        """Сместить карту вправо на зум"""
        self._coord[0] += self._zoom
        self.update_map()

    def move_up(self):
        """Сместить карту вверх на зум"""
        self._coord[1] -= self._zoom
        self.update_map()

    def move_down(self):
        """Сместить карту вниз на зум"""
        self._coord[1] += self._zoom
        self.update_map()

    def add_image(self, request: requests, info):
        # проверка на нужность
        if info[0] in [self._coord[0] + self._zoom * i for i in [-1, 1]] or info[1] in \
           [self._coord[1] + self._zoom * i for i in [-1, 1]] or self._coord == info[:2]:
            if info[2] == self._zoom and info[3] == self._type:
                # если работаает
                if request.status_code == 200:
                    self._images[info[:3]] = image.load(BytesIO(request.content))
                    print(f"add {info[:3]}, {self._images[info[:3]]}")
                else:
                    raise Exception(f"Что-то пошло не так фрейм не загрузился")

    def update_map(self):
        """обновление и генерация кадра"""
        # загрузка новых кадров
        _coord = self._coord[0], self._coord[1]
        if (_coord[0], _coord[1], self._zoom, self._type) not in self.loads:
            params = {
                "ll": f"{_coord[0]},{_coord[1]}",
                "l": self._type,
                "z": self._zoom,
                "size": "600,450"
            }
            self.app.add_thread(LoadChunk(self.api_server, params, self.add_image, (_coord[0], _coord[1], self._zoom, self._type)))
        for _y in [1, -1]:
            _coord = self._coord[0], self._coord[1] + self._zoom * _y
            if (_coord[0], _coord[1], self._zoom, self._type) not in self.loads:
                params = {
                    "ll": f"{_coord[0]},{_coord[1]}",
                    "l": self._type,
                    "z": self._zoom,
                    "size": "600,450"
                }
                self.app.add_thread(LoadChunk(self.api_server, params, self.add_image, (_coord[0], _coord[1], self._zoom, self._type)))
                self.loads.append((_coord[0], _coord[1], self._zoom, self._type))
        for _x in [1, -1]:
            _coord = self._coord[0] + self._zoom * _x, self._coord[1]
            if (_coord[0], _coord[1], self._zoom, self._type) not in self.loads:
                params = {
                    "ll": f"{_coord[0]},{_coord[1]}",
                    "l": self._type,
                    "z": self._zoom,
                    "size": "600,450"
                }
                self.app.add_thread(LoadChunk(self.api_server, params, self.add_image, (_coord[0], _coord[1], self._zoom, self._type)))
                self.loads.append((_coord[0], _coord[1], self._zoom, self._type))
        # генерация изображения
        try:
            self.set_image(self._images[tuple(self._coord)])
        except Exception:
            self.set_image(Surface((600, 450)))

    # для тестов
    def get_surface(self):
        self.update_map()
        return self.image


if __name__ == '__main__':
    app = Application((500, 500))
    map = Map(app)
    app.add_widget(map)
    app.run()
