"""Module that generates report graphs."""
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import DatetimeTickFormatter
from flask_login import current_user
from .database import db
from .database import Transaction, Category, Business, Account
from sqlalchemy.sql import func
from collections import OrderedDict


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


class PieGraph():
    """Pie graph."""

    def __init__(self):
        """Initialise."""
        super().__init__()
        self.data = []

    def get_html(self):
        """Get HTML components."""
        if self.data:
            totals = []
            labels = []
            for row in self.data:
                labels.append(row[0])
                totals.append(row[1])
        else:
            labels = ["No Data"]
            totals = [100]
        # data = pd.Series(totals, index=labels)
        # pie_chart = Donut(data, responsive=True, logo=None)
        # script, div = components(pie_chart)
        # return script, div


class ExpensesByCategoryPieGraph(PieGraph):
    """Expenses by category pie graph."""

    def __init__(self):
        """Perform database query."""
        super().__init__()
        self.data = db.session.query(Category.catname,
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
        self.data = db.session.query(Business.busname,
                                     func.sum(Transaction.amount)).\
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
        self.data = db.session.query(Category.catname,
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
        self.data = db.session.query(Business.busname,
                                     func.sum(Transaction.amount)).\
            filter(Transaction.id == current_user.id).\
            filter(Transaction.busno == Business.busno).\
            filter(Transaction.catno == Category.catno).\
            filter(Category.cattype == 'Income').\
            group_by(Business.busname).\
            all()


class LineGraph():
    """
    Line graph.

    Expects data to be { item1: [[x-values], [y-values]],
                         item2: [[x-values], [y-values]],
                         ...                              }
    """

    def __init__(self):
        """Initialise."""
        super().__init__()
        self.data = OrderedDict()

    def get_html(self):
        """Get HTML components."""
        plot = figure(x_axis_type='datetime', x_axis_label='Date',
                      y_axis_label='Amount', logo=None)

        DATE_TIME_FORMAT = {'days': ['%d/%m/%y'],
                            'months': ['%m/%Y']}
        plot.xaxis.formatter = DatetimeTickFormatter(**DATE_TIME_FORMAT)
        if self.data:
            for num, item in enumerate(self.data.keys()):
                dates = self.data[item][0]
                amounts = self.data[item][1]
                plot.line(dates, amounts, legend=item,
                          line_color=self.get_next_color(num), line_width=2)
        plot.sizing_mode = 'scale_width'
        script, div = components(plot)
        return script, div

    def get_next_color(self, num):
        """Generate the next color."""
        colors = {0: 'green', 1: 'blue', 2: 'orange'}
        num = num % 3
        return colors[num]


class AccountBalancesLineGraph(LineGraph):
    """Account balances line graph."""

    def __init__(self):
        """Perform database query and populate data structure."""
        super().__init__()
        accounts = db.session.query(Account.accname, Account.accno).\
            filter(Account.id == current_user.id).\
            order_by(Account.accname).\
            all()
        for accname, accno in accounts:
            balance = db.session.query(func.sum(Account.balance)).\
                filter(Account.id == current_user.id).\
                filter(Account.accname == accname).\
                first()[0] / 100.0
            transactions = db.session.query(Transaction.date,
                                            Transaction.amount,
                                            Category.cattype).\
                filter(Transaction.id == current_user.id).\
                filter(Transaction.accno == accno).\
                filter(Transaction.catno == Category.catno).\
                order_by(Transaction.date).\
                all()
            dates = []
            amounts = []
            for date, amount, cattype in transactions:
                if cattype == 'Expense':
                    balance -= amount / 100.0
                else:
                    balance += amount / 100.0
                dates.append(date)
                amounts.append(balance)
            self.data[accname] = [dates, amounts]


class CashFlowLineGraph(LineGraph):
    """Cash flow line graph."""

    def __init__(self):
        """Perform database query and populate data structure."""
        super().__init__()
        balance = db.session.query(func.sum(Account.balance)).\
            filter(Account.id == current_user.id).\
            first()[0] / 100.0
        transactions = db.session.query(Transaction.date,
                                        Transaction.amount,
                                        Category.cattype).\
            filter(Transaction.id == current_user.id).\
            filter(Transaction.catno == Category.catno).\
            order_by(Transaction.date).\
            all()
        dates = []
        amounts = []
        for date, amount, cattype in transactions:
            if cattype == 'Expense':
                balance -= amount / 100.0
            else:
                balance += amount / 100.0
            dates.append(date)
            amounts.append(balance)
        self.data['Net Total'] = [dates, amounts]
