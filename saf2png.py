#!/usr/bin/python
import xml.etree.ElementTree as ET
import re
import matplotlib as mpl
mpl.use('Agg')  # required to work headless / without X
import matplotlib.pyplot as plt


class SAFReader(object):

    def __init__(self, filename):
        """ read and parse a SAF file

            :param str filename: filename
        """
        xml = self._read_xml(filename)
        self.histograms = []
        for histo in xml.findall('Histo'):
            desc = self._parse_element(histo.find('Description').text)
            stat = self._parse_element(histo.find('Statistics').text)
            data = self._parse_element(histo.find('Data').text)
            h = self._parse_statistics(stat)
            h.update(self._parse_description(desc))
            h.update(self._parse_data(data))
            self.histograms.append(h)

    def _read_xml(self, filename):
        """ read a SAF file and parse it as XML

        """
        # wrap with proper XML root tag
        xmlstr = '<?xml version="1.0"?><data>'
        with open(filename) as f:
            xmlstr += f.read()
        xmlstr += "</data>"
        try:
            return ET.fromstring(xmlstr)
        except Exception:
            ValueError("Failed to parse SAF file as XML")

    def _parse_element(self, element_text):
        """ parse the text content of a SAF element and return the result as a
        list of lists, one list entry per line.

        :param str element_text: element text as multi-line string

        """
        data = []
        for line in element_text.split('\n'):
            # strip empty/comment-only lines
            if re.search('^\s*(#.*|)$', line):
                continue
            # stip comments after data
            line = re.sub('\s*#.*$', '', line)
            data.append(line.split())
        return data

    def _parse_description(self, safdata):
        """ parse the <Description> tag of the SAF data

            :param list safdata: preprocessed description
        """
        if type(safdata) != list or len(safdata) != 3:
            raise ValueError("Cannot parse SAF Description")
        name = " ".join(safdata[0])[1:-1]  # strip quotes from name
        nbins = int(safdata[1][0])
        xmin = float(safdata[1][1])
        xmax = float(safdata[1][2])
        regions = [r[0] for r in safdata[2:]]
        return {'name': name, 'nbins': nbins, 'xmin': xmin, 'xmax':
                xmax, 'regions': regions}

    def _parse_statistics(self, safdata):
        """ parse the <Statistics> tag of the SAF data

            :param list safdata: preprocessed statistics
        """
        if type(safdata) != list or len(safdata) != 7:
            raise ValueError("Cannot parse SAF Statistics")
        nevents = int(safdata[0][0])
        nevents_neg = int(safdata[0][1])
        nevents_w = float(safdata[1][0])
        nevents_w_neg = float(safdata[1][1])
        nentries = int(safdata[2][0])
        nentries_neg = int(safdata[2][1])
        sumw = float(safdata[3][0])
        sumw_neg = float(safdata[3][1])
        sumww = float(safdata[4][0])
        sumww_neg = float(safdata[4][1])
        sumxw = float(safdata[5][0])
        sumxw_neg = float(safdata[5][1])
        sumxxw = float(safdata[6][0])
        sumxxw_neg = float(safdata[6][1])
        return {'nevents': nevents, 'nevents_neg': nevents_neg,
                'nevents_w': nevents_w, 'nevents_w_neg':
                nevents_w_neg, 'nentries': nentries, 'nentries_neg':
                nentries_neg, 'sum_w': sumw, 'sum_w_neg': sumw_neg,
                'sum_ww': sumww, 'sum_ww_neg': sumww_neg, 'sum_xw':
                sumxw, 'sum_xw_neg': sumxw_neg, 'sum_xxw': sumxxw,
                'sum_xxw_neg': sumxxw_neg}

    def _parse_data(self, safdata):
        """ parse the <Data> tag of the SAF data

            :param list safdata: preprocessed data
        """
        if type(safdata) != list:
            raise ValueError("Cannot parse SAF Data")
        values = []
        for entry in safdata:
            values.append(float(entry[0]) - float(entry[1]))
        return {'values': values}


