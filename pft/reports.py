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
    elif report_name == "Cash Flow":
        graph = CashFlowLineGraph()
    elif report_name == "Account Balances":
        graph = AccountBalancesLineGraph()
    return graph.get_html()


class Graph():
    """Report graph."""

    def __init__(self):
        """Initialise."""
        pass


class PieGraph(Graph):
    """Pie graph."""

    def __init__(self):
        """Initialise."""
        super().__init__()
        self.query_result = None

    def get_html(self):
        """Get HTML components."""
        if self.query_result:
            totals = []
            labels = []
            for row in self.query_result:
                labels.append(row[0])
                totals.append(row[1])
        else:
            labels = ["No Data"]
            totals = [100]
        data = pd.Series(totals, index=labels)
        pie_chart = Donut(data, responsive=True, logo=None)
        script, div = components(pie_chart)
        return script, div


class ExpensesByCategoryPieGraph(PieGraph):
    """Expenses by category pie graph."""

    def __init__(self):
        """Perform database query."""
        super().__init__()
        self.query_result = db.session.query(Category.catname,
                                             func.sum(Transaction.amount)).\
            filter(Transaction.id == current_user.id).\
            filter(Transaction.catno == Category.catno).\
            filter(Category.cattype == 'Expense').\
            group_by(Category.catname).\
            all()


class ExpensesByBusinessPieGraph(PieGraph):
    """Expenses by business pie graph."""

    def __init__(self):
        """Perform database query."""
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
    """Income by category pie graph."""

    def __init__(self):
        """Perform database query."""
        super().__init__()
        self.query_result = db.session.query(Category.catname,
                                             func.sum(Transaction.amount)).\
            filter(Transaction.id == current_user.id).\
            filter(Transaction.catno == Category.catno).\
            filter(Category.cattype == 'Income').\
            group_by(Category.catname).\
            all()


class IncomeByBusinessPieGraph(PieGraph):
    """Income by business pie graph."""

    def __init__(self):
        """Perform database query."""
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
    """Line graph."""

    def __init__(self):
        """Initialise."""
        super().__init__()
        self.query_result = None

    def get_html(self):
        """Get HTML components."""
        if self.query_result:
            dates = []
            amounts = []
            for row in self.query_result:
                dates.append(row[0])
                print(row[0])
                amounts.append(row[1]/100.0)
        else:
            dates = [1]
            amounts = [0]

        plot = figure(x_axis_type='datetime', x_axis_label='Date',
                      y_axis_label='Amount', logo=None)
        plot.line(dates, amounts, legend="First", line_color="green",
                  line_width=2)
        plot.sizing_mode = 'scale_width'
        script, div = components(plot)
        return script, div


class CashFlowLineGraph(LineGraph):
    """Cash flow line graph."""

    def __init__(self):
        """Perform database query."""
        super().__init__()
        self.query_result = db.session.query(Transaction.date,
                                             Transaction.amount).\
            filter(Transaction.id == current_user.id).\
            filter(Category.cattype == 'Expense').\
            order_by(Transaction.date).\
            all()


class AccountBalancesLineGraph(LineGraph):
    """Account balances line graph."""

    pass
