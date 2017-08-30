"""Module that generates report graphs."""
from bokeh.plotting import figure
from bokeh.embed import components
from bkcharts import Donut
import pandas as pd
from flask_login import current_user
from .database import db
from .database import Transaction, Category, Business
from sqlalchemy.sql import func


def graph(report_name):
    """Report graph."""
    if report_name == "Expenses by Category" or\
            report_name == "Expenses by Business" or\
            report_name == "Income by Category" or\
            report_name == "Income by Business":
        return pie_graph(report_name)
    if report_name == "Cash Flow" or report_name == "Account Balances":
        return line_graph(report_name)


def line_graph(report_name):
    """Line graph."""
    plot = figure(x_axis_label='Date', y_axis_label='Amount', logo=None)
    dates = [1, 2, 3, 4, 5, 6, 7]
    amounts = [8, 1, 2, 9, 1, 4, 4]
    plot.line(dates, amounts, legend="First", line_color="green", line_width=2)
    dates = [1, 2, 3, 4, 5]
    amounts = [1, 2, 4, 1, 6]
    plot.line(dates, amounts, legend="Second", line_color="blue", line_width=2)
    plot.sizing_mode = 'scale_width'
    script, div = components(plot)
    return script, div


def pie_graph(report_name):
    """Pie graph."""
    totals, labels = pie_data(report_name)
    data = pd.Series(totals, index=labels)
    pie_chart = Donut(data, responsive=True, logo=None)
    script, div = components(pie_chart)
    return script, div


def pie_data(report_name):
    """Calculate pie graph data."""
    data = []

    if report_name == "Expenses by Category":
        data = db.session.query(Category.catname,
                                func.sum(Transaction.amount)).\
            filter(Transaction.id == current_user.id).\
            filter(Transaction.catno == Category.catno).\
            filter(Category.cattype == 'Expense').\
            group_by(Category.catname).\
            all()
        if data:
            totals = []
            labels = []
            for label, total in data:
                totals.append(total)
                labels.append(label)
        else:
            totals = [100]
            labels = ["No Data"]

    if report_name == "Expenses by Business":
        data = db.session.query(Business.busname,
                                func.sum(Transaction.amount),
                                Category.cattype).\
            filter(Transaction.id == current_user.id).\
            filter(Transaction.busno == Business.busno).\
            filter(Transaction.catno == Category.catno).\
            filter(Category.cattype == 'Expense').\
            group_by(Business.busname).\
            all()
        if data:
            totals = []
            labels = []
            for label, total, cattype in data:
                totals.append(total)
                labels.append(label)
        else:
            totals = [100]
            labels = ["No Data"]

    if report_name == "Income by Category":
        data = db.session.query(Category.catname,
                                func.sum(Transaction.amount)).\
            filter(Transaction.id == current_user.id).\
            filter(Transaction.catno == Category.catno).\
            filter(Category.cattype == 'Income').\
            group_by(Category.catname).\
            all()
        if data:
            totals = []
            labels = []
            for label, total in data:
                totals.append(total)
                labels.append(label)
        else:
            totals = [100]
            labels = ["No Data"]

    if report_name == "Income by Business":
        data = db.session.query(Business.busname,
                                func.sum(Transaction.amount),
                                Category.cattype).\
            filter(Transaction.id == current_user.id).\
            filter(Transaction.busno == Business.busno).\
            filter(Transaction.catno == Category.catno).\
            filter(Category.cattype == 'Income').\
            group_by(Business.busname).\
            all()
        if data:
            totals = []
            labels = []
            for label, total, cattype in data:
                totals.append(total)
                labels.append(label)
        else:
            totals = [100]
            labels = ["No Data"]

    return totals, labels
