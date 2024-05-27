# импортируем библиотеку
import random

# создаем класс для работы с utilites
class Utilities:
    def __init__(self):
        # инициализируем файл
        super(Utilities, self).__init__()

    def random_police_number(self):
        # функция для создания случайного номера для полиса
        out = str()
        a = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        range_start = 10 ** (8 - 1)
        range_end = (10 ** 8) - 1
        out += ''.join(random.choices(a, k=3)) + str(random.randint(range_start, range_end))
        return out