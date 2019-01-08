import os


def absjoin(*args):
    return os.path.abspath(os.path.join(*args))
