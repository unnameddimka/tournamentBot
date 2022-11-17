import json
import sys


class QuestionForm:
    def __init__(self):
        self.questions = []
        self.sql_request = ''


class Question:
    def __init__(self):
        self.text = ''
        self.answer = ''


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


if __name__ == '__main__':
    qf = QuestionForm()
    qf.sql_request = "SELECT 'hello world'"
    q = Question()
    q.text = 'Ultimate Question of Life, the Universe, and Everything'
    q.answer = '42'
    qf.questions.append(q)
    file = open('test/questions.json', 'w')
    json.dump(qf, file, cls=QuestionFormEncoder)
    file.close()
    file = open('test/questions.json', 'r')
    res = json.load(file, object_hook=question_form_hook)
    print(type(res))
    file.close()

    str1 = json.dumps(qf, cls=QuestionFormEncoder)
    str2 = json.dumps(res, cls=QuestionFormEncoder)

    if str1 == str2:
        print('ok')
        sys.exit(0)
    else:
        print('not ok')
        sys.exit(1)
