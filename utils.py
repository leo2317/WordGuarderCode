import random
from collections import UserList
from typing import List

import pygame


with open("./words.txt", 'r') as f:
    _WORDS = f.read().splitlines()

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
    _ID_TO_KEY = {
        pygame.K_BACKSPACE: "backspace",
        pygame.K_a: 'a',
        pygame.K_b: 'b',
        pygame.K_c: 'c',
        pygame.K_d: 'd',
        pygame.K_e: 'e',
        pygame.K_f: 'f',
        pygame.K_g: 'g',
        pygame.K_h: 'h',
        pygame.K_i: 'i',
        pygame.K_j: 'j',
        pygame.K_k: 'k',
        pygame.K_l: 'l',
        pygame.K_m: 'm',
        pygame.K_n: 'n',
        pygame.K_o: 'o',
        pygame.K_p: 'p',
        pygame.K_q: 'q',
        pygame.K_r: 'r',
        pygame.K_s: 's',
        pygame.K_t: 't',
        pygame.K_u: 'u',
        pygame.K_v: 'v',
        pygame.K_w: 'w',
        pygame.K_x: 'x',
        pygame.K_y: 'y',
        pygame.K_z: 'z',
    }

    KEY_BACKSPACE = "backspace"

    @classmethod
    def read_key(cls, event):
        if event.type == pygame.KEYDOWN:
            if event.unicode.isalnum():
                return event.unicode
            elif event.key == pygame.K_BACKSPACE:
                return cls.KEY_BACKSPACE
        return None

def get_word():
    return random.choice(_WORDS)