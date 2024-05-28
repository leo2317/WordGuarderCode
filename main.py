import sys

import pygame
from pygame.locals import QUIT

import items
from commands import (
    Commands,
    parse_arg,
)
from components import (
    WordRunningBoard,
    TowerManager,
)
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
    _MIN_SCORE = -50

    def __init__(self, height, width, fps):
        # pygame setting
        self._running = False
        self._again = False
        self._display_surf = None
        self._fps = fps
        self._frame_per_sec = None

        # app setting
        self.size = self.width, self.height = width, height
        self.page = Pages.home
        self.board = None
        self.tower_manager = None
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
        self._again = True
        Item.set_display_serf(self._display_surf)

    def on_start(self):
        if self.board is None:
            self.board = WordRunningBoard(10, (0, 10), self.width)
        self.board.clear()
        if self.tower_manager is None:
            self.tower_manager = TowerManager()
        self.tower_manager.clear()
        # for i in range(10):
        #     self.tower_manager.add_tower(i + 1)
        if self.user_input_display is None:
            self.user_input_display = UserInputDisplay((20, self.height - 30))
        self.user_input_display.clear()
        if self.game_info is None:
            self.game_info = GameInfo((500, self.height - 30))
        self._info_table["score"] = 0
    
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
        self.tower_manager.update()
        is_match = self.board.is_match
        oob_n = self.board.oob_count()
        input_str = self.user_input_display.update(is_match)

        # handling command
        if input_str and input_str[-1] == '\n':  # is a finished command
            command_str = parse_arg(input_str)
            if command_str[0] == Commands.pause.value:
                pass
            elif command_str[0] == Commands.tower.value:
                ypos = int(command_str[1])
                self.tower_manager.add_tower(ypos)
                self.board.lines[ypos - 1].have_tower = True
            else:
                print("unknow command")
            self.user_input_display.mode = self.user_input_display._TYPING_MODE
            self.user_input_display.clear()
        
        # handling collision between word and bullet
        for i, first_bullet in enumerate(self.tower_manager.first_bullets):
            for j, first_word in enumerate(self.board.first_words):
                if first_bullet is None or first_word is None:
                    continue
                if first_bullet.body.colliderect(first_word.body):
                    self.tower_manager.towers[i].bullet_queue.pop(0)
                    self.board.lines[j].word_queue.pop(0)

        # handling information table
        if is_match:
            self._info_table["score"] += self._SCORE_PER_WORD
        if oob_n > 0:
            self._info_table["score"] -= self._SCORE_PER_WORD*oob_n
        self.game_info.update(self._info_table)

        is_over = self._info_table["score"] <= self._MIN_SCORE

        return is_over
    
    def on_render(self):
        pygame.display.update()
        self._frame_per_sec.tick(self._fps)
    
    def on_cleanup(self):
        self._display_surf.fill(self._BACKGROUND_COLOR)
    
    def home_loop(self):
        start_button = Button(self.width/2, self.height/2, "start!")
        is_start = False
        while self._running and not is_start:
            for event in pygame.event.get():
                self.on_event(event)
                if start_button.handle_event(event):
                    self.page = Pages.main
                    is_start = True
            start_button.draw()
            self.on_render()
    
    def main_loop(self):
        self.on_start()
        is_over = False

        while self._running and not is_over:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_cleanup()
            is_over = self.update_items()
            self.on_render()
    
    def exit_loop(self):
        gap, padding = 100, 10
        again_button = Button(self.width/2, self.height/2 - gap - padding, "again!")
        check_record_button = Button(self.width/2, self.height/2, "check record")
        exit_button = Button(self.width/2, self.height/2 + gap + padding, "exit")

        self._again = False
        while self._running and not self._again:
            for event in pygame.event.get():
                self.on_event(event)
                '''
                TODO: wraping this handle_event() into on_event()
                '''
                if again_button.handle_event(event):
                    self.page = Pages.main
                    self._again = True
                if check_record_button.handle_event(event):
                    pass
                if exit_button.handle_event(event):
                    self._running = False
            again_button.draw()
            check_record_button.draw()
            exit_button.draw()
            self.on_render()

    def on_execute(self):
        self.home_loop()
        while self._again:
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