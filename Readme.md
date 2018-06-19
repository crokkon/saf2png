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

PNGs are written into the current working directory. The file name is based on the name in the `<Description>` tag in the SAF file.