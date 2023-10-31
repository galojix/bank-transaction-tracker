"""Module that generates report graphs."""
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import DatetimeTickFormatter, NumeralTickFormatter
from bokeh.palettes import Category20, Category20b, Category10
from flask import session
from flask_login import current_user
from .database import db
from .database import Transaction, Category
from sqlalchemy.sql import func
from collections import OrderedDict
from numpy import pi
import datetime


def graph(report_name):
    """Report graph."""
    start_date = session.get("start_date", None)
    end_date = session.get("end_date", None)
    account_name = session.get("account_name", None)
    if report_name == "Expenses by Category":
        graph = ExpensesByCategoryPieGraph(start_date, end_date)
    elif report_name == "Income by Category":
        graph = IncomeByCategoryPieGraph(start_date, end_date)
    elif report_name == "Cash Flow":
        graph = CashFlowLineGraph(start_date, end_date)
    elif report_name == "Account Balances":
        graph = AccountBalancesLineGraph(start_date, end_date, account_name)
    return graph.get_html()


class PieGraph:
    """Pie graph."""

    def __init__(self, start_date=None, end_date=None):
        """Initialise."""
        self.data = []
        if start_date is None:
            self.start_date = datetime.datetime(year=1, month=1, day=1)
        else:
            self.start_date = start_date
        self.end_date = (
            datetime.datetime.now() if end_date is None else end_date
        )

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
        running_totals = [amounts[0], amounts[1]]
        for num, value in enumerate(amounts):
            if num in [0, 1]:
                continue
            running_totals.append(sum(amounts[0 : num + 1]))
        start_angles = [2 * pi * value for value in running_totals[:-1]]
        end_angles = [2 * pi * value for value in running_totals[1:]]
        num_colors = len(labels)
        colors = (Category20[20] + Category20b[20]) * int(num_colors / 20 + 1)
        pie_chart = figure(
            x_range=(-1, 1),
            y_range=(-1, 1),
            toolbar_location="right",
            tools="wheel_zoom,save, reset",
        )
        pie_chart.axis.visible = False
        pie_chart.grid.visible = False
        pie_chart.outline_line_color = None
        pie_chart.sizing_mode = "scale_width"
        pie_chart.toolbar_location = "below"
        pie_chart.toolbar.active_drag = None
        pie_chart.toolbar.logo = None

        raw_data = []

        for num, label in enumerate(labels):
            percent = " " + str(round(amounts[num + 1] * 100, 1)) + "%"
            legend = label + percent
            if num <= 10:
                pie_chart.wedge(
                    x=0,
                    y=0,
                    radius=0.9,
                    start_angle=start_angles[num],
                    end_angle=end_angles[num],
                    color=colors[num],
                    legend_label=legend,
                )
            else:
                pie_chart.wedge(
                    x=0,
                    y=0,
                    radius=0.9,
                    start_angle=start_angles[num],
                    end_angle=end_angles[num],
                    color=colors[num],
                )
            raw_data.append((label, percent))

        pie_chart.legend.label_text_font_size = "10pt"
        pie_chart.legend.location = "bottom_left"
        pie_chart.legend.background_fill_alpha = 0.3
        pie_chart.legend.glyph_height = 15
        pie_chart.legend.glyph_width = 15
        pie_chart.legend.label_height = 15

        script, div = components(pie_chart)
        return script, div, raw_data


class ExpensesByCategoryPieGraph(PieGraph):
    """Expenses by category pie graph."""

    def __init__(self, start_date, end_date):
        """Perform database query."""
        super().__init__(start_date, end_date)
        print(self.start_date, self.end_date)
        self.data = (
            db.session.query(Category.catname, func.sum(Transaction.amount))
            .filter(Transaction.group_id == current_user.group().group_id)
            .filter(Transaction.catno == Category.catno)
            .filter(Category.cattype == "Expense")
            .filter(Transaction.date >= self.start_date)
            .filter(Transaction.date <= self.end_date)
            .group_by(Category.catname)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )


