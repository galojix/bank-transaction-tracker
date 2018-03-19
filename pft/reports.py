"""Module that generates report graphs."""
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import DatetimeTickFormatter, NumeralTickFormatter, Legend
from bokeh.palettes import Category20, Category20b, Category10
from flask import session
from flask_login import current_user
from .database import db
from .database import Transaction, Category, Account
from sqlalchemy.sql import func
from collections import OrderedDict
from numpy import pi
import datetime


def graph(report_name):
    """Report graph."""
    start_date = session.get('start_date', None)
    end_date = session.get('end_date', None)
    account_name = session.get('account_name', None)
    if report_name == "Expenses by Category":
        graph = ExpensesByCategoryPieGraph(start_date, end_date)
    elif report_name == "Income by Category":
        graph = IncomeByCategoryPieGraph(start_date, end_date)
    elif report_name == "Cash Flow":
        graph = CashFlowLineGraph(start_date, end_date)
    elif report_name == "Account Balances":
        graph = AccountBalancesLineGraph(start_date, end_date, account_name)
    return graph.get_html()


class PieGraph():
    """Pie graph."""

    def __init__(self, start_date=None, end_date=None):
        """Initialise."""
        self.data = []
        if start_date is None:
            self.start_date = datetime.datetime(year=1, month=1, day=1)
        else:
            self.start_date = start_date
        if end_date is None:
            self.end_date = datetime.datetime.now()
        else:
            self.end_date = end_date

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
        colors = (Category20[20] + Category20b[20]) * int(num_colors / 20 + 1)
        pie_chart = figure(
            x_range=(-1, 1), y_range=(-1, 1), logo=None, plot_width=200,
            plot_height=200)
        pie_chart.axis.visible = False
        pie_chart.grid.visible = False
        pie_chart.outline_line_color = None
        pie_chart.sizing_mode = 'scale_width'

        for num, label in enumerate(labels):
            percent = ' ' + str(round(amounts[num+1] * 100, 1)) + '%'
            legend = label + percent
            if num <= 10:
                pie_chart.wedge(
                    x=0, y=0, radius=1, start_angle=start_angles[num],
                    end_angle=end_angles[num], color=colors[num],
                    legend=legend)
            else:
                pie_chart.wedge(
                    x=0, y=0, radius=1, start_angle=start_angles[num],
                    end_angle=end_angles[num], color=colors[num])

        pie_chart.legend.label_text_font_size = '10pt'
        pie_chart.legend.location = "bottom_left"
        pie_chart.legend.background_fill_alpha = 0.3

        script, div = components(pie_chart)
        return script, div


class ExpensesByCategoryPieGraph(PieGraph):
    """Expenses by category pie graph."""

    def __init__(self, start_date, end_date):
        """Perform database query."""
        super().__init__(start_date, end_date)
        print(self.start_date, self.end_date)
        self.data = (
            db.session.query(Category.catname, func.sum(Transaction.amount))
            .filter(Transaction.id == current_user.id)
            .filter(Transaction.catno == Category.catno)
            .filter(Category.cattype == 'Expense')
            .filter(Transaction.date >= self.start_date)
            .filter(Transaction.date <= self.end_date)
            .group_by(Category.catname)
            .order_by(func.sum(Transaction.amount).desc())
            .all())


class IncomeByCategoryPieGraph(PieGraph):
    """Income by category pie graph."""

    def __init__(self, start_date=None, end_date=None):
        """Perform database query."""
        super().__init__(start_date, end_date)
        self.data = (
            db.session.query(Category.catname, func.sum(Transaction.amount))
            .filter(Transaction.id == current_user.id)
            .filter(Transaction.catno == Category.catno)
            .filter(Category.cattype == 'Income')
            .filter(Transaction.date >= self.start_date)
            .filter(Transaction.date <= self.end_date)
            .group_by(Category.catname)
            .order_by(func.sum(Transaction.amount).desc())
            .all())


