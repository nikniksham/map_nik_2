from pygame import Surface
from pygame.transform import *
import pygame
import os
from threading import Thread
from pygame.draw import *
from ctypes import *
import requests
# Импортируем всё необходимое


def get_lang():
    user32 = windll.user32
    hwnd = user32.GetForegroundWindow()
    thread_ID = user32.GetWindowThreadProcessId(hwnd, None)
    return 'ru' if user32.GetKeyboardLayout(thread_ID) == 68748313 else 'eng'


# Эти строки мазахизма - русская раскладка
rus_text = {'`': 'ё', 'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г',
            'i': 'ш', 'o': 'щ', 'p': 'з', '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в',
            'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л', 'l': 'д', ';': 'ж', "'": 'э',
            'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь', ',': 'б',
            '.': 'ю'}
good_symbols = ['`', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', 'a', 's', 'd', 'f',
                'g', 'h', 'j', 'k', 'l', ';', "'", 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '0',
                '1', '2', '3', '4', '5', '6', '7', '8', '9', '-']
pygame.init()
# Константы
FONT_STYLE = 'data/Font/NeogreyMedium.otf'


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    # if colorkey is not None:
    if colorkey == -1:
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    image = image.convert_alpha()
    return image


def check_image(image, help_name=None, color_key=None):
    """Проверка картинки, или путя к ней
    Есть 2 параметра: 1 обязательный - путь к картинке, 2 - необязательный, это имя, нужное для отладки"""
    # 2 параметра - картинка, или путь к ней, а так же её имя, нужное для отладки
    if type(image) != pygame.Surface:
        if type(image) == str:
            image = load_image(image, color_key)
        else:
            if help_name is None:
                help_name = image
            raise Exception(f'Неподходяций формат, заданый картинке {help_name}')
    return image


class Smooth:
    """Создаёт скруглёное Изображение"""
    def __init__(self, pos, size, smooth, color=(255, 255, 255)):
        """pos - левая верхняя точка
        size - размер всего изображения
        smooth - радиус закругления
        color - цвет изображения"""
        # Радиус закругления
        self.smooth = 0
        # Изображение
        self.image = pygame.Surface((10, 10))
        # Прямоугольник изображения
        self.rect = pygame.Rect(0, 0, 0, 0)
        # Задаём позицию
        self.set_pos(pos)
        # Задаём размер кнопки
        self.set_size(size)
        # Задаём радиус закругления
        self.set_smooth(smooth)
        # Задаём цвет
        self.color = color
        # Режим отладки выводит отладочную иномацию
        self.test = False
        self.api_server = "http://static-maps.yandex.ru/1.x/"

    def set_pos(self, pos):
        """Задать позицию"""
        if len(pos) != 2:
            raise Exception(f"pos is not pos")
        self.rect.x, self.rect.y = pos

    def set_size(self, size):
        """Задать размер"""
        if len(size) != 2:
            raise Exception(f"size is not size")
        self.rect.width, self.rect.height = size
        self.image = pygame.Surface(size)

    def set_smooth(self, smooth):
        """задать радиус скругления"""
        if type(smooth) != int:
            raise TypeError(f"type {smooth} != type int")
        if min(self.rect.width, self.rect.height) // 2 >= smooth:
            self.smooth = smooth
        else:
            raise Exception(f"Smooth more than max smooth")

    def set_color(self, color):
        """Задать цвет RGB"""
        if len(color) != 3:
            raise Exception(f"{color} is not color.")
        self.color = color

    def generate_smooth(self):
        """сгенерировать изображение
        возвращает готовое изображение"""
        self.image.set_colorkey((0, 0, 0))
        if self.test:
            print('Smooth Image')
            # print(self.rect, self.smooth)
            # print(self.rect.width - self.smooth)
            print(self.smooth, self.smooth)
            print(self.rect.width - self.smooth, self.smooth)
            print(self.smooth, self.rect.height - self.smooth)
            print(self.rect.width - self.smooth, self.rect.height - self.smooth)
            print((0, self.smooth), (self.rect.width, self.rect.height - self.smooth * 2))
            print((self.smooth, 0), (self.rect.width - self.smooth * 2, self.rect.height))
        # левый верхний круг
        circle(self.image, self.color, (self.smooth, self.smooth), self.smooth)
        # правый верхний круг
        circle(self.image, self.color, (self.rect.width - self.smooth, self.smooth), self.smooth)
        # левый нижний круг
        circle(self.image, self.color, (self.smooth, self.rect.height - self.smooth), self.smooth)
        # правый нижний круг
        circle(self.image, self.color, (self.rect.width - self.smooth, self.rect.height - self.smooth), self.smooth)
        # горизонтальный прямоугольник
        rect(self.image, self.color, ((0, self.smooth), (self.rect.width, self.rect.height - self.smooth * 2)))
        # вертикальный прямоугольник
        rect(self.image, self.color, ((self.smooth, 0), (self.rect.width - self.smooth * 2, self.rect.height)))
        return self.image


