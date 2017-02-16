from flask import Flask, render_template
from database_setup import User, Transaction, session

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home_page():
    transactions = session.query(Transaction).all()
    return render_template('index.xhtml',transactions=transactions)

if __name__ == '__main__':
    app.debug = True
    app.run(port=5000)
