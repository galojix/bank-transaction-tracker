"""Module that generates report graphs."""
from bokeh.plotting import figure
from bokeh.embed import components


def graph(report_name):
    """Demo graph."""
    plot = figure(title=report_name, x_axis_label='Date',
                  y_axis_label='Amount')
    plot.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=2)
    script, div = components(plot)
    return script, div
