import time as tm
from model import HW, Message
from typing import List, Tuple, Dict, Optional, Union, Any


class Page:
    '''
    A smart constructor of web pages.
    All such pages contain list of blocks, which can be updated by adding those at the end.
    For lists of blocks which order may change use containers.  
    You can only add blocks without removing and update containers, also you may update all blocks with an info about homework.
    Supported blocks:
        heading:     HTML tag <h*> where * in [1, 6]
        panel:       HTML borderless table with one row that contains links to some pages
        line:        HTML tag <hr />
        break:       HTML tag <br>
        hw_res:      HTML code of the student's attempt result
        hw_short:    HTML code of a short homework description (name, deadline, mark)
        hw_long:     HTML code of a long homework description (name, problem, date, deadline, mark)
        message:     HTML code of a message (a student's try or a checker output)
        text_input:  HTML tag <textarea>
        file_input:  HTML tag <input type="file">
        button_post: HTML tag <button> with a script that sends selected input as a JSON data
    Supported containers:
        hws_list: HTML code of a list of hw_short blocks sorted by a passed key
        dialog:   HTML code of a list of message blocks sorted by a passed key
        results:  HTML code of a list of hw_res blocks sorted by a passed key
    To get HTML code of the page use repr function.
    '''

    def __init__(self, url: str):
        '''
        :param url: an URL of the page
        '''

        self.__url = url
        self.__body = []
        self.__containers = []
        self.__hws_blocks = {}
        self.__cache = None

    def __repr__(self):
        if self.__cache is None:
            self.__cache = '\n'.join(map(lambda b: repr(b), self.__body))
        return self.__cache

    @property
    def n_containers(self):
        return len(self.__containers)

    def update(self, hw: HW):
        '''
        Updates view of all homeworks representations in the page.
        :param hw: an updating homework
        '''

        self.__cache = None
        if hw.id in self.__hws_blocks:
            for b in self.__hws_blocks[hw.id]:
                b.update_view(hw)

    def insert_to(self, index: int, key: Any, obj: Union[HW, Message], *args, **kwargs):
        '''
        Inserts a block into an existing container. 
        :param index: an index of the container
        :param key: a key of the new block
        :param obj: a object which representation block will be added
        :raises IndexError: if an index of the container is out of range
        '''

        if -len(self.__containers) > index or len(self.__containers) <= index:
            raise IndexError('container index is out of range')
        self.__cache = None
        self.__containers[index].insert(key, obj, *args, **kwargs)

        if type(self.__containers[index]).__name__ == '_HWsList':
            self.__hws_blocks[obj.id].append(self.__containers[index])

    def filter_container(self, index: int, filt_attr: str, filt_val: Any):
        '''
        Filters blocks in a container by a attribute value. Use None values to remove filter.
        :param index: an index of the container
        :param filt_attr: the name of the attribute of an object (like HW or Message) what is represented by a block
        :param filt_val: all blocks with attribute above this value will be ignored
        :raises IndexError: if an index of the container is out of range
        '''

        if -len(self.__containers) > index or len(self.__containers) <= index:
            raise IndexError('container index is out of range')
        self.__cache = None
        self.__containers[index].set_filter(filt_attr, filt_val)

    def __add_block(self, block: 'Page._Block') -> 'Page':
        self.__cache = None
        self.__body.append(block)
        return self

    def add_heading(self, lvl: int, text: str) -> 'Page':
        '''
        Adds a new heading block to the end of the page.
        :param lvl: a number * in the <h*> tag
        :param text: a text of the heading
        :returns: self
        '''

        return self.__add_block(self._Heading(lvl, text))

    def add_panel(self, elems: List[Tuple[str, str]]) -> 'Page':
        '''
        Adds a new panel block to the end of the page.
        :param elems: a list of tuples (URL, text)
        :returns: self
        '''

        return self.__add_block(self._Panel(elems))

    def add_line(self) -> 'Page':
        '''
        Adds a new line block to the end of the page.
        :returns: self
        '''

        return self.__add_block(self._Line())

    def add_break(self) -> 'Page':
        '''
        Adds a new break block to the end of the page.
        :returns: self
        '''

        return self.__add_block(self._Break())

    def add_hw_res(self, hw: HW, url: str, time: tm.struct_time) -> 'Page':
        '''
        Adds a new hw_res block to the end of the page.
        :param hw: a homework description to add
        :param url: a link to a task page
        :param time: the last time when the result was updated
        :returns: self
        '''

        return self.__add_block(self._HWRes(hw, url, time))

    def add_hw_short(self, hw: HW, url: str) -> 'Page':
        '''
        Adds a new hw_short block to the end of the page.
        :param hw: a homework description to add
        :param url: a link to a task page
        :returns: self
        '''

        block = self._HWShort(hw, url)
        if hw.id not in self.__hws_blocks:
            self.__hws_blocks[hw.id] = [block]
        else:
            self.__hws_blocks[hw.id].append(block)

        return self.__add_block(block)

    def add_hw_long(self, hw: HW) -> 'Page':
        '''
        Adds a new hw_long block to the end of the page.
        :param hw: a homework description to add
        :returns: self
        '''

        block = self._HWLong(hw)
        if hw.id not in self.__hws_blocks:
            self.__hws_blocks[hw.id] = [block]
        else:
            self.__hws_blocks[hw.id].append(block)

        return self.__add_block(block)

    def add_message(self, message: Message) -> 'Page':
        '''
        Adds a new message block to the end of the page.
        :param message: a message content to add
        :returns: self
        '''

        return self.__add_block(self._Message(message))

    def add_text_input(self, name: str, desc: str, rows: int) -> 'Page':
        '''
        Adds a new text_input block to the end of the page.
        :param name: a name of HTML class that allows scripts to collect input data
        :param desc: a description for the user
        :param rows: a rows parameter of the HTML tag <textarea>
        :returns: self
        '''

        return self.__add_block(self._TextInput(name, desc, rows))

    def add_date_time_input(self, name: str, desc: str, min_date: Optional[tm.struct_time] =None) -> 'Page':
        '''
        Adds a new date_time_input block to the end of the page.
        :param name: a name of HTML class that allows scripts to collect input data
        :param desc: a description for the user
        :param min_date: a bottom boundary of the input
        :returns: self
        '''

        return self.__add_block(self._DateTimeInput(name, desc, min_date))

    def add_file_input(self, name: str, desc: str, types: List[str] =[]):
        '''
        Adds a new file_input block to the end of the page.
        :param name: a name of HTML class that allows scripts to collect input data
        :param desc: a description for the user
        :param types: a list of the acceptable file types, if it's empty it accepts all file types
        :returns: self
        '''

        return self.__add_block(self._FileInput(name, desc, types))

    def add_button_post(self, text: str, url: str, elems: List[str], files: List[str] = []) -> 'Page':
        '''
        Adds a new button_post block to the end of the page.
        :param text: a text in the button
        :param url: a web page to redirect on click
        :param elems: a list of names of the input blocks which input data will be sent on click
        :param files: a list of names of the file_input blocks which data will be sent on click
        :returns: self
        '''

        return self.__add_block(self._ButtonPOST(text, self.__url, url, elems, files))

    def __add_container(self, container: 'Page._Container') -> 'Page':
        self.__containers.append(container)
        return self.__add_block(container)

    def add_hws_list(self, reverse: bool =False) -> 'Page':
        '''
        Adds a new hws_list container to the end of the page.
        :param reverse: if true then new blocks will be inserted to the top of the container
        :returns: self
        '''

        return self.__add_container(self._HWsList(self.__hws_blocks, reverse))

    def add_dialog(self, reverse: bool =False) -> 'Page':
        '''
        Adds a new dialog container to the end of the page.
        :param reverse: if true then new blocks will be inserted to the top of the container
        :returns: self
        '''

        return self.__add_container(self._Dialog(reverse))

    def add_results(self, reverse: bool =False) -> 'Page':
        '''
        Adds a new results container to the end of the page.
        :param reverse: if true then new blocks will be inserted to the top of the container
        :returns: self
        '''

        return self.__add_container(self._Results(reverse))

    class _Block:
        def __init__(self, obj: Any =None):
            self.obj = obj 
            self.view = ''

        def __repr__(self):
            return self.view

    class _Line(_Block):
        def __init__(self):
            super().__init__()
            self.view = '<hr />\n'

    class _Break(_Block):
        def __init__(self):
            super().__init__()
            self.view = '<br>\n'

    class _Heading(_Block):
        def __init__(self, lvl: int, text: str):
            super().__init__()
            self.view = f'<h{lvl}>{text}</h{lvl}>\n'

    class _Panel(_Block):
        def __init__(self, elems: List[Tuple[str, str]]):
            super().__init__()
            sz = 100 // len(elems)
            self.view = (
                '<table style="border-collapse: collapse; width: 100%; max-width: 600px;" border="0"><tbody>\n\t<tr>\n' + \
                ''.join(map(lambda el: f'\t\t<td style="width: {sz}%;"><a href="{el[0]}">{el[1]}</a></td>\n', elems)) +
                '\t</tr>\n</tbody></table>\n'
            )

    class _HWRes(_Block):
        def __init__(self, hw: HW, url: str, time: tm.struct_time):
            super().__init__(hw)
            time_str = tm.strftime('%d.%m.%Y %H:%M', time)
            self.view = (
                f'<h3><a href="{url}">{hw.name}</a></h3>\n'
                f'<p><strong>Время проверки:</strong> {time_str}</p>\n'
                f'<p><strong>Оценка:</strong> {hw.mark}</p>\n'
            )

    class _HWShort(_Block):
        def __init__(self, hw: HW, url: str):
            super().__init__(hw)
            self.__url = url
            self.update_view(hw)

        def update_view(self, hw: HW):
            deadline_str = tm.strftime('%d.%m.%Y %H:%M', hw.deadline)
            self.view = (
                f'<h3><a href="{self.__url}">{hw.name}</a></h3>\n'
                f'<p><strong>Дедлайн:</strong> {deadline_str}</p>\n'
            )
            self.view += '<p><strong>Нет проверенных решений</p></strong>\n' if hw.mark is None else f'<p><strong>Оценка:</strong> {hw.mark}</p>\n'
            
    class _HWLong(_Block):
        def __init__(self, hw: HW):
            super().__init__(hw)
            self.update_view(hw)

        def update_view(self, hw: HW):
            date_str     = tm.strftime('%d.%m.%Y %H:%M', hw.date)
            deadline_str = tm.strftime('%d.%m.%Y %H:%M', hw.deadline)
            self.view = (
                f'<h2>{hw.name}</h2>\n'
                f'<p style="width: 800px; word-wrap: break-word; white-space: pre-line;">{hw.problem}</p>\n'
                f'<p><strong>Опубликовано:</strong> {date_str}</p>\n'
                f'<p><strong>Дедлайн:</strong> {deadline_str}</p>\n'
            )
            self.view += '<p><strong>Нет проверенных решений</p></strong>\n' if hw.mark is None else f'<p><strong>Оценка:</strong> {hw.mark}</p>\n'

    class _Message(_Block):
        def __init__(self, message: Message):
            super().__init__(message)

            time_str = tm.strftime('%d.%m.%Y %H:%M', message.time)
            if message.url.startswith('http://'):
                url = message.url[5:]
            elif message.url.startswith('https://'):
                url = message.url[6:]
            elif not message.url.startswith('//'):
                url = '//' + message.url
            else:
                url = message.url

            self.view = (
                '<table style="border-collapse: collapse; background-color: #d9d9d9;" border="0"><tbody>\n'
                '\t<tr><td style="width: 100%;"><blockquote>\n'
                f'\t\t<p><a href="{url}">{message.url}</a></p>\n'
                f'\t\t<p style="width: 500px; word-wrap: break-word; white-space: pre-line;">{message.text}</p>\n'
                f'\t\t<p style="text-align: right;"><em>{time_str}</em></p>\n'
                '\t</blockquote></td></tr>\n'
                '</tbody></table>\n'
            )

    class _TextInput(_Block):
        def __init__(self, name: str, desc: str, rows: int):
            super().__init__()
            self.view = (
                f'<p>{desc}:</p>\n'
                f'<p><textarea rows="{rows}" cols="75" class="{name}" style="resize: vertical"></textarea></p>\n'
            )

    class _DateTimeInput(_Block):
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

    class _FileInput(_Block):
        __n_finputs = 0

        def __init__(self, name: str, desc: str, types: List[str] =[]):
            super().__init__()
            n = self.__n_finputs
            self.__n_finputs += 1
            self.view = (
                '<script type="text/javascript">\n' + \
                f'\tvar {name} = null;\n\tvar {name}_loading = false;\n' + \
                '\tfunction onloadf%d() {\n' % n + \
                f'\t\t{name} = null;\n' + \
                f'\t\tif (!document.querySelector(".{name}").files[0])' + ' {\n\t\t\treturn;\n\t\t}\n' + \
                f'\t\t{name}_loading = true;\n' + \
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

    class _ButtonPOST(_Block):
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

    class _Container(_Block):
        def __init__(self, separator: str, reverse=False):
            super().__init__()
            self.__sep = separator
            self.__reverse = reverse
            self.__filt_by = None
            self.__filt_val = None
            self.__blocks = {}

        def set_filter(self, filt_attr: str, filt_val: Any):
            self.__filt_attr = filt_attr
            self.__filt_val = filt_val
            self.update_view()

        def insert_block(self, key: Any, block: 'Page._Block'):
            if key in self.__blocks:
                self.__blocks[key].append(block)
            else:
                self.__blocks[key] = [block]
            self.update_view()

        def update_view(self, *args, **kwargs):
            if self.__filt_val is None:
                self.view = self.__sep.join([self.__sep.join(map(lambda b: repr(b), bs)) for _, bs in sorted(self.__blocks.items(), key=lambda item: item[0], reverse=self.__reverse)])
            else:
                self.view = self.__sep.join(filter(None, [self.__sep.join(filter(None, map(lambda b: repr(b) if getattr(b.obj, self.__filt_attr) < self.__filt_val else '', bs))) for _, bs in sorted(self.__blocks.items(), key=lambda item: item[0], reverse=self.__reverse)]))

    class _HWsList(_Container):
        def __init__(self, hws_blocks: Dict[int, List['Page._Block']], *args, **kwargs):
            super().__init__('<hr />\n', *args, **kwargs)
            self.__hws_blocks = hws_blocks

        def insert(self, key: Any, hw: HW, url: str):
            block = Page._HWShort(hw, url)
            self.insert_block(key, block)
            if hw.id not in self.__hws_blocks:
                self.__hws_blocks[hw.id] = [block]
            else:
                self.__hws_blocks[hw.id].append(block)

    class _Dialog(_Container):
        def __init__(self, *args, **kwargs):
            super().__init__('<br>\n', *args, **kwargs)

        def insert(self, key: Any, message: Message):
            self.insert_block(key, Page._Message(message))

    class _Results(_Container):
        def __init__(self, *args, **kwargs):
            super().__init__('<hr />\n', *args, **kwargs)

        def insert(self, key: Any, hw: HW, url: str, time: tm.struct_time):
            block = Page._HWRes(hw, url, time)
            self.insert_block(key, block)
