import sys
import traceback


def exceptlog(ex_cls, ex, tb):
    text = f'{ex_cls.__name__}: {ex}:\n'
    text += ''.join(traceback.format_tb(tb))
    print(text)
    quit()


def activate():
    sys.excepthook = exceptlog
