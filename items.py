from typing import Tuple, Mapping, Union

import pygame

from utils import PygameFunction


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

class Item(pygame.sprite.Sprite):
    _DISPLAY_SURF = None

    def __init__(self):
        super().__init__()
    
    @classmethod
    def set_display_serf(cls, display_surf):
        assert isinstance(display_surf, pygame.Surface), "Error: type error"
        cls._DISPLAY_SURF = display_surf
    
    @property
    def pos(self):
        raise NotImplementedError
    
    def build(self, obj, rec):
        assert self._DISPLAY_SURF is not None, "Error: please setting display serface before build item."
        self._DISPLAY_SURF.blit(obj, rec)

class Word(Item):
    _FONT_STYLE = 'freesansbold.ttf'
    _FONT_SIZE = 15
    _FONT_COLOR = WHITE

    def __init__(self, text: str, pos: Tuple[int, int], color: str=None, *args):
        super().__init__(*args)

        self._FONT = pygame.font.Font(self._FONT_STYLE, self._FONT_SIZE) 
        self.font_color = self._FONT_COLOR if color is None else color
        self.text = text
        self._create_word(pos)
    
    def __eq__(self, __value: str):
        return self.text.__eq__(__value)
    
    @property
    def pos(self):
        return self.word_rec.topleft
    
    def _set_pos(self, xy: Tuple[int, int]):
        self.word = self._FONT.render(self.text, True, self.font_color) 
        self.word_rec = self.word.get_rect()
        self.word_rec.topleft = xy
    
    def _create_word(self, pos: Tuple[int, int]):
        self._set_pos(pos)
        self.build(self.word, self.word_rec)
    
    def update(self, new_pos: Tuple[int, int]=None):
        if new_pos is None:
            new_pos = self.pos
        self._create_word(new_pos)

class RunningWord(Word):
    _SAFE_COLOR = GREEN
    _WARNING_COLOR = YELLOW
    _DENGEOUS_COLOR = RED
    _SAFE_BOUNDRY = 500
    _WARNING_BOUNDRY = 800

    _RUNNING_SPEED = 2

    def __init__(self, text: str, pos: Tuple[int, int], *args):
        super().__init__(text, pos, self._SAFE_COLOR, *args)
    
    def _color_update(self, x: int):
        if x > self._WARNING_BOUNDRY:
            self.font_color = self._DENGEOUS_COLOR
        elif x > self._SAFE_BOUNDRY:
            self.font_color = self._WARNING_COLOR

    def update(self):
        x, y = self.pos
        x += self._RUNNING_SPEED
        new_pos = (x, y)
        self._color_update(x)
        super().update(new_pos)

class UserInputDisplay(Word):
    def __init__(self, pos: Tuple[int, int], *args):
        super().__init__("", pos, *args)
    
    def _add_key(self, key: str):
        assert isinstance(key, str)
        self.text += key
    
    def _pop(self):
        self.text = self.text[:-1]
    
    def read(self, key: str):
        if key == PygameFunction.KEY_BACKSPACE:
            self._pop()
        elif key is not None:
            self._add_key(key)

    def update(self, match: bool):
        super().update()
        if match:
            self.clear()

    def clear(self):
        self.text = ""

class GameInfo(Word):
    def __init__(self, pos: Tuple[int], *args):
        super().__init__("", pos, *args)
    
    @classmethod
    def info_format(cls, k: str, v: Union[int, float]):
        if isinstance(v, float):
            return f"{k}: {v:.2f}"
        return f"{k}: {v}"
    
    def update(self, info_table: Mapping):
        self.text = ', '.join(GameInfo.info_format(*pair) for pair in info_table.items())
        super().update()
    