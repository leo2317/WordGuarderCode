import sys
from enum import Enum
from time import time

import pygame
from pygame.locals import QUIT

from commands import (
    Commands,
    parse_arg,
)
from components import (
    WordRunningBoard,
    TowerManager,
)
from items import (
    Button,
    Item,
    UserInputDisplay,
    GameInfo,
    Word,
    RunningWord,
    ErrorMessage,
    HelpInfo,
)
from utils import (
    Colors,
    Fonts,
    GUIDE_CONTENT,
    PygameFunction,
    InfoTable,
    plot_history,
)



class Pages(Enum):
    home = "home"
    help = "help"
    level = "level"  # TODO
    main = "main"
    exit = "exit"

class Levels(Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class App:
    # pygame constants
    _BACKGROUND_COLOR = Colors.BLACK.value

    # app constants
    _game_level = None
    _max_score = None
    _MIN_SCORE = -20
    _level_config_table = {         # (max_score, running_word_speed, word_generate_cycle)
        Levels.easy: (50, 2, 2),
        Levels.medium: (100, 3, 1.5),
        Levels.hard: (150, 4, 1.5),
    }

    def __init__(self, height, width, fps):
        # pygame setting
        self._running = False
        self._pause = False
        self._exit = False
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
        self.error_msg = None
        self.pause_time = None

        self._info_table = InfoTable()

        self.on_init()
    
    def on_init(self):
        # pygame setting
        pygame.init()
        pygame.key.set_repeat(500, 50)  # Delay: 500 ms, Interval: 50 ms
        self._display_surf = pygame.display.set_mode(self.size)
        self._frame_per_sec = pygame.time.Clock()
        pygame.display.set_caption("文字防線")

        # app setting
        self.pages_loop = {
            Pages.home: self.home_loop,
            Pages.help: self.help_loop,
            Pages.level: self.level_loop,
            Pages.main: self.main_loop,
            Pages.exit: self.exit_loop,
        }
        Item.set_display_serf(self._display_surf)
        
    def on_start(self):
        # layout args
        info_buttom_padding = 40

        # components setting
        if self.board is None:
            self.board = WordRunningBoard(10, (0, 10), self.width)
        self.board.clear()

        if self.tower_manager is None:
            self.tower_manager = TowerManager()
        self.tower_manager.clear()

        if self.user_input_display is None:
            self.user_input_display = UserInputDisplay((20, self.height - info_buttom_padding))
        self.user_input_display.clear()

        if self.game_info is None:
            self.game_info = GameInfo((670, self.height - info_buttom_padding))
        self._info_table.reset()

        if self.error_msg is None:
            self.error_msg = ErrorMessage((450, self.height - info_buttom_padding))
        self.error_msg.reset()
    
    def on_event(self, event):
        if event.type == QUIT:
            self._running = False
            self._exit = True
            return

        if self.page == Pages.home:
            pass
        elif self.page == Pages.main:
            key = PygameFunction.read_key(event)
            if key is not None:
                self.user_input_display.read(key)
                if self.user_input_display.is_full():
                    self.error_msg.input_full_warning()
                if self._pause:
                    self._pause = False
                    self._info_table._start_time += time() - self.pause_time
        elif self.page == Pages.help:
            pass
        else:
            pass
    
    '''
    TODO:
        1. command error
        2. error message
    '''
    def command_handler(self, input_str):
        if not input_str or input_str[-1] != '\n':
            return

        command_str = parse_arg(input_str)
        print(command_str)
        if command_str[0] == Commands.pause.value:
            if len(command_str) > 1:
                self.error_msg.param_error()
            else:
                self._pause = True
                self.pause_time = time()
        elif command_str[0] == Commands.tower.value:
            if len(command_str) != 2:
                self.error_msg.param_error()
            else:
                ypos = command_str[1]
                if not isinstance(ypos, int) or ypos <= 0 or ypos > 10 or self.board.lines[ypos - 1].tower is not None:
                    self.error_msg.param_error()
                else:
                    new_toewr = self.tower_manager.add_tower(ypos, self._info_table)
                    if new_toewr is None:
                        self.error_msg.tower_error()
                    else:
                        self.board.lines[ypos - 1].tower = new_toewr
        else:
            self.error_msg.unknown_command_error()
        self.user_input_display.mode = self.user_input_display._TYPING_MODE
        self.user_input_display.clear()
    
    def collision_handler(self):
        for i, first_bullet in enumerate(self.tower_manager.first_bullets):
            for j, first_word in enumerate(self.board.first_words):
                if first_bullet is None or first_word is None:
                    continue
                if first_bullet.body.colliderect(first_word.body):
                    self.tower_manager.towers[i].bullet_queue.pop(0)
                    self.board.lines[j].word_queue.pop(0)
    
    def update_game_info(self):
        self._info_table.score += self.board.total_match_word_score
        self._info_table.score -= self.board.total_oob_word_score

        try:
            total_word_num = self.board.total_char_num/5
        except ZeroDivisionError:
            total_word_num = 0.0

        if not self._pause:
            self._info_table.wpm = total_word_num/self._info_table.timer*60

        self.game_info.update(self._info_table)
        self.error_msg.update()
        self._info_table.checkpoint()
    
    def update_items(self):
        user_input = self.user_input_display.inputbox
        self.board.update(user_input, is_pause=self._pause)
        self.tower_manager.update(is_pause=self._pause)

        is_match = self.board.is_match
        input_str = self.user_input_display.update(is_match)

        pygame.draw.line(self._display_surf, Colors.WHITE.value, (0, self.height - 50), (self.width, self.height - 50), 3)

        if self.user_input_display.mode == UserInputDisplay._COMMAND_MODE:
            self.command_handler(input_str)
        self.collision_handler()
        self.update_game_info()

        score = self._info_table.score
        is_over = (
            score <= self._MIN_SCORE or
            score >= self._max_score
        )

        return is_over
    
    def on_render(self):
        pygame.display.update()
        self._frame_per_sec.tick(self._fps)
    
    def on_cleanup(self):
        self._display_surf.fill(self._BACKGROUND_COLOR)
    
    def home_loop(self):
        gap, padding = 100, 10
        start_button = Button(self.width/2, self.height/2 - (gap + padding)/2, "start !")
        help_button = Button(self.width/2, self.height/2 + (gap + padding)/2, "help")
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
                if start_button.handle_event(event):
                    self.page = Pages.level
                    self._running = False
                elif help_button.handle_event(event):
                    self.page = Pages.help
                    self._running = False
            self.on_cleanup()
            start_button.draw()
            help_button.draw()
            self.on_render()

    def level_loop(self):
        gap, padding = 100, 10
        easy_button = Button(self.width/2, self.height/2 - gap - padding, "easy")
        medium_button = Button(self.width/2, self.height/2, "medium")
        hard_button = Button(self.width/2, self.height/2 + gap + padding, "hard")
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)

                if easy_button.handle_event(event):
                    self._game_level = Levels.easy
                elif medium_button.handle_event(event):
                    self._game_level = Levels.medium
                elif hard_button.handle_event(event):
                    self._game_level = Levels.hard
                
                if self._game_level is not None:
                    self.page = Pages.main
                    self._running = False
                    self._max_score, RunningWord._RUNNING_SPEED, WordRunningBoard._GENERATE_CYCLE = \
                        self._level_config_table[self._game_level]

            self.on_cleanup()
            easy_button.draw()
            medium_button.draw()
            hard_button.draw()
            self.on_render()
    
    def main_loop(self):
        self.on_start()
        is_over = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_cleanup()
            is_over = self.update_items()

            if is_over:
                self.page = Pages.exit
                self._running = False

            self.on_render()
    
    def help_loop(self):
        gap, padding = 70, 10
        content = HelpInfo(GUIDE_CONTENT, (300, 30))
        back_button = Button(self.width/2, self.height - gap - padding, "back")
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
                if back_button.handle_event(event):
                    self.page = Pages.home
                    self._running = False
            self.on_cleanup()
            content.update()
            back_button.draw()
            self.on_render()

    def exit_loop(self):
        gap, padding = 100, 10
        again_button = Button(self.width/2, self.height/2 - gap - padding, "again !")
        check_record_button = Button(self.width/2, self.height/2, "check info")
        exit_button = Button(self.width/2, self.height/2 + gap + padding, "exit")

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
                '''
                TODO: wraping this handle_event() into on_event()
                '''
                if again_button.handle_event(event):
                    self.page = Pages.level
                    self._game_level = None
                    self._running = False
                elif check_record_button.handle_event(event):
                    '''
                    BUG: after ploting performance, the game window will change its size automatically...
                    '''

                    plot_history(self._info_table._history, self._info_table.timer)
                elif exit_button.handle_event(event):
                    self._exit = True
                    self._running = False
            again_button.draw()
            check_record_button.draw()
            exit_button.draw()
            self.on_render()

    def on_execute(self):
        while not self._exit:
            self._running = True
            self.pages_loop[self.page]()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    height, width = 500, 1000
    fps = 30

    app = App(height, width, fps)
    app.on_execute()