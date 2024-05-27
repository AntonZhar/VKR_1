# импортируем основную библиотеку и backend

import flet as ft
from flet_navigator import PageData
from modules.CRUD import CRUD


#создаем класс для страницы
class Login:
    def __init__(self, db):
        # подвязываем backend для работоспособности страницы
        super(Login, self).__init__()
        self.__crud = CRUD(db)

    def login(self, pg: PageData):
        def login_btn(e):
            # подкласс для проверки логина и пароля
            if len(user_login.value) > 0 and len(user_password.value) > 0:
                # Проверям наличие логина\пароля в БД
                if self.__crud.check_login(user_login.value, user_password.value):
                    pg.page.session.set('creds', [user_login.value, user_password.value])
                    #если логин и пароль проходит - нас перекидывает на главную страницу
                    pg.navigator.navigate('main', pg.page)
                else:
                    # в ином случае открывается диалоговое окно
                    open_dlg_modal(None)
            else:
                open_dlg_modal(None)

        def close_dlg(e):
            #под класс для кнопки "Ок" в диалоговом окне
            dlg_modal.open = False
            pg.page.update()

        def redirect_on_reg(e):
            # подкласс для кнопки "Регистрация", чтобы перекидывало на страницу
            pg.navigator.navigate('registration', pg.page)

        def open_dlg_modal(e):
            # подкласс для открытия диалогового окна
            pg.page.dialog = dlg_modal
            dlg_modal.open = True
            pg.page.update()

        pg.page.title = "Страница входа" # название страницы

        #указываем как у нас на странице будут распологаться элементы
        pg.vertical_alignment = ft.MainAxisAlignment.CENTER
        pg.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # создаем элементы для страницы
        name_page = ft.Text(value='Вход', text_align=ft.TextAlign.CENTER, size=32) #ft.Text - просто текст на странице
        login_text = ft.Text(value='Логин', text_align=ft.TextAlign.CENTER, size=20)
        user_login = ft.TextField(width=334, height=41) # ft.TextField - текстовое поле куда вводяться данные
        password_text = ft.Text(value='Пароль', text_align=ft.TextAlign.CENTER, size=20)
        user_password = ft.TextField(width=334, height=41, password=True, can_reveal_password=True)
        #кнопки войти и "Зарегестрироваться", on_click - означает, что когда мы нажали на кнопку, будет срабатываение функции login_btn или redirect_on_reg
        login_button = ft.FilledButton(text='Войти', width=334, height=41, on_click=login_btn)
        reg_button = ft.FilledButton(text='Зарегестрироваться', width=334, height=41, on_click=redirect_on_reg)

        #инициализируем диалоговое окно
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Вы ввели неверные данные"), # название окна
            content=ft.Text("Повторите попытку"), # контент который рапологается в окне
            actions=[
                ft.TextButton("Ок", on_click=close_dlg), #кнопка для закрытия окна
            ],
            actions_alignment=ft.MainAxisAlignment.END, # расположение кнопки в диалоговом окне
        )
        pg.page.add( # добавляем элементы на страницу
            ft.Row([
                name_page
            ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Row([
                ft.Column([
                    login_text,
                    user_login,
                    password_text,
                    user_password,
                    login_button,
                    reg_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )