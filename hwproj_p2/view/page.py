import time as tm
from model import HW, Message
from typing import List, Tuple, Optional


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
        file_input:  HTML tag <input type="file">
        button_post: HTML tag <button> with a script that sends selected input as a JSON data
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

    def add_file_input(self, name: str, desc: str, types: List[str] =[]):
        '''
        Adds a new file_input block to the selected section.
        :param name: a name of HTML class that allows scripts to collect input data
        :param desc: a description for the user
        :param types: a list of the acceptable file types, if it's empty it accepts all file types
        :returns: self
        '''

        self.__cache = None
        self.__body[self.__selected].append(self.__FileInput(name, desc, types))
        return self

    def add_button_post(self, text: str, url: str, elems: List[str], files: List[str] = []) -> 'Page':
        '''
        Adds a new button_post block to the selected section.
        :param text: a text in the button
        :param url: a web page to redirect on click
        :param elems: a list of names of the input blocks which input data will be sent on click
        :param files: a list of names of the file_input blocks which data will be sent on click
        :returns: self
        '''

        self.__cache = None
        self.__body[self.__selected].append(self.__ButtonPOST(text, self.__url, url, elems, files))
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
                    f'<p><label for="{name}" style="padding-right: 20px;">{desc}:</label>\n'
                    f'<input type="datetime-local" class="{name}" min="{min_date_str}"></p>\n'
                )
            else:
                self.view = (
                    f'<p><label for="{name}" style="padding-right: 20px;">{desc}:</label>\n'
                    f'<input type="datetime-local" class="{name}"></p>\n'
                )

    class __FileInput(__Block):
        __n_finputs = 0

        def __init__(self, name: str, desc: str, types: List[str] =[]):
            super().__init__()
            n = self.__n_finputs
            self.__n_finputs += 1
            self.view = (
                '<script type="text/javascript">\n' + \
                f'\tvar {name} = null;\n\tvar {name}_loading = false;\n' + \
                '\tfunction onloadf%d() {\n' % n + \
                f'\t\t{name} = null;\n\t\t{name}_loading = true;\n' + \
                '\t\tconst reader = new FileReader();\n'
                f'\t\treader.readAsText(document.querySelector(".{name}").files[0]);\n'
                '\t\treader.onload = () => {\n'
                f'\t\t\t{name} = reader.result;\n\t\t\t{name}_loading = false;\n'
                '\t\t};\n\t}\n</script>'
            )
            if not types:
                self.view += (
                    f'<p><label for="{name}" style="padding-right:20px;">{desc}:</label>\n'
                    f'<input type="file" class="{name}" onchange="onloadf{n}()"></p>\n'
                )
            else:
                self.view += (
                    f'<p><label for="{name}" style="padding-right:20px;">{desc}:</label>\n'
                    f'<input type="file" class="{name}" onchange="onloadf{n}()" accept="' + ','.join(map(lambda t: t if t.startswith('.') else f'.{t}', types)) + '"></p>\n'
                )

    class __ButtonPOST(__Block):
        __n_buttons = 0

        def __init__(self, text: str, url_post: str, url_redirect: str, elems: List[str], files: List[str]):
            super().__init__()
            n = self.__n_buttons
            self.__n_buttons += 1
            self.view = (
                '<script type="text/javascript">\n' + \
                '\tfunction send%d() {\n' % n + \
                ''.join(map(lambda el: f'\t\tvar {el} = document.querySelector(".{el}").value;\n', elems))
            )
            if files:
                self.view += (
                    '\t\tif (' + ' || '.join(map(lambda fl: f'{fl} == null', files)) + ') {\n'
                    '\t\t\tif (' + ' || '.join(map(lambda fl: f'{fl}_loading', files)) + ') {\n\t\t\t\talert("Файл загружается");\n\t\t\t\treturn;\n'
                    '\t\t\t} else {\n\t\t\t\talert("Файл не выбран");\n\t\t\t\treturn;\n\t\t\t}\n\t\t}\n'
                )
            self.view += (
                '\t\tif (' + ' && '.join(map(lambda el: f'{el}.length > 0', elems)) + ') {\n'
                '\t\t\tlet xhr = new XMLHttpRequest();\n'
                f'\t\t\txhr.open("POST", "{url_post}", true);\n'
                '\t\t\txhr.setRequestHeader("Content-Type", "application/json");\n'
                '\t\t\txhr.send(JSON.stringify({ ' + ', '.join(map(lambda el: f'"{el}": {el}', elems)) + ', ' +
                ', '.join(map(lambda fl: f'"{fl}": {fl}', files)) + ' }));\n'
                f'\t\t\twindow.location.href = "{url_redirect}";\n'
                '\t\t} else {\n\t\t\talert("Заполните все поля");\n\t\t}\n\t}\n'
                f'</script>\n<button onclick="send{n}()">{text}</button>\n'
            )
