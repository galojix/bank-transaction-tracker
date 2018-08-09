"""Module that runs application in development mode."""
from flask_script import Manager, Shell
import os
from pft import create_app
from pft.database import db, User, Category, Account, Transaction
from pft.demo_db import create_db
import unittest
from pft.classification import (
    collect_data, split_data, vectorize_data, feature_selection, naive_bayes,
    svm_predict, accuracy)


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    """Create a shell context so that can use REPL."""
    return dict(app=app, db=db, User=User, Category=Category, Account=Account,
                Transaction=Transaction)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def test():
    """Run the unit tests."""
    tests = unittest.TestLoader().discover('pft.tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def demo():
    """Create a demo database."""
    print("Creating a new demo database...")
    create_db()
    print("Done.")


@manager.command
def classify():
    """Test ML transaction categorization."""
    feature_data, label_data = collect_data()
    features_train, features_test, labels_train, labels_test = split_data(
        feature_data, label_data)
    features_train, features_test = vectorize_data(
        features_train, features_test)
    features_train, features_test = feature_selection(
        features_train, features_test, labels_train)
    predict = svm_predict(features_train, labels_train, features_test)
    predict = naive_bayes(features_train, labels_train, features_test)
    score = accuracy(labels_test, predict)
    print('Score: ', score)
    # print(features_train)
    # print()
    # print(features_test)
    # print()
    # print(labels_train)
    # print()
    # print(labels_test)


if __name__ == '__main__':
    manager.run()