class TextBox(pygame.sprite.Sprite):
    """Создаёт текст"""
    def __init__(self, size_pixel, text, color=(0, 0, 0)):
        """size_pixel - размер текста в пикселях
        text - текст
        color - цвет текста"""
        pygame.sprite.Sprite.__init__(self)
        # текст
        self.text = ''
        # размер шрифта
        self.font_size = 0
        # цвет шрифта
        self.color = (0, 0, 0)
        # изображение
        self.image = pygame.Surface((10, 10))
        # задаём размер шрифта
        self.set_font_size(size_pixel)
        # задаём текст
        self.set_text(text)
        # задаём цвет
        self.set_color(color)
        # инициализируем пугаме текст
        pygame.font.init()
        # задаём шрифт
        self.font = pygame.font.Font('data/Font/NeogreyMedium.otf', self.font_size)

    def set_font_size(self, size_pixels):
        """Задать размер текста в пикселях"""
        if type(size_pixels) not in [int, float]:
            raise TypeError(f"type {type(size_pixels)} not in [int, float]")
        self.font_size = int(size_pixels)

    def set_text(self, text):
        """Задать текст"""
        if type(text) != str:
            raise TypeError(f"type {type(text)} != type str")
        self.text = text

    def set_color(self, color):
        """Задать цвет RGB"""
        if len(color) != 3:
            raise Exception(f"{color} is not color.")
        self.color = color

    def get_image(self):
        """Получить изображение с текстом"""
        self.image = self.font.render(self.text, False, self.color)
        return self.image


def scale_to(image, size):
    size = (round(size[0]), round(size[1]))
    return scale(image, size)


def create_text(text, size, color):
    font_type = pygame.font.Font(FONT_STYLE, size)
    return font_type.render(text, True, color)


class Event:
    def __init__(self, a):
        self.type = a


class ThreadApp(Thread):
    def __init__(self, funk):
        """Запускает поток который выполняет функцию"""
        super().__init__(target=funk, args=[self])
        self.app = None
        self.status = True

    def set_status(self, status: bool):
        """установить статус выполненого задания"""
        self.status = bool(status)
        if not self.status and self.app is not None:
            self.app.thread_break = True

    def get_status(self):
        return self.status

    def add_app(self, app):
        self.app = app

    def remove_app(self):
        self.app = None


