from typing import Tuple

from items import (
    RunningWord,
    Word,
)
from utils import (
    get_word,
    Queue,
)


class WordRunningLine:
    def __init__(self, pos: Tuple[int, int], line_boundry: int):
        self.pos = pos
        self.word_queue = Queue()

        self._LINE_BOUNDRY = line_boundry

        self._is_match = False
    
    @property
    def word_num(self):
        return len(self.word_queue)
    
    @property
    def is_match(self):
        match_flag = self._is_match
        self._is_match = False  # reset
        return match_flag
    
    @property
    def is_oob(self):
        first_word = self.word_queue.head

        if first_word is None:
            return False

        x, y = first_word.pos
        is_oob = x > self._LINE_BOUNDRY

        if is_oob:
            oob_word = self.word_queue.pop()
            # del oob_word

        return is_oob

    def _add_word(self, text):
        self.word_queue.append(RunningWord(text, self.pos))
    
    def _remove_word(self, idx):
        self.word_queue.delete(idx)
    
    def update(self, input_word):
        if input_word in self.word_queue:
            self._is_match = True
            self.word_queue.remove(input_word)

        word_queue_copy = list(self.word_queue)
        for word in word_queue_copy:
            word.update()

class WordRunningBoard:
    _LINE_GAP = 40

    def __init__(self, line_num: int, pos: Tuple[int, int], line_boundry: int):
        x, y = pos
        self.lines = [WordRunningLine((x, y + i*self._LINE_GAP), line_boundry) for i in range(line_num)]

        for line in self.lines:
            line._add_word(get_word())
    
    @property
    def is_match(self):
        return any(line.is_match for line in self.lines)

    def oob_count(self):
        return sum(line.is_oob for line in self.lines)
    
    def update(self, input_word):
        for line in self.lines:
            line.update(input_word)
