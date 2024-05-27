# импортируем основную библиотеку, дополнительные библиотеки для работы кода и backend
import copy
import datetime
import random
import flet as ft
from flet_navigator import PageData
from modules.CRUD import CRUD


class PolicyCard:
    def __init__(self, db):
        # инициализируем backend, нужные данные для отображения на странице элементов, работы кода
        super(PolicyCard, self).__init__()
        self.__crud = CRUD(db)
        self.__fields = None
        self.__drivers = list()
        self.__drivers_cards = list()
        self.__date_picker = list()

    def policy_card(self, pg: PageData):
        def back(e):
            # функция для возврата на главную страницу
            self.__drivers = list()
            self.__drivers_cards = list()
            self.__date_picker = list()
            pg.navigator.navigate('main', pg.page)

        def build_agents(agent_type):
            # заполинть выпадающий список агентами
            agents = list()
            for agent in self.__crud.get_agents(agent_type):
                agents.append(ft.dropdown.Option(text=f'{agent[1]} {agent[2]} {agent[3]}', key=agent[0]))
            return agents

        def set_policy_holder(e):
            # подставить ID агента на страницу
            for i in range(2):
                if i == 0:
                    self.__fields[7].value = self.__fields[6].value
                else:
                    self.__fields[9].value = self.__crud.get_id_agent_by_fio(self.__fields[8].value, False)
            pg.page.update()


        def close_dlg_off(e):
            # закрыть диалоговое окно
            dlg_modal.open = False
            pg.page.update()

        # инициализация диалогового окна
        dlg_modal = ft.AlertDialog(
            modal=True,
            content_padding=ft.padding.all(30),
            title=ft.Text('Оповещение', text_align=ft.TextAlign.CENTER),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Text('Полис успешно сохранен'),
            actions=[
                ft.ElevatedButton('Закрыть', on_click=close_dlg_off)
            ],
            actions_alignment=ft.MainAxisAlignment.END
            )

        def add_date_picker(quanity):
            # инициализация календаря
            for i in range(quanity):
                self.__date_picker.append(ft.DatePicker(
                    first_date=datetime.datetime(1970, 12, 31),
                    last_date=datetime.datetime(2100, 12, 31),
                )
                )
                pg.page.overlay.append(self.__date_picker[-1])

        def add_policy(e):
            # добавление значений о водителях, статусе оплаты и др.
            full_data = list()
            if self.__fields[30].value == 'Оплачен':
                self.__fields[4].value = 'активен'
            full_data.extend(self.__fields)
            full_data.append(self.__date_picker)
            full_data.append(self.__drivers)
            self.__crud.add_policy(full_data, pg.page.session.get('creds'))
            pg.page.dialog = dlg_modal
            dlg_modal.open = True
            pg.page.update()

        def calculator(e):
            # калькулятор для кнопки - рассчитать
            output = list()
            ko = {True: 2.32, False: 1}
            # матрица для работы функции
            matrix = [[2.27, 1.92, 1.84, 1.65, 1.62, 0, 0, 0],
                      [1.88, 1.72, 1.71, 1.13, 1.1, 1.19, 0, 0],
                      [1.72, 1.6, 1.54, 1.09, 1.08, 1.07, 1.02, 0],
                      [1.56, 1.5, 1.48, 1.05, 1.04, 1.01, 0.97, 0.95],
                      [1.54, 1.47, 1.46, 1.00, 0.97, 0.95, 0.94, 0.93],
                      [1.5, 1.44, 1.43, 0.96, 0.95, 0.94, 0.93, 0.91],
                      [1.46, 1.4, 1.39, 0.93, 0.92, 0.91, 0.90, 0.86],
                      [1.43, 1, 36, 1.35, 0.91, 0.9, 0.89, 0.88, 0.83]]

            def calculate_hp(hp):
                # лощадиные силы авто
                km = 0
                if 1 <= hp <= 50:
                    km = 0.6
                elif 51 <= hp <= 70:
                    km = 1
                elif 71 <= hp <= 100:
                    km = 1.1
                elif 101 <= hp <= 120:
                    km = 1.2
                elif 121 <= hp <= 150:
                    km = 1.4
                elif hp >= 151:
                    km = 1.6
                return km

            def calculate_ks():
                # вычислить кс
                ratio = 0
                ks = int((self.__date_picker[2].value - self.__date_picker[0].value).days / 30)
                if 1 <= ks <= 3:
                    ratio = 0.5
                elif ks == 4:
                    ratio = 0.6
                elif ks == 5:
                    ratio = 0.65
                elif ks == 6:
                    ratio = 0.7
                elif ks == 7:
                    ratio = 0.8
                elif ks == 8:
                    ratio = 0.9
                elif ks == 9:
                    ratio = 0.95
                elif ks >= 10:
                    ratio = 1
                return ratio

            def get_index_by_year():
                # вычислить сколько лет водителю и взять нужные данные из матрицы выше
                matrix_row_index = 0
                driver_old = datetime.datetime.now() - self.__date_picker[4 + index * 3].value
                if 16 <= int(driver_old.days / 365) <= 21:
                    matrix_row_index = 0
                elif 22 <= int(driver_old.days / 365) <= 24:
                    matrix_row_index = 1
                elif 25 <= int(driver_old.days / 365) <= 29:
                    matrix_row_index = 2
                elif 30 <= int(driver_old.days / 365) <= 34:
                    matrix_row_index = 3
                elif 35 <= int(driver_old.days / 365) <= 39:
                    matrix_row_index = 4
                elif 40 <= int(driver_old.days / 365) <= 49:
                    matrix_row_index = 5
                elif 50 <= int(driver_old.days / 365) <= 59:
                    matrix_row_index = 6
                elif int(driver_old.days / 365) >= 60:
                    matrix_row_index = 7
                return matrix_row_index

            def get_index_by_experience():
                # вычислить стаж вождения и взять нужные данные
                matrix_column_index = 0
                driving_experience = datetime.datetime.now() - self.__date_picker[3 + (index + 1) * 3].value
                if int(driving_experience.days / 365) == 0:
                    matrix_column_index = 0
                elif int(driving_experience.days / 365) == 1:
                    matrix_column_index = 1
                elif int(driving_experience.days / 365) == 2:
                    matrix_column_index = 2
                elif int(driving_experience.days / 365) in [3, 4]:
                    matrix_column_index = 3
                elif int(driving_experience.days / 365) in [5, 6]:
                    matrix_column_index = 4
                elif int(driving_experience.days / 365) in [5, 6, 7, 8, 9]:
                    matrix_column_index = 5
                elif int(driving_experience.days / 365) in [10, 11, 12, 13, 14]:
                    matrix_column_index = 6
                elif int(driving_experience.days / 365) > 14:
                    matrix_column_index = 7
                return matrix_column_index

            def bonus_malus():
                # вычисление КБМ
                kbm_index = random.randint(0, 14)
                if self.__date_picker[0].value < datetime.datetime(2022, 4, 1):
                    ratio = [2.45, 2.3, 1.55, 1.4, 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5]
                    selected_kbm = ratio[kbm_index]
                else:
                    ratio = [3.92, 2.94, 2.25, 1.76, 1.17, 1, 0.91, 0.83, 0.78, 0.74, 0.68, 0.63, 0.57, 0.52, 0.46]
                    selected_kbm = ratio[kbm_index]
                return selected_kbm
            try:
                for index, driver in enumerate(self.__drivers):
                    if not self.__fields[23].value:
                        bonus_malus_ok = bonus_malus()
                        output.append([matrix[get_index_by_year()][get_index_by_experience()], bonus_malus_ok])
                        driver[3].value = matrix[get_index_by_year()][get_index_by_experience()]
                        driver[4].value = bonus_malus_ok
                    else:
                        driver[3].value = 1
                        driver[4].value = 1.17

                if not self.__fields[23].value:
                    data = list()
                    data1 = list()
                    for i in output:
                        data.append(i[0])
                        data1.append(i[1])
                    kvs = max(data)
                    ok_bonus_malus = max(data1)
                else:
                    kvs = 1
                    ok_bonus_malus = 1.17
                # сам калькулятор - подсчет нужных значений из функций выше
                self.__fields[26].value = round((4590.5 * 1.8 * calculate_hp(float(self.__fields[18].value)) * kvs * ko[self.__fields[23].value] * calculate_ks() * ok_bonus_malus), 2)
                self.__fields[27].value = round((float(self.__fields[26].value) / 100) * float(self.__fields[25].value), 2)
                self.__fields[28].value = round(float(self.__fields[26].value) + float(self.__fields[27].value), 2)
                print('-' * 30)
                print('Базовый тариф = 4590.5\nКТ = 1.8\nКМ = ', calculate_hp(float(self.__fields[18].value)))
                print('КВС = ', kvs)
                print('КО = ', ko[self.__fields[23].value])
                print('КС = ', calculate_ks())
                print('КБМ = ', ok_bonus_malus)
                print('-' * 30)
                pg.page.update() # обновляем страницу с показом нужных значений на странице
            except Exception as e:
                pass

        def add_driver(e):
            # добавление водителя
            add_date_picker(3)
            full_name1 = ft.TextField(label='ФИО')
            gender1 = ft.Dropdown(
                    label='Пол',
                    options=[
                        ft.dropdown.Option('М'),
                        ft.dropdown.Option('Ж')
                    ]
                )
            date1 = 4 + copy.deepcopy(len(self.__drivers))*3
            date2 = 5 + copy.deepcopy(len(self.__drivers)) * 3
            date3 = 6 + copy.deepcopy(len(self.__drivers)) * 3

            # создание элементов для водителя
            date_of_birth1 = ft.ElevatedButton(text='Дата рождения', icon='CALENDAR_MONTH',
                                               on_click=lambda _: self.__date_picker[date1].pick_date(), width=300,
                                               height=60)
            valid_number_VU1 = ft.TextField(label='Номер действ. ВУ:')
            graduation_date1 = ft.ElevatedButton(text='Дата окончания ВУ', icon='CALENDAR_MONTH',
                                                 on_click=lambda _: self.__date_picker[date2].pick_date(), width=300,
                                                 height=60)
            date_receipt_first1 = ft.ElevatedButton(text='Дата получения первого ВУ', icon='CALENDAR_MONTH',
                                                    on_click=lambda _: self.__date_picker[date3].pick_date(), width=300,
                                                    height=60)
            KVS1 = ft.TextField(label='КВС', disabled=True)
            KBM1 = ft.TextField(label='КБМ', disabled=True)
            passport_data1 = ft.TextField(label='Серия и номер паспорта')
            self.__drivers.append(
                [full_name1, gender1, valid_number_VU1, KVS1, KBM1, passport_data1, date_of_birth1, graduation_date1,
                 date_receipt_first1])
            try:
                self.__drivers_cards[-1].pop(-1)
            except:
                pass

            # заполнение элементов на страницу
            self.__drivers_cards.append(
                ft.Column([
                    ft.Row([
                        self.__drivers[-1][0],
                        self.__drivers[-1][1],
                        self.__drivers[-1][6],
                        self.__drivers[-1][2]
                    ]),
                    ft.Row([
                        self.__drivers[-1][7],
                        self.__drivers[-1][8],
                        self.__drivers[-1][3],
                        self.__drivers[-1][4]
                    ]),
                    ft.Row([
                        self.__drivers[-1][5]
                    ]),
                    ft.Divider(thickness=1, color="white"),
                ]
                )
            )
            pg.page.update() # обновляем страницу для отображения на ней всех элементов, добавленных ранее

        def block_fields(e):
            # функция для блокировки элементов (при нажатии на кнопку удалить водителя)
            if e.data == 'true':
                for i in self.__drivers:
                    for index, j in enumerate(i):
                        if index in [0, 1, 2, 5]:
                            j.value = None
                            j.disabled = True
            else:
                for i in self.__drivers:
                    for index, j in enumerate(i):
                        if index in [0, 1, 2, 5]:
                            j.disabled = False
            pg.page.update()

        def build_fields():
            # функция для создания и заполнения на страницу основных элементов

            # создаем кнопки/поля
            self.__fields = [
                ft.FilledButton(text='Назад', icon='ARROW_BACK',
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5),
                                                     color=ft.colors.GREEN), on_click=back),
                ft.FilledButton(text='Сохранить', icon='SAVE',
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5),
                                                     color=ft.colors.PURPLE), on_click=add_policy),
                ft.TextField(label='Номер полиса', disabled=True,
                             value=str(self.__crud.get_policy_numbers())),
                ft.TextField(label='Уч. номер аддендума', disabled=True,
                             value=str(self.__crud.get_addendum_last_code())),
                ft.TextField(label='Состояние', disabled=True, value='не активен'),
                ft.Dropdown(
                    label='Продукт',
                    options=[
                        ft.dropdown.Option(text='ОСАГО')
                    ]
                ),
                ft.Dropdown(
                    label='Агент (ФИО)',
                    options=build_agents(True),
                    on_change=set_policy_holder
                ),
                ft.TextField(label='Код агента', disabled=True),
                ft.TextField(label='Страхователь (ФИО)', on_change=set_policy_holder),
                ft.TextField(label='Код страхователя', disabled=True),
                ft.TextField(label='Номер телефона страхователя'),
                ft.TextField(label='Марка'),
                ft.TextField(label='Модель'),
                ft.TextField(label='Год выпуска'),
                ft.TextField(label='Пробег, км'),
                ft.TextField(label='VIN-номер'),
                ft.TextField(label='Гос. номер'),
                ft.TextField(label='Собственник'),
                ft.TextField(label='Мощность л/с'),
                ft.TextField(label='СТС'),
                ft.Dropdown(label='Условие владение', options=[ft.dropdown.Option('Собственность')]),
                ft.Dropdown(label='Цель использования', options=[ft.dropdown.Option('Личное')]),
                ft.FilledButton(text='Добавить водителя', on_click=add_driver),
                ft.Checkbox(label='Неограниченная страховка', on_change=block_fields),
                ft.FilledButton(text='Рассчитать', on_click=calculator),
                ft.TextField(label='Комиссия агента, %', value='10'),
                ft.TextField(label='Стоимость полиса, руб', disabled=True),
                ft.TextField(label='Комиссия агента, руб', disabled=True),
                ft.TextField(label='Страховая премия', disabled=True),
                ft.TextField(label='Шаг полиса', value='В бухгалтерии', disabled=True),
                ft.Dropdown(
                    label='Статус платежа',
                    value='Не оплачен',
                    options=[
                        ft.dropdown.Option(text='Оплачен'),
                        ft.dropdown.Option(text='Не оплачен')
                    ]
                ),
            ]

        pg.page.title = 'Добавить карточку полиса' # название страницы
        pg.page.scroll = 'always' # добавляем скролл на страницу

        # добавляем нужные элементы
        data = ft.Text(value='Данные', size=25)
        datsisis = ft.ElevatedButton(text='Дата оформления', icon='CALENDAR_MONTH',
                                     on_click=lambda _: self.__date_picker[0].pick_date(), width=300,
                                     height=60)
        start_date = ft.ElevatedButton(text='Дата начала', icon='CALENDAR_MONTH',
                                       on_click=lambda _: self.__date_picker[1].pick_date(), width=300, height=60)
        expiration_date = ft.ElevatedButton(text='Дата окончания', icon='CALENDAR_MONTH',
                                            on_click=lambda _: self.__date_picker[2].pick_date(), width=300, height=60)
        date_of_birth_strahov = ft.ElevatedButton(text='Дата рождения', icon='CALENDAR_MONTH',
                                                  on_click=lambda _: self.__date_picker[3].pick_date(), width=300,
                                                  height=60)
        car_text = ft.Text(value='Транпортное средство', size=25)
        driver_text = ft.Text(value='Данные о водителе', size=25)
        policy_text = ft.Text(value='Полис', size=25)
        build_fields()
        add_date_picker(4)
        add_driver(None)

        # добавляем все элементы на страницу
        pg.page.add(
            ft.Column(
                [
                    ft.Row([
                        self.__fields[0],
                        self.__fields[1],
                    ]),
                    ft.Divider(thickness=3, color="white"),
                    ft.Row([
                        data,
                    ]),
                    ft.Column([
                        ft.Row([
                            self.__fields[2],
                            self.__fields[3],
                            self.__fields[4],
                            self.__fields[5],
                        ]),
                        ft.Row([
                            datsisis,
                            self.__fields[6],
                            self.__fields[7],
                            start_date,
                        ]),
                        ft.Row([
                            expiration_date,
                            self.__fields[8],
                            self.__fields[9],
                        ]),
                        ft.Row([
                            date_of_birth_strahov,
                            self.__fields[10]
                        ]),
                        ft.Divider(thickness=3, color="white"),
                    ]),
                    ft.Row([
                        car_text,
                    ]),
                    ft.Column([
                        ft.Row([
                            self.__fields[11],
                            self.__fields[12],
                            self.__fields[13],
                            self.__fields[14],
                        ]),
                        ft.Row([
                            self.__fields[15],
                            self.__fields[16],
                            self.__fields[17],
                            self.__fields[18],
                        ]),
                        ft.Row([
                            self.__fields[19],
                            self.__fields[20],
                            self.__fields[21],
                        ]),
                        ft.Divider(thickness=3, color="white"),
                    ]),
                    ft.Row([
                        driver_text,
                        self.__fields[22],
                        self.__fields[23]
                    ]),
                    ft.Column(self.__drivers_cards),
                    ft.Divider(thickness=3, color="white"),
                    ft.Row([
                        policy_text,
                        self.__fields[24],
                        self.__fields[25],
                    ]),
                    ft.Column([
                        ft.Row([
                            self.__fields[26],
                            self.__fields[27],
                            self.__fields[28],
                            self.__fields[29],
                            self.__fields[30],
                        ])
                    ])
                ],
                scroll="always", # инициализируем scroll, чтобы можно было листать страницу
                on_scroll_interval=0,
            )

        )
