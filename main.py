#main.py - инициализация всего проекта, запускать с этого файла


#импорт библиотек
import flet as ft
import os
from modules.db import DB
from UI.visual_draw import UI
from modules.config_parser import ConfigParser

#конфига для проекта
config_name = 'secrets.json'

#запуск основных файлов проекта
if __name__ == '__main__':
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(config_name)
    db = DB(config.get_config()['db_path'])
    ui = UI(config.get_config(), db)
    ft.app(target=ui.main, port=9996)