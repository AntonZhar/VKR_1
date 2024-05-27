 # импортируем основную библиотеку и backend
import flet as ft
import datetime
from flet_navigator import PageData
from modules.CRUD import CRUD


# создаем класс для главной страницы
class MainPage:
    def __init__(self, db):
        super(MainPage, self).__init__()
        self.__table = None
        self.__filter_fields2 = None
        self.__filter_fields = list()
        self.__crud = CRUD(db)

    def main_page(self, pg: PageData):

        def build_agent_names():
            agents = list()
            for agent in self.__crud.get_agents(True):
                agents.append(ft.dropdown.Option(f'{agent[1]} {agent[2]} {agent[3]}'))
            return agents

        # инициализация текстовых полей/кнопок для фильтра
        def build_filter_fields():
            self.__filter_fields = [
                ft.TextField(label="Номер полиса:", on_change=validate_filter),
                ft.TextField(label="Уч. номер аддендума:", on_change=validate_filter),
                ft.Dropdown(
                    label='Агент (ФИО)',
                    options=build_agent_names()
                ),
                ft.TextField(label="Код страхователя:", on_change=validate_filter),
                ft.TextField(label="VIN-номер:", on_change=validate_filter),
                ft.TextField(label="Гос. номер машины:", on_change=validate_filter),
                ft.FilledButton(text='Действует на дату', icon="CALENDAR_MONTH",
                                on_click=lambda _: date_picker.pick_date()),
                ft.Checkbox(label="Не показывать аннулированные", value=False,
                            on_change=validate_filter),
            ]
            return self.__filter_fields

        # инициализация текстового поля для аннулирования
        def build_filter_fields2():
            self.__filter_fields2 = [
                anigilator,
            ]
            return self.__filter_fields2

        # очищаем поля в фильтре, если нажали кнопку "Закрыть"
        def clear_field_filter(e):
            for index, input in enumerate(self.__filter_fields):
                match index:
                    case 6:
                        date_picker.value = None
                    case _:
                        input.value = None
            self.__table.rows.clear()
            load_table_info(False)
            pg.page.update()

        # данные для фильтра, по коду смотрим какие поля введены и меняем таблицу под схожие данные в фильтре
        def validate_filter(e):
            restriction = list()
            for index, input in enumerate(self.__filter_fields):
                if index in [2, 6, 7]:
                    match index:
                        case 2:
                            if input.value is not None:
                                restriction.append(input.value)
                            else:
                                restriction.append(False)
                        case 6:
                            if date_picker.value is not None:
                                restriction.append(date_picker.value)
                            else:
                                restriction.append(False)
                        case 7:
                            restriction.append(input.value)
                else:
                    if len(input.value) > 0:
                        restriction.append(input.value)
                    else:
                        restriction.append(False)
            self.__table.rows.clear()
            load_table_info(True, restriction)
            pg.page.update()

        def create(e):
            # функция чтобы нас перекидывало на страницу создания карточки полиса
            pg.navigator.navigate('policycard', pg.page)

        def change(e):
            # функция чтобы нас перекидывало на страницу изменения карточки полиса
            pg.navigator.navigate('changecard', pg.page)

        def check(e):
            # функция чтобы нас перекидывало на страницу просмотра карточки полиса
            if pg.page.session.get('policy_id'):
                pg.navigator.navigate('checkcard', pg.page)

        def prolongation(e):
            # функция чтобы нас перекидывало на страницу пролонгации карточки полиса
            if pg.page.session.get('policy_id'):
                pg.navigator.navigate('prolongation', pg.page)

        def close_dlg(e):
            # функция для закрытия диалогового окна с сохранением в нем введенных данных
            validate_filter(e)
            dlg_modal.open = False
            pg.page.update()

        def close_dlg_off(e):
            # функция для закрытия диалогового окна
            clear_field_filter(e)
            dlg_modal.open = False
            pg.page.update()

        def open_dlg_modal(e):
            # функция для открытия диалогового окна
            pg.page.dialog = dlg_modal
            dlg_modal.open = True
            pg.page.update()

        # создаем само диалоговое окно - фильтры
        dlg_modal = ft.AlertDialog(
            modal=True,
            content_padding=ft.padding.all(30),
            title=ft.Text("Фильтр", text_align=ft.TextAlign.CENTER),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Column(build_filter_fields()),
            actions=[
                ft.ElevatedButton("Сохранить", on_click=close_dlg),
                ft.ElevatedButton("Закрыть", on_click=close_dlg_off)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def close_dlg2(e):
            # функция закрытия диалогового окна - аннулирования с сохранением причины
            self.__crud.cancel_policy(pg.page.session.get('policy_id'), anigilator.value)
            dlg_modal2.open = False
            self.__table.rows.clear()
            load_table_info(False)
            pg.page.update()

        def close_dlg_off2(e):
            # функция закрытия диалогового окна - аннулирования
            clear_field_filter(e)
            dlg_modal2.open = False
            pg.page.update()

        def open_dlg_modal2(e):
            # функция открытия диалогового окна - аннулирования
            pg.page.dialog = dlg_modal2
            dlg_modal2.open = True
            pg.page.update()

        # создание диалогового окна - аннулирование карточки
        anigilator = ft.TextField(label="Причина аннулирования")
        dlg_modal2 = ft.AlertDialog(
            modal=True,
            content_padding=ft.padding.all(30),
            title=ft.Text("Аннулировать", text_align=ft.TextAlign.CENTER),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Column(build_filter_fields2()),
            actions=[
                ft.ElevatedButton("Сохранить", on_click=close_dlg2),
                ft.ElevatedButton("Закрыть", on_click=close_dlg_off2)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # создание календаря
        date_picker = ft.DatePicker(
            on_change=validate_filter,
            first_date=datetime.datetime(2023, 12, 31),
            last_date=datetime.datetime(2050, 12, 31),
        )

        # подкласс для проверки чекбоксов в таблице - если выбран, разблокируются определенные кнопки
        def set_checkbox(e):
            check_btn.disabled = False
            renew_btn.disabled = False
            for item in self.__table.rows:
                if item.cells[0].content.tooltip != e.control.tooltip and item.cells[0].content.value:
                    item.cells[0].content.value = 'false'
            status = self.__crud.get_status_by_id(e.control.tooltip)
            if status[0] == 'не активен' or status[1] == 'Не оплачен':
                change_btn.disabled = False
            else:
                change_btn.disabled = True
            pg.page.update()
            pg.page.session.set('policy_id', e.control.tooltip)

        # подкласс для подгрузки данных для таблицы из базы данных
        def load_table_info(flag, restrictions=None):
            if not flag:
                # получение данных из backend из функции get.basic_query
                data = self.__crud.get_basic_query()
            else:
                # получение данных из backend из функции get.restricted_query
                data = self.__crud.get_restricted_query(restrictions)
            for row in data:
                #получение определенных данных в переменные
                car_info = self.__crud.get_car_by_id(row[3])
                agent_fio = self.__crud.get_agent_by_id(row[9])
                policy_holder = self.__crud.get_agent_by_id(row[4])
                self.__table.rows.append(ft.DataRow(
                    # загрузка данных из БД
                    cells=[
                        # заполняем данные в таблицу по ключевой строке - row[0], row[1] и так далее, т.е. в нужную строку под определенный заговок в таблице
                        ft.DataCell(ft.Checkbox(value=False, tooltip=row[0], on_change=set_checkbox)),
                        ft.DataCell(ft.Text(row[0])),
                        ft.DataCell(ft.Text(row[1])),
                        ft.DataCell(ft.Text(row[2])),
                        ft.DataCell(ft.Text(car_info)),
                        ft.DataCell(ft.Text(f'{policy_holder} ({row[4]})')),
                        ft.DataCell(ft.Text(row[5])),
                        ft.DataCell(ft.Text(row[6])),
                        ft.DataCell(ft.Text(row[7])),
                        ft.DataCell(ft.Text(row[8])),
                        ft.DataCell(ft.Text(agent_fio)),
                        ft.DataCell(ft.Text(row[10])),
                        ft.DataCell(ft.Text(row[11])),
                    ],
                ),
                )

        pg.page.title = 'Главная страница'  # название для страницы
        pg.page.scroll = 'always'  # добавляем скролл для таблицы

        # создаем кнопки в вверху страницы
        new_btn = ft.FilledButton(text="Новый", icon="ADD",
                                  style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5),
                                                       color=ft.colors.GREEN), on_click=create)
        change_btn = ft.FilledButton(text="Изменить", icon="CREATE_SHARP",
                                     style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5),
                                                          color=ft.colors.ORANGE), disabled=True, on_click=change)
        renew_btn = ft.FilledButton(text="Пролонгировать", icon="AUTORENEW",
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5),
                                                         color=ft.colors.LIGHT_BLUE), on_click=prolongation,
                                    disabled=True)
        cancel_btn = ft.FilledButton(text="Аннулировать", icon="CANCEL",
                                     style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5),
                                                          color=ft.colors.RED), on_click=open_dlg_modal2)
        filter_btn = ft.FilledButton(text="Фильтр", icon="SETTINGS",
                                     style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5),
                                                          color=ft.colors.PURPLE), on_click=open_dlg_modal)
        check_btn = ft.FilledButton(text="Просмотреть", icon="REMOVE_RED_EYE",
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5),
                                                         color=ft.colors.BLACK), on_click=check, disabled=True)

        # создаем таблицу
        self.__table = ft.DataTable(
            border=ft.border.all(2, "white"),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, "black"),
            horizontal_lines=ft.border.BorderSide(1, "black"),
            # создаем поля для таблицы, 1ое поле - для чекбокса
            columns=[
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("Уч. номер аддендума")),
                ft.DataColumn(ft.Text("Номер полиса")),
                ft.DataColumn(ft.Text("Продукт")),
                ft.DataColumn(ft.Text("Объект")),
                ft.DataColumn(ft.Text("Страхователь")),
                ft.DataColumn(ft.Text("Состояние")),
                ft.DataColumn(ft.Text("Дата оформления")),
                ft.DataColumn(ft.Text("Дата начала")),
                ft.DataColumn(ft.Text("Дата окончания")),
                ft.DataColumn(ft.Text("Агент")),
                ft.DataColumn(ft.Text("Размер страховой премии")),
                ft.DataColumn(ft.Text("Статус оплаты"))
            ]
        )
        # добавляем поля на таблицу
        load_table_info(False)

        pg.page.overlay.append(date_picker)  # инициализируем выбор даты в "Фильтре"
        pg.page.add(  # добавляем элементы на страницу
            ft.Row([
                new_btn,
                change_btn,
                check_btn,
                renew_btn,
                cancel_btn,
                filter_btn,
            ]),
            ft.Row([
                # загружаем данные для таблицы
                self.__table
            ],
                scroll="always",  # задаем параметр scroll для того чтобы можно было листать таблицу
                alignment=ft.MainAxisAlignment.CENTER
            )
        )
