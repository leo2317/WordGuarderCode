import random
import json
from collections import UserList
from enum import Enum
from typing import List, Mapping
from time import time
from datetime import datetime, timezone, timedelta

import pygame


with open("./words.txt", 'r') as f:
    _WORDS = f.read().splitlines()

GUIDE_CONTENT = '''/tower [position]:
    add tower
/pause:
    pause game
'''


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
    norm_word_font = "./fonts/word.ttf"
    std_font = "./fonts/std.ttf"
    sym_font = "./fonts/sym.ttf"

class InfoTable:
    _CHECKPOING_INTERVAL = 5

    def __init__(self):
        self.score = None
        self.wpm = None
        self._start_time = None

        self._previous_ckpt_time = time()
        self._history = {
            "score": [],
            "wpm": [],
        }
    
    @property
    def timer(self):
        return time() - self._start_time
    
    def reset(self):
        self.score = 0
        self.wpm = 0
        self._start_time = time()

        for v in self._history.values():
            v.clear()
    
    def checkpoint(self):
        if time() - self._previous_ckpt_time <= self._CHECKPOING_INTERVAL:
            return
        
        self._previous_ckpt_time = time()
        self._history["score"].append(self.score)
        self._history["wpm"].append(self.wpm)

    def save(self):
        file_name = get_date()
        with open(f"./history/{file_name}.json") as f:
            json.dump(self._history, f)


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


def time_format(t: float):
    m, s = t//60, t % 60
    return f"{m:02d}:{s:02d}"

def get_date():
    return datetime.now(timezone(timedelta(hours=+8))).strftime("%Y-%m-%d_%H-%M")

def get_word():
    return random.choice(_WORDS)


# visualize
def plot_history(history: Mapping, play_time: float):
    # import inner for speed up game loading
    import numpy as np
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    for i, (ax, (k, v)) in enumerate(zip(axes, history.items())):
        color = f"C{i}"
        x = [play_time/len(v)*i for i in range(len(v))]
        ax.plot(x, v, marker='o', color=color)
        ax.set_title(k.title() if i == 0 else k.upper())
        ax.set_xlabel("Time (s)")
        ax.grid(True)
    fig.suptitle("Performance")
    fig.canvas.manager.set_window_title("Visualizer")

    plt.show()
