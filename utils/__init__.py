import json2
from pathlib import Path

class Config(dict):

    def __init__(self, config_file):
        self.file = Path(config_file)
        if self.file.exists():
            with self.file.open('r') as fp:
                super().__init__(json2.load(fp))
        else:
            print('Missing config file', self.file)

    def path(self, path: str):
        path = path.strip('/')
        elements = path.split('/')
        value = self.get(elements[0])
        for item in elements[1:]:
            value = value.get(item)
        return value

    def root(self):
        return Path(self.path('photos/root'))


def safe_get_value(val, t, default=None):
    try:
        return t(val)
    except:
        print(f'safe_get_value got wrong value {val}', flush=True)
        return default


if __name__ == '__main__':
    C = Config('config.json')
    print(C.path('/photos/ignore/'))
    print(C.root())

    # print(C.root())
    # print(C.get.photos.root)