class LineGraph():
    """
    Line graph.

    Expects data to be { item1: [[x-values], [y-values]],
                         item2: [[x-values], [y-values]],
                         ...                              }
    """

    def __init__(self, start_date=None, end_date=None, account_name=None):
        """Initialise."""
        self.data = OrderedDict()
        if start_date is None:
            self.start_date = datetime.datetime(year=1, month=1, day=1)
        else:
            self.start_date = start_date
        if end_date is None:
            self.end_date = datetime.datetime.now()
        else:
            self.end_date = end_date
        if account_name is None:
            self.account_name = 'All'

    def get_html(self):
        """Get HTML components."""
        plot = figure(
            x_axis_type='datetime', x_axis_label='Date', y_axis_label='Amount',
            logo=None)

        DATE_TIME_FORMAT = {
            'days': ['%d/%m/%y'], 'months': ['%m/%Y']}
        plot.xaxis.formatter = DatetimeTickFormatter(**DATE_TIME_FORMAT)
        plot.yaxis.formatter = NumeralTickFormatter(format="$0,0")

        num_colors = len(self.data)
        colors = Category10[10] * int(num_colors / 10 + 1)
        items = []
        if self.data:
            for num, label in enumerate(self.data):
                dates = list(self.data[label].keys())
                amounts = list(self.data[label].values())
                line = plot.step(
                    dates, amounts, line_color=colors[num], line_width=3,
                    mode='after')
                items.append((label, [line]))
                plot.sizing_mode = 'scale_width'

        legend = Legend(items=items, location=(0, 0))

        plot.add_layout(legend, 'below')
        plot.legend.click_policy = 'hide'

        script, div = components(plot)
        return script, div


class AccountBalancesLineGraph(LineGraph):
    """Account balances line graph."""

    def __init__(self, start_date, end_date, account_name):
        """Perform database query and populate data structure."""
        super().__init__(start_date, end_date, account_name)

        if account_name == 'All':
            accounts = (
                db.session.query(Account.accname, Account.accno)
                .filter(Account.id == current_user.id)
                .filter(Account.accname != 'Unknown')
                .order_by(Account.accname)
                .all())
        else:
            accounts = (
                db.session.query(Account.accname, Account.accno)
                .filter(Account.id == current_user.id)
                .filter(Account.accname == account_name)
                .order_by(Account.accname)
                .all())
        for accname, accno in accounts:
            balance = 0
            start_balance = 0
            end_balance = 0
            transactions = (
                db.session.query(
                    Transaction.date, Transaction.amount, Category.cattype)
                .filter(Transaction.id == current_user.id)
                .filter(Transaction.accno == accno)
                .filter(Transaction.catno == Category.catno)
                .order_by(Transaction.date)
                .all())
            balance_data = OrderedDict()
            for date, amount, cattype in transactions:
                if cattype == 'Expense' or cattype == 'Transfer Out':
                    balance -= amount / 100.0
                else:
                    balance += amount / 100.0
                if date < start_date:
                    start_balance = balance
                elif date <= end_date:
                    end_balance = balance
                    balance_data[date] = balance

            balance_data[start_date] = start_balance
            balance_data.move_to_end(start_date, last=False)
            balance_data[end_date] = end_balance

            self.data[accname] = balance_data


class CashFlowLineGraph(LineGraph):
    """Cash flow line graph."""

    def __init__(self, start_date, end_date):
        """Perform database query and populate data structure."""
        super().__init__(start_date, end_date)

        transactions = current_user.transactions

        balance = 0
        start_balance = 0
        end_balance = 0

        cash_flow_data = OrderedDict()

        for transaction in transactions:
            if (
                transaction.category.cattype == 'Expense'
                or transaction.category.cattype == 'Transfer Out'
            ):
                balance -= transaction.amount / 100.0
            else:
                balance += transaction.amount / 100.0
            if transaction.date < start_date:
                start_balance = balance
            elif transaction.date <= end_date:
                end_balance = balance
                cash_flow_data[transaction.date] = balance

        cash_flow_data[start_date] = start_balance
        cash_flow_data.move_to_end(start_date, last=False)
        cash_flow_data[end_date] = end_balance

        self.data['Total Cash'] = cash_flow_data
