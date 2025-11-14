import json
import os


class ScoreSession:

    def __init__(self) -> None:
        pass

class Project:

    def __init__(
            self,
            metadata = None,
            scores = None
        ) -> None:

        self.metadata = {}
        self.scores = []

    def _metadata_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

    def add_score(self, score):
        if not isinstance(score, ScoreSession):
            raise TypeError('Passed argument is not of type score.')
        self.scores.append(score)

    def remove_score(self, score):
        i = self.scores.index(score)
        self.scores.pop(i)

    def move_score(self, score, move_by = 1):
        

