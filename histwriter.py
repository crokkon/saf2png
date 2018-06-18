#!/usr/bin/python
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


class HistWriter(object):

    def __init__(self, hist):
        """ load histogram data for plotting

            :param dict hist: histogram data as created by the SAFReader class
        """
        if type(hist) != dict:
            raise ValueError("Invalid input data: hist needs to be a dict")
        required_keys = set(['xmax', 'xmin', 'values', 'errors',
                             'nbins', 'name'])
        if required_keys & set(hist.keys()) != required_keys:
            missing = required_keys - set(hist.keys())
            raise ValueError("Invalid input data: hist dict is missing the "
                             "following keys: %s" % (", ".join(missing)))
        self.hist = hist
        self.value_range = hist['xmax'] - hist['xmin']
        self.xticks = [hist['xmin'] + i * self.value_range /
                       hist['nbins'] for i in range(hist['nbins'])]

    def create_png(self, filename=None, figsize=None, title=None,
                   xlabel=None, ylabel=None, bar_args={}, grid=True,
                   optstat=True, show_yerrs=False):
        """ write the histgram to a PNG file and return the file name.

            :param str filename: (optional) target output file name. Defaults
                to "[histogram_name].png".
            :param tuple figsize: (optional) target PNG dimensions as tuple
                (width, heigh) in inch. Defaults to (12, 6).
            :param str title: (optional) set histogram title. Defaults to the
                name contained in the data if not set here.
            :param str xlabel: (optional) label for the x-axis. Default: None
            :param str ylabel: (optional) label for the y-axis. Default: None
            :param dict bar_args: (optional) arguments to ``har``, e.g. colors,
                styles, etc.
            :param bool grid: (optional) include a grid. Default: enabled
            :param bool opstat: (optional) include a text box with statistics.
                Default: enabled
            :param bool show_yerrs: (optional) Draw error bars in y direction.
                Default: False

        """
        figsize = figsize or (12, 6)
        title = title or self.hist['name']
        filename = filename or "%s.png" % (self.hist['name'])
        yerrs = None
        if show_yerrs:
            yerrs = self.hist['errors']

        width = self.value_range / self.hist['nbins']
        plt.figure(figsize=figsize)
        plt.bar(self.xticks, self.hist['values'][1:-1], width=width,
                yerr=yerrs, align="edge", **bar_args)
        if grid:
            plt.grid()
        if title is not None:
            plt.title(title)
        if xlabel is not None:
            plt.xlabel(xlabel)
        if ylabel is not None:
            plt.ylabel(ylabel)
        plt.savefig(filename)
        return filename
