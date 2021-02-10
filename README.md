# Kassia

Kassia is a scoring program for creating music written in Byzantine notation. It takes an XML file (schema file to be released later), parses the neumes and lyrics, and generates a formatted PDF using [ReportLab](https://www.reportlab.com).

## Requirements

Python 3.7+

## Setup

1. Install Python 3.7
2. Make sure pip is installed by running ```which pip```
3. Install necessary packages by running ```pip install -r requirements.txt```
4. Re-create the sample score in /examples to make sure everything works properly by running ```python  kassia.py examples/sample.xml examples/sample.pdf```

Note: [pipenv](https://pipenv.pypa.io/en/latest) or [poetry](https://python-poetry.org/) is likely a better alternative to pip and requirements.txt.

## Running Kassia

```python kassia.py [input_xml_file] [output_pdf_file]```

The [examples](https://github.com/t-bullock/kassia/examples) folder has sample scores for you to experiment with. Input files must be in xml format, and output files must be in PDF format.

## Editing Scores

Scores are saved as xml files. Take a look at the contents of [sample.xml](examples/sample.xml).

## Fonts

Kassia can utilize true type fonts files to draw neumes. To add new neume fonts, create a folder with the font name, place TTF files in the folder, and create classes.yaml and glyphnames.yaml files. The wiki has more information on how the yaml files should be structured.

Some sample fonts are included for headings and lyrics (Alegreya, EB Garamond, and Gentium Plus). Kassia will scan the /fonts folder and use any TTF files found there.