class IncomeByCategoryPieGraph(PieGraph):
    """Income by category pie graph."""

    def __init__(self, start_date=None, end_date=None):
        """Perform database query."""
        super().__init__(start_date, end_date)
        self.data = (
            db.session.query(Category.catname, func.sum(Transaction.amount))
            .filter(Transaction.group_id == current_user.group().group_id)
            .filter(Transaction.catno == Category.catno)
            .filter(Category.cattype == "Income")
            .filter(Transaction.date >= self.start_date)
            .filter(Transaction.date <= self.end_date)
            .group_by(Category.catname)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )


class LineGraph:
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
        self.end_date = (
            datetime.datetime.now() if end_date is None else end_date
        )
        if account_name is None:
            self.account_name = "All"

    def get_html(self):
        """Get HTML components."""
        plot = figure(
            x_axis_type="datetime",
            x_axis_label="Date",
            y_axis_label="Amount",
            toolbar_location="right",
            tools="pan,wheel_zoom,box_zoom, save, reset",
        )

        DATE_TIME_FORMAT = {"days": ["%d/%m/%y"], "months": ["%m/%Y"]}
        plot.xaxis.formatter = DatetimeTickFormatter(**DATE_TIME_FORMAT)
        plot.yaxis.formatter = NumeralTickFormatter(format="$0,0")

        if self.data:
            num_colors = len(self.data)
            colors = Category10[10] * int(num_colors / 10 + 1)
            for num, label in enumerate(self.data):
                dates = list(self.data[label].keys())
                amounts = list(self.data[label].values())
                plot.step(
                    dates,
                    amounts,
                    line_color=colors[num],
                    line_width=3,
                    mode="after",
                    legend_label=label,
                )
                plot.sizing_mode = "scale_width"

        plot.legend.click_policy = "hide"
        plot.legend.label_text_font_size = "8pt"
        plot.legend.location = "top_right"
        plot.legend.background_fill_alpha = 0.3
        plot.toolbar_location = "below"
        plot.toolbar.active_drag = None
        plot.toolbar.logo = None

        script, div = components(plot)
        return script, div


class AccountBalancesLineGraph(LineGraph):
    """Account balances line graph."""

    def __init__(self, start_date, end_date, account_name):
        """Perform database query and populate data structure."""
        super().__init__(start_date, end_date, account_name)

        accounts = []
        if account_name == "All":
            accounts = [
                account
                for account in current_user.group().accounts
                if account.accname != "Unknown"
            ]
        else:
            accounts = [
                account
                for account in current_user.group().accounts
                if account.accname == account_name
            ]

        for account in accounts:
            balance = 0
            start_balance = 0
            end_balance = 0
            transactions = account.transactions
            balance_data = OrderedDict()
            for transaction in transactions:
                if transaction.category.cattype in ["Expense", "Transfer Out"]:
                    balance -= transaction.amount / 100.0
                else:
                    balance += transaction.amount / 100.0
                if transaction.date < start_date:
                    start_balance = balance
                elif transaction.date <= end_date:
                    end_balance = balance
                    balance_data[transaction.date] = balance

            if not balance_data:
                end_balance = start_balance

            balance_data[start_date] = start_balance
            balance_data.move_to_end(start_date, last=False)
            now = datetime.datetime.now()
            if end_date > now:
                balance_data[now] = end_balance
            else:
                balance_data[end_date] = end_balance

            self.data[account.accname] = balance_data


class CashFlowLineGraph(LineGraph):
    """Cash flow line graph."""

    def __init__(self, start_date, end_date):
        """Perform database query and populate data structure."""
        super().__init__(start_date, end_date)

        transactions = current_user.group().transactions

        balance = 0
        start_balance = 0
        end_balance = 0

        cash_flow_data = OrderedDict()

        for transaction in transactions:
            if transaction.category.cattype in ["Expense", "Transfer Out"]:
                balance -= transaction.amount / 100.0
            else:
                balance += transaction.amount / 100.0
            if transaction.date < start_date:
                start_balance = balance
            elif transaction.date <= end_date:
                end_balance = balance
                cash_flow_data[transaction.date] = balance

        if not cash_flow_data:
            end_balance = start_balance

        cash_flow_data[start_date] = start_balance
        cash_flow_data.move_to_end(start_date, last=False)
        now = datetime.datetime.now()
        if end_date > now:
            cash_flow_data[now] = end_balance
        else:
            cash_flow_data[end_date] = end_balance

        self.data["Total Cash"] = cash_flow_data
