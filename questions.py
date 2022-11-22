import json
import sys
import os
import uuid
from aiogram.dispatcher.filters.state import State, StatesGroup


class QuestionForm:
    def __init__(self):
        self.questions = []
        self.sql_request = ''
        self.title = ''
        self.description = ''
        self.id = str(uuid.uuid1())
        self.state_group = ''
        self.command = ''
        self.footer = ''

    def fill_states(self):
        states = dict()
        for question in self.questions:
            states["state_"+question.id] = State()
            question.state = states["state_"+question.id]
        self.state_group = type('StateGroup_'+self.id, (StatesGroup,), states)


class Question:
    def __init__(self):
        self.text = ''
        self.answer = ''
        self.id = ''
        self.state = ''
        self.next_id = ''
        self.data_request = ''


class QuestionFormEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, QuestionForm) | isinstance(o, Question):
            return o.__dict__
        else:
            json.JSONEncoder.default(self, o)


def question_form_hook(json_dict: dict):
    if "sql_request" in json_dict.keys():
        result = QuestionForm()
        result.__dict__ = json_dict
        return result
    else:
        result = Question()
        result.__dict__ = json_dict
        return result


def load_form_lib(path):
    form_lib = []
    for filename in os.listdir(path):
        f = os.path.join(path, filename)
        lib_file = open(f, 'r', encoding="utf-8")
        cur_form = json.load(lib_file, object_hook=question_form_hook)
        form_lib.append(cur_form)
    return form_lib


def dump_form_lib(lib: list, path: str):
    for cur_form in lib:

        filename = cur_form.id
        f = os.path.join(path, filename)
        os.makedirs(path, exist_ok=True)
        lib_file = open(f, 'w', encoding="utf-8")
        json.dump(cur_form, lib_file, cls=QuestionFormEncoder, ensure_ascii=False)
        lib_file.close()

# ################ tests


def test_1():
    qf = QuestionForm()
    qf.sql_request = "SELECT 'hello world'"
    qf.description = 'описание тестовой формы'
    qf.title = 'тестовая форма'
    qf.command = 'start'
    qf.footer = 'Спасибо за ваши ответы.'
    q = Question()
    q.text = 'Ultimate Question of Life, the Universe, and Everything'
    q.answer = '42'
    q.id = 'question_1'
    q.data_request = "SELECT 'hello world'"

    qf.questions.append(q)
    file = open('test/questions.json', 'w', encoding="utf-8")
    json.dump(qf, file, cls=QuestionFormEncoder, ensure_ascii=False)
    file.close()
    file = open('test/questions.json', 'r', encoding="utf-8")
    res = json.load(file, object_hook=question_form_hook)
    print(type(res))
    file.close()

    str1 = json.dumps(qf, cls=QuestionFormEncoder)
    str2 = json.dumps(res, cls=QuestionFormEncoder)

    if str1 == str2:
        print('test 1 ok')
        return 0
    else:
        print('test 1 not ok')
        return 1


def test_2():
    test_lib = []

    qf = QuestionForm()
    qf.sql_request = "SELECT 'hello world'"
    qf.title = 'тестовая форма2'
    q = Question()
    q.text = 'Ultimate Question of Life, the Universe, and Everything'
    q.answer = '42'
    q.id = 'question_1'
    qf.questions.append(q)
    test_lib.append(qf)
    dump_form_lib(test_lib, 'test/lib')

    test_lib_2 = load_form_lib('test/lib')

    str1 = json.dumps(test_lib, cls=QuestionFormEncoder)
    str2 = json.dumps(test_lib_2, cls=QuestionFormEncoder)

    # cleaning up
    for filename in os.listdir('test/lib'):
        f = os.path.join('test/lib', filename)
        os.remove(f)
    os.rmdir('test/lib')

    if str1 == str2:
        print('test 2 ok')
        return 0
    else:
        print('test 2 not ok')
        return 1


if __name__ == '__main__':
    if test_1() == 1:
        sys.exit(1)
    if test_2() == 1:
        sys.exit(1)

    sys.exit(0)
