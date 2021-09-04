from reportlab.platypus import Flowable

from coord import Coord
from lyric import Lyric
from neume import Neume
from neume_chunk import NeumeChunk
from neume_type import NeumeType
from syllable_type import SyllableType


class Syllable(Flowable):
    def __init__(self,
                 neume_chunk: NeumeChunk = None,
                 neume_chunk_pos: Coord = None,
                 lyric: Lyric = None,
                 lyric_pos: Coord = None,
                 ):
        super().__init__()
        self.neume_chunk: NeumeChunk = neume_chunk
        self.neume_chunk_pos: Coord = neume_chunk_pos if neume_chunk_pos is not None else Coord(0, 0)
        self.lyric: Lyric = lyric
        self.lyric_pos: Coord = lyric_pos if lyric_pos is not None else Coord(0, 0)
        self.width, self.height = self.calc_size()
        self.category: SyllableType = self.calc_category()

    def calc_size(self) -> [float, float]:
        width = max(getattr(self.neume_chunk, 'width', 0), getattr(self.lyric, 'width', 0))
        height = getattr(self.neume_chunk, 'height', 0)\
            + getattr(self.lyric, 'height', 0)
        return width, height

    def calc_category(self) -> SyllableType:
        """Calculate syllable category, based on contained neumechunk category.
        """
        if self.base_neume.category == NeumeType.martyria:
            return SyllableType.martyria
        else:
            return SyllableType.ordinary

    def draw(self, canvas):
        canvas.saveState()
        canvas.translate(self.neume_chunk_pos.x, self.neume_chunk_pos.y)
        pos_x: float = 0
        for i, neume in enumerate(self.neume_chunk):
            canvas.setFillColor(neume.color)
            canvas.setFont(neume.font_fullname, neume.font_size)
            if i > 0:
                pos_x += self.neume_chunk[i - 1].width
            canvas.drawString(pos_x, self.neume_chunk_pos.y, neume.char)
        canvas.restoreState()

        if self.lyric and self.lyric.text:
            canvas.setFillColor(self.lyric.color)
            canvas.setFont(self.lyric.font_family, self.lyric.font_size)
            canvas.drawString(self.lyric_pos.x, self.lyric_pos.y, self.lyric.text)

    def has_lyric_text(self) -> bool:
        return bool(self.lyric and self.lyric.text is not None)

    def has_connector_type(self) -> bool:
        return bool(self.lyric and self.lyric.connector is not None)

    def contains_lyric_text(self, lyric_text: str) -> bool:
        return bool(self.lyric and self.lyric.text == lyric_text)

    def contains_connector_type(self, connector_type: str) -> bool:
        return bool(self.lyric and self.lyric.connector == connector_type)

    @property
    def base_neume(self) -> Neume:
        """Returns the base neume of the neume chunk.
        """
        return self.neume_chunk.base_neume

    @property
    def lyric_text(self) -> str or None:
        """Returns the lyric offset of the base neume of a chunk.
        """
        if self.lyric:
            return self.lyric.text
        else:
            return None

    @property
    def lyric_offset(self) -> float:
        """Returns the lyric offset of the base neume of a chunk.
        """
        return self.neume_chunk.lyric_offset

    @property
    def takes_lyric(self) -> bool:
        """Returns whether syllable can take a lyric.
        """
        return self.neume_chunk.takes_lyric
