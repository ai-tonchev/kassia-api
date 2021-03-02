from reportlab.pdfbase import pdfmetrics

from connector import Connector


class Lyric:
    def __init__(self, text, font_family, font_size, color, top_margin, connector: str):
        self.text: str = text
        self.font_family: str = font_family
        self.font_size: int = font_size
        self.color: str = color
        self.top_margin: float = top_margin
        self.connector: Connector = connector
        self.recalc_width()
        self.calc_height()

    def recalc_width(self):
        if self.text:
            self.width = pdfmetrics.stringWidth(self.text, self.font_family, self.font_size)
        else:
            self.width = 0

    def calc_height(self):
        ascent, descent = pdfmetrics.getAscentDescent(self.font_family, self.font_size)
        self.height = ascent - descent
