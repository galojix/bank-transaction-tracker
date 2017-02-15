from flask import Flask
from database_setup import User, session

app = Flask(__name__)


@app.route('/')
@app.route('/hello')
def HelloWorld():
    users = session.query(User)
    output = ''
    for user in users:
        output += user.username
        output += '</br>'
    return output

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
