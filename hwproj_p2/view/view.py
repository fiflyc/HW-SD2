import time as tm
from enum import Enum
from model import HW, Message
from typing import List, Tuple, Optional


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
        )
        self.__hws_student_page = (
            Page("http://localhost:8888/student")
            .add_heading(1, "Все задания")
            .add_panel([("http://localhost:8888/student/results", "Успеваемость")])
            .add_line()
        )
        self.__hw_student_pages = {}
        self.__hw_teacher_pages = {}
        self.__res_student_page = (
            Page("http://localhost:8888/student/results")
            .add_heading(1, "Успеваемость")
            .add_panel([("http://localhost:8888/student", "Задания")])
            .add_line()
        )
        self.__res_teacher_page = (
            Page("http://localhost:8888/teacher/results")
            .add_heading(1, "Успеваемость")
            .add_panel([
                ("http://localhost:8888/teacher/add", "Новое задание"),
                ("http://localhost:8888/teacher", "Все задания")])
            .add_line()
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
            .add_button_post("Создать", "http://localhost:8888/teacher", ["hw_name", "hw_problem", "hw_start", "hw_end"])
        )

    def get_homeworks_page(self, user: UserType) -> str:
        '''
        Returns a web page with a list of homeworks.
        :param user: a type of an user who looks the page
        :returns: HTML code of the web page
        '''

        if user == UserType.STUDENT:
            return repr(self.__hws_student_page)
        elif user == UserType.TEACHER:
            return repr(self.__hws_teacher_page
    )

    def get_task_page(self, hw_id: int, user: UserType) -> str:
        '''
        Returns a web page with a homework description.
        :param hw_id: an id of a homework
        :param user: a type of an user who looks the page
        :returns: HTML code of the web page
        :throws KeyError: if a web page of a homework with such id does not exist
        '''

        try:
            if user == UserType.STUDENT:
                return repr(self.__hw_student_pages[hw_id])
            elif user == UserType.TEACHER:
                return repr(self.__hw_teacher_pages[hw_id])
        except KeyError:
            raise KeyError(f'a web page of a homework with id {hw_id} does not exist') from None

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

        self.__hws_student_page.add_hw_short(hw, url_student)
        self.__hws_teacher_page.add_hw_short(hw, url_teacher)
        self.__hw_student_pages[hw.id] = (
            Page(url_student, sections=2)
            .add_heading(1, "Сдать решение")
            .add_panel([
                ("http://localhost:8888/student", "Все задания"),
                ("http://localhost:8888/student/results", "Успеваемость")])
            .add_line()
            .add_hw_long(hw)
            .add_line()
            .add_break()
            .select(1)
            .add_line()
            .add_text_input("m_url", "Ссылка на решение", rows=1)
            .add_text_input("m_text", "Комментарий", rows=12)
            .add_button_post("Отправить", url_student, ["m_url", "m_text"])
            .select(0)
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
        )

    def on_hw_updated(self, hw: HW):
        '''
        Updates web pages that contain info about updated homework.
        :param hw: an updated homework
        '''

        self.__hws_student_page.update(hw)
        self.__hws_teacher_page.update(hw)
        self.__res_student_page.update(hw)
        self.__res_teacher_page.update(hw)
        self.__hw_student_pages[hw.id].update(hw)
        self.__hw_teacher_pages[hw.id].update(hw)

    def on_message_send(self, hw_id: int, message: Message):
        '''
        Updates homework web page that contains attempts messages.
        :param hw_id: an id of a homework with updated progress
        :param message: a new attempt message
        :throws KeyError: if a homework with such id does not exist
        '''

        try:
            self.__hw_student_pages[hw_id].add_message(message)
            self.__hw_teacher_pages[hw_id].add_message(message)
        except KeyError:
            raise KeyError(f'a homework with id {hw_id} does not exist') from None


