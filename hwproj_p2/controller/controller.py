import time as tm
from model import Model, HW, Message
from view import View


class Controller:
    '''
    A class that handles all requests from a frontend.
    '''

    def __init__(self, model: Model, view: View):
        self.__model = model
        self.__view  = view

    def send_solution(self, hw_id: int, url: str, text: str):
        '''
        Sends a new message with passed parameters.
        :param hw_id: an id of homework which dialog to update
        '''

        message = Message(tm.localtime(), url, text)
        self.__model.send_message(hw_id, message)
        self.__view.on_message_send(hw_id, message)

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

        self.__model.set_mark(hw_id, mark)
