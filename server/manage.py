from flask_script import Manager, Server
from app import app
import threading, signal
import os, sys, time
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
lock = threading.Condition()

manager = Manager(app)

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger = True,
    use_reloader = True,
    host = '0.0.0.0',
    port = 8090)
)

@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

class Loop(threading.Thread):
    def __init__(self, lock):
        self._lock = lock
        threading.Thread.__init__(self)
 
    def run(self):
        while True:
            if self._lock.acquire():
                self.tick()
                self._lock.release()
            time.sleep(1800)

    def tick(self):
        from main import models
        models.add_data()

def quit(signum, frame):
    print('You choose to stop me.')
    sys.exit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    l = Loop(lock)
    l.setDaemon(True)
    l.start()
    manager.run()
