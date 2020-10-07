import flask
from flask_cors import CORS

from controller_test import Controller

app = flask.Flask(__name__)
CORS(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

controller = Controller()

@app.route('/info', methods = ['GET'])
def get_accounts():
    return flask.jsonify(controller.get_info())

'''
context = ('server.crt', 'server.key')
app.run(host = '0.0.0.0', ssl_context = context)
'''

app.run(host = '0.0.0.0')
