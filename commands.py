from enum import Enum


class Commands(Enum):
    pause: str = "pause"
    tower: str = "tower"


def parse_arg(command: str):
    if command[-1] == '\n':
        command = command[:-1]

    command_str = command.split(' ')
    return command_str

