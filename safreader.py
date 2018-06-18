#!/usr/bin/python
import xml.etree.ElementTree as ET
import re


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
        region = safdata[2][0]  # TODO: can there be more than one region?
        return {'name': name, 'nbins': nbins, 'xmin': xmin, 'xmax':
                xmax, 'region': region}

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
                nentries_err, 'sum_w': sumw, 'sumw_err': sumw_err,
                'sum_ww': sumww, 'sumww_err': sumww_err, 'sum_xw':
                sumxw, 'sumxw_err': sumxw_err, 'sum_xxw': sumxxw,
                'sumxxw_err': sumxxw_err}

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
