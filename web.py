from flask import Flask, render_template
from database_setup import User, Transaction, session

app = Flask(__name__)


@app.route('/')
@app.route('/transactions')
def transactions_page():
    transactions = session.query(Transaction).all()
    return render_template('transactions.xhtml',transactions=transactions)

@app.route('/businesses')
def businesses_page():
    businesses = session.query(Business).all()
    return render_template('businesses.xhtml',businesses=businesses)

@app.route('/categories')
def categiries_page():
    categories = session.query(Category).all()
    return render_template('categories.xhtml',categories=categories)





if __name__ == '__main__':
    app.debug = True
    app.run(port=5000)
