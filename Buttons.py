from Widget import *


class Button(Widget):
    def __init__(self, images, action, coord, circle=True, type_button='Push', scale_zoom_x=0.05, scale_zoom_y=0.05,
                 name=None):
        """Загрузка картинок, действие, координаты, тип - push, toggle"""
        self.images = []
        self.circle = circle
        self.scale_zoom_x = scale_zoom_x
        self.scale_zoom_y = scale_zoom_y
        self.name = name
        self.original_images = []
        for image in images:
            img = check_image(image, color_key=-1)
            self.images.append(img)
            self.original_images.append(img)
        self.action = action
        self.pressed = False
        self.type_button = type_button
        self.pos = coord
        super().__init__(self.images[0], coord)
        self.test = False

    def get_active(self):
        return self.active or self.pressed

    def get_rect(self):
        return self.rect

    def get_pressed(self):
        return self.pressed

    def set_pressed(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.type_button == 'Push':
                self.pressed = event.button == 1 and self.rect.collidepoint(event.pos)
        if self.type_button == 'Toggle':
            if event.button == 1:
                if self.pressed:
                    self.pressed = not self.pressed
                else:
                    self.pressed = self.rect.collidepoint(event.pos)
        if self.type_button == 'Radio':
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.pressed = True
                button_list = self.get_radio_list().get_buttons()[:]
                button_list.remove(self)
                for button in button_list:
                    button.pressed = False

    def get_surface(self):
        if not self.pressed:
            if self.active:
                return self.images[1]
            else:
                return self.images[0]
        else:
            return self.images[2]

    def set_application(self, app):
        self.app = app
        self.generate_image()

    def generate_image(self):
        self.images.clear()
        # size = self.app.size_screen
        for image in self.original_images:
            if self.circle:
                self.images.append(scale_to(image, [self.app.get_size(0, self.scale_zoom_x)[1]] * 2))
            else:
                self.images.append(scale_to(image, self.app.get_size(self.scale_zoom_x, self.scale_zoom_y)))
        self.rect = self.images[0].get_rect()
        self.rect.x, self.rect.y = self.app.get_size(*self.pos)
        if self.test:
            print(self.rect, 'ggw')
            # self.coord =self.app.get_size(*self.pos)[0] - self.images[0].get_width(), 0

    def update(self, event):
        """Обновление стандартной кнопки"""
        if event.type == pygame.MOUSEBUTTONUP:
            self.set_pressed(event)
            if self.get_pressed():
                self.set_image(self.images[2])
                if self.action is not None:
                    self.action()


class TextWidget(Button):
    def __init__(self, image, coord):
        if image is None:
            self.image = Surface((100, 100))
        else:
            self.image = check_image(image, 'image_text_widget')
        self.action = self.write_text
        self.pressed = False
        self.last_key = ''
        self.len_text = 0
        self.text = ''
        super().__init__([self.image] * 2, self.write_text, coord)

    def get_surface(self):
        return self.image

    def set_pressed(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and event.button == 1:
                self.pressed = not self.pressed
            else:
                self.pressed = event.button == 1 and self.rect.collidepoint(event.pos)

    def write_text(self, keys):
        """Функция написания текста в виджете TextWidget"""
        # print(keys)
        # Получение имени клавиши, если в программе выбран язык - английский, если выбран русский, то
        # подключается словарь "мазахиста"
        for key in keys:
            key_name = pygame.key.name(key)
            if key_name == 'return':
                self.set_active(False)
                return
            if key_name in good_symbols and self.len_text <= 16000:
                # Проверка раскладки
                if get_lang() == 'eng' and key_name != self.last_key:
                    self.text += key_name
                if get_lang() == 'ru' and key_name != self.last_key:
                    if key_name in list(rus_text.keys()):
                        if rus_text[key_name] != self.last_key:
                            self.text += rus_text[key_name]
                    else:
                        self.text += key_name
            if key_name == 'space' and self.len_text <= 16000 and key_name != self.last_key:
                self.text += ' '
            if key_name == 'backspace' and len(self.text) >= 0:
                self.text = self.text[:-1]
            self.last_key = key_name
            if get_lang() == 'ru':
                if key_name in list(rus_text.keys()):
                    self.last_key = rus_text[key_name]

    def search_point(self):
        json_response = requests.get(
            f'https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={self.text}&format=json')
        if json_response.status_code == 200:
            if len(json_response.json()['response']['GeoObjectCollection']['featureMember']) > 0:
                coord = json_response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']["Point"]["pos"].split()
                self.app.get_map().go_to_point([float(coord[0]), float(coord[1])])

    def get_normal_text(self):
        """Эта функция возвращает текст для вывода"""
        return self.text

    def set_text(self, text):
        """Эта функция задаёт текст из переменной text"""
        self.text = text

    def delete_text(self):
        self.text = ''
        self.generate_image()

    def generate_image(self):
        image = Smooth((0, 0), self.app.get_size(0.3, 0.05), int(self.app.get_size(0.3, 0.015)[1]),
                       (200, 200, 200)).generate_smooth()
        text = TextBox(self.app.get_size(0.3, 0.035)[1], self.get_normal_text(), color=(10, 10, 10)).get_image()
        self.len_text = text.get_width()
        image.blit(text, [10, 0], ((text.get_width() - self.app.get_size(0.21, 0)[0], 0),
                                   self.app.get_size(0.21, 0.05)))
        if image.get_width() != self.image.get_width() or image.get_height() != self.image.get_height():
            self.image = image
            self.rect = self.image.get_rect()
        self.set_image(image)

    def update(self, *args):
        """Обновление текстового виджета"""
        if self.app.write_tik >= 10:
            event = args[0]
            if event.type == 'buttons' and self.get_pressed() or self.active:
                self.write_text(self.app.pressed_key)
            self.generate_image()
            self.set_pressed(event)
            self.app.write_tik = 0


class Slider(Widget):
    def __init__(self, image, coord, height_slider, width_slider=10,
                 color_slider=(150, 150, 150)):
        """Кнопка 'Slider'
        Очень полезная вещь, используется для динамичного регулирования параметров
        звука, зума и тд"""
        # изображение
        self.image_slider = image
        # координаты чего-то
        self.coord = coord
        # радиус шарика слайдера
        self.radius = image.get_width() // 2
        # координаты кнопки
        self.coord_button = coord
        # высота слайдера
        self.height_slider = height_slider
        # ширина слайдера
        self.width_slider = width_slider
        # координаты слайдера
        self.coord_slider = [0, 0]
        # цвет полоски слайдера
        self.color_slider = color_slider
        # нажат ли слайдер
        self.pressed = False
        super().__init__([image], self.coord, stock=False)
        self.rect = pygame.Rect(coord, (self.radius * 2, height_slider))
        self.generate_image()

    def get_pressed(self):
        """Возвращает информацию - нажата ли кнопка"""
        return self.pressed

    def set_pressed(self):
        """Проверка на то, что кнопка активна"""
        self.pressed = pygame.mouse.get_pressed()[0] == 1 and self.rect.collidepoint(pygame.mouse.get_pos()[0],
                                                                                     pygame.mouse.get_pos()[1])

    def get_active(self):
        return self.active or self.pressed

    def generate_image(self):
        image = pygame.Surface((self.rect.width, self.rect.height))
        image.set_colorkey((0, 0, 0))
        if self.rect.y + self.radius <= pygame.mouse.get_pos()[1] <= self.rect.y + self.height_slider - self.radius:
            self.coord_slider[1] = pygame.mouse.get_pos()[1] - self.rect.y - self.radius
        pygame.draw.rect(image, self.color_slider, ((self.radius - self.width_slider // 2, 0), (self.width_slider,
                                                                                                self.height_slider)))
        image.blit(self.image_slider, (0, self.coord_slider[1]))
        self.set_image(image)

    def get_value(self):
        return abs(self.coord_slider[1] - self.app.get_size(0, self.coord_button[1])[1] - 10) / self.height_slider

    def update(self, event):
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION] and self.app.mouse_pressed(1):
            self.set_pressed()
            if self.get_active():
                self.generate_image()


class RadioButtons:
    def __init__(self, buttons):
        """Список кнопок, с 1 выбором"""
        self.buttons = []
        for b in buttons:
            b.set_radio_list(self)
            self.buttons.append(b)
        self.choice = 'map'

    def add_button(self, button):
        """Добавляет кнопки в список"""
        if button not in self.buttons:
            self.buttons.append(button)
        else:
            raise Exception('Такая кнопка в списке кнопок уже есть')

    def remove_button(self, button):
        """Удаляет кнопку из списка"""
        if button in self.buttons:
            self.buttons.remove(button)
        else:
            raise Exception('Такой кнопки в списке кнопок нет')

    def get_choice(self):
        """Возвращает выбор"""
        return self.choice

    def set_choice(self, choice):
        """Устанавливает выбор"""
        self.choice = choice

    def get_buttons(self):
        """Получить список кнопок"""
        return self.buttons


class RadioButton(Button):
    def __init__(self, images, action, coord, choice, circle=False, type_button='Radio', scale_zoom_x=0.08,
                 scale_zoom_y=0.035, name=None):
        super().__init__(images, action, coord, circle, type_button, scale_zoom_x, scale_zoom_y, name)
        self.radio_list = None
        self.choice = choice
        self.action = self.set_choice

    def set_choice(self):
        """Устанавливает выбор"""
        if self.radio_list is not None:
            if self.radio_list.get_choice() != self.choice:
                self.radio_list.set_choice(self.choice)
        else:
            raise Exception('Эта кнопка не относится к списку радио кнопок')

    def set_radio_list(self, radio_list):
        """Задаёт список радиокнопок"""
        self.radio_list = radio_list

    def s_p(self):
        self.pressed = True

    def get_radio_list(self):
        """Возвращает список кнопок, к которой относится эта кнопка"""
        return self.radio_list