class Widget:
    def __init__(self, surfaces, coord, active=False, is_zooming=False, zoom=1, max_zoom=1, min_zoom=0.15,
                 is_scrolling_x=False, is_scrolling_y=False, is_scroll_line_x=False, is_scroll_line_y=False, scroll_x=0,
                 scroll_y=0, size=None, stock=True):        # размер экрана
        self.size = size
        # зум
        self.zoom = zoom
        self.stock = stock
        # скролл по y
        self.scroll_y = scroll_y
        # скролл по x
        self.scroll_x = scroll_x
        # скролимый по x
        self.is_scrolling_x = is_scrolling_x
        # скролимый по x иил нет
        self.is_scrolling_y = is_scrolling_y
        # программа
        self.app = None
        self.start_zoom = zoom
        # оригинальное изоьражение
        res_surfaces = []
        if type(surfaces) == str:
            res_surfaces.append(load_image(surfaces).copy())
        elif type(surfaces) == Surface:
            res_surfaces = [surfaces]
        else:
            for surface in surfaces:
                res_surfaces.append(check_image(surface, 'Widget'))
        self.images_orig = res_surfaces[:]
        self.set_image(self.images_orig[0])
        # рект
        self.rect = self.image.get_rect()
        # коорданиаты
        self.coord = coord
        self.rect.x, self.rect.y = 0, 0
        # активени или нет
        self.active = active
        # зумируемый
        self.is_zooming = is_zooming
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        # есть скрол лента по x или нет
        self.is_scroll_line_x = is_scroll_line_x and is_scrolling_x
        # есть скрол лента по y или нет
        self.is_scroll_line_y = is_scroll_line_y and is_scrolling_y

    def set_image(self, image):
        self.image_orig = image
        self.image = self.image_orig
        if self.size is not None and self.stock:
            self.image = scale_to(self.image, self.size)
        if self.app is not None:
            self.set_position()
        if self.stock:
            self.zoom = self.start_zoom
        if self.zoom != 1:
            self.set_zoom(zoom=self.zoom)

    # пересчитать позицию
    def set_position(self):
        w_, h_ = self.coord
        size = self.app.get_size(1, 1)
        # self.image = scale_to(self.image_orig, (w, h))
        if w_ < 0:
            self.rect.right = size[0] - size[0] * abs(w_)
        else:
            self.rect.x = size[0] * abs(w_)
        if h_ < 0:
            self.rect.bottom = size[1] - size[1] * abs(h_)
        else:
            self.rect.y = size[1] * abs(h_)

    # используется в приложении или нет
    def in_application(self):
        return True if self.app is not None else False

    # задать приложение в котором используется
    def set_application(self, app):
        self.app = app

    def get_application(self):
        return self.app

    # получить зумиреумый
    def get_is_zooming(self):
        return self.is_zooming

    # получить зум
    def get_zoom(self):
        # получить зум
        if self.is_zooming:
            return self.zoom
        return 1

    def zoom_update(self, event):
        if self.rect.collidepoint(event.pos):
            if event.button == 5:
                self.zoom += self.zoom * 0.1
                if self.zoom > self.max_zoom:
                    self.zoom = self.max_zoom
            elif event.button == 4:
                self.zoom -= self.zoom * 0.1
                if self.zoom < self.min_zoom:
                    self.zoom = self.min_zoom
            self.set_zoom(self.zoom)

    def set_zoom(self, zoom):
        w = self.image_orig.get_width() * zoom
        h = self.image_orig.get_height() * zoom
        w_, h_ = self.image_orig.get_size()
        scroll_x = -self.scroll_x if self.is_scrolling_x else -((w_ - w) / 2)
        scroll_y = -self.scroll_y if self.is_scrolling_y else -((h_ - h) / 2)
        self.image = Surface((w, h))
        self.image.blit(self.image_orig, (scroll_x, scroll_y))
        self.image = scale(self.image, (self.image_orig.get_width(), self.image_orig.get_height()))
        if self.size is not None:
            self.image = scale_to(self.image, self.size)
        print(self.image.get_rect())
        self.rect.width, self.rect.height = self.image.get_size()
        if self.app is not None:
            self.set_position()

    # получить скролимый по x
    def get_is_scrolling_x(self):
        return self.is_scrolling_x

    # получить скролимый по y
    def get_is_scrolling_y(self):
        return self.is_scrolling_y

    # получить скрол по x
    def get_scroll_x(self):
        # скрол по x если нельзя, то return False
        if self.is_scrolling_x:
            return self.scroll_x
        return False

    # полчучить скрол по y
    def get_scroll_y(self):
        # скрол по y если нельзя, то return False
        if self.is_scrolling_y:
            return self.scroll_y
        return False

    # проскролить по x
    def set_scroll_x(self, add_num):
        # добавить скрол по x, иначе return False
        if self.is_scrolling_x:
            self.scroll_x += add_num
            return True
        return False

    # проскролить по y
    def set_scroll_y(self, add_num):
        # добавить скрол по y, иначе return False
        if self.is_scrolling_x:
            self.scroll_x += add_num
            return True
        return False

    # обновить виджет
    def update(self, event):
        pass

    # получить активен ли виджет
    def get_active(self):
        return self.active

    # устнавить активным виджет
    def set_active(self, pos):
        if type(pos) in [list, tuple]:
            self.active = self.rect.collidepoint(pos)
            return self.rect.collidepoint(pos)

    # получить эзображение
    def get_surface(self):
        return self.image

    # получить координаты
    def get_coord(self):
        return self.rect.x, self.rect.y

    # поллучить Rect
    def get_rect(self):
        return self.rect

    def generate_image(self):
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.app.get_size(*self.coord)


