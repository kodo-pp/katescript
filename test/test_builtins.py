from kates.runner import *

import pytest


def test_id():
    a = ''

    def set_value(runner, args):
        del runner
        assert len(args) == 1
        nonlocal a
        a = args[0]

    functions = {'set': set_value}

    script_ok = Script([
        Assignment('x', PlainCommand('id', [LiteralArgument('Test')])),
        PlainCommand('set', [VariableArgument('x')]),
    ])

    script_wrong_1 = Script([
        PlainCommand('id', [])
    ])

    script_wrong_2 = Script([
        PlainCommand('id', [LiteralArgument('a'), LiteralArgument('b')])
    ])

    assert Runner(functions, script_ok).run() == 'end'
    assert a == 'Test'

    with pytest.raises(ScriptExecutionError) as exc_info:
        Runner(functions, script_wrong_1).run()
    assert isinstance(exc_info.value.err, ArgumentsError)

    with pytest.raises(ScriptExecutionError) as exc_info:
        Runner(functions, script_wrong_2).run()
    assert isinstance(exc_info.value.err, ArgumentsError)


def test_equals_and_not_equals():
    a = []

    def append(runner, args):
        del runner
        assert len(args) == 1
        nonlocal a
        a.append(args[0])

    functions = {'append': append}

    script_ok = Script([
        Assignment('x', PlainCommand('==', [LiteralArgument('foo'), LiteralArgument('bar')])),
        PlainCommand('append', [VariableArgument('x')]),
        Assignment('x', PlainCommand('==', [LiteralArgument('foo'), LiteralArgument('foo')])),
        PlainCommand('append', [VariableArgument('x')]),
        Assignment('x', PlainCommand('!=', [LiteralArgument('foo'), LiteralArgument('bar')])),
        PlainCommand('append', [VariableArgument('x')]),
        Assignment('x', PlainCommand('!=', [LiteralArgument('foo'), LiteralArgument('foo')])),
        PlainCommand('append', [VariableArgument('x')]),
    ])

    script_wrong_1 = Script([
        PlainCommand('==', [])
    ])

    script_wrong_2 = Script([
        PlainCommand('id', [LiteralArgument('a'), LiteralArgument('b'), LiteralArgument('c')])
    ])

    assert Runner(functions, script_ok).run() == 'end'
    assert ''.join(a) == '0110'

    with pytest.raises(ScriptExecutionError) as exc_info:
        Runner(functions, script_wrong_1).run()
    assert isinstance(exc_info.value.err, ArgumentsError)

    with pytest.raises(ScriptExecutionError) as exc_info:
        Runner(functions, script_wrong_2).run()
    assert isinstance(exc_info.value.err, ArgumentsError)
