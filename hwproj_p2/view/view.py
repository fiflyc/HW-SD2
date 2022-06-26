import time as tm
from enum import Enum
from hwproj_p2.view.page import Page
from hwproj_p2.model import HW, Message


class UserType(Enum):
    '''
    A type of a MyHWProj user.
    Values:
        TEACHER
        STUDENT
    '''

    TEACHER = 0
    STUDENT = 1


class View:
    '''
    A class that contains all web pages.
    '''

    def __init__(self):
        self.__hws_teacher_page = (
            Page("http://localhost:8888/teacher")
            .add_heading(1, "Все задания")
            .add_panel([
                ("http://localhost:8888/teacher/add", "Новое задание"),
                ("http://localhost:8888/teacher/results", "Успеваемость")])
            .add_line()
            .add_hws_list()
        )
        self.__hws_student_page = (
            Page("http://localhost:8888/student")
            .add_heading(1, "Все задания")
            .add_panel([("http://localhost:8888/student/results", "Успеваемость")])
            .add_line()
            .add_hws_list()
        )
        self.__hw_creation_date = {}
        self.__hw_student_pages = {}
        self.__hw_teacher_pages = {}
        self.__res_student_page = (
            Page("http://localhost:8888/student/results")
            .add_heading(1, "Успеваемость")
            .add_panel([("http://localhost:8888/student", "Задания")])
            .add_line()
            .add_results(reverse=True)
        )
        self.__res_teacher_page = (
            Page("http://localhost:8888/teacher/results")
            .add_heading(1, "Успеваемость")
            .add_panel([
                ("http://localhost:8888/teacher/add", "Новое задание"),
                ("http://localhost:8888/teacher", "Все задания")])
            .add_line()
            .add_results(reverse=True)
        )
        self.__new_hw_page = (
            Page("http://localhost:8888/teacher/add")
            .add_heading(1, "Новое задание")
            .add_panel([
                ("http://localhost:8888/teacher", "Все задания"),
                ("http://localhost:8888/teacher/results", "Успеваемость")])
            .add_line()
            .add_text_input("hw_name", "Название работы", rows=1)
            .add_text_input("hw_problem", "Условие", rows=24)
            .add_date_time_input("hw_start", "Начало", min_date=tm.localtime())
            .add_date_time_input("hw_end", "Дедлайн", min_date=tm.localtime())
            .add_file_input("hw_script", "Bash скрипт проверки", ["sh"])
            .add_button_post("Создать", "http://localhost:8888/teacher", ["hw_name", "hw_problem", "hw_start", "hw_end"], ["hw_script"])
        )
        self.__invalid_hw_teacher_page = (
            Page("http://localhost:8888/teacher/homework/err")
            .add_heading(1, "Нет такого задания")
            .add_panel([("http://localhost:8888/teacher", "Все задания")])
        )
        self.__invalid_hw_student_page = (
            Page("http://localhost:8888/student/homework/err")
            .add_heading(1, "Нет такого задания")
            .add_panel([("http://localhost:8888/student", "Все задания")])
        )

    def get_homeworks_page(self, user: UserType) -> str:
        '''
        Returns a web page with a list of homeworks.
        :param user: a type of an user who looks the page
        :returns: HTML code of the web page
        '''

        if user == UserType.STUDENT:
            self.__hws_student_page.filter_container(0, 'date', tm.localtime())
            return repr(self.__hws_student_page)
        elif user == UserType.TEACHER:
            return repr(self.__hws_teacher_page)

    def get_task_page(self, hw_id: int, user: UserType) -> str:
        '''
        Returns a web page with a homework description.
        :param hw_id: an id of a homework
        :param user: a type of an user who looks the page
        :returns: HTML code of the web page
        '''

        try:
            if user == UserType.STUDENT:
                if self.__hw_creation_date[hw_id] > tm.localtime():
                    return repr(self.__invalid_hw_student_page)
                else:
                    return repr(self.__hw_student_pages[hw_id])
            elif user == UserType.TEACHER:
                return repr(self.__hw_teacher_pages[hw_id])
        except KeyError:
            if user == UserType.STUDENT:
                return repr(self.__invalid_hw_student_page)
            elif user == UserType.TEACHER:
                return repr(self.__invalid_hw_teacher_page)

    def get_results_page(self, user: UserType) -> str:
        '''
        Returns a web page with a student progress.
        :param user: a type of an user who looks the page
        :returns: HTML code of the web page
        '''

        if user == UserType.STUDENT:
            return repr(self.__res_student_page)
        elif user == UserType.TEACHER:
            return repr(self.__res_teacher_page)

    def get_hw_creation_page(self) -> str:
        '''
        Returns a web page with a form creating a new homework.
        :returns: HTML code of the web page
        '''

        return repr(self.__new_hw_page)

    def on_hw_created(self, hw: HW):
        '''
        Updates web pages that contain info about homeworks.
        :param hw: a created homework
        '''

        url_student = f"http://localhost:8888/student/homework/{hw.id}"
        url_teacher = f"http://localhost:8888/teacher/homework/{hw.id}"

        self.__hw_creation_date[hw.id] = hw.date
        self.__hws_student_page.insert_to(0, hw.deadline, hw, url_student)
        self.__hws_teacher_page.insert_to(0, hw.deadline, hw, url_teacher)
        self.__hw_student_pages[hw.id] = (
            Page(url_student)
            .add_heading(1, "Сдать решение")
            .add_panel([
                ("http://localhost:8888/student", "Все задания"),
                ("http://localhost:8888/student/results", "Успеваемость")])
            .add_line()
            .add_hw_long(hw)
            .add_line()
            .add_break()
            .add_dialog()
            .add_break()
            .add_line()
            .add_text_input("m_url", "Ссылка на решение", rows=1)
            .add_text_input("m_text", "Комментарий", rows=12)
            .add_button_post("Отправить", url_student, ["m_url", "m_text"])
        )
        self.__hw_teacher_pages[hw.id] = (
            Page(url_teacher)
            .add_heading(1, "Просмотр посылок")
            .add_panel([
                ("http://localhost:8888/teacher/add", "Новое задание"),
                ("http://localhost:8888/teacher", "Все задания"),
                ("http://localhost:8888/teacher/results", "Успеваемость")])
            .add_line()
            .add_hw_long(hw)
            .add_line()
            .add_break()
            .add_dialog()
            .add_break()
        )

    def __on_hw_updated(self, hw: HW):
        self.__hws_student_page.update(hw)
        self.__hws_teacher_page.update(hw)
        self.__res_student_page.update(hw)
        self.__res_teacher_page.update(hw)
        self.__hw_student_pages[hw.id].update(hw)
        self.__hw_teacher_pages[hw.id].update(hw)

    def on_mark_updated(self, hw: HW, time: tm.struct_time):
        '''
        Updates web pages that contain info about student marks.
        :param hw: a homework with a mark updated
        :param time: time when the mark was set
        '''

        url_student = f"http://localhost:8888/student/homework/{hw.id}"
        url_teacher = f"http://localhost:8888/teacher/homework/{hw.id}"

        self.__res_student_page.insert_to(0, time, hw, url_student, time)
        self.__res_teacher_page.insert_to(0, time, hw, url_teacher, time)
        self.__on_hw_updated(hw)

    def on_message_send(self, hw_id: int, message: Message):
        '''
        Updates homework web page that contains attempts messages.
        :param hw_id: an id of a homework with updated progress
        :param message: a new attempt message
        :throws KeyError: if a homework with such id does not exist
        '''

        try:
            self.__hw_student_pages[hw_id].insert_to(0, message.time, message)
            self.__hw_teacher_pages[hw_id].insert_to(0, message.time, message)
        except KeyError:
            raise KeyError(f'a homework with id {hw_id} does not exist') from None
