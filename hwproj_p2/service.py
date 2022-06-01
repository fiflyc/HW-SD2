from flask import Flask
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
    return view.get_task_page(hw_id, UserType.STUDENT)

@service.route('/teacher/homework/<int:hw_id>')
def get_homework_teacher():
    return view.get_task_page(hw_id, UserType.TEACHER)

@service.route('/student/results')
def get_results_list_student():
    return view.get_results_page(UserType.STUDENT)

@service.route('/teacher/results')
def get_results_list_teacher():
    return view.get_results_page(UserType.TEACHER)

@service.route('/teacher/add', methods=['GET', 'POST'])
def add_homework_teacher():
    return view.get_hw_creation_page()


if __name__ == '__main__':
    service.run(host="localhost", port=8888)
