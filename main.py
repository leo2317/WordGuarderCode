import sys

import pygame
from pygame.locals import QUIT

import items
from components import WordRunningBoard
from definitions import Pages
from items import (
    Button,
    Item,
    UserInputDisplay,
    GameInfo,
)
from utils import PygameFunction


class App:
    # pygame constants
    _BACKGROUND_COLOR = items.BLACK

    # app constants
    _SCORE_PER_WORD = 10

    def __init__(self, height, width, fps):
        # pygame setting
        self._running = False
        self._display_surf = None
        self._fps = fps
        self._frame_per_sec = None

        # app setting
        self.size = self.width, self.height = width, height
        self.page = Pages.home
        self.board = None
        self.user_input_display = None
        self.game_info = None

        self._info_table = {
            "score": 0,
        }
    
    def on_init(self):
        # pygame setting
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size)
        self._frame_per_sec = pygame.time.Clock()
        pygame.display.set_caption("Typing Game")

        # app setting
        self._running = True
        Item.set_display_serf(self._display_surf)

    def on_start(self):
        self.board = WordRunningBoard(10, (0, 10), self.width)
        self.user_input_display = UserInputDisplay((20, self.height - 30))
        self.game_info = GameInfo((500, self.height - 30))
    
    def on_event(self, event):
        if event.type == QUIT:
            self._running = False
            return

        if self.page == Pages.home:
            pass
        elif self.page == Pages.main:
            key = PygameFunction.read_key(event)
            if key is not None:
                self.user_input_display.read(key)
        else:
            pass
    
    def update_items(self):
        self.board.update(self.user_input_display.inputbox)
        is_match = self.board.is_match
        oob_n = self.board.oob_count()
        self.user_input_display.update(is_match)
        if is_match:
            self._info_table["score"] += self._SCORE_PER_WORD
        if oob_n > 0:
            self._info_table["score"] -= self._SCORE_PER_WORD*oob_n
        self.game_info.update(self._info_table)
    
    def on_render(self):
        pygame.display.update()
        self._frame_per_sec.tick(self._fps)
    
    def on_cleanup(self):
        self._display_surf.fill(self._BACKGROUND_COLOR)
    
    def home_loop(self):
        button = Button(self.width/2, self.height/2, "start!")
        is_start = False
        while self._running and not is_start:
            for event in pygame.event.get():
                self.on_event(event)
                if button.handle_event(event):
                    self.page = Pages.main
                    is_start = True
            button.draw()
            self.on_render()
    
    def main_loop(self):
        self.on_start()

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_cleanup()
            self.update_items()
            self.on_render()
    
    def exit_loop(self):
        while self._running:
            pass

    def on_execute(self):
        self.home_loop()
        self.main_loop()
        self.exit_loop()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    height, width = 500, 1000
    fps = 24

    app = App(height, width, fps)
    app.on_init()
    app.on_execute()