class AnimationWidgets(Widget):
    def __init__(self, surfaces, coord, sec, active=False, is_zooming=False, zoom=1, max_zoom=1, min_zoom=0.15,
                 is_scrolling_x=False, is_scrolling_y=False, is_scroll_line_x=False, is_scroll_line_y=False, scroll_x=0,
                 scroll_y=0):
        super().__init__(surfaces, coord, active, is_zooming, zoom, max_zoom, min_zoom, is_scrolling_x, is_scrolling_y,
                         is_scroll_line_x, is_scroll_line_y, scroll_x, scroll_y)
        self.sec = sec
        self.tick = 0
        self.index = 0

    def get_active(self):
        return self.active

    def update(self, FPS):
        self.tick += 1 / FPS
        if self.tick >= self.sec:
            self.index += 1
            self.index %= len(self.images_orig)
            self.set_image(self.images_orig[self.index])
            self.tick = 0


class Application:
    # создание экрана
    def set_screen(self, size, full_screen=False):
        # экран
        self.screen = pygame.display.set_mode(size)
        self.screen.fill(self.fill_color)
        # развёрнут на весь экран
        self.full_screen = full_screen
        # размер экрана
        self.size_screen = size
        #  ширина и высота
        self.widht, self.height = size

    def __init__(self, size_screen, fill_color=(0, 0, 0), full_screen=False):
        # создание экрана
        self.fill_color = fill_color
        self.set_screen(size_screen, full_screen)
        # нажатые клавиши клавиатуры
        self.pressed_key = []
        # нажатые клавиши мыши
        self.pressed_mouse_button = []
        # виджеты ключь=слой значение [виджеты]
        self.widgets = {}
        self.index_layers = []
        # аудио байлы
        self.audios = []
        # события функции
        self.events = []
        # потоки
        self.threads = []
        # поток(и) закончил работу
        self.threads_break = False
        # анимационные виджеты
        self.animations = []
        # часы для граничения FPS
        self.clock = pygame.time.Clock()
        # количество кадров в секунду 0 - неограничено
        self.FPS = 80
        # приложение работает
        self.running = True
        # картинка мыши если None то обычная мышь
        self.mouse_image = None
        # список картинок мыши
        self.mouse_images = []
        self.mouse_rect = pygame.Rect(0, 0, 0, 0)
        self.map = None

    def set_map(self, _map):
        self.map = _map

    def get_map(self):
        return self.map

    def get_size(self, x, y):
        return [round(self.size_screen[0] * x), round(self.size_screen[1] * y)]

    # получить FPS
    def get_fps(self):
        """получить количество кадров в секунду"""
        return self.FPS

    # устатвить FPS 0 - неограничено
    def set_fps(self, count_fps: int):
        """установить количество кадров в секунду
        count_fps - желаемок количество fps"""
        # возвращает True если установилость, False если не установилось
        if count_fps >= 0:
            self.FPS = count_fps
            return True
        return False

    # получить виджеты
    def get_widgets(self, layer=None, reverse=False):
        """получить виджеты
        layer - слой с которого хотите получить виджеты по умолчанию, None - все
        reverse - получить в обратной последовательности"""
        # получить виджеты с ключом слой
        if layer is not None:
            return self.widgets[layer]
        else:
            res = []
            keys = sorted(self.widgets.keys(), reverse=reverse)
            for key in keys:
                res += self.widgets[key]
            return res

    # добавить виджеты
    def add_widget(self, widget: Widget, layer=1):
        """добавить виджет
        widget - виджет которй хотите добавить
        layer - слой на который хотите добавить"""
        # добавить виджет на экран на слой=layer если не получается то return False
        if issubclass(type(widget), Widget):
            widget.set_application(self)
            widget.set_position()
            if layer in self.widgets:
                if widget not in self.widgets[layer]:
                    self.widgets[layer].append(widget)
            else:
                self.widgets[layer] = [widget]
            return True
        return False

    def remove_widget(self, widget: Widget):
        """удалить виджет из приложения
        widget - виджет который хотите удалить"""
        good = False
        for layer in self.get_layers():
            if widget in self.widgets[layer]:
                self.widgets[layer].remove(widget)
                good = True
                break
        if not good:
            raise Exception(f"widget not in widgets")

    # получить слои
    def get_layers(self):
        """получить количество слоёв
        sort - отсортированых"""
        # получить список слоёв
        res = list(self.widgets.keys())
        res.sort()
        return res

    # добавить ивент
    def add_event(self, event):
        """добавить функцию которая при вызове не принимает параметры"""
        # добавляем событие выполняется каждую итерацию
        if event not in self.events:
            self.events.append(event)

    def remove_event(self, event):
        """удалить функцию из списка функций"""
        if event in self.events:
            self.events.remove(event)
            return True
        return False

    def add_thread(self, thread):
        """добавить поток"""
        if issubclass(type(thread), ThreadApp):
            if len(self.threads) <= 64:
                self.threads.append(thread)
                thread.add_app(self)
                thread.start()
            else:
                self.threads = []
        else:
            raise Exception(f"ThreadErr: thread is not is subclass ThreadApp or can't add thread")

    def remove(self, thread):
        """удалить поток"""
        if thread in self.threads:
            self.threads.remove(thread)
            thread.remove_app()
            thread.join()
            thread = None
        else:
            raise Exception(f"thread not in application threads")

    # получить размер экрана
    def get_size_screen(self):
        """получить размер экрана"""
        # получить размер экрана
        return self.size_screen

    def get_width(self):
        """получить ширину экрана"""
        # получить ширину экрана
        return self.widht

    def get_height(self):
        """получить высоту экрана"""
        # получить высоту экрана
        return self.height

    def get_full_screen(self):
        """получить режим экрана"""
        # получить развёрнуто на полный экран или нет
        return self.full_screen

    def quit(self):
        """функция которая выполняется при закрытии приложения"""
        # выполняется при закрытии приложения
        pass

    def load_mouse_image(self, file):
        """загрузить изображение для мыши"""
        image = check_image(file, 'mouse')
        self.mouse_images.append(image)

    def set_mouse_image(self, index):
        """задать изображение для мыши
        index - номер изображения в списке считая с 0"""
        # установить картинку мыши из списка картинок мыши
        pygame.mouse.set_visible(False)
        self.mouse_image = self.mouse_images[index]
        self.mouse_rect = self.mouse_image.get_rect()

    def set_mouse_normal(self):
        """задать мышь по умолчанию от OC"""
        # вернуть видимость мыши
        pygame.mouse.set_visible(True)
        self.mouse_image = None

    def draw_mouse(self):
        """отрисовываем мышь"""
        # отрисовка мыши
        if self.mouse_image is not None:
            self.mouse_rect.x, self.mouse_rect.y = pygame.mouse.get_pos()
            self.screen.blit(self.mouse_image, self.mouse_rect)

    def update_screen(self, width, height):
        """обновляем виджеты
        width - ширина
        height - высота"""
        self.set_screen((width, height), self.get_full_screen())
        for widget in self.get_widgets():
            widget.set_position(width, height)

    # main loop
    def run(self):
        """основной цикл"""
        # основной цикл
        while self.running:
            if len(self.pressed_key) != 0:
                for widget in self.get_widgets(reverse=True):
                    if widget.get_active():
                        widget.update(Event('buttons'))
            # print(len(self.threads), 'thread')
            # обробатываем события
            for event in pygame.event.get():
                # событие закрытия
                if event.type == pygame.QUIT:
                    self.running = False
                    return self.quit()
                if event.type == pygame.VIDEORESIZE:
                    width, height = event.w, event.h
                    self.set_screen((width, height), self.get_full_screen())
                    for widget in self.get_widgets():
                        widget.set_position()
                        widget.generate_image()
                if event.type == pygame.MOUSEMOTION:
                    self.set_active_widgets(event)
                    self.widget_event(event)
                # событие нажатия клавиши мыши
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.pressed_mouse_button.append(event.button)
                    self.mouse_key_event(event)
                # событие нажатия клавиши клавиатуры
                if event.type == pygame.KEYDOWN:
                    self.pressed_key.append(event.key)
                    self.get_key_pressed_event(event)
                # событие отжатия клавиши мыши
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button in self.pressed_mouse_button:
                        self.pressed_mouse_button.remove(event.button)
                    self.mouse_key_event(event)
                # событие отжатия клавиши клавиатуры
                if event.type == pygame.KEYUP:
                    if event.key in self.pressed_key:
                        self.pressed_key.remove(event.key)
                    self.widget_event(event)
            # обработка функций
            for funk in self.events:
                funk()
            # отрисовка экрана
            # print(len(self.threads), 'threads')
            for widget in self.get_widgets():
                self.render(widget)
            for i in range(len(self.threads) - 1, -1, -1):
                if not self.threads[i].get_status():
                    self.threads[i].join()
                    self.threads.pop(i)
            # отрисовка мыши
            self.draw_mouse()
            # обновление экрана
            pygame.display.flip()
            if self.FPS != 0:
                self.clock.tick(self.FPS)
            else:
                self.clock.tick()
            self.screen.fill(self.fill_color)
        if not self.running:
            return self.quit()

    # отрисовка экрана
    def render(self, widget):
        """отрисовка виджета
        widget - виджет который надо отрисовать"""
        if issubclass(type(widget), AnimationWidgets):
            if self.FPS != 0:
                widget.update(self.FPS)
            elif self.clock.get_fps() != 0:
                widget.update(self.clock.get_fps())
            self.screen.blit(widget.get_surface(), widget.get_rect())
        elif issubclass(type(widget), Widget):
            self.screen.blit(widget.get_surface(), widget.get_rect())

    def widget_event(self, event):
        for widget in self.get_widgets(reverse=True):
            if widget.get_active():
                widget.update(event)

    # обработчик событий мыши
    def set_active_widgets(self, event):
        """задать виджет кативным"""
        pos = event.pos
        good = False
        for widget in self.get_widgets(reverse=True):
            if good:
                widget.active = False
            else:
                if widget.set_active(pos):
                    good = True

    def mouse_key_event(self, event):
        """обработка событий мыши"""
        # asd
        if event.button == 1 and event.type == pygame.MOUSEBUTTONUP:
            self.widget_event(event)
        else:
            self.mouse_event(event)

    # обработчик всех событий мыши кроме нажатия левой кнопкой мыши
    def mouse_event(self, event):
        """обработка всех событий мыши кроме нажатия левой кнопки мыши"""
        if event.button in [4, 5]:
            for widget in self.get_widgets(reverse=True):
                if widget.get_active() and widget.get_is_zooming():
                    widget.zoom_update(event)
        else:
            self.widget_event(event)

    # проверить нажата ли кнопка мыши
    def mouse_pressed(self, number_mouse):
        """проверить нажата ли эта кнопка мыши
        number_mouse - номер кнопки мыши"""
        return number_mouse in self.pressed_mouse_button

    # получить нажатые кнопки
    def get_pressed_mouse(self):
        """полуить нажатые кнопки мыши"""
        return self.pressed_mouse_button

    #
    # работа с клавиатурой
    #
    # получает события клавиатуры
    def get_key_pressed_event(self, event):
        """обновление кнопок клавиатуры"""
        self.widget_event(event)

    # проверить нажата ли кнопка клавиатуры
    def key_pressed(self, key):
        """получить нажата ли эта кнопка"""
        return key in self.pressed_key

    # получить список нажатых кнопок
    def get_pressed_key(self):
        """получить нажатые кнопки клавиатуры"""
        return self.pressed_key
