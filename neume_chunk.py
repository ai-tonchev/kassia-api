import collections

from reportlab.pdfbase import pdfmetrics

from neume import Neume


class NeumeChunk(collections.MutableSequence):
    """A collection of Neumes, but with a calculated width and height.
    A chunk contains one base neume, and other neumes that are anchored to the base neume.
    """
    def __init__(self, *args):
        self.width: float = 0
        self.height: float = 0
        self.base_neume: Neume or None = None
        self.takes_lyric: bool = False  # whether some neume in the chunk could take a lyric
        self.list = []
        self.extend(list(args))

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        del self.list[i]
        self.set_width()

    def __setitem__(self, i, v):
        self.set_width()
        self.list[i] = v

    def insert(self, i, v):
        self.add_width(v)
        if self.height == 0:
            self.set_height(v)
        self.list.insert(i, v)

        self.assign_base_neume()

    def __str__(self):
        return str(self.list)

    def set_width(self):
        sum(pdfmetrics.stringWidth(neume.char, neume.font_fullname, neume.font_size) for neume in self.list if neume.standalone)

    def set_height(self, neume):
        ascent, descent = pdfmetrics.getAscentDescent(neume.font_fullname, neume.font_size)
        self.height = ascent - descent

    def add_width(self, neume):
        self.width += neume.width

    def assign_base_neume(self):
        """Set base neume in neume chunk.
        Special case for bareia, since it's the first neume, but is not a base neume.
        """
        if self.base_neume:
            return

        try:
            if self.list[0].keep_with_next and len(self.list) > 1:
                self.base_neume = self.list[1]
            else:
                self.base_neume = self.list[0]
        except IndexError:
            return

    @property
    def lyric_offset(self) -> float:
        """Get the position at the bottom of the page, taking into account margins.
        The bottom of the page is essentially 0 (plus any bottom margins).
        :return: Position at bottom of the page.
        """
        return self.base_neume.lyric_offset
