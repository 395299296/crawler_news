from flask_script import Manager, Server
from main import app
import threading
import os, sys, time
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
lock = threading.Condition()

manager = Manager(app.app)

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger = True,
    use_reloader = True,
    host = '0.0.0.0',
    port = 8080)
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
        app.tick()


if __name__ == "__main__":
    l = Loop(lock)
    l.start()
    manager.run()
