## SAF2PNG

Plot MadAnalysis5 SAF histogram files as PNGs with matplotlib.

### Usage / Features

The tool works with both python2 and python3.

#### As standalone tool with default settings
```
$ ./saf2png.py -h

usage: saf2png.py [-h] -f FILES [FILES ...] [-i] [-s]

optional arguments:
  -h, --help            show this help message and exit
  -f FILES [FILES ...], --files FILES [FILES ...]
                        One or more SAF files. Separate multiple files with
                        spaces
  -i, --interactive     Interactive mode: ask for titles and labels
  -s, --stats           Show text boxes with statistics information
```

Each SAF file can contain multiple histograms. The tool creates one PNG for each histogram in each SAF file provided as command line argument. The PNGs are written into the same directory as the SAF files are and contain both the SAF file name and the histogram name from the SAF `<Description>` tag in the PNG filename.

Call `saf2png.py` with one or more SAF file after the `-f/--files` parameter:

```
$ ./saf2png.py -f example_histos.saf example_histos2.saf
Created example_histos.ptj1.png
Created example_histos.etaj1.png
Created example_histos.ptg1.png
Created example_histos.etag1.png
Created example_histos2.ptj1.png
Created example_histos2.etaj1.png
Created example_histos2.ptg1.png
Created example_histos2.etag1 example.png
```

Sample output:

![example_histos.ptj1.png](https://cdn.steemitimages.com/DQmW8simpsfLruRzZyRgicYVydtMmYkKg6BJ2N4hPsJs1KA/example_histos.ptj1.png)

`-s/--stats` integrates text boxes with statistics information:

```
$ ./saf2png.py -f example_histos.saf --stats
```

Sample output:

![example_histos.ptj1.png](https://cdn.steemitimages.com/DQmZyPpStTbK7z6H5eSiS3XnfS1LAWpopPo2vS2YLQvHRoQ/example_histos.ptj1.png)

Axis labels are unset in this mode, since this information is not contained in the SAF files. The histogram name as contained in the `<Description>` tag in the SAF file is set as histogram title.


#### As standalone tool in interactive mode

An interactive mode via `-i/--interactive` enables to set titles and axis labels from user input at run time:

```
$ ./saf2png.py -f example_histos.saf -i
Histogram title for example_histos.saf.ptj1: My custom histogram title
X-axis label for example_histos.saf.ptj1: transverse momentum
Y-axis label for example_histos.saf.ptj1: a.u.
Created example_histos.ptj1.png
[...]
```

![example_histos.ptj1.png](https://cdn.steemitimages.com/DQmdEKwETkUeD899tcrXYU94uZkperZRBrBdrAXaTX9Xznu/example_histos.ptj1.png)


User input can also be provided in a TeX-like math mode:

```
$ ./saf2png.py -f example_histos.saf -i
Histogram title for example_histos.saf.ptj1: $p_{t}(j_{1})$
X-axis label for example_histos.saf.ptj1: transverse momentum $p_{t}$ (MeV)
Y-axis label for example_histos.saf.ptj1: a.u.
Created example_histos.ptj1.png
[...]
```

![example_histos.ptj1.png](https://cdn.steemitimages.com/DQmVHM3SJ816XHrahuuAUEg4rBYhwyxr89bjNwK2e3X8CdQ/example_histos.ptj1.png)


### Usage as a module in custom code

The matplotlib `Figure`, `AxesSubplot` and `BarContainer` instances are available as `Histwriter.fig`, `HistWriter.ax` and `HistWriter.bar` for histogram customization:

```python
from saf2png import SAFReader, HistWriter
reader = SAFReader("example_histogram.saf")
for hist in reader.histograms:
    writer = HistWriter(hist, bar_args={'label':'data label'})
    writer.ax.set_title("my histogram title")
    writer.ax.set_xlabel("my xlabel")
    writer.ax.set_ylim([0, 1])
    writer.ax.set_xscale("log")
    writer.ax.grid()
    writer.ax.legend()
    writer.fig.savefig(hist['name'] + ".png")
```

The common `matplotlib` methods can be used to customize the histogram to the user needs before writing the results to a file. Additionally, the `matplotlib` objects could be stored as pickled files for later processing/customization.
