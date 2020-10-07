from gevent import monkey
monkey.patch_all()

import os
from gevent.pywsgi import WSGIServer
from server import app

if __name__ == '__main__':
    http_server = WSGIServer(('192.168.20.30', 5000), app)
    http_server.serve_forever()