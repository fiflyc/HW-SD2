import asyncio
from quart import Quart, request
import time as tm
from hwproj_p2.controller import Controller
from hwproj_p2.controller.checker import Checker
from hwproj_p2.model import Model
from hwproj_p2.view import View, UserType

service = Quart('MyHWProj')
view: View = None
checker: Checker = None
controller: Controller = None


@service.route('/student')
def get_homeworks_list_student():
    return view.get_homeworks_page(UserType.STUDENT)


@service.route('/teacher')
def get_homeworks_list_teacher():
    return view.get_homeworks_page(UserType.TEACHER)


@service.route('/student/homework/<int:hw_id>', methods=['GET', 'POST'])
async def send_solution_student(hw_id):
    if request.method == 'POST':
        data = await request.json
        service.add_background_task(controller.send_solution, hw_id, data['m_url'], data['m_text'])
    return view.get_task_page(hw_id, UserType.STUDENT)


@service.route('/teacher/homework/<int:hw_id>')
def get_homework_teacher(hw_id):
    return view.get_task_page(hw_id, UserType.TEACHER)


@service.route('/student/results')
def get_results_list_student():
    return view.get_results_page(UserType.STUDENT)


@service.route('/teacher/results')
def get_results_list_teacher():
    return view.get_results_page(UserType.TEACHER)


@service.route('/teacher/add', methods=['GET', 'POST'])
async def add_homework_teacher():
    if request.method == 'GET':
        return view.get_hw_creation_page()
    else:
        data = await request.json
        controller.create_homework(
            data['hw_name'],
            data['hw_problem'],
            tm.strptime(data['hw_start'], '%Y-%m-%dT%H:%M'),
            tm.strptime(data['hw_end'], '%Y-%m-%dT%H:%M'),
            data["hw_script"]
        )
        return view.get_homeworks_page(UserType.TEACHER)


@service.before_serving
async def startup():
    global view, checker, controller
    view = View()
    checker = await Checker.create_checker()
    controller = Controller(Model(None), view, checker)


if __name__ == '__main__':
    service.run(host="localhost", port=8888)
