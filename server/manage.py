from flask_script import Manager, Server
from app import app
import signal
import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

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

def quit(signum, frame):
    print('You choose to stop me.')
    sys.exit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    manager.run()
