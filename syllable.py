from neume_type import NeumeType
from typing import Tuple

from reportlab.platypus import Flowable

from lyric import Lyric
from neume import Neume
from neume_chunk import NeumeChunk
from syllable_type import SyllableType


class Syllable(Flowable):
    def __init__(self,
                 neume_chunk: NeumeChunk = None,
                 neume_chunk_pos: Tuple[float, float] = None,
                 lyric: Lyric = None,
                 lyric_pos: Tuple[float, float] = None,
                 # fthora: Fthora = None,
                 # fthora_pos: Tuple = [float, float]
                 ):
        super().__init__()
        self.neume_chunk = neume_chunk  # A list of neumes, one base neume and some zero width supporting characters
        self.neume_chunk_pos = neume_chunk_pos if neume_chunk_pos is not None else [0, 0]
        self.lyric: Lyric = lyric
        self.lyric_pos = lyric_pos if lyric_pos is not None else [0, 0]
        # self.fthora = fthora
        # self.fthora_pos = fthora_pos if fthora_pos is not None else [0, 0]
        self.set_size()
        self.category: SyllableType = self.calc_category()

    def set_size(self):
        self.width = max(getattr(self.neume_chunk, 'width', 0), getattr(self.lyric, 'width', 0))
        self.height = getattr(self.neume_chunk, 'height', 0)\
            + getattr(self.lyric, 'height', 0)

    def calc_category(self) -> SyllableType:
        """Calculate syllable category, based on contained neumechunk category.
        """
        if self.base_neume.category == NeumeType.martyria:
            return SyllableType.martyria
        else:
            return SyllableType.ordinary

    def draw(self, canvas):
        canvas.saveState()
        canvas.translate(self.neume_chunk_pos[0], self.neume_chunk_pos[1])
        pos_x: float = 0
        for i, neume in enumerate(self.neume_chunk):
            canvas.setFillColor(neume.color)
            canvas.setFont(neume.font_fullname, neume.font_size)
            if i > 0:
                pos_x += self.neume_chunk[i - 1].width
            canvas.drawString(pos_x, self.neume_chunk_pos[1], neume.char)
        canvas.restoreState()

        if self.lyric and self.lyric.text:
            canvas.setFillColor(self.lyric.color)
            canvas.setFont(self.lyric.font_family, self.lyric.font_size)
            canvas.drawString(self.lyric_pos[0], self.lyric_pos[1], self.lyric.text)

    def has_lyric_text(self) -> bool:
        return bool(self.lyric and self.lyric.text is not None)

    def has_connector_type(self) -> bool:
        return bool(self.lyric and self.lyric.connector is not None)

    def contains_lyric_text(self, text: str) -> bool:
        return bool(self.lyric and self.lyric.text == text)

    def contains_connector_type(self, text: str) -> bool:
        return bool(self.lyric and self.lyric.connector == text)

    @property
    def base_neume(self) -> Neume:
        """Returns the base neume of a chunk.
        """
        return self.neume_chunk.base_neume

    @property
    def lyric_text(self) -> float:
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
