# flet - импортируем основную библиотеку, на которой построен проект, flet_navigator - помогает переходить на другие
# страницы, далее файлы импортируем сами страницы для их дальнейшего использования
import flet as ft
from flet_navigator import VirtualFletNavigator
from UI.Pages.main import MainPage
from UI.Pages.login import Login
from UI.Pages.registration import Registration
from UI.Pages.policycard import PolicyCard
from UI.Pages.changecard import ChangeCard
from UI.Pages.checkcard import CheckCard
from UI.Pages.prolongation import Prolongation


#создаем класс UI для инициализации страниц
class UI:
    def __init__(self, config, db):
        # тут происходит инициализация объектов страниц
        super(UI, self).__init__()
        self.__vault_keys = ['current_user']
        self.__config = config
        self.__db = db
        self.__pagemain = MainPage(db)
        self.__login = Login(db)
        self.__reg = Registration(db)
        self.__policycard = PolicyCard(db)
        self.__changecard = ChangeCard(db)
        self.__checkcard = CheckCard(db)
        self.__prolongation = Prolongation(db)

    def main(self, page: ft.Page):
        flet_navigator = VirtualFletNavigator(
            {
                #присваиваем каждой странице свой путь
                '/': self.__login.login,
                'main': self.__pagemain.main_page,
                'registration': self.__reg.registration,
                'policycard': self.__policycard.policy_card,
                'changecard': self.__changecard.change_card,
                'checkcard': self.__checkcard.check_card,
                'prolongation': self.__prolongation.prolongation
            }
        )
        # отрисовываем страницу для показа на экране
        flet_navigator.render(page)
