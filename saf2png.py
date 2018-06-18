#!/usr/bin/python
import argparse
from safreader import SAFReader
from histwriter import HistWriter

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
        # write histogram to file
        writer = HistWriter(hist)
        filename = writer.create_png()
        print("%s: Created %s" % (saffile, filename))
