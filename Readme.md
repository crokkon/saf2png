## SAF2PNG

Plot MadAnalysis5 SAF histogram files as PNGs with matplotlib.

### Usage as standalone tool with default settings

```
usage: saf2png.py [-h] -f FILES [FILES ...]

optional arguments:
  -h, --help            show this help message and exit
  -f FILES [FILES ...], --files FILES [FILES ...]
                        One or more SAF files. Separate multiple files with
                        spaces
```

PNGs are written into the same directory as the SAF files are. The PNG output file names are based on the name in the SAF file name and the histogram names in the `<Description>` tags in the SAF file.

Example output:
![example_histos.ptj1.png](https://cdn.steemitimages.com/DQmZyPpStTbK7z6H5eSiS3XnfS1LAWpopPo2vS2YLQvHRoQ/example_histos.ptj1.png)


### Usage as library

The matplotlib `Figure`, `AxesSubplot` and `BarContainer` instances are available as `Histwriter.fig`, `HistWriter.ax` and `HistWriter.bar` for histogram customization:

```python
from saf2png import SAFReader, HistWriter
reader = SAFReader("example_histogram.saf")
for hist in reader.histograms:
    writer = HistWriter(hist, bar_args={'label':'data label'})
    writer.ax.set_title("my histogram title")
    writer.ax.set_xlabel("my xlabel")
    writer.ax.set_ylim([0, 1])
    writer.ax.grid()
    writer.ax.legend()
    writer.fig.savefig(hist['name'] + ".png")
```
