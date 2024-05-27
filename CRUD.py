# импортируем библиотеку для работы с backend'ом

import json
from modules.utilities import Utilities
############static variables#####################
config_name = 'secrets.json' # берем данные из secrets.json
#################################################

# создаем класс для работы с файлом
class CRUD:
    def __init__(self, db):
        # инициализируем данные для работы
        super(CRUD, self).__init__()
        self.__db = db
        self.__utilities = Utilities()

    def check_login(self, login, password):
        # функция для проверки логина
        data = self.__db.db_read('SELECT COUNT(*) FROM users WHERE login = ? AND password = ?', (login, password))[0][0]
        if data > 0:
            return True

    def add_user(self, data):
        # функция для добавления пользователя
        self.__db.db_write('INSERT INTO users (name, lastname, patronymic, email, login, password) VALUES (?, ?, ?, ?, ?, ?)', data)

    def get_basic_query(self):
        # получение данных из бд о осаго
        return self.__db.db_read('SELECT addendum, policy_number, product, car, policyholder, status,'
                                 ' date_registration, date_start, date_end, agent, policy_prize, payment_status FROM osago', ())

    def get_agent_by_id(self, agent_id):
        # получение фио агента по его ID
        data = self.__db.db_read('SELECT name, lastname, patronymic FROM agents WHERE row_id = ?', (agent_id, ))
        if len(data) > 0:
            return f'{data[0][0]} {data[0][1]} {data[0][2]}'
        else:
            return ''

    def get_id_agent_by_fio(self, fio, agent_type):
        # получение id агента по фио
        try:
            data = fio.split(' ')
            data.append(agent_type)
            return self.__db.db_read('SELECT row_id FROM agents WHERE name = ? AND lastname = ? AND patronymic = ? AND type = ?', data)[0][0]
        except:
            pass

    def get_car_by_id(self, car_id):
        # получение машины по id
        data = self.__db.db_read('SELECT brand, model, year, plate_number FROM cars WHERE row_id = ?', (car_id,))
        if len(data) > 0:
            return f'{data[0][0]}, {data[0][1]}, {data[0][2]}, {data[0][3]}'
        else:
            return ''

    def get_car_id_by_vin(self, vin_number):
        # получение машины по vin номеру
        data = self.__db.db_read('SELECT row_id FROM cars WHERE vin_number = ?', (vin_number, ))
        if len(data) > 0:
            return data[0][0]
        else:
            return -1

    def get_car_id_by_plate_number(self, plate_number):
        # получение машины по гос.номеру
        data = self.__db.db_read('SELECT row_id FROM cars WHERE plate_number = ?', (plate_number, ))
        if len(data) > 0:
            return data[0][0]
        else:
            return -1

    def get_restricted_query(self, restrictions):
        # получение данных о осаго
        def add_and():
            if not first:
                return ' AND'
            else:
                return ''
        basic_query = 'SELECT addendum, policy_number, product, car, policyholder, status, date_registration, ' \
                      'date_start, date_end, agent, policy_prize, payment_status FROM osago'
        first = True
        for index, restriction in enumerate(restrictions):
            if restriction:
                if first:
                    basic_query += ' WHERE'
                match index:
                    case 0:
                        basic_query += add_and() + f' policy_number = "{restriction}"'
                    case 1:
                        try:
                            basic_query += add_and() + f' addendum = "{int(restriction)}"'
                        except:
                            pass
                    case 2:
                        basic_query += add_and() + f' agent = "{self.get_id_agent_by_fio(restriction, True)}"'
                    case 3:
                        try:
                            basic_query += add_and() + f' policyholder = "{int(restriction)}"'
                        except:
                            pass
                    case 4:
                        basic_query += add_and() + f' car = "{self.get_car_id_by_vin(restriction)}"'
                    case 5:
                        basic_query += add_and() + f' car = "{self.get_car_id_by_plate_number(restriction)}"'
                    case 6:
                        basic_query += add_and() + f' date_end > "{restriction}"'
                    case 7:
                        basic_query += add_and() + f' status <> "аннулирован"'
                first = False
        return self.__db.db_read(basic_query, ())

    def get_status_by_id(self, addendum_id):
        # получение статуса, статуса оплаты
        return self.__db.db_read('SELECT status, payment_status FROM osago WHERE addendum = ?', (addendum_id, ))[0]

    def cancel_policy(self, policy_id, description):
        # функция для аннулирования полиса
        self.__db.db_write('UPDATE osago SET status = ?, cancellation_desc = ? WHERE addendum = ?', ("аннулирован", description, policy_id))

    def get_policy_numbers(self):
        # получение номера полиса
        while True:
            random_number = self.__utilities.random_police_number()
            if self.__db.db_read('SELECT COUNT(*) FROM osago WHERE policy_number = ?', (random_number, ))[0][0] == 0:
                return random_number

    def get_addendum_last_code(self):
        # получение последнего кода аддендума
        data = self.__db.db_read('SELECT MAX(addendum) FROM osago', ())
        if data[0][0]:
            return int(data[0][0])+1
        else:
            return 1

    def get_agent_info_full(self, row_id):
        # получение информации об агенте
        data = self.__db.db_read('SELECT name, lastname, patronymic, birthdate, phone_number, type FROM agents WHERE row_id = ?', (row_id, ))
        if len(data) > 0:
            return data[0]
        else:
            return [None, None, None, None, None, None]

    def get_car_by_id_full(self, car_id):
        # получение информации о машине
        data = self.__db.db_read('SELECT brand, model, year, plate_number, mileage, vin_number, owner, power, sts, own_conditions, own_purpose FROM cars WHERE row_id = ?', (car_id, ))
        if len(data) > 0:
            return data[0]
        else:
            return [None, None, None, None, None, None, None, None, None, None, None]

    def get_osago_by_addendum(self, addendum_id):
        # получение инфы о осаго по номеру аддендума
        return self.__db.db_read('SELECT policy_number, product, car, policyholder, status, date_registration, date_start, '
                          'date_end, agent, policy_prize, payment_status, worker_id, drivers, cancellation_desc, '
                          'fee_percent, policy_prize_without_fee FROM osago WHERE addendum = ?', (addendum_id, ))[0]

    def get_agents(self, agent_type):
        # получение списка агентов
        return self.__db.db_read('SELECT row_id, name, lastname, patronymic FROM agents WHERE type = ?', (agent_type, ))

    def get_worker_id(self, creds):
        # получение id страхователя
        data = self.__db.db_read('SELECT row_id FROM users WHERE login = ? AND password = ?', creds)
        if len(data) > 0:
            return data[0][0]
        else:
            return None

    def get_driver_by_id_all(self, row_id):
        # полчение данных о водителе
        return self.__db.db_read('SELECT name, lastname, patronymic, sex, license_number, kvs, kbm, passport, birthdate, exp_license_number, first_license_number FROM drivers WHERE row_id = ?', (row_id, ))[0]

    def add_policy(self, data, creds):
        # функция добавления полиса
        car = list()
        policy = list()
        policy_holder = list()
        drivers = list()
        drivers_ids = list()
        car_id = None
        policy_holder_id = None
        keylogg = 0
        for index, element in enumerate(data):
            if index in range(11, 22):
                if element.value is not None:
                    if len(str(element.value)) > 0:
                        car.append(str(element.value))
                    else:
                        car.append('')
                else:
                    car.append('')
            if index in [2, 5, 4, 31, 7, 28, 30, 25, 26]: # индексы полей
                if index == 31:
                    for g in element[0:3]:
                        if g.value is not None:
                            policy.append(g.value)
                        else:
                            policy.append('')
                else:
                    if element.value is not None:
                        try:
                            if len(str(element.value)) > 0:
                                policy.append(str(element.value))
                            else:
                                policy.append('')
                        except TypeError:
                            policy.append(element.value)
                    else:
                        policy.append('')
            if index in [10, 8, 31]:
                if index == 31:
                    if element[3].value is not None:
                        policy_holder.append(element[3].value)
                    else:
                        policy_holder.append('')
                elif index == 8:
                    fio = str(element.value).split(' ')
                    for i in range(3):
                        try:
                            policy_holder.append(fio[i])
                        except:
                            policy_holder.append('')
                else:
                    if element.value is not None:
                        if len(str(element.value)) > 0:
                            policy_holder.append(str(element.value))
                        else:
                            policy_holder.append('')
                    else:
                        policy_holder.append('')
            if index == 32:
                for indexx, driver in enumerate(element):
                    drivers.append([])
                    for gg, field in enumerate(driver[:6]):
                        if gg == 0:
                            fio = str(field.value).split(' ')
                            for i in range(3):
                                try:
                                    drivers[indexx].append(fio[i])
                                except:
                                    drivers[indexx].append('')
                        else:
                            if field.value is not None:
                                try:
                                    if len(str(field.value)) > 0:
                                        drivers[indexx].append(str(field.value))
                                    else:
                                        drivers[indexx].append('')
                                except TypeError:
                                    drivers[indexx].append(field.value)
                            else:
                                drivers[indexx].append('')
                    lr = 4 + indexx*3
                    for date in data[index-1][lr:lr+3]:
                        if date.value is not None:
                            drivers[indexx].append(date.value)
                        else:
                            drivers[indexx].append('')
        if len(set(car)) > 1:
            keylogg += 1
            car_id = self.add_car(car)
        if len(set(policy_holder)) > 1:
            policy_holder.append(False)
            keylogg += 1
            policy_holder_id = self.add_policy_holder(policy_holder)
        for driver in drivers:
            if len(set(driver)) > 1:
                keylogg += 1
                driver_id = self.add_driver(driver)
                drivers_ids.append(driver_id)
        if len(set(policy)) > 5 and keylogg >= 3: # policy обработчик
            worker_id = self.get_worker_id(creds)
            self.add_policy_db(policy + [car_id, policy_holder_id, json.dumps(drivers_ids), worker_id, ''])

    def add_car(self, data):
        # функция добавления машины
        self.__db.db_write('INSERT INTO cars (brand, model, year, mileage, vin_number, plate_number, owner, '
                           'power, sts, own_conditions, own_purpose) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
        return int(self.__db.db_read('SELECT MAX(row_id) FROM cars', ())[0][0])

    def add_policy_holder(self, data):
        # функция добавления держателя полиса
        self.__db.db_write('INSERT INTO agents (name, lastname, patronymic, '
                           'phone_number, birthdate, type) VALUES (?, ?, ?, ?, ?, ?)', data)
        return int(self.__db.db_read('SELECT MAX(row_id) FROM agents', ())[0][0])

    def change_car(self, data, car_id):
        # функция изменения машины
        self.__db.db_write('UPDATE cars SET brand = ?, model = ?, year = ?, plate_number = ?, mileage = ?, vin_number = ?,'
                           f'owner = ?, power = ?, sts = ?, own_conditions = ?, own_purpose = ? WHERE row_id = "{car_id}"', data)

    def change_policy_holder(self, data, policy_holder_id):
        # функция изменения держателя полиса
        self.__db.db_write(f'UPDATE agents SET name = ?, lastname = ?, patronymic = ?, '
                           f'phone_number = ?, birthdate = ?, type = ? WHERE row_id = "{policy_holder_id}"', data)

    def add_driver(self, data):
        # функция добавления водителя
        self.__db.db_write('INSERT INTO drivers (name, lastname, patronymic, sex, license_number, kvs, kbm, passport, '
                           'birthdate, exp_license_number, first_license_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
        return int(self.__db.db_read('SELECT MAX(row_id) FROM drivers', ())[0][0])

    def change_driver(self, data, driver_id):
        # функция изменения водителя
        self.__db.db_write('UPDATE drivers SET name = ?, lastname = ?, patronymic = ?, sex = ?, license_number = ?, '
                           'kvs = ?, kbm = ?, '
                           'passport = ?, birthdate = ?, exp_license_number = ?, first_license_number = ? '
                           f'WHERE row_id = "{driver_id}"', data)

    def add_policy_db(self, data):
        # функция добавления полиса в бд
        self.__db.db_write('INSERT INTO osago (policy_number, status, product, agent, fee_percent, '
                           'policy_prize_without_fee, policy_prize, '
                           'payment_status, date_registration, date_start, date_end, car, policyholder, '
                           'drivers, worker_id, cancellation_desc) VALUES '
                           '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)

    def prolongate_policy_db(self, data):
        # функция добавления полиса в бд
        self.__db.db_write('INSERT INTO osago (policy_number, status, product, agent, fee_percent, '
                           'policy_prize_without_fee, policy_prize, '
                           'payment_status, cancellation_desc, date_registration, date_start, date_end, car, policyholder, '
                           'drivers, worker_id) VALUES '
                           '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)

    def change_policy(self, data, policy_id):
        # функция изменения полиса
        self.__db.db_write('UPDATE osago SET policy_number = ?, status = ?, product = ?, agent = ?, fee_percent = ?,'
                           'policy_prize_without_fee = ?, policy_prize = ?, payment_status = ?, cancellation_desc = ?, date_registration = ?, date_start = ?,'
                           f'date_end = ?, car = ?, policyholder = ?, drivers = ?, worker_id = ? WHERE addendum = "{policy_id}"', data)

    def change_policy_db(self, data, creds, osago_id, source):
        # функция изменения полиса в бд
        car = list()
        policy = list()
        policy_holder = list()
        drivers = list()
        drivers_ids = list()
        datas = self.get_osago_by_addendum(osago_id)
        policy_holder_id = datas[3]
        car_id = datas[2]
        old_drivers = json.loads(datas[12])
        for index, element in enumerate(data):
            if index in range(11, 22):
                if element.value is not None:
                    if len(str(element.value)) > 0:
                        car.append(str(element.value))
                    else:
                        car.append('')
                else:
                    car.append('')
            if index in [2, 5, 4, 31, 7, 28, 30, 25, 26, 32]:  # индексы полей
                if index == 32:
                    for g in element[0:3]:
                        if g.value is not None:
                            policy.append(g.value)
                        else:
                            policy.append('')
                else:
                    if element.value is not None:
                        try:
                            if len(str(element.value)) > 0:
                                policy.append(str(element.value))
                            else:
                                policy.append('')
                        except TypeError:
                            policy.append(element.value)
                    else:
                        policy.append('')
            if index in [10, 8, 32]:
                if index == 32:
                    if element[3].value is not None:
                        policy_holder.append(element[3].value)
                    else:
                        policy_holder.append('')
                elif index == 8:
                    fio = str(element.value).split(' ')
                    for i in range(3):
                        try:
                            policy_holder.append(fio[i])
                        except:
                            policy_holder.append('')
                else:
                    if element.value is not None:
                        if len(str(element.value)) > 0:
                            policy_holder.append(str(element.value))
                        else:
                            policy_holder.append('')
                    else:
                        policy_holder.append('')
            if index == 33:
                for indexx, driver in enumerate(element):
                    drivers.append([])
                    for gg, field in enumerate(driver[:6]):
                        if gg == 0:
                            fio = str(field.value).split(' ')
                            for i in range(3):
                                try:
                                    drivers[indexx].append(fio[i])
                                except:
                                    drivers[indexx].append('')
                        else:
                            if field.value is not None:
                                try:
                                    if len(str(field.value)) > 0:
                                        drivers[indexx].append(str(field.value))
                                    else:
                                        drivers[indexx].append('')
                                except TypeError:
                                    drivers[indexx].append(field.value)
                            else:
                                drivers[indexx].append('')
                    lr = 4 + indexx * 3
                    for date in data[index - 1][lr:lr + 3]:
                        if date.value is not None:
                            drivers[indexx].append(date.value)
                        else:
                            drivers[indexx].append('')
                    drivers[indexx].append(driver[10])
        if len(set(car)) > 1:
            self.change_car(car, car_id)
        if len(set(policy_holder)) > 1:
            policy_holder.append(False)
            self.change_policy_holder(policy_holder, policy_holder_id)
        for index, driver in enumerate(drivers):
            if not driver[11]:
                if index+1 <= len(old_drivers):
                    if len(set(driver)) > 1:
                        self.change_driver(driver[:11], old_drivers[index])
                        drivers_ids.append(old_drivers[index])
                else:
                    if len(set(driver)) > 1:
                        driver_id = self.add_driver(driver[:11])
                        drivers_ids.append(driver_id)
        if len(set(policy)) > 5:  # policy обработчик
            worker_id = self.get_worker_id(creds)
            if not source:
                self.change_policy(policy + [car_id, policy_holder_id, json.dumps(drivers_ids), worker_id], osago_id)
            else:
                self.prolongate_policy_db(policy + [car_id, policy_holder_id, json.dumps(drivers_ids), worker_id])