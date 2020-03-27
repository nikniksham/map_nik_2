from Widget import ThreadApp, Thread
import requests


class WebLoad(ThreadApp):
    def __init__(self, url: str, params: dict, res_to):
        """Делает запрос и возвращает результат request
        url - адресс с которого надо загрузить
        params - параметры для запроса
        res_to - функциюкоторую надо будет вызвать после завершения запроса"""
        Thread.__init__(self)
        self.status = True
        self.url = url
        self.params = params
        self.res_to = res_to

    def run(self):
        """Запуск потока"""
        # Скачиваем файл
        self.download_file()
        self.res_to(*self.get_res())
        # Статус завершили работать
        self.status = False
        self.app.thread_break = True

    def get_res(self):
        res = self.res
        self.res = None
        return (res,)

    def download_file(self):
        """Скачиваем файл"""
        print("start")
        self.res = requests.get(self.url, params=self.params)
        print("loaded")


class LoadChunk(WebLoad):
    def __init__(self, url: str, params: dict, res_to, coord):
        self.coord = coord
        super().__init__(url, params, res_to)

    def get_res(self):
        res = self.res
        self.res = None
        return (res, self.coord)
