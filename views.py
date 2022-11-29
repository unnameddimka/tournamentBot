import sys
import data
import json
import os


class DataView:
    def __init__(self):
        self.request = ''
        self.param_src = []  # source of parameter data. ID of some previous question in the form.
        self.params = tuple()  # parameter data itself.
        self.string_template = ''
        self.command = ''
        self.title = ''
        self.id = ''

    def fetch_data(self):
        cursor = data.exec_request(self.request, self.params)
        if len(cursor) == 0:
            return '-------------'
        result = [self.string_template.format(*row) for row in cursor]
        return result


class DataViewEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, DataView) | isinstance(o, DataView):
            return o.__dict__
        else:
            json.JSONEncoder.default(self, o)


def data_view_hook(json_dict: dict):
    result = DataView()
    result.__dict__ = json_dict
    return result


def load_form_lib(path):
    form_lib = []
    for filename in os.listdir(path):
        f = os.path.join(path, filename)
        lib_file = open(f, 'r', encoding="utf-8")
        cur_form = json.load(lib_file, object_hook=data_view_hook)
        form_lib.append(cur_form)
    return form_lib


def test_1():
    dw = DataView()
    dw.request = "SELECT %s"
    dw.params = ('hello world',)
    dw.string_template = 'test {0}'
    dw.command = 'test'
    dw.param_src = ["test param"]
    dw.id = 'test'
    dw.title = 'тестовая вьюха'
    file = open('test/view.json', 'w', encoding="utf-8")
    json.dump(dw, file, cls=DataViewEncoder, ensure_ascii=False)
    file.close()
    file = open('test/view.json', 'r', encoding="utf-8")
    res = json.load(file, object_hook=data_view_hook)
    res_data = res.fetch_data()
    print(res)
    if res_data[0] == 'test hello world':
        return 1
    else:
        return 'ERROR'


if __name__ == '__main__':
    # print(locals())
    if test_1() == 1:
        sys.exit(0)
    sys.exit(1)
