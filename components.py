from random import random
from time import time
from typing import Tuple

import numpy as np
import pygame

from items import RunningWord, Word, Tower
from utils import (
    get_word,
    Queue,
)

_STD_LINE_GAP = 40


class WordRunningLine:
    ID = 1

    def __init__(self, pos: Tuple[int, int], line_boundry: int):
        self.pos = pos
        self.word_queue = Queue()
        self.have_tower = False

        self._LINE_BOUNDRY = line_boundry

        self._is_match = False

        xpos, ypos = self.pos
        self.line_id = Word(f"{self.ID:2d}", (self._LINE_BOUNDRY - 20, ypos))
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

    def add_word(self, text):
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

        if not self.have_tower:
            self.line_id.update()
    
    def clear(self):
        self.word_queue.clear()
        self.have_tower = False

class WordRunningBoard:
    _LINE_GAP = _STD_LINE_GAP

    _GENERATE_CYCLE = 2  # sec/word

    def __init__(self, line_num: int, pos: Tuple[int, int], line_boundry: int):
        x, y = pos
        self.lines = [WordRunningLine((x, y + i*self._LINE_GAP), line_boundry) for i in range(line_num)]

        self.prev_generate_time = time()
    
    @property
    def first_words(self):
        return [line.first_word for line in self.lines]
    
    @property
    def is_match(self):
        return any(line.is_match for line in self.lines)

    def oob_count(self):
        return sum(line.is_oob for line in self.lines)
    
    def can_generate(self):
        return time() - self.prev_generate_time > self._GENERATE_CYCLE
    
    def generate_word(self):
        random_idx = np.random.randint(0, len(self.lines))
        selected_line = self.lines[random_idx]
        generated_word = get_word()
        selected_line.add_word(generated_word)

        self.prev_generate_time = time()
    
    def update(self, input_word):
        if self.can_generate():
            self.generate_word()

        for line in self.lines:
            line.update(input_word)
    
    def clear(self):
        for line in self.lines:
            line.clear()

class TowerManager:
    _LINE_GAP = _STD_LINE_GAP

    def __init__(self):
        self.towers = []
    
    @property
    def first_bullets(self):
        return [tower.first_bullet for tower in self.towers]
    
    def add_tower(self, ypos: int):
        assert ypos >= 0
        ypos = (ypos - 1)*self._LINE_GAP
        self.towers.append(Tower(ypos))
        
    def update(self):
        for tower in self.towers:
            tower.update()

    def clear(self):
        for tower in self.towers:
            tower.bullet_queue.clear()
        self.towers.clear()

