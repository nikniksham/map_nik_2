import requests

address = input("Введите адрес: ")
json_response = requests.get(f'https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={address}&format=json')
coord = json_response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']["Point"]["pos"]
print(coord)