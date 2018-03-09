"""Module that generates report graphs."""
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import DatetimeTickFormatter, Legend
from bokeh.palettes import Plasma256, linear_palette
from flask_login import current_user
from .database import db
from .database import Transaction, Category, Account
from sqlalchemy.sql import func
from collections import OrderedDict
from numpy import pi


def graph(report_name):
    """Report graph."""
    if report_name == "Expenses by Category":
        graph = ExpensesByCategoryPieGraph()
    elif report_name == "Income by Category":
        graph = IncomeByCategoryPieGraph()
    elif report_name == "Cash Flow":
        graph = CashFlowLineGraph()
    elif report_name == "Account Balances":
        graph = AccountBalancesLineGraph()
    return graph.get_html()


class PieGraph():
    """Pie graph."""

    def __init__(self):
        """Initialise."""
        self.data = []

    def get_html(self):
        """Get HTML components."""
        if self.data:
            amounts = [0]
            labels = []
            for row in self.data:
                labels.append(row[0])
                amounts.append(row[1])
        else:
            labels = ["No Data"]
            amounts = [0, 100]
        total = sum(amounts)
        amounts = [value / total for value in amounts]
        running_totals = []
        running_totals.append(amounts[0])
        running_totals.append(amounts[1])
        for num, value in enumerate(amounts):
            if num == 0 or num == 1:
                continue
            running_totals.append(sum(amounts[0:num + 1]))
        start_angles = [2 * pi * value for value in running_totals[:-1]]
        end_angles = [2 * pi * value for value in running_totals[1:]]
        num_colors = len(labels)
        if num_colors <= 256:
            colors = linear_palette(Plasma256, num_colors)
        else:
            colors = linear_palette(Plasma256, 256) * int(num_colors / 256 + 1)
        pie_chart = figure(
            x_range=(-1, 1), y_range=(-1, 1), plot_width=800, plot_height=600,
            logo=None)
        pie_chart.xaxis.visible = False
        pie_chart.yaxis.visible = False

        legend_items = []
        for num, label in enumerate(labels):
            wedge = pie_chart.wedge(
                x=0, y=0, radius=0.75, start_angle=start_angles[num],
                end_angle=end_angles[num], color=colors[num])
            percent = ' ' + str(round(amounts[num+1] * 100, 1)) + '%'
            legend_items.append((label + percent, [wedge]))

        legend = Legend(items=legend_items, location=(0, 0))
        pie_chart.add_layout(legend, 'right')

        script, div = components(pie_chart)
        return script, div


class ExpensesByCategoryPieGraph(PieGraph):
    """Expenses by category pie graph."""

    def __init__(self):
        """Perform database query."""
        super().__init__()
        self.data = (
            db.session.query(Category.catname, func.sum(Transaction.amount))
            .filter(Transaction.id == current_user.id)
            .filter(Transaction.catno == Category.catno)
            .filter(Category.cattype == 'Expense')
            .group_by(Category.catname)
            .order_by(func.sum(Transaction.amount))
            .all())


class IncomeByCategoryPieGraph(PieGraph):
    """Income by category pie graph."""

    def __init__(self):
        """Perform database query."""
        super().__init__()
        self.data = (
            db.session.query(Category.catname, func.sum(Transaction.amount))
            .filter(Transaction.id == current_user.id)
            .filter(Transaction.catno == Category.catno)
            .filter(Category.cattype == 'Income')
            .group_by(Category.catname)
            .order_by(func.sum(Transaction.amount))
            .all())


class LineGraph():
    """
    Line graph.

    Expects data to be { item1: [[x-values], [y-values]],
                         item2: [[x-values], [y-values]],
                         ...                              }
    """

    def __init__(self):
        """Initialise."""
        self.data = OrderedDict()

    def get_html(self):
        """Get HTML components."""
        plot = figure(
            x_axis_type='datetime', x_axis_label='Date', y_axis_label='Amount',
            logo=None)

        DATE_TIME_FORMAT = {
            'days': ['%d/%m/%y'], 'months': ['%m/%Y']}
        plot.xaxis.formatter = DatetimeTickFormatter(**DATE_TIME_FORMAT)
        num_colors = len(self.data)
        if num_colors > 256:
            num_colors = 256
        colors = linear_palette(Plasma256, len(self.data))
        items = []
        if self.data:
            for num, label in enumerate(self.data.keys()):
                dates = self.data[label][0]
                amounts = self.data[label][1]
                num = num % num_colors  # Start colors again if all used
                line = plot.line(
                    dates, amounts, line_color=colors[num], line_width=2)
                items.append((label, [line]))
        plot.sizing_mode = 'scale_width'

        legend = Legend(items=items, location=(0, 0))

        plot.add_layout(legend, 'below')

        script, div = components(plot)
        return script, div


class AccountBalancesLineGraph(LineGraph):
    """Account balances line graph."""

    def __init__(self):
        """Perform database query and populate data structure."""
        super().__init__()
        accounts = (
            db.session.query(Account.accname, Account.accno)
            .filter(Account.id == current_user.id)
            .order_by(Account.accname)
            .all())
        for accname, accno in accounts:
            balance = (
                db.session.query(func.sum(Account.balance))
                .filter(Account.id == current_user.id)
                .filter(Account.accname == accname)
                .first()[0] / 100.0)
            transactions = (
                db.session.query(
                    Transaction.date, Transaction.amount, Category.cattype)
                .filter(Transaction.id == current_user.id)
                .filter(Transaction.accno == accno)
                .filter(Transaction.catno == Category.catno)
                .order_by(Transaction.date)
                .all())
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
        balance = (
            db.session.query(func.sum(Account.balance))
            .filter(Account.id == current_user.id)
            .first()[0] / 100.0)
        transactions = (
            db.session.query(
                Transaction.date, Transaction.amount, Category.cattype)
            .filter(Transaction.id == current_user.id)
            .filter(Transaction.catno == Category.catno)
            .order_by(Transaction.date)
            .all())
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
