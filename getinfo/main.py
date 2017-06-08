from browser import Firefox
from common import config
from common import util
from imp import reload
import threading, signal
import time, sys


def quit(signum, frame):
    print('You choose to stop me.')
    sys.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    modules = {}
    file_list = util.get_files(basename=True, _pre='get_', _ext='.py', _filter='wechat')
    firefox = Firefox()
    firefox.init()
    firefox.find_info()
    index = 0
    while True:
        name = file_list[index%len(file_list)]
        util.print_d(name)
        if name not in modules:
            modules[name] = __import__(name)
        else:
            reload(modules[name])

        c = getattr(modules[name], 'Spider')
        s = name.replace('get_', '')
        spider = c(s, config.urls[s])
        spider.clone(firefox)
        spider.browse_page()
        print('\n\n')
        index += 1
        if index % len(file_list) == 0:
            time.sleep(1800)
        if index / len(file_list) == 2:
            break
        time.sleep(300)

    firefox.clear_up()
