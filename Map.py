import requests
from pygame import Surface, image
import pygame
from io import BytesIO
from Widget import Widget, Application
from WEB_requests import LoadChunk


class Map(Widget):
    def __init__(self, app):
        """Инициализация виджета"""
        super().__init__(Surface((100, 100)), (0, 0), size=(800, 600))
        self.app = app
        self.radio_buttons = None
        # координаты
        self._coord = [37.618564, 55.755486]
        # зум
        self.zoom_step = {2: 10, 3: 6, 4: 3, 5: 1.5, 6: 0.75, 7: 0.4, 8: 0.2, 9: 0.1, 10: 0.05, 11: 0.025, 12: 0.0125,
                          13: 0.006, 14: 0.003, 15: 0.0015, 16: 0.00075, 17: 0.0004, 18: 0.0002, 19: 0.0001}
        self._zoom = 12
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

    def set_radio_button(self, radio_button):
        self.radio_buttons = radio_button

    def clear(self):
        self._images.clear()
        self.loads.clear()

    def zoom_in(self):
        """Приблизить карту"""
        self._zoom += 1
        if self._zoom > 19:
            self._zoom = 19
        self.clear()
        self.update_map()

    def zoom_out(self):
        """Отдалить карту"""
        self._zoom -= 1
        if self._zoom < 2:
            self._zoom = 2
        self.clear()
        self.update_map()

    def move_left(self):
        """Сместить карту влево на зум"""
        s = self._coord[0]
        self._coord[0] -= self.zoom_step[self._zoom]
        if self._coord[0] < -180:
            if s == -180:
                self._coord[0] = 180
            else:
                self._coord[0] = -180
        self.update_map()

    def move_right(self):
        """Сместить карту вправо на зум"""
        s = self._coord[0]
        self._coord[0] += self.zoom_step[self._zoom]
        if self._coord[0] > 180:
            if s == 180:
                self._coord[0] = -180
            else:
                self._coord[0] = 180
        self.update_map()

    def move_up(self):
        """Сместить карту вверх на зум"""
        self._coord[1] += self.zoom_step[self._zoom]
        if self._coord[1] > 90:
            self._coord[1] = 90
        self.update_map()

    def move_down(self):
        """Сместить карту вниз на зум"""
        self._coord[1] -= self.zoom_step[self._zoom]
        if self._coord[1] < -90:
            self._coord[1] = -90
        self.update_map()

    def check_type(self):
        if self.radio_buttons is not None:
            if self._type != self.radio_buttons.get_choice():
                self._type = self.radio_buttons.get_choice()
                self.clear()

    def add_image(self, request: requests, info):
        # проверка на нужность
        if info[0] in [self._coord[0] + self._zoom * i for i in [-1, 1]] or info[1] in \
                [self._coord[1] + self._zoom * i for i in [-1, 1]] or tuple(self._coord) == info[:2]:
            if info[2] == self._zoom and info[3] == self._type:
                # если работаает
                if request.status_code == 200:
                    self._images[info[:2]] = image.load(BytesIO(request.content))
                else:
                    pass
                    # print(f"Что-то пошло не так фрейм не загрузился")

    def update_map(self):
        """обновление и генерация кадра"""
        # загрузка новых кадров
        self.check_type()
        _coord = self._coord[0], self._coord[1]
        if (_coord[0], _coord[1], self._zoom, self._type) not in self.loads:
            params = {
                "ll": f"{_coord[0]},{_coord[1]}",
                "l": self._type,
                "z": self._zoom,
                "size": "600,450"
            }
            self.app.add_thread(
                LoadChunk(self.api_server, params, self.add_image, (_coord[0], _coord[1], self._zoom, self._type)))
            self.loads.append((_coord[0], _coord[1], self._zoom, self._type))
        for _y in [1, -1]:
            _coord = self._coord[0], self._coord[1] + self._zoom * _y
            if (_coord[0], _coord[1], self._zoom, self._type) not in self.loads:
                params = {
                    "ll": f"{_coord[0]},{_coord[1]}",
                    "l": self._type,
                    "z": self._zoom,
                    "size": "600,450"
                }
                self.app.add_thread(
                    LoadChunk(self.api_server, params, self.add_image, (_coord[0], _coord[1], self._zoom, self._type)))
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
                self.app.add_thread(
                    LoadChunk(self.api_server, params, self.add_image, (_coord[0], _coord[1], self._zoom, self._type)))
                self.loads.append((_coord[0], _coord[1], self._zoom, self._type))
        # генерация изображения
        try:
            if len(self.app.threads) == 0:
                self.set_image(self._images[tuple(self._coord)])
        except Exception as error:
            self.set_image(Surface((800, 600)))
            print(f'Произошла ошибка: {type(error)}')

    # для тестов
    def get_surface(self):
        self.update_map()
        return self.image

    def update(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.move_right()
            if event.key == pygame.K_LEFT:
                self.move_left()
            if event.key == pygame.K_UP:
                self.move_up()
            if event.key == pygame.K_DOWN:
                self.move_down()
            if event.key == pygame.K_PAGEUP:
                self.zoom_out()
            if event.key == pygame.K_PAGEDOWN:
                self.zoom_in()


if __name__ == '__main__':
    app = Application((800, 600))
    map = Map(app)
    app.add_widget(map)
    app.run()
