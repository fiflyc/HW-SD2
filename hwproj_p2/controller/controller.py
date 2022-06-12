import time as tm
from model import Model, HW, Message
from view import View
from controller.Checker import Checker


class Controller:
    '''
    A class that handles all requests from a frontend.
    '''

    def __init__(self, model: Model, view: View):
        self.__model   = model
        self.__view    = view
        self.__checker = Checker()

    def send_solution(self, hw_id: int, url: str, text: str):
        '''
        Sends a new message with passed parameters.
        :param hw_id: an id of homework which dialog to update
        '''

        message = Message(tm.localtime(), url, text)
        self.__model.send_message(hw_id, message)
        self.__view.on_message_send(hw_id, message)
        self.__checker.call(self.__model.get_hw(hw_id), url, self.set_mark)

    def create_homework(self, *args, **kwargs):
        '''
        Creates new homework with passed parameters.
        '''

        hw = HW(*args, **kwargs)
        self.__model.add_hw(hw)
        self.__view.on_hw_created(hw)

    def set_mark(self, hw_id: int, mark: int):
        '''
        Sets mark to a homework.
        :param hw_id: an id of a homework
        :param mark: a mark
        :throws KeyError: if a homework with such id does not exist
        '''

        hw = self.__model.set_mark(hw_id, mark)
        self.__view.on_mark_updated(hw, tm.localtime())
        self.send_solution(hw_id, '', f'Работа проверена.\nОценка: {mark}')
