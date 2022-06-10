import time as tm
from typing import Generator


class HW:
    '''
    A class that contains information about task.
    Properties:
        id: unique id of a homework
        name: name of a homework
        problem: description
        date: publication date
        deadline: deadline date
        script: path to a checker as a bash script
        mark: checker result
    '''

    __n_homeworks = 0

    def __init__(self,
                 name: str,
                 problem: str,
                 date: tm.struct_time,
                 deadline: tm.struct_time,
                 script: str):
        self.__name     = name
        self.__problem  = problem
        self.__date     = date
        self.__deadline = deadline
        self.__script   = script
        self.__mark     = None
        self.__id       = HW.__n_homeworks
        HW.__n_homeworks += 1

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def problem(self):
        return self.__problem

    @property
    def date(self):
        return self.__date

    @property
    def deadline(self):
        return self.__deadline

    @property
    def script(self):
        return self.__script

    @property
    def mark(self):
        return self.__mark

    @mark.setter
    def mark(self, value: int):
        self.__mark = value


class Message:
    '''
    A class that contains information about student's try or checker result.
    Properties:
        time: time when message was sent
        url: url with a link to a student's solution
        text: a commentary
    '''

    def __init__(self, time: tm.struct_time, url: str, text: str):
        self.__time = time
        self.__url  = url
        self.__text = text

    @property
    def time(self):
        return self.__time

    @property
    def url(self):
        return self.__url

    @property
    def text(self):
        return self.__text


class Model:
    '''
    A class that handles all requests to a backend.
    '''

    def __init__(self, checker):
        self.__hws     = {}
        self.__dialogs = {}
        self.__checker = checker

    def send_message(self, hw_id: int, message: 'Message'):
        '''
        Adds message to a homework dialog.
        :param hw_id: an id of a homework
        :param msg: a message
        :throws KeyError: if a homework with such id does not exist
        '''
            
        try:
            self.__dialogs[hw_id].append(message)
        except KeyError:
            raise KeyError(f'a homework with id {hw_id} does not exist') from None

    def set_mark(self, hw_id: int, mark: int):
        '''
        Sets mark to a homework.
        :param hw_id: an id of a homework
        :param mark: a mark
        :throws KeyError: if a homework with such id does not exist
        '''
        
        try:
            self.__hws[hw_id].mark = mark
        except KeyError:
            raise KeyError(f'a homework with id {hw_id} does not exist') from None

    def get_hws(self, date_filter: bool =False) -> Generator['HW', None, None]:
        '''
        :param date_filter: if True then the result will not include future homeworks
        :returns: a generator with a homeworks 
        '''

        if date_filter:
            return (hw for hw in self.__hws if hw.date <= tm.localtime())
        else:
            return (hw for hw in self.__hws)

    def get_hw_dialog(self, hw_id: int) -> Generator['Message', None, None]:
        '''
        :param hw_id: and id of a homework
        :returns: a generator with all messages in a homework dialog
        :throws KeyError: if a homework with such id does not exist
        '''

        try:
            return (m for m in self.dialogs[hw_id])
        except KeyError:
            raise KeyError(f'a homework with id {hw_id} does not exist') from None

    def add_hw(self, hw: 'HW'):
        '''
        Adds a new homework to a course.
        :param hw: a homework to add
        '''

        self.__hws[hw.id] = hw
        self.__dialogs[hw.id] = []
