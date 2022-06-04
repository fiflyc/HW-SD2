from flask import Flask, request
import time as tm
from controller import Controller
from model import Model
from view import View, UserType


service = Flask('MyHWProj')
view = View()
controller = Controller(Model(None), view)


@service.route('/student')
def get_homeworks_list_student():
    return view.get_homeworks_page(UserType.STUDENT)

@service.route('/teacher')
def get_homeworks_list_teacher():
    return view.get_homeworks_page(UserType.TEACHER)

@service.route('/student/homework/<int:hw_id>', methods=['GET', 'POST'])
def send_solution_student(hw_id):
    if request.method == 'POST':
        data = request.json
        controller.send_solution(
            hw_id,
            data['m_url'],
            data['m_text']
        )
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
def add_homework_teacher():
    if request.method == 'GET':
        return view.get_hw_creation_page()
    else:
        data = request.json
        controller.create_homework(
            data['hw_name'],
            data['hw_problem'],
            tm.strptime(data['hw_start'], '%Y-%m-%dT%H:%M'),
            tm.strptime(data['hw_end'], '%Y-%m-%dT%H:%M'),
            data["hw_script"]
        )
        return view.get_homeworks_page(UserType.TEACHER)


if __name__ == '__main__':
    service.run(host="localhost", port=8888)
