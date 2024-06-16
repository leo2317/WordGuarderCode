import sys
from enum import Enum

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
    ErrorMessage,
)
from utils import (
    Colors,
    Fonts,
    GUIDE_CONTENT,
    PygameFunction,
    InfoTable,
    plot_history,
    set_keyboard_layout,
)



class Pages(Enum):
    home = "home"
    help = "help"
    level = "level"  # TODO
    main = "main"
    exit = "exit"

class App:
    # pygame constants
    _BACKGROUND_COLOR = Colors.BLACK.value

    # app constants
    _MIN_SCORE = -20

    def __init__(self, height, width, fps):
        # pygame setting
        self._running = False
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

        self._info_table = InfoTable()

        self.on_init()
    
    def on_init(self):
        # pygame setting
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size)
        self._frame_per_sec = pygame.time.Clock()
        pygame.display.set_caption("文字防線")

        # app setting
        self.pages_loop = {
            Pages.home: self.home_loop,
            Pages.help: self.help_loop,
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
            self.game_info = GameInfo((650, self.height - info_buttom_padding))
        self._info_table.reset()

        if self.error_msg is None:
            self.error_msg = ErrorMessage((400, self.height - info_buttom_padding))
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
        if command_str[0] == Commands.pause.value:
            if len(command_str) > 1:
                self.error_msg.param_error()
        elif command_str[0] == Commands.tower.value:
            ypos = int(command_str[1])
            new_toewr = self.tower_manager.add_tower(ypos, self._info_table)
            if new_toewr is not None:
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
        total_word_num = self.board.total_char_num/5
        self._info_table.wpm = total_word_num/self._info_table.timer*60

        self.game_info.update(self._info_table)
        self.error_msg.update()
        self._info_table.checkpoint()
    
    def update_items(self):
        user_input = self.user_input_display.inputbox
        self.board.update(user_input)
        self.tower_manager.update()

        is_match = self.board.is_match
        input_str = self.user_input_display.update(is_match)

        pygame.draw.line(self._display_surf, Colors.WHITE.value, (0, self.height - 50), (self.width, self.height - 50), 3)

        if self.user_input_display.mode == UserInputDisplay._COMMAND_MODE:
            self.command_handler(input_str)
        self.collision_handler()
        self.update_game_info()

        is_over = self._info_table.score <= self._MIN_SCORE

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
        is_start = False
        while self._running and not is_start:
            for event in pygame.event.get():
                self.on_event(event)
                if start_button.handle_event(event):
                    self.page = Pages.main
                    is_start = True
                    self._running = False
                elif help_button.handle_event(event):
                    self.page = Pages.help
                    self._running = False
            self.on_cleanup()
            start_button.draw()
            help_button.draw()
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
    
    def help_loop(self):
        gap, padding = 100, 10
        content = Word(GUIDE_CONTENT, (self.width/2, 10), Fonts.sym_font.value)
        back_button = Button(self.width/2, self.height/2, "back")
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
                    self.page = Pages.main
                    self._running = False
                elif check_record_button.handle_event(event):
                    plot_history(self._info_table._history)
                elif exit_button.handle_event(event):
                    self._exit = True
                    self._running = False
            again_button.draw()
            check_record_button.draw()
            exit_button.draw()
            self.on_render()

    def on_execute(self):
        # self.home_loop()
        # while self._again:
        #     self.main_loop()
        #     self.exit_loop()

        while not self._exit:
            self._running = True
            self.pages_loop[self.page]()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    height, width = 500, 1000
    fps = 24

    app = App(height, width, fps)
    app.on_execute()