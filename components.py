from time import time
from typing import Tuple

import numpy as np

from items import RunningWord, Word, Tower
from utils import (
    get_word,
    Queue,
    InfoTable,
)

_STD_LINE_GAP = 40


class WordRunningLine:
    ID = 1

    def __init__(self, pos: Tuple[int, int], line_boundry: int):
        self.pos = pos
        self.word_queue = Queue()
        self.tower = None

        self._LINE_BOUNDRY = line_boundry

        self._is_match = False
        self.match_word_score = None
        self.oob_word_score = None
        self.char_num = 0

        xpos, ypos = self.pos
        self.line_id = Word(f"{self.ID:3d}", (self._LINE_BOUNDRY - 50, ypos))
        WordRunningLine.ID += 1
    
    @property
    def word_num(self):
        return len(self.word_queue)

    @property
    def first_word(self):
        return self.word_queue.head
    
    @property
    def is_match(self):
        match_flag = self._is_match
        self._is_match = False  # reset
        return match_flag
    
    def have_tower(self):
        return (
            self.tower is not None and
            not self.tower.is_expired()
        )
    
    def get_oob_word(self):
        if self.first_word is None:
            return None

        x, y = self.first_word.pos
        is_oob = x > self._LINE_BOUNDRY

        if not is_oob:
            return None

        return self.word_queue.pop(0)

    def add_word(self, text: str):
        self.word_queue.append(RunningWord(text, self.pos))
    
    def check_match(self, input_word: str):
        if input_word not in self.word_queue:
            return

        self._is_match = True
        idx = self.word_queue.index(input_word)
        self.match_word_score = self.word_queue[idx].score
        self.word_queue.remove(input_word)
        self.char_num += len(input_word)
    
    def update(self, input_word: str, *, is_pause: bool=False):
        self.match_word_score = 0
        self.oob_word_score = 0

        self.check_match(input_word) 
        
        oob_word = self.get_oob_word()
        if oob_word is not None:
            self.oob_word_score = oob_word.score

        for word in self.word_queue:
            word.update(is_pause=is_pause)

        if not self.have_tower():
            self.line_id.update()
            self.tower = None
    
    def clear(self):
        self.word_queue.clear()
        self.char_num = 0
        self.tower = None

class WordRunningBoard:
    _LINE_GAP = _STD_LINE_GAP

    _GENERATE_CYCLE = 2  # sec/word

    def __init__(self, line_num: int, pos: Tuple[int, int], line_boundry: int):
        x, y = pos
        self.lines = [WordRunningLine((x, y + i*self._LINE_GAP), line_boundry) for i in range(line_num)]
        self.total_match_word_score = None
        self.total_oob_word_score = None
        self.total_char_num = 0

        self.prev_generate_time = time()

        self.generate_record = [-1]*3  # only record recent 3 line's idx, used to avoiding word overlapping
    
    @property
    def first_words(self):
        return [line.first_word for line in self.lines]
    
    @property
    def is_match(self):
        return any(line.is_match for line in self.lines)
    
    def can_generate(self):
        return time() - self.prev_generate_time > self._GENERATE_CYCLE
    
    # handle word overlapping
    def get_random_idx(self):
        random_idx = np.random.randint(0, len(self.lines))

        if random_idx in self.generate_record:
            random_idx = self.get_random_idx()
        
        # update record like sliding window
        self.generate_record = [random_idx] + self.generate_record[:-1]
        
        return random_idx

    def generate_word(self):
        random_idx = self.get_random_idx()
        selected_line = self.lines[random_idx]
        generated_word = get_word()
        selected_line.add_word(generated_word)

        self.prev_generate_time = time()
    
    def update(self, input_word: str, *, is_pause: bool=False):
        if self.can_generate() and not is_pause:
            self.generate_word()

        self.total_match_word_score = 0
        self.total_oob_word_score = 0
        for line in self.lines:
            line.update(input_word, is_pause=is_pause)
            self.total_match_word_score += line.match_word_score
            self.total_oob_word_score += line.oob_word_score
        self.total_char_num = sum(line.char_num for line in self.lines)
    
    def clear(self):
        self.prev_generate_time = time()
        for line in self.lines:
            line.clear()

class TowerManager:
    _LINE_GAP = _STD_LINE_GAP

    _TOWER_COST = 10

    def __init__(self):
        self.towers = []
    
    @property
    def first_bullets(self):
        return [tower.first_bullet for tower in self.towers]
    
    def add_tower(self, ypos: int, info_table: InfoTable):
        assert ypos >= 0

        if info_table.score < self._TOWER_COST:
            print(f"toewr cost is {self._TOWER_COST}, your score {info_table.score} is too low")
            return None

        info_table.score -= self._TOWER_COST
        ypos = (ypos - 1)*self._LINE_GAP
        new_tower = Tower(ypos)
        self.towers.append(new_tower)

        return new_tower
        
    def update(self, *, is_pause: bool=False):
        for tower in self.towers:
            tower.update(is_pause=is_pause)

    def clear(self):
        for tower in self.towers:
            tower.bullet_queue.clear()
        self.towers.clear()