class Page:
    '''
    A smart constructor of web pages.
    All such pages contain list of sections, each of the second ones can be updated by adding blocks at the end.
    You can only add blocks without removing, also you may update blocks with an info about homework.
    Supported blocks:
        heading:     HTML tag <h*> where * in [1, 6]
        panel:       HTML borderless table with one row that contains links to some pages
        line:        HTML tag <hr />
        break:       HTML tag <br>
        hw_short:    HTML code of a short homework description (name, deadline, mark)
        hw_long:     HTML code of a long homework description (name, problem, date, deadline, mark)
        message:     HTML code of a message (a student's try or a checker output)
        text_input:  HTML tag <textarea>
        button_post: HTML tag <button> with a script that sends selected input
    To get HTML code of the page use repr function.
    '''

    def __init__(self, url: str, sections: int =1):
        '''
        :param url: an URL of the page
        :param sections: a number of sections 
        '''

        self.__url = url
        self.__hws_blocks = {}
        self.__body = [[] for _ in range(sections)]
        self.__selected = 0
        self.__cache = None

    def __repr__(self):
        if self.__cache is None:
            self.__cache = '\n'.join(map(lambda s: '\n'.join(map(lambda b: repr(b), s)), self.__body))
        return self.__cache

    def update(self, hw: HW):
        '''
        Updates view of all homeworks representations in the page.
        :param hw: an updating homework
        '''

        self.__cache = None
        if hw.id in self.__hws_blocks:
            for b in self.__hws_blocks[hw.id]:
                b.update_view(hw)

    def select(self, section: int) -> 'Page':
        '''
        Selects section for adding blocks at the end of it.
        :param section: an index of the section
        :raises IndexError: if an index of the section is out of range
        '''

        if -len(self.__body) > section or len(self.__body) <= section:
            raise IndexError('section index out of range')
        self.__selected = section
        return self

    def add_heading(self, lvl: int, text: str) -> 'Page':
        '''
        Adds a new heading block to the selected section.
        :param lvl: a number * in the <h*> tag
        :param text: a text of the heading
        :returns: self
        '''

        self.__cache = None
        self.__body[self.__selected].append(self.__Heading(lvl, text))
        return self

    def add_panel(self, elems: List[Tuple[str, str]]) -> 'Page':
        '''
        Adds a new panel block to the selected section.
        :param elems: a list of tuples (URL, text)
        :returns: self
        '''

        self.__cache = None
        self.__body[self.__selected].append(self.__Panel(elems))
        return self

    def add_line(self) -> 'Page':
        '''
        Adds a new line block to the selected section.
        :returns: self
        '''

        self.__cache = None
        self.__body[self.__selected].append(self.__Line())
        return self

    def add_break(self) -> 'Page':
        '''
        Adds a new break block to the selected section.
        :returns: self
        '''

        self.__cache = None
        self.__body[self.__selected].append(self.__Break())
        return self

    def add_hw_short(self, hw: HW, url: str) -> 'Page':
        '''
        Adds a new hw_short block to the selected section.
        :param hw: a homework description to add
        :param url: a link to a task page
        :returns: self
        '''

        self.__cache = None

        block = self.__HWShort(hw, url)
        self.__body[self.__selected].append(block)
        if hw.id not in self.__hws_blocks:
            self.__hws_blocks[hw.id] = [block]
        else:
            self.__hws_blocks[hw.id].append(block)

        return self

    def add_hw_long(self, hw: HW) -> 'Page':
        '''
        Adds a new hw_long block to the selected section.
        :param hw: a homework description to add
        :returns: self
        '''

        self.__cache = None

        block = self.__HWLong(hw)
        self.__body[self.__selected].append(block)
        if hw.id not in self.__hws_blocks:
            self.__hws_blocks[hw.id] = [block]
        else:
            self.__hws_blocks[hw.id].append(block)

        return self

    def add_message(self, message: Message) -> 'Page':
        '''
        Adds a new message block to the selected section.
        :param message: a message content to add
        :returns: self
        '''

        self.__cache = None
        self.__body[self.__selected].append(self.__Message(message))
        return self

    def add_text_input(self, name: str, desc: str, rows: int) -> 'Page':
        '''
        Adds a new text_input block to the selected section.
        :param name: a name of HTML class that allows scripts to collect input data
        :param desc: a description for the user
        :param rows: a rows parameter of the HTML tag <textarea>
        :returns: self
        '''

        self.__cache = None
        self.__body[self.__selected].append(self.__TextInput(name, desc, rows))
        return self

    def add_date_time_input(self, name: str, desc: str, min_date: Optional[tm.struct_time] =None) -> 'Page':
        '''
        Adds a new date_time_input block to the selected section.
        :param name: a name of HTML class that allows scripts to collect input data
        :param desc: a description for the user
        :param min_date: a bottom boundary of the input
        :returns: self
        '''

        self.__cache = None
        self.__body[self.__selected].append(self.__DateTimeInput(name, desc, min_date))
        return self

    def add_button_post(self, text: str, url: str, elems: List[str]) -> 'Page':
        '''
        Adds a new button_post block to the selected section.
        :param text: a text in the button
        :param url: a web page to redirect on click
        :param elems: a list of names of the input blocks which input data will be sent on click
        :returns: self
        '''

        self.__cache = None
        self.__body[self.__selected].append(self.__ButtonPOST(text, self.__url, url, elems))
        return self

    class __Block:
        def __init__(self):
            self.view = ''

        def __repr__(self):
            return self.view

    class __Line(__Block):
        def __init__(self):
            super().__init__()
            self.view = '<hr />\n'

    class __Break(__Block):
        def __init__(self):
            super().__init__()
            self.view = '<br>\n'

    class __Heading(__Block):
        def __init__(self, lvl: int, text: str):
            super().__init__()
            self.view = f'<h{lvl}>{text}</h{lvl}>\n'

    class __Panel(__Block):
        def __init__(self, elems: List[Tuple[str, str]]):
            super().__init__()
            sz = 100 // len(elems)
            self.view = (
                '<table style="border-collapse: collapse; width: 100%; max-width: 600px;" border="0"><tbody>\n\t<tr>\n' + \
                ''.join(map(lambda el: f'\t\t<td style="width: {sz}%;"><a href="{el[0]}">{el[1]}</a></td>\n', elems)) +
                '\t</tr>\n</tbody></table>\n'
            )

    class __HWShort(__Block):
        def __init__(self, hw: HW, url: str):
            super().__init__()
            self.__url = url
            self.update_view(hw)

        def update_view(self, hw: HW):
            deadline_str = tm.strftime('%d.%m.%Y %H:%M', hw.deadline)
            self.view = (
                f'<h3><a href="{self.__url}">{hw.name}</a></h3>\n'
                f'<p><strong>Дедлайн:</strong> {deadline_str}</p>\n'
                '<p><strong>Нет проверенных решений</p></strong>\n' if hw.mark is None else f'<p><strong>Оценка:</strong> {hw.mark}</p>\n'
            )

    class __HWLong(__Block):
        def __init__(self, hw: HW):
            super().__init__()
            self.update_view(hw)

        def update_view(self, hw: HW):
            date_str     = tm.strftime('%d.%m.%Y %H:%M', hw.date)
            deadline_str = tm.strftime('%d.%m.%Y %H:%M', hw.deadline)
            self.view = (
                f'<h2>{hw.name}</h2>\n'
                f'<p style="width: 800px; word-wrap: break-word;">{hw.problem}</p>\n'
                f'<p><strong>Опубликовано:</strong> {date_str}</p>\n'
                f'<p><strong>Дедлайн:</strong> {deadline_str}</p>\n'
                '<p><strong>Нет проверенных решений</p></strong>\n' if hw.mark is None else f'<p><strong>Оценка:</strong> {hw.mark}</p>\n'
            )

    class __Message(__Block):
        def __init__(self, message: Message):
            super().__init__()

            time_str = tm.strftime('%d.%m.%Y %H:%M', message.time)
            if not message.url.startswith('//'):
                url = '//' + message.url
            else:
                url = message.url

            self.view = (
                '<table style="border-collapse: collapse; background-color: #d9d9d9;" border="0"><tbody>\n'
                '\t<tr><td style="width: 100%;"><blockquote>\n'
                f'\t\t<p><a href="{url}">{message.url}</a></p>\n'
                f'\t\t<p style="width: 500px; word-wrap: break-word;">{message.text}</p>\n'
                f'\t\t<p style="text-align: right;"><em>{time_str}</em></p>\n'
                '\t</blockquote></td></tr>\n'
                '</tbody></table>\n<br>\n'
            )

    class __TextInput(__Block):
        def __init__(self, name: str, desc: str, rows: int):
            super().__init__()
            self.view = (
                f'<p>{desc}:</p>\n'
                f'<p><textarea rows="{rows}" cols="75" class="{name}" style="resize: vertical"></textarea></p>\n'
            )

    class __DateTimeInput(__Block):
        def __init__(self, name: str, desc: str, min_date: Optional[tm.struct_time]):
            super().__init__()
            if min_date is not None:
                min_date_str = tm.strftime('%Y-%m-%dT%H:%M', min_date)
                self.view = (
                    f'<p><label for="{name}" style="padding-right: 20px;">{desc}:</label>'
                    f'<input type="datetime-local" class="{name}" min="{min_date_str}"></p>'
                )
            else:
                self.view = (
                    f'<p><label for="{name}" style="padding-right: 20px;">{desc}:</label>'
                    f'<input type="datetime-local" class="{name}"></p>'
                )

    class __ButtonPOST(__Block):
        __n_buttons = 0

        def __init__(self, text: str, url_post: str, url_redirect: str, elems: List[str]):
            super().__init__()
            n = self.__n_buttons
            self.__n_buttons += 1
            self.view = (
                '<script type="text/javascript">\n' + \
                '\tfunction fun%d() {\n' % n + \
                ''.join(map(lambda el: f'\t\tvar {el} = document.querySelector(".{el}").value;\n', elems)) + \
                '\t\tif (' + ' && '.join(map(lambda el: f'{el}.length > 0', elems)) + ') {\n'
                '\t\t\tlet xhr = new XMLHttpRequest();\n'
                f'\t\t\txhr.open("POST", "{url_post}", true);\n'
                '\t\t\txhr.setRequestHeader("Content-Type", "application/json");\n'
                '\t\t\txhr.send(JSON.stringify({ ' + ', '.join(map(lambda el: f'"{el}": {el}', elems)) + ' }));\n'
                f'\t\t\twindow.location.href = "{url_redirect}";\n'
                '\t\t} else {\n\t\t\talert("Заполните все поля");\n\t\t}\n\t}\n'
                f'</script>\n<button onclick="fun{n}()">{text}</button>\n'
            )
