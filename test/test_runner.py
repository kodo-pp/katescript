from kates.runner import *

import pytest


def test_simple():
    a = 5

    def func(runner, args):
        del runner
        del args
        nonlocal a
        a += 1
    
    functions = {
        'func': func,
    }

    script = Script([
        PlainCommand('func', []),
    ])

    runner = Runner(functions, script)
    reason = runner.run()
    assert reason == 'end'
    assert a == 6


def test_multiple_commands():
    a = []

    def append(runner, args):
        del runner
        assert len(args) == 1
        nonlocal a
        a.append(args[0])

    def append_multiple(runner, args):
        del runner
        nonlocal a
        a += args
    
    functions = {
        'append': append,
        'append_multiple': append_multiple,
    }

    script = Script([
        PlainCommand('append', [LiteralArgument('foo')]),
        PlainCommand('append', [LiteralArgument('bar')]),
        PlainCommand(
            'append_multiple',
            [LiteralArgument('baz'), LiteralArgument(''), LiteralArgument('aaa')],
        ),
        PlainCommand('append_multiple', []),
    ])

    runner = Runner(functions, script)
    reason = runner.run()
    assert reason == 'end'
    assert a == ['foo', 'bar', 'baz', '', 'aaa']


def test_variables():
    a = []

    def append(runner, args):
        del runner
        assert len(args) == 1
        nonlocal a
        a.append(args[0])

    def get(runner, args):
        del runner
        assert len(args) == 1
        index = int(args[0])
        nonlocal a
        return a[index]
    
    functions = {
        'append': append,
        'get': get,
    }

    script = Script([
        PlainCommand('append', [LiteralArgument('foo')]),
        PlainCommand('append', [LiteralArgument('bar')]),
        Assignment('x', PlainCommand('get', [LiteralArgument('1')])),
        PlainCommand('append', [VariableArgument('x')]),
    ])

    runner = Runner(functions, script)
    reason = runner.run()
    assert reason == 'end'
    assert a == ['foo', 'bar', 'bar']


def test_stops():
    a = ''

    def setvar(runner, args):
        del runner
        assert len(args) == 1
        nonlocal a
        a = args[0]

    def stop(runner, args):
        assert len(args) == 1
        runner.execution_stop_reason = args[0]
    
    functions = {
        'setvar': setvar,
        'stop': stop,
    }

    script = Script([
        PlainCommand('setvar', [LiteralArgument('a')]),
        PlainCommand('stop', [LiteralArgument('A')]),
        PlainCommand('setvar', [LiteralArgument('b')]),
        PlainCommand('stop', [LiteralArgument('B')]),
        PlainCommand('stop', [LiteralArgument('C')]),
        PlainCommand('setvar', [LiteralArgument('c')]),
    ])

    runner = Runner(functions, script)
    assert runner.run() == 'A'
    assert a == 'a'
    assert runner.run() == 'B'
    assert a == 'b'
    assert runner.run() == 'C'
    assert a == 'b' # Not a mistake, 'b' should indeed be here
    assert runner.run() == 'end'
    assert a == 'c'


def test_if():
    a = []

    def append(runner, args):
        del runner
        assert len(args) == 1
        nonlocal a
        a.append(args[0])

    true = lambda r, a: '1'
    false = lambda r, a: '0'
 
    functions = {
        'append': append,
    }

    """
        append('.')
        if cond1:
            append('1')
            if cond2:
                append('2')
            else:
                append('3')
            append('4')
        else:
            append('5')
            if cond2:
                append('6')
            else:
                append('7')
            append('8')
        append('9')
    """

    script = Script([
        PlainCommand('append', [LiteralArgument('.')]),
        If(PlainCommand('cond1', [])),
            PlainCommand('append', [LiteralArgument('1')]),
            If(PlainCommand('cond2', [])),
                PlainCommand('append', [LiteralArgument('2')]),
            Else(),
                PlainCommand('append', [LiteralArgument('3')]),
            Endif(),
            PlainCommand('append', [LiteralArgument('4')]),
        Else(),
            PlainCommand('append', [LiteralArgument('5')]),
            If(PlainCommand('cond2', [])),
                PlainCommand('append', [LiteralArgument('6')]),
            Else(),
                PlainCommand('append', [LiteralArgument('7')]),
            Endif(),
            PlainCommand('append', [LiteralArgument('8')]),
        Endif(),
        PlainCommand('append', [LiteralArgument('9')]),
    ])
    
    assert Runner(
        {**functions, 'cond1': false, 'cond2': false},
        script,
    ).run() == 'end'

    assert Runner(
        {**functions, 'cond1': false, 'cond2': true},
        script,
    ).run() == 'end'

    assert Runner(
        {**functions, 'cond1': true, 'cond2': false},
        script,
    ).run() == 'end'

    assert Runner(
        {**functions, 'cond1': true, 'cond2': true},
        script,
    ).run() == 'end'

    assert ''.join(a) == '.5789.5689.1349.1249'


def test_inexistent_function():
    functions = {}
    script = Script([
        PlainCommand('inexistent_function', []),
    ])
    
    with pytest.raises(ScriptExecutionError) as exc_info:
        Runner(functions, script).run()

    assert isinstance(exc_info.value.err, NoSuchFunctionError)


def test_inexistent_variable(): 
    functions = {'ignore': lambda r, a: ''}
    script = Script([
        PlainCommand('ignore', [VariableArgument('inexistent_variable')]),
    ])
    
    with pytest.raises(ScriptExecutionError) as exc_info:
        Runner(functions, script).run()

    assert isinstance(exc_info.value.err, NoSuchVariableError)


def test_stray_endif(): 
    script = Script([
        Endif(),
    ])
    
    with pytest.raises(ScriptExecutionError) as exc_info:
        Runner({}, script).run()

    assert isinstance(exc_info.value.err, StrayEndifError)
