# импортируем библиотеки для работы конфиг_парсера

import json
import os
import sys



# создаем класс
class ConfigParser:
    def __init__(self, file_path):
        # инициализируем backend
        super(ConfigParser, self).__init__()
        self.__file_path = file_path
        self.__default = {'threads_count': 5, 'db_path': 'db.sqlite3'}
        self.__current_config = None
        self.load_conf()

    def load_conf(self):
        # считывание данных с secrets.json
        if os.path.exists(self.__file_path):
            with open(self.__file_path, 'r', encoding='utf-8') as file:
                self.__current_config = json.loads(file.read())
        else:
            self.create_conf(self.__default)
            sys.exit('config is not existed')

    def create_conf(self, config):
        # создание secrets.json, в случае если он отсутствует
        with open(self.__file_path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(config, sort_keys=True, indent=4))

    def get_config(self):
        # получение конфига
        return self.__current_config