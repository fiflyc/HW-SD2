import pytest
import re
import time as tm
from view import View, UserType
from model import HW, Message


HTMLs = {
    'HWS_LIST_STUDENT_EMPTY': '',
    'HWS_LIST_TEACHER_EMPTY': '',
    'RESULTS_STUDENT_EMPTY': '',
    'RESULTS_TEACHER_EMPTY': '',
    'HW_INVALID_STUDENT': '',
    'HW_INVALID_TEACHER': '',
    'NEW_HW': '',
    'HWS_LIST_STUDENT_1': '',
    'HWS_LIST_TEACHER_1': '',
    'HW0_STUDENT': '',
    'HW0_TEACHER': '',
    'HW0_STUDENT_MESSAGES_1': '',
    'HW0_TEACHER_MESSAGES_1': '',
    'HWS_LIST_STUDENT_SOLVED_1': '',
    'HWS_LIST_TEACHER_SOLVED_1': '',
    'RESULTS_STUDENT_1': '',
    'RESULTS_TEACHER_1': '',
}


@pytest.fixture(scope='module', autouse=True)
def my_fixture():
    prefix = './test/html/'
    suffix = '.html'
    for page in HTMLs:
        with open(prefix + page.lower() + suffix, 'r') as file:
            HTMLs[page] = file.read()


def test_all_init_pages():
    view = View()

    assert HTMLs['HWS_LIST_STUDENT_EMPTY'] == view.get_homeworks_page(UserType.STUDENT)
    assert HTMLs['HWS_LIST_TEACHER_EMPTY'] == view.get_homeworks_page(UserType.TEACHER)
    assert HTMLs['RESULTS_STUDENT_EMPTY'] == view.get_results_page(UserType.STUDENT)
    assert HTMLs['RESULTS_TEACHER_EMPTY'] == view.get_results_page(UserType.TEACHER)

def test_hw_creation_page():
    view = View()

    assert re.sub(r'min="[^"]*"', 'min=""', HTMLs['NEW_HW']) == \
           re.sub(r'min="[^"]*"', 'min=""', view.get_hw_creation_page())

def test_add_new_actual_hw__lists_updated():
    HW._HW__n_homeworks = 0
    view = View()

    hw = HW('NAME-00', 'PROBLEM-00', tm.localtime(), tm.localtime(), '')
    view.on_hw_created(hw)

    assert re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', HTMLs['HWS_LIST_STUDENT_1']) == \
           re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', view.get_homeworks_page(UserType.STUDENT))
    assert re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', HTMLs['HWS_LIST_TEACHER_1']) == \
           re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', view.get_homeworks_page(UserType.TEACHER))

def test_add_new_future_hw__lists_updated():
    HW._HW__n_homeworks = 0
    view = View()

    date = tm.strptime('2099-12-12T12:00', '%Y-%m-%dT%H:%M')
    hw = HW('NAME-00', 'PROBLEM-00', date, date, '')
    view.on_hw_created(hw)

    assert HTMLs['HWS_LIST_STUDENT_EMPTY'] == view.get_homeworks_page(UserType.STUDENT)
    assert re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', HTMLs['HWS_LIST_TEACHER_1']) == \
           re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', view.get_homeworks_page(UserType.TEACHER))

def test_add_new_actual_hw__pages_created():
    HW._HW__n_homeworks = 0
    view = View()

    hw = HW('NAME-00', 'PROBLEM-00', tm.localtime(), tm.localtime(), '')
    view.on_hw_created(hw)

    assert re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', HTMLs['HW0_STUDENT']) == \
           re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', view.get_task_page(0, UserType.STUDENT))
    assert re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', HTMLs['HW0_TEACHER']) == \
           re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', view.get_task_page(0, UserType.TEACHER))

def test_add_new_future_hw__pages_created():
    HW._HW__n_homeworks = 0
    view = View()

    date = tm.strptime('2099-12-12T12:00', '%Y-%m-%dT%H:%M')
    hw = HW('NAME-00', 'PROBLEM-00', date, date, '')
    view.on_hw_created(hw)

    assert HTMLs['HW_INVALID_STUDENT'] == view.get_task_page(0, UserType.STUDENT)
    assert re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', HTMLs['HW0_TEACHER']) == \
           re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', view.get_task_page(0, UserType.TEACHER))

def test_send_solution__hw_page_updated():
    HW._HW__n_homeworks = 0
    view = View()

    hw = HW('NAME-00', 'PROBLEM-00', tm.localtime(), tm.localtime(), '')
    view.on_hw_created(hw)
    msg = Message(tm.localtime(), 'github.com', 'comment-00-00')
    view.on_message_send(0, msg)

    assert re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', HTMLs['HW0_STUDENT_MESSAGES_1']) == \
           re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', view.get_task_page(0, UserType.STUDENT))
    assert re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', HTMLs['HW0_TEACHER_MESSAGES_1']) == \
           re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', view.get_task_page(0, UserType.TEACHER))

def test_mark_set__pages_updated():
    HW._HW__n_homeworks = 0
    view = View()

    hw = HW('NAME-00', 'PROBLEM-00', tm.localtime(), tm.localtime(), '')
    view.on_hw_created(hw)
    hw.mark = 10
    view.on_mark_updated(hw, tm.localtime())

    assert re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', HTMLs['HWS_LIST_STUDENT_SOLVED_1']) == \
           re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', view.get_homeworks_page(UserType.STUDENT))
    assert re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', HTMLs['HWS_LIST_TEACHER_SOLVED_1']) == \
           re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', view.get_homeworks_page(UserType.TEACHER))
    assert re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', HTMLs['RESULTS_STUDENT_1']) == \
           re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', view.get_results_page(UserType.STUDENT))
    assert re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', HTMLs['RESULTS_TEACHER_1']) == \
           re.sub(r'>\s*\d{2}.\d{2}.\d{4} \d{2}:\d{2}\s*<', '><', view.get_results_page(UserType.TEACHER))
