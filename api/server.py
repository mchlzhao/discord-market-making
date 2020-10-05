import flask

from controller_test import Controller

app = flask.Flask(__name__)

controller = Controller()

@app.route('/accounts', methods = ['GET'])
def get_accounts():
    return controller.get_account_info()

app.run()