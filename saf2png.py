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
        nevents_err = int(safdata[0][1])
        nevents_w = float(safdata[1][0])
        nevents_w_err = float(safdata[1][1])
        nentries = int(safdata[2][0])
        nentries_err = int(safdata[2][1])
        sumw = float(safdata[3][0])
        sumw_err = float(safdata[3][1])
        sumww = float(safdata[4][0])
        sumww_err = float(safdata[4][1])
        sumxw = float(safdata[5][0])
        sumxw_err = float(safdata[5][1])
        sumxxw = float(safdata[6][0])
        sumxxw_err = float(safdata[6][1])
        return {'nevents': nevents, 'nevents_err': nevents_err,
                'nevents_w': nevents_w, 'nevents_w_err':
                nevents_w_err, 'nentries': nentries, 'nentries_err':
                nentries_err, 'sum_w': sumw, 'sum_w_err': sumw_err,
                'sum_ww': sumww, 'sum_ww_err': sumww_err, 'sum_xw':
                sumxw, 'sum_xw_err': sumxw_err, 'sum_xxw': sumxxw,
                'sum_xxw_err': sumxxw_err}

    def _parse_data(self, safdata):
        """ parse the <Data> tag of the SAF data

            :param list safdata: preprocessed data
        """
        if type(safdata) != list:
            raise ValueError("Cannot parse SAF Data")
        values = []
        errors = []
        for entry in safdata:
            values.append(float(entry[0]))
            errors.append(float(entry[1]))
        return {'values': values, 'errors': errors}


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
                   show_stats=True, show_yerrs=True):
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
            :param bool show_stats: (optional) include a text box with
                statistics. Default: True
            :param bool show_yerrs: (optional) Draw error bars in y direction.
                Default: True

        """
        figsize = figsize or (12, 6)
        title = title or self.hist['name']
        filename = filename or "%s.png" % (self.hist['name'])
        yerrs = None
        if show_yerrs:
            yerrs = self.hist['errors'][1:-1]

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
        if show_stats:
            textstr = r'$n_{events}=%d$' % (self.hist['nevents']) + "\n" + \
                      r'$\frac{\sum{w}}{n_{events}}=%e \pm %e$' % \
                      (self.hist['nevents_w'], self.hist['nevents_w_err']) + \
                      "\n" + "$n_{entries}=%d$\n" % (self.hist['nentries']) + \
                      r'$\frac{\sum{w}}{n_{entries}}=%e \pm %e$' % \
                      (self.hist['sum_w'], self.hist['sum_w_err']) + "\n" + \
                      r'$\frac{\sum{w^{2}}}{n_{entries}}=%e \pm %e$' % \
                      (self.hist['sum_ww'], self.hist['sum_ww_err']) + "\n" + \
                      r'$\frac{\sum{xw}}{n_{entries}}=%e \pm %e$' % \
                      (self.hist['sum_xw'], self.hist['sum_xw_err']) + "\n" + \
                      r'$\frac{\sum{x^{2}w}}{n_{entries}}=%e \pm %e$' % \
                      (self.hist['sum_xxw'], self.hist['sum_xxw_err'])
            props = dict(boxstyle='round', facecolor='white',
                         alpha=0.5)
            plt.gca().text(0.65, 0.99, textstr,
                           transform=plt.gca().transAxes, fontsize=10,
                           verticalalignment='top',
                           horizontalalignment='left', bbox=props)

        plt.savefig(filename)
        return filename


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
            # write histogram to file
            writer = HistWriter(hist)
            writer.create_png(filename=outfile)
            print("Created %s" % (outfile))
