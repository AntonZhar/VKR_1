# ипортируем библиотеки для работы с базой данных

import sqlite3
import os
from threading import Lock

# создаем класс для БД
class DB:
    def __init__(self, path):
        # инициализируем бд
        super(DB, self).__init__()
        self.__lock = Lock()
        self.__db_path = path
        self.__cursor = None
        self.__db = None
        self.init()

    def init(self):
        # создаем 5 таблицы для базы данных, если их нет
        if not os.path.exists(self.__db_path):
            self.__db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.__cursor = self.__db.cursor()
            self.__cursor.execute('''
            CREATE TABLE users(
            row_id INTEGER primary key autoincrement not null,
            name TEXT,
            lastname TEXT,
            patronymic TEXT,
            email TEXT,
            login TEXT,
            password TEXT
            )
            ''')
            self.__cursor.execute('''
            CREATE TABLE agents(
            row_id INTEGER primary key autoincrement not null,
            name TEXT,
            lastname TEXT,
            patronymic TEXT,
            birthdate DATE,
            phone_number TEXT,
            type BOOL
            )
            ''')
            self.__cursor.execute('''
            CREATE TABLE cars(
            row_id INTEGER primary key autoincrement not null,
            brand TEXT,
            model TEXT,
            year INTEGER,
            plate_number TEXT,
            mileage TEXT,
            vin_number TEXT,
            owner TEXT,
            power TEXT,
            sts TEXT,
            own_conditions TEXT,
            own_purpose TEXT
            )
            ''')
            self.__cursor.execute('''
            CREATE TABLE drivers(
            row_id INTEGER primary key autoincrement not null,
            name TEXT,
            lastname TEXT,
            patronymic TEXT,
            sex BOOL,
            birthdate DATE,
            license_number TEXT,
            exp_license_number DATE,
            first_license_number DATE,
            kvs FLOAT,
            kbm FLOAT,
            passport TEXT
            )
            ''')
            self.__cursor.execute('''
            CREATE TABLE osago(
            addendum INTEGER primary key autoincrement not null,
            policy_number INTEGER,
            product TEXT,
            car INTEGER,
            policyholder INTEGER,
            status TEXT,
            date_registration DATE,
            date_start DATE,
            date_end DATE,
            agent INTEGER,
            policy_prize FLOAT,
            payment_status TEXT,
            worker_id INTEGER,
            drivers TEXT,
            cancellation_desc TEXT,
            fee_percent INTEGER,
            policy_prize_without_fee FLOAT
            )
            ''')
            self.__db.commit() # сохраняем базу данных
        else:
            self.__db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.__cursor = self.__db.cursor()

    def db_write(self, queri, args):
        # функция для записи в базу данных
        with self.__lock:
            self.__cursor.execute(queri, args)
            self.__db.commit()

    def db_read(self, queri, args):
        # функция для считывания с базы данных
        with self.__lock:
            self.__cursor.execute(queri, args)
            return self.__cursor.fetchall()