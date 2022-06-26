import asyncio
import time as tm
from hwproj_p2.model import Model, HW, Message
from hwproj_p2.view import View
from hwproj_p2.controller.checker import Checker


class Controller:
    """
    A class that handles all requests from a frontend.
    """

    def __init__(self, model: Model, view: View, checker: Checker):
        self.__model = model
        self.__view = view
        self.__checker = checker

    def __send_message(self, hw_id, title: str, message: str):
        message = Message(tm.localtime(), title, message)
        self.__model.send_message(hw_id, message)
        self.__view.on_message_send(hw_id, message)

    async def send_solution(self, hw_id: int, url: str, text: str):
        """
        Sends a new message with passed parameters.
        :param hw_id: an id of homework which dialog to update
        """
        self.__send_message(hw_id, url, text)
        await self.__checker.call(self.__model.get_hw(hw_id), url, self.set_mark)

    def create_homework(self, *args, **kwargs):
        """
        Creates new homework with passed parameters.
        """

        hw = HW(*args, **kwargs)
        self.__model.add_hw(hw)
        self.__view.on_hw_created(hw)

    async def set_mark(self, hw_id: int, mark: int):
        """
        Sets mark to a homework.
        :param hw_id: an id of a homework
        :param mark: a mark
        :throws KeyError: if a homework with such id does not exist
        """

        hw = self.__model.set_mark(hw_id, mark)
        self.__view.on_mark_updated(hw, tm.localtime())
        self.__send_message(hw_id, '', f'Работа проверена.\nОценка: {mark}')