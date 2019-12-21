from kates.parser import parse, ParseError
from kates import parser
from kates.runner import *

import pytest


def must_equal(a, b):
    assert type(a) is type(b)
    assert a == b


def test_simple():
    result = parse('aaa bbb  !@#$%^&*()')
    ground_truth = [
        PlainCommand(
            'aaa',
            [LiteralArgument('bbb'), LiteralArgument('!@#$%^&*()')],
        ),
    ]
    must_equal(result, ground_truth)


def test_multiline():
    result = parse('0\n1 2\n3 4 5\n 6 7\n        8')
    ground_truth = [
        PlainCommand('0', []),
        PlainCommand('1', [LiteralArgument('2')]),
        PlainCommand('3', [LiteralArgument('4'), LiteralArgument('5')]),
        PlainCommand('6', [LiteralArgument('7')]),
        PlainCommand('8', []),
    ]
    must_equal(result, ground_truth)


def test_empty_lines():
    result = parse('\n\na  \n    \n \n\n')
    ground_truth = [
        PlainCommand('nop', []),
        PlainCommand('nop', []),
        PlainCommand('a', []),
        PlainCommand('nop', []),
        PlainCommand('nop', []),
        PlainCommand('nop', []),
        PlainCommand('nop', []),
    ]
    must_equal(result, ground_truth)


def test_if():
    result = parse('''
        if a b c
            foo bar
        else
            x y z
        endif
    '''.strip())
    ground_truth = [
        If(PlainCommand('a', [LiteralArgument('b'), LiteralArgument('c')])),
        PlainCommand('foo', [LiteralArgument('bar')]),
        Else(),
        PlainCommand('x', [LiteralArgument('y'), LiteralArgument('z')]),
        Endif(),
    ]
    must_equal(result, ground_truth)


def test_assignment():
    result = parse('x = a b')
    ground_truth = [
        Assignment('x', PlainCommand('a', [LiteralArgument('b')]))
    ]
    must_equal(result, ground_truth)


def test_empty_command():
    with pytest.raises(ParseError) as excinfo:
        parse('x = ')
    assert type(excinfo.value.__cause__) is parser.EmptyCommandError


def test_invalid_else():
    with pytest.raises(ParseError) as excinfo:
        parse('else x')
    cause = excinfo.value.__cause__
    assert type(cause) is parser.InvalidBuiltinCommandUsageError
    assert 'else' in str(cause)


def test_invalid_endif():
    with pytest.raises(ParseError) as excinfo:
        parse('endif x')
    cause = excinfo.value.__cause__
    assert type(cause) is parser.InvalidBuiltinCommandUsageError
    assert 'endif' in str(cause)


def test_variable():
    result = parse('a $b\na $$c\na "$$$d"')
    ground_truth = [
        PlainCommand('a', [VariableArgument('b')]),
        PlainCommand('a', [LiteralArgument('$c')]),
        PlainCommand('a', [LiteralArgument('$$d')]),
    ]
    must_equal(result, ground_truth)
