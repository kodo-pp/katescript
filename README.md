# KateScript
*KateScript* (or *Kates* to be short) is an extremely simple
scripting language written specially to be used in UnderKate game
(yet to be developed as for 12/22/2019).

## Syntax

A program consists of zero or more statements, each written on its own line.
Empty lines are equivalent to `nop` command, which does nothing.
All statements can be represented as lists of tokens. Tokens are whitespace-separated
parts of the line which are obtained by applying `shlex.split` to the source line.

There are two main kinds of statements: a plain command and an assignment.
A plain command executes a function with some parameters and discards its
result. An assignment does the same thing, but instead of discarding the returned
result it assigns it to a variable.

In a plain command the first token is considered to be the name of the function
that is to be called. All subsequent tokens (if any) in the statement constitute function's arguments
(all arguments are strings; see the **Functions** section). Very few functions are built-in. Instead,
it is expected that applications using KateScript provide their own functions
that can implement any required logic. When a function is called, KateScript will
try to find it by its name. If either KateScript or the application provides this function,
then it is executed. Otherwise, an error is raised. 

***I'm too lazy to write the rest of documentation now,
so I'll just attach a bunch of examples***

## Examples

In all examples, most functions used are expected to be provided by an application

### Integer division
```
x = input_number
y = input_number
if y = 0
    print "Division by zero"
else
    q = divide $x $y
    print $q
endif
```

### An in-game effect
```
player.disable_controls
glow_sprite = game.spawn_sprite "technical/effects/glow" 40 80
game.wait_for_death $glow_sprite
player.enable_controls
```
