import collections
from typing import List

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable

from coord import Coord
from lyric import Lyric
from syllable import Syllable


class SyllableLine(Flowable, collections.MutableSequence):
    """This class is a collection of Syllables.
    """
    def __init__(self, leading=0, syllable_spacing=0, *args):
        super().__init__(*args)
        self.list: List[Syllable] = list()
        self.extend(list(args))
        self.leading = leading
        self.syllableSpacing = syllable_spacing

    def wrap(self, *args):
        self.set_size()
        return self.width, self.height

    def draw(self, canvas: Canvas = None):
        """This class is overloaded from Flowable's draw function.

        Note: If a score gets split, platypus will treat the syllableLine
        as a Flowable and call this draw function without any parameters.

        param: canvas: The canvas to draw on. Canvas only gets received as an
        argument when this draw function is called by Score directly.
        """
        if not canvas:
            canvas = self.canv

        for syl in self.list:
            syl.draw(canvas)

        self.draw_dashes(canvas)
        self.draw_extenders(canvas)

    def draw_dashes(self, canvas):
        """Draw dashes connecting lyrics in a line of syllables.

        Loop through syllables in list. Draw dash whenever connector is found.
        Dashes after syllable come after lyric, while dashes on no lyric are
        centered under syllable.

        :param canvas: The canvas to draw extender on.
        """
        starting_lyric = None
        for syl in self.list:
            if syl.contains_connector_type('d'):
                if starting_lyric is None:
                    starting_lyric = syl.lyric

                # Start of word
                if syl.lyric.text is not None:
                    starting_lyric = syl.lyric
                    coord = self._get_initial_dash_position(syl)
                # Middle of word
                else:
                    coord = syl.lyric_pos
                    
                if syl.takes_lyric:
                    self._draw_dash(canvas,
                                    coord,
                                    starting_lyric.color,
                                    starting_lyric.font_family,
                                    starting_lyric.font_size)
            # End of word
            elif starting_lyric is not None:
                starting_lyric = None
    
    def draw_extenders(self, canvas):
        """Draw extenders connecting two or more sets of lyrics in a line.

        Loop through syllables in list. Begin extender if necessary.
        When encountering new lyric, end current extender and begin new one.
        Keep adding end of neume pos as end of extender.
        Draw extender if get to end of line.

        :param canvas: The canvas to draw extender on.
        """
        starting_lyric, x1, x2, y1, y2 = None, None, None, None, None
        for i, syl in enumerate(self.list):
            if syl.contains_connector_type('u'):
                # Begin extender if necessary
                if x1 is None:
                    starting_lyric = syl.lyric
                    y1, y2 = (syl.lyric_pos.y, syl.lyric_pos.y)

                    # If starting new line with extender, begin extender at front of neume
                    # Otherwise begin right after current lyric
                    if i == 0 and syl.lyric.text is None:
                        x1 = syl.neume_chunk_pos.x
                    else:
                        x1 = self._get_extender_start_position(syl)

                # If encounter new lyric, end current extender and start new one
                if syl.lyric.text is not None and x2:
                    # If syneches elafron, special case
                    if syl.lyric_offset:
                        x2 = self._get_special_extender_end_position(syl)
                    self._draw_extender(canvas, x1, y1, x2, y2, starting_lyric)
                    starting_lyric = syl.lyric
                    x1 = self._get_extender_start_position(syl)

                # Set extender end to ending position of neume
                x2 = self._get_extender_end_position(syl)

            # If no more extender connection, end and draw it
            elif x1 is not None and x2 is not None:
                if syl.base_neume.name == 'syne' and x1:
                    x2 = self._get_special_extender_end_position(syl)
                self._draw_extender(canvas, x1, y1, x2, y2, starting_lyric)
                x1, x2 = None, None
        
        # If extender goes to end of line
        if x1 is not None:
            self._draw_extender(canvas, x1, y1, x2, y2, starting_lyric)

    @staticmethod
    def _get_initial_dash_position(syl: Syllable) -> Coord:
        """Return dash position for the passed lyric.

        param: syl: Current syllable.
        returns: Dash position as Coordinate
        """      
        lyric_space_width = pdfmetrics.stringWidth(' ', syl.lyric.font_family, syl.lyric.font_size)
        return Coord(syl.lyric_pos.x + syl.lyric.width + (lyric_space_width*2), syl.lyric_pos.y)
    
    @staticmethod
    def _get_extender_start_position(syl: Syllable) -> float:
        """Return extender starting position (x position), after lyric.

        param: syl: Current syllable.
        """
        lyric_space_width = pdfmetrics.stringWidth(' ', syl.lyric.font_family, syl.lyric.font_size)
        return syl.lyric_pos.x + syl.lyric.width + lyric_space_width
    
    @staticmethod
    def _get_extender_end_position(syl: Syllable) -> float:
        """Return extender end position (x position), which is at end of neume (neume width).

        param: syl: Current syllable.
        """
        return syl.neume_chunk_pos.x + syl.width
    
    @staticmethod
    def _get_special_extender_end_position(syl: Syllable) -> float:
        """Return extender end position when special lyric offset.
        param: syl: Current syllable.
        """
        return syl.neume_chunk_pos.x + syl.lyric_offset
    
    @staticmethod
    def _draw_extender(canvas: Canvas, x1: float, y1: float, x2: float, y2: float, starting_lyric: Lyric):
        """Draw an underscore extender connecting two or more sets of lyrics.
        param: canvas: The canvas to draw extender to.
        param: x1: Start of extender, x coordinate.
        param: y1: Start of extender, y coordinate.
        param: x2: End of extender, x coordinate.
        param: y2: End of extender, y coordinate.
        param: starting_syllable: Syllable which starts the extender.
        """
        if x1 is not None and x2 is not None:
            canvas.setStrokeColor(starting_lyric.color)
            canvas.setFont(starting_lyric.font_family, starting_lyric.font_size)
            canvas.line(x1, y1, x2, y2)
    
    @staticmethod
    def _draw_dash(canvas: Canvas, dash_coord: Coord, color: str, font_family: str, font_size: int):
        """Draw a set of dashes connecting two or more sets of lyrics.
        param: canvas: The canvas to draw extender to.
        param: dash_coord: Position to draw dash at.
        param: color: Color of dash to draw.
        param: font_family: Font family of dash to draw.
        param: font_size: Font size of dash to draw.
        """
        canvas.setFillColor(color)
        canvas.setFont(font_family, font_size)
        canvas.drawCentredString(dash_coord.x, dash_coord.y, '-')

    def set_size(self):
        if self.list:
            width = (self.list[-1].neume_chunk_pos.x + self.list[-1].width) - self.list[0].neume_chunk_pos.x
            self.width = width
            max_syl_height = max(syl.height for syl in self.list)
            self.height = max(max_syl_height, self.leading)

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        self.set_size()
        del self.list[i]

    def __setitem__(self, i, v):
        self.set_size()
        self.list[i] = v

    def insert(self, i, v):
        self.set_size()
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)
