from .error import Error

import abc
from typing import Callable, Dict, List, Optional, NewType


class NoSuchVariableError(Error):
    def __init__(self, variable_name: str):
        super().__init__(f'No such variable: {repr(variable_name)}')
        self.variable_name = variable_name

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return self.variable_name == other.variable_name


class NoSuchFunctionError(Error):
    def __init__(self, function_name: str):
        super().__init__(f'No such function: {repr(function_name)}')
        self.function_name = function_name

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return self.function_name == other.function_name


class ArgumentsError(Error):
    def __init__(self):
        super().__init__('Invalid number of arguments')

    def __eq__(self, other) -> bool:
        return type(self) is type(other)


class StrayEndifError(Error):
    def __init__(self):
        super().__init__('Stray endif')

    def __eq__(self, other) -> bool:
        return type(self) is type(other)


class ScriptExecutionError(Error):
    def __init__(self, err, runner):
        super().__init__(f'Error raised while executing the script (command {runner.command_index+1}): {err}')
        self.err = err
        self.runner = runner

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return (self.err, self.runner) == (other.err, other.runner)


class Argument:
    @abc.abstractmethod
    def evaluate(self, runner: 'Runner') -> str:
        ...


class LiteralArgument(Argument):
    def __init__(self, value: str):
        self.value = value

    def evaluate(self, runner: 'Runner') -> str:
        del runner
        return self.value

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return self.value == other.value

    def __repr__(self) -> str:
        return f'LiteralArgument({self.value})'


class VariableArgument(Argument):
    def __init__(self, variable_name: str):
        self.variable_name = variable_name

    def evaluate(self, runner: 'Runner') -> str:
        if self.variable_name not in runner.variables:
            raise NoSuchVariableError(self.variable_name)
        return runner.variables[self.variable_name]

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return self.variable_name == other.variable_name

    def __repr__(self) -> str:
        return f'VariableArgument({self.variable_name})'


class Command:
    @abc.abstractmethod
    def run(self, runner: 'Runner') -> str:
        ...

    def is_special(self) -> bool:
        return False


class PlainCommand(Command):
    def __init__(self, function_name: str, arguments: List[Argument]):
        self.function_name = function_name
        self.arguments = arguments

    def run(self, runner: 'Runner') -> str:
        if self.function_name not in runner.functions:
            raise NoSuchFunctionError(self.function_name)
        function = runner.functions[self.function_name]
        arguments = [arg.evaluate(runner) for arg in self.arguments]
        return function(runner, arguments)

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return (self.function_name, self.arguments) == (other.function_name, other.arguments)

    def __repr__(self) -> str:
        return f'PlainCommand({self.function_name} of {self.arguments})'


class Assignment(Command):
    def __init__(self, variable_name: str, command: Command):
        self.variable_name = variable_name
        self.command = command

    def run(self, runner: 'Runner') -> str:
        result = self.command.run(runner)
        runner.variables[self.variable_name] = result
        return result

    def __repr__(self) -> str:
        return f'Assignment({self.variable_name} = {self.command})'

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return (self.variable_name, self.command) == (other.variable_name, other.command)


class If(Command):
    def __init__(self, command: Command):
        self.command = command

    def run(self, runner: 'Runner') -> str:
        result = self.command.run(runner)
        condition = (result == '0' or result == '')
        runner.push_no_execution_state(condition)
        return ''

    def is_special(self) -> bool:
        return True

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return self.command == other.command

    def __repr__(self) -> str:
        return f'If({self.command})'


class Else(Command):
    def run(self, runner: 'Runner') -> str:
        runner.switch_no_execution_state()
        return ''

    def is_special(self) -> bool:
        return True

    def __eq__(self, other) -> bool:
        return type(self) is type(other)

    def __repr__(self) -> str:
        return f'Else'


class Endif(Command):
    def run(self, runner: 'Runner') -> str:
        runner.pop_no_execution_state()
        return ''

    def is_special(self) -> bool:
        return True

    def __eq__(self, other) -> bool:
        return type(self) is type(other)

    def __repr__(self) -> str:
        return f'Endif'


class Script:
    def __init__(self, commands: List[Command]):
        self.commands = commands

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.commands == other.commands

    def __repr__(self) -> str:
        return f'Script({self.commands})'


def builtin_id(runner: 'Runner', args: List[str]) -> str:
    if len(args) != 1:
        raise ArgumentsError()
    return args[0]


def builtin_equals(runner: 'Runner', args: List[str]) -> str:
    if len(args) != 2:
        raise ArgumentsError()
    return '1' if args[0] == args else '0'


def builtin_not_equals(runner: 'Runner', args: List[str]) -> str:
    if len(args) != 2:
        raise ArgumentsError()
    return '0' if args[0] == args else '1'


def builtin_nop(runner: 'Runner', args: List[str]) -> str:
    del args
    return ''


FunctionType = Callable[['Runner', List[str]], str]
ExecutionStopReason = NewType('ExecutionStopReason', str)


class Runner:
    def __init__(self, functions: Dict[str, FunctionType], script: Script):
        self._no_execution_stack = [False]
        self.command_index = 0
        self.execution_stop_reason: Optional[ExecutionStopReason] = None
        self.functions: Dict[str, FunctionType] = {
            '!=': builtin_not_equals,
            '==': builtin_equals,
            'id': builtin_id,
            'nop': builtin_nop,
            **functions,
        }
        self.script = script
        self.variables: Dict[str, str] = {}

    def run(self) -> ExecutionStopReason:
        while self.command_index < len(self.script.commands):
            self.run_single_command()
            if self.execution_stop_reason is not None:
                reason, self.execution_stop_reason = self.execution_stop_reason, None
                return reason
        return ExecutionStopReason('end')

    def push_no_execution_state(self, state: bool):
        self._no_execution_stack.append(state)

    def pop_no_execution_state(self):
        if len(self._no_execution_stack) <= 1:
            raise StrayEndifError()
        self._no_execution_stack.pop()

    def get_no_execution_state(self):
        return any(self._no_execution_stack)

    def switch_no_execution_state(self):
        self._no_execution_stack[-1] = not self._no_execution_stack[-1]

    def should_execute(self) -> bool:
        return not self.get_no_execution_state()

    def run_single_command(self):
        command = self.script.commands[self.command_index]
        self.command_index += 1
        if self.should_execute() or command.is_special():
            try:
                command.run(self)
            except Exception as e:
                raise ScriptExecutionError(e, self) from e

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return all((
            self._no_execution_stack == other._no_execution_stack,
            self.command_index == other.command_index,
            self.execution_stop_reason == other.execution_stop_reason,
            self.functions == other.functions,
            self.script == other.script,
            self.variables == other.variables,
        ))
