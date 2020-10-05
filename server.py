import flask

from controller_test import Controller

app = flask.Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

controller = Controller()

@app.route('/accounts', methods = ['GET'])
def get_accounts():
    return flask.jsonify(controller.get_account_info())

app.run()