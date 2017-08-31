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
    if report_name == "Expenses by Category":
        graph = ExpensesByCategoryPieGraph()
    elif report_name == "Expenses by Business":
        graph = ExpensesByBusinessPieGraph()
    elif report_name == "Income by Category":
        graph = IncomeByCategoryPieGraph()
    elif report_name == "Income by Business":
        graph = IncomeByBusinessPieGraph()
    # elif report_name == "Cash Flow":
    #     graph = CashFlowLineGraph()
    # elif report_name == "Account Balances":
    #     graph = AccountBalancesLineGraph()
    return graph.get_html()


class Graph():
    def __init__(self):
        self.query_result = None


class PieGraph(Graph):
    def __init__(self):
        super().__init__()

    def get_html(self):
        """Get HTML components."""
        if self.query_result:
            totals = []
            labels = []
            for row in self.query_result:
                totals.append(row[1])
                labels.append(row[0])
        else:
            totals = [100]
            labels = ["No Data"]
        data = pd.Series(totals, index=labels)
        pie_chart = Donut(data, responsive=True, logo=None)
        script, div = components(pie_chart)
        return script, div


class ExpensesByCategoryPieGraph(PieGraph):
    def __init__(self):
        super().__init__()
        self.query_result = db.session.query(Category.catname,
                                             func.sum(Transaction.amount)).\
            filter(Transaction.id == current_user.id).\
            filter(Transaction.catno == Category.catno).\
            filter(Category.cattype == 'Expense').\
            group_by(Category.catname).\
            all()


class ExpensesByBusinessPieGraph(PieGraph):
    def __init__(self):
        super().__init__()
        self.query_result = db.session.query(Business.busname,
                                             func.sum(Transaction.amount),
                                             Category.cattype).\
            filter(Transaction.id == current_user.id).\
            filter(Transaction.busno == Business.busno).\
            filter(Transaction.catno == Category.catno).\
            filter(Category.cattype == 'Expense').\
            group_by(Business.busname).\
            all()


class IncomeByCategoryPieGraph(PieGraph):
    def __init__(self):
        super().__init__()
        self.query_result = db.session.query(Category.catname,
                                             func.sum(Transaction.amount)).\
            filter(Transaction.id == current_user.id).\
            filter(Transaction.catno == Category.catno).\
            filter(Category.cattype == 'Income').\
            group_by(Category.catname).\
            all()


class IncomeByBusinessPieGraph(PieGraph):
    def __init__(self):
        super().__init__()
        self.query_result = db.session.query(Business.busname,
                                             func.sum(Transaction.amount),
                                             Category.cattype).\
            filter(Transaction.id == current_user.id).\
            filter(Transaction.busno == Business.busno).\
            filter(Transaction.catno == Category.catno).\
            filter(Category.cattype == 'Income').\
            group_by(Business.busname).\
            all()


class LineGraph(Graph):
    pass


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
