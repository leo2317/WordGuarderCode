from time import time
from typing import Tuple, Mapping, Union

import pygame

from commands import Commands
from utils import Colors, Fonts, PygameFunction, Queue


# String

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
    _FONT_STYLE = Fonts.std_font.value
    _FONT_SIZE = 20
    _FONT_COLOR = Colors.WHITE.value

    def __init__(self, text: str, pos: Tuple[int, int], color: str=None, *args):
        super().__init__(*args)

        self.font = pygame.font.Font(self._FONT_STYLE, self._FONT_SIZE) 
        self.font_color = self._FONT_COLOR if color is None else color
        self.text = text
        self._create_word(pos)
    
    def __eq__(self, __value: str):
        return self.text.__eq__(__value)
    
    @property
    def pos(self):
        return self.word_rec.topleft
    
    def _set_pos(self, xy: Tuple[int, int]):
        self.word = self.font.render(self.text, True, self.font_color) 
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
    _FONT_STYLE = Fonts.running_word_font.value
    _SAFE_COLOR = Colors.GREEN.value
    _WARNING_COLOR = Colors.YELLOW.value
    _DENGEOUS_COLOR = Colors.RED.value
    _SAFE_BOUNDRY = 500
    _WARNING_BOUNDRY = 800

    '''
    1. (5, 12)
        easy:       11.70%
        median:     84.80%
        hard:        4.40%
    2. (7, 12) - more reasonable
        easy:       39.97%
        median:     42.23%
        hard:       18.70%
    '''

    _EASY_THRESHOLD = 7  # 5
    _HARD_THRESHOLD = 12  # 12
    _RUNNING_SPEED = 2

    def __init__(self, text: str, pos: Tuple[int, int], *args):
        super().__init__(text, pos, self._SAFE_COLOR, *args)

        self.score = self.get_score()
    
    @property
    def body(self):
        return self.word_rec
    
    def _color_update(self, x: int):
        if x > self._WARNING_BOUNDRY:
            self.font_color = self._DENGEOUS_COLOR
        elif x > self._SAFE_BOUNDRY:
            self.font_color = self._WARNING_COLOR
    
    def get_score(self):
        word_len = len(self.text)

        if word_len < self._EASY_THRESHOLD:
            return 3
        elif word_len < self._HARD_THRESHOLD:
            return 5
        else:
            return 10

    def update(self):
        x, y = self.pos
        x += self._RUNNING_SPEED
        new_pos = (x, y)
        self._color_update(x)
        super().update(new_pos)

class UserInputDisplay(Word):
    _COMMAND_PREFIX = '/'

    _TYPING_MODE = 0
    _COMMAND_MODE = 1

    def __init__(self, pos: Tuple[int, int], *args):
        super().__init__("", pos, *args)

        self.inputbox = ""
        '''
        typing: (default)
        command: "/" prefix
        '''
        self.mode = UserInputDisplay._TYPING_MODE
    
    @property
    def mode(self):
        return self._mode
    
    @property
    def is_empty(self):
        return len(self.inputbox) == 0
    
    @mode.setter
    def mode(self, new_mode: int):
        self._mode = new_mode
        self.update_text()
    
    def _add_key(self, key: str):
        assert isinstance(key, str)
        self.inputbox += key
        self.update_text()
    
    def _pop(self):
        self.inputbox = self.inputbox[:-1]
        self.update_text()
    
    def read(self, key: str):
        if key == PygameFunction.KEY_BACKSPACE:
            self._pop()
            return

        if key == UserInputDisplay._COMMAND_PREFIX and self.mode == UserInputDisplay._COMMAND_MODE:
            self.mode = UserInputDisplay._TYPING_MODE
        elif key is not None:
            if self.is_empty and key == UserInputDisplay._COMMAND_PREFIX:
                self.mode = UserInputDisplay._COMMAND_MODE
            else:
                self._add_key(key)

    def update(self, match: bool):
        super().update()
        if match:
            self.clear()
        
        return self.inputbox

    def update_text(self):
        mode_name = "typing" if self.mode == UserInputDisplay._TYPING_MODE else "command"
        mode_str = f"[ {mode_name} ] "
        input_str = f"\"{self.inputbox}\""
        self.text = mode_str + input_str
    
    def clear(self):
        self.inputbox = ""
        self.update_text()

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

class Tower(Word):
    _GUARDING_LINE_POS = 950  # screen width: 1000
    _PADDING = 7
    _SYMBOL = "-=("
    _COOL_TIME = 2
    _LIFE_CYCLE = 20

    _FONT_STYLE = Fonts.sym_font.value
    _FONT_SIZE = 30
    _TOWER_COLOR = Colors.PURPLE.value

    def __init__(self, ypos):
        super().__init__(
            text=self._SYMBOL,
            pos=(self._GUARDING_LINE_POS, ypos + self._PADDING),
            color=self._TOWER_COLOR
        )

        self.bullet_queue = Queue()
        self.create_time = self.previous_fire_time = time()
    
    @property
    def first_bullet(self):
        return self.bullet_queue.head
    
    def is_expired(self):
        return time() - self.create_time > self._LIFE_CYCLE
    
    def can_fire(self):
        return (
            not self.is_expired() and
            time() - self.previous_fire_time > self._COOL_TIME
        )
    
    def fire(self):
        self.bullet_queue.append(Bullet(self.pos))
        self.previous_fire_time = time()
    
    def update(self):
        if not self.is_expired():
            super().update()

        if self.can_fire():
            self.fire()

        bullet_queue_copy = list(self.bullet_queue)
        for bullet in bullet_queue_copy:
            bullet.update()
            if bullet.is_oob():
                self.bullet_queue.pop(0)

class Bullet(Word):
    _GUARDING_LINE_POS = 980  # screen width: 1000
    _PADDING = 10
    _SYMBOL = '@'
    _SPEED = 3

    _FONT_STYLE = Fonts.sym_font.value
    _FONT_SIZE = 30
    _BULLET_COLOR = Colors.PURPLE.value

    def __init__(self, pos):
        super().__init__(
            text=self._SYMBOL,
            pos=pos,
            color=self._BULLET_COLOR
        )
    
    @property
    def body(self):
        return self.word_rec
    
    def is_oob(self):
        xpos, ypos = self.pos
        return xpos < 0
    
    def update(self):
        xpos, ypos = self.pos
        new_pos = (xpos - self._SPEED, ypos)
        super().update(new_pos)

# Widget

class Button(Item):
    _FONT_STYLE = Fonts.std_font.value
    _FONT_SIZE = 40
    
    WIDTH = 350
    HEIGHT = 100

    def __init__(self, x: int, y: int, text: str, text_color=Colors.BLACK.value, button_color=Colors.GRAY.value, hover_color=Colors.GREEN.value):
        x -= self.WIDTH/2
        y -= self.HEIGHT/2
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.font = pygame.font.Font(self._FONT_STYLE, self._FONT_SIZE)
        self.text = text
        self.text_color = text_color
        self.button_color = button_color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self):
        # Change button color if hovered
        color = self.hover_color if self.is_hovered else self.button_color

        # Draw button
        pygame.draw.rect(self._DISPLAY_SURF, color, self.rect)

        # Render text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.build(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Check if mouse is over the button
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if mouse click is on the button
            if self.is_hovered:
                return True
        return False
