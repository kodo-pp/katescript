from . import runner
from .error import Error

import shlex
from typing import List


class EmptyCommandError(Error):
    def __init__(self):
        super().__init__('Command cannot be empty')


class InvalidBuiltinCommandUsageError(Error):
    def __init__(self, command):
        super().__init__(f'Invalid usage of builtin command: {command}')


class ParseError(Error):
    def __init__(self, line_number, err):
        super().__init__(f'Parse error (line {line_number}): {err}')
        self.line_number = line_number
        self.err = err


def parse_argument(token: str) -> runner.Argument:
    if token.startswith('$$'):
        return runner.LiteralArgument(token[1:])
    if token.startswith('$'):
        return runner.VariableArgument(token[1:])
    return runner.LiteralArgument(token)


def parse_command(tokens: List[str]) -> runner.Command:
    if len(tokens) == 0:
        raise EmptyCommandError()

    if tokens[0] == 'if':
        command = parse_command(tokens[1:])
        return runner.If(command)
    if tokens[0] == 'else':
        if len(tokens) != 1:
            raise InvalidBuiltinCommandUsageError('else')
        return runner.Else()
    if tokens[0] == 'endif':
        if len(tokens) != 1:
            raise InvalidBuiltinCommandUsageError('endif')
        return runner.Endif()
    function_name = tokens[0]
    arguments = list(map(parse_argument, tokens[1:]))
    return runner.PlainCommand(function_name, arguments)


def parse_line(line: str) -> runner.Command:
    tokens = shlex.split(line)
    if len(tokens) == 0:
        return runner.PlainCommand('nop', [])
    if len(tokens) >= 2 and tokens[1] == '=':
        variable_name = tokens[0]
        command = parse_command(tokens[2:])
        return runner.Assignment(variable_name, command)
    return parse_command(tokens)


def parse(code: str) -> List[runner.Command]:
    result: List[runner.Command] = []
    lines = code.split('\n')

    i = 0
    try:
        for i, line in enumerate(lines):
            result.append(parse_line(line))
    except Exception as e:
        raise ParseError(i + 1, e) from e

    return result
