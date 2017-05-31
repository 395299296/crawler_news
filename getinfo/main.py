from common import util
from imp import reload
import threading, signal
import time, sys

def quit(signum, frame):
    print('You choose to stop me.')
    sys.exit()

def print_d(_str):
    s = 70
    l = len(_str)
    n = int((s - l - 10) / 2)
    r = s - n - l - 10
    print('-'*s)
    print('*'*n + ' '*5 + _str + ' '*5 + '*'*r)
    print('-'*s)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    index = 0
    file_list = util.get_files(basename=True, _pre='get_', _ext='.py', _filter='wechat')
    while True:
        print_d(file_list[index])
        module = __import__(file_list[index])
        # reload(module)
        print('\n\n')
        index += 1
        if index >= len(file_list):
            index = 0
        time.sleep(60)
