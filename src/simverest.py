
#this is for pyinstaller to ensure dependencies are met
from twisted.web import server
from twisted.web import wsgi
from twisted.python.threadpool import ThreadPool
from twisted.internet import reactor

from options import get_executable_config
import daemon

if __name__ == "__main__":
    daemon.main(get_executable_config(), os.environ["_MEIPASS2"])
