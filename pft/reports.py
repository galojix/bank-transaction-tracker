"""Module that generates report graphs."""
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.charts import Donut
import pandas as pd


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
    plot = figure(x_axis_label='Date', y_axis_label='Amount')
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
    amounts = [10, 0.15, 4, 2]
    categories = ["category1", "category2", "category3", "category4"]
    data = pd.Series(amounts, index=categories)
    pie_chart = Donut(data, responsive=True)
    script, div = components(pie_chart)
    return script, div
