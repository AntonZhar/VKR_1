# импортируем основную библиотеку и backend
import flet as ft
from flet_navigator import PageData
from modules.CRUD import CRUD


#создаем класс для страницы
class Registration:
    def __init__(self, db):
        # подвязываем backend для работоспособности страницы
        super(Registration, self).__init__()
        self.__dlg_modal = None
        self.__crud = CRUD(db)

    def registration(self, pg: PageData):
        def reg_btn(e):
            # Проверям наличие логина\пароля в БД
            if not self.__crud.check_login(login_field.value, pass_field.value):
                # считываем данные с текстовых полей и добавляем в базу данных через backend функцию add_user
                self.__crud.add_user([name_field.value, sur_name_field.value, patronymic_field.value, email_field.value, login_field.value, pass_field.value])
                pg.page.session.set('creds', [login_field.value, pass_field.value])
                pg.navigator.navigate('main', pg.page)
            else:
                # В случае если логин с паролем уже существуют в БД, будет выскакивать диалоговое окно, о том, что такой пользователь уже существует
                open_dlg_modal(None)

        def close_dlg(e):
            # функция для кнопки, чтобы закрыть диалоговое окно
            dlg_modal.open = False
            pg.page.update()

        def open_dlg_modal(e):
            # инициализация для открытия диалогового окна
            pg.page.dialog = dlg_modal
            dlg_modal.open = True
            pg.page.update()

        def validate(event):
            # проверка на заполненность полей, если не все поля заполнены, то кнопка "Зарегестрироваться будет заблокирована"
            if all([name_field.value, sur_name_field.value, email_field.value, login_field.value, pass_field.value]):
                reg_button.disabled = False
            else:
                # в случае если пароля и логина не существует в бд, то происходит запись, а так же переброс на главную страницу
                reg_button.disabled = True
            pg.page.update()

        pg.page.title = "Страница регистрации" # название страницы

        # создаем элементы для страницы
        name_page = ft.Text(value='Регистрация', text_align=ft.TextAlign.CENTER, size=32)
        name_text = ft.Text(value='Имя', text_align=ft.TextAlign.CENTER, size=20)
        name_field = ft.TextField(width=334, height=41, on_change=validate)
        sur_name_text = ft.Text(value='Фамилия', text_align=ft.TextAlign.CENTER, size=20)
        sur_name_field = ft.TextField(width=334, height=41, on_change=validate)
        patronymic_text = ft.Text(value='Отчество', text_align=ft.TextAlign.CENTER, size=20)
        patronymic_field = ft.TextField(width=334, height=41, on_change=validate)
        email_text = ft.Text(value='Почта', text_align=ft.TextAlign.CENTER, size=20)
        email_field = ft.TextField(width=334, height=41, on_change=validate)
        login_text = ft.Text(value='Логин', text_align=ft.TextAlign.CENTER, size=20)
        login_field = ft.TextField(width=334, height=41, on_change=validate)
        pass_text = ft.Text(value='Пароль', text_align=ft.TextAlign.CENTER, size=20)
        pass_field = ft.TextField(width=334, height=41, password=True, can_reveal_password=True, on_change=validate)
        reg_button = ft.FilledButton(text='Зарегестрироваться', width=334, height=41, disabled=True, on_click=reg_btn)

        # инициализация диалогового окна
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Аккаунт с такими данными уже существует"),
            content=ft.Text("Повторите попытку"),
            actions=[
                ft.TextButton("Ok", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        pg.page.add( # добавляем все элементы на страницу
            ft.Row([ft.Column([name_page], alignment=ft.MainAxisAlignment.CENTER)], ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Column([
                    name_text,
                    name_field,
                    sur_name_text,
                    sur_name_field,
                    email_text,
                    email_field,
                    patronymic_text,
                    patronymic_field,
                    login_text,
                    login_field,
                    pass_text,
                    pass_field,
                    reg_button
                ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )