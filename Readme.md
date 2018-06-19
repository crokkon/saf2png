## SAF2PNG

Plot MadAnalysis5 SAF histogram files as PNGs with matplotlib.

### Usage

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
![example_histos.ptj1.png](https://cdn.steemitimages.com/DQmT4dGoi3eesgPddvvwysYmCcPqBE14NR1g4M7e4FiW9Fz/example_histos.ptj1.png)