class HistWriter(object):

    def __init__(self, hist, figsize=None, bar_args={}):
        """ load histogram data for plotting

            :param dict hist: histogram data as created by the SAFReader class
            :param tuple figsize: (optional) target PNG dimensions as tuple
                (width, heigh) in inch. Defaults to (12, 6).
            :param dict bar_args: (optional) arguments to ``bar``, e.g. colors,
                styles, etc.
        """
        if type(hist) != dict:
            raise ValueError("Invalid input data: hist needs to be a dict")
        required_keys = set(['xmax', 'xmin', 'values', 'nbins', 'name'])
        if required_keys & set(hist.keys()) != required_keys:
            missing = required_keys - set(hist.keys())
            raise ValueError("Invalid input data: hist dict is missing the "
                             "following keys: %s" % (", ".join(missing)))
        self.hist = hist
        self.value_range = hist['xmax'] - hist['xmin']
        self.xticks = [hist['xmin'] + i * self.value_range /
                       hist['nbins'] for i in range(hist['nbins'])]
        figsize = figsize or (12, 6)
        width = self.value_range / self.hist['nbins']

        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.bar = self.ax.bar(self.xticks, self.hist['values'][1:-1],
                               width=width, align="edge", **bar_args)


    def create_png(self, filename=None, title=None, xlabel=None,
                   ylabel=None, grid=True,
                   show_stats=True):
        """ write the histgram to a PNG file and return the file name.

            :param str filename: (optional) target output file name. Defaults
                to "[histogram_name].png".
            :param str title: (optional) set histogram title. Defaults to the
                name contained in the data if not set here.
            :param str xlabel: (optional) label for the x-axis. Default: None
            :param str ylabel: (optional) label for the y-axis. Default: None
            :param bool grid: (optional) include a grid. Default: True
            :param bool show_stats: (optional) include a text box with
                statistics. Default: True

        """
        title = title or self.hist['name']
        self.filename = filename or "%s.png" % (self.hist['name'])
        if grid:
            self.ax.grid()
        if title is not None:
            self.ax.set_title(title)
        if xlabel is not None:
            self.ax.set_xlabel(xlabel)
        if ylabel is not None:
            self.ax.set_ylabel(ylabel)
        if show_stats:
            props = dict(boxstyle='round', facecolor='white', alpha=0.5)
            text = r'$overflow=%e$' % (self.hist['values'][-1]) + "\n" + \
                   r'$underflow=%e$' % (self.hist['values'][0])
            self.ax.text(1.05, 1, text, transform=plt.gca().transAxes,
                         fontsize=10, verticalalignment='top',
                         horizontalalignment='left', bbox=props)
            text = "Positive weighted entries:\n" + \
                   r'$n_{evt}=%d$' % (self.hist['nevents']) + "\n" + \
                   r'$\sum{w_{evt}}=%e$' % (self.hist['nevents_w']) + "\n" + \
                   r'$n_{entr}=%d$' % (self.hist['nentries']) + "\n" + \
                   r'$\sum{w}=%e$' % (self.hist['sum_w']) + "\n" + \
                   r'$\sum{w^{2}}=%e$' % (self.hist['sum_ww']) + "\n" + \
                   r'$\sum{xw}=%e$' % (self.hist['sum_xw']) + "\n" + \
                   r'$\sum{x^{2}w}=%e$' % (self.hist['sum_xxw'])
            self.ax.text(1.05, 0.85, text,
                         transform=plt.gca().transAxes, fontsize=10,
                         verticalalignment='top',
                         horizontalalignment='left', bbox=props)
            text = "Negative weighted entries:\n" + \
                   r'$n_{evt}=%d$' % (self.hist['nevents_neg']) + "\n" + \
                   r'$\sum{w_{evt}}=%e$' % (self.hist['nevents_w_neg']) + "\n" + \
                   r'$n_{entr}=%d$' % (self.hist['nentries_neg']) + "\n" + \
                   r'$\sum{w}=%e$' % (self.hist['sum_w_neg']) + "\n" + \
                   r'$\sum{w^{2}}=%e$' % (self.hist['sum_ww_neg']) + "\n" + \
                   r'$\sum{xw}=%e$' % (self.hist['sum_xw_neg']) + "\n" + \
                   r'$\sum{x^{2}w}=%e$' % (self.hist['sum_xxw_neg'])
            self.ax.text(1.05, 0.4, text,
                           transform=plt.gca().transAxes, fontsize=10,
                           verticalalignment='top',
                           horizontalalignment='left', bbox=props)
            self.fig.subplots_adjust(right=0.75)

        self.fig.savefig(filename)
        return self.filename


if __name__ == "__main__":
    import argparse
    import os
    parser = argparse.ArgumentParser()
    helptext = 'One or more SAF files. Separate multiple files with spaces'
    parser.add_argument('-f', '--files', type=str, nargs="+",
                        help=helptext, required=True)
    args = parser.parse_args()

    # iterate over all SAF files provided as command line arguments
    for saffile in args.files:
        # read and parse SAF file
        reader = SAFReader(saffile)
        # iterate over all histograms contained in the SAF file
        for hist in reader.histograms:
            # assemble output file name
            basename, ext = os.path.splitext(saffile)
            outfile = "%s.%s.png" % (basename, hist['name'])
            writer = HistWriter(hist)
            # write histogram to file with default settings
            writer.create_png(filename=outfile)

            # alternatively: customize the histogram
            # writer.ax.set_title("my title")
            # writer.ax.set_ylim([0,1])
            # writer.fig.savefig(outfile)
            print("Created %s" % (outfile))
