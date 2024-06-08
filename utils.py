import random
from collections import UserList
from enum import Enum
from typing import List

import pygame


with open("./words.txt", 'r') as f:
    _WORDS = f.read().splitlines()

class Colors(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (200, 200, 200)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    PURPLE = (160, 32, 240)

class Fonts(Enum):
    running_word_font = "./fonts/word.ttf"
    std_font = "./fonts/std.ttf"
    sym_font = "./fonts/sym.ttf"

class Queue(UserList):
    @property
    def head(self):
        try:
            return self.data[0]
        except IndexError:
            return None
    
    @property
    def tail(self):
        try:
            return self.data[-1]
        except IndexError:
            return None

class PygameFunction:
    KEY_BACKSPACE = "backspace"
    KEY_RETURN = '\n'

    @classmethod
    def read_key(cls, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                return cls.KEY_BACKSPACE
            elif event.key == pygame.K_RETURN:
                return cls.KEY_RETURN
            else:
                return event.unicode
        return None


def get_word():
    return random.choice(_WORDS)
