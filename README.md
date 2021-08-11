# Kassia

![build](https://img.shields.io/github/workflow/status/t-bullock/kassia/build)

Kassia is a scoring program for creating music written in Byzantine notation. It takes an XML file, parses the neumes and lyrics, and generates a formatted PDF using [ReportLab](https://www.reportlab.com).

## Requirements

Python 3.7+

## Setup

1. Install Python 3.7
2. Install [pipenv](https://pipenv.pypa.io/en/latest/)
3. Install necessary packages by running ```pipenv install```
4. Re-create the sample score in /examples to make sure everything works properly by running ```python kassia.py examples/sample.xml examples/sample.pdf```

## Running Kassia

```python kassia.py [input_xml_file] [output_pdf_file]```

The [examples](https://github.com/t-bullock/kassia/examples) folder has sample scores to experiment with. Input files must be XML files, using the syntax of the sample scores. Output files will be in PDF format.

## Editing Scores

Scores are saved as XML files (called BNML). Our [wiki page](https://github.com/t-bullock/kassia/wiki/Structure-of-BNML) explains the structure of a score.

## Fonts

Kassia can utilize true type fonts files to draw neumes. To add new neume fonts, create a folder with the font name, place TTF files in the folder, and create classes.yaml and glyphnames.yaml files. The [wiki](https://github.com/t-bullock/kassia/wiki/Adding-New-Neume-Fonts) has more information about how the YAML files should be structured.

Some sample fonts are included for headings and lyrics (Alegreya, EB Garamond, and Gentium Plus). Kassia will scan the /fonts folder and use any TTF files found there.

## Contributing

We need your help with documentation, testing, and submitting fixes and features!

Before submitting a pull request, make sure your changes pass all tests.

1. Install development dependencies by running ```pipenv install --dev```
2. Install [imagemagick](http://www.imagemagick.org) and [poppler](https://github.com/freedesktop/poppler)
3. Run tests:
  - ```pipenv run pytest```
  - ```pipenv run flake8```
  - ```pipenv run isort . --recursive --diff```
