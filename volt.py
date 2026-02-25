#!/usr/bin/env python3
"""
Volt Programming Language v2.0
Usage:
    python volt.py <filename.volt>    Run a Volt program
    python volt.py                    Start the interactive REPL
    python volt.py --help             Show help
    python volt.py --version          Show version
"""

import sys
import os
from interpreter import Interpreter, VoltRuntimeError
from lexer import LexerError
from parser import ParserError


VOLT_VERSION = "2.0.0"

BANNER = f"""
 ⚡ Volt Language v{VOLT_VERSION}
 Type your code below. Use 'exit' or 'quit' to leave.
 Use 'help' for quick reference.
"""

HELP_TEXT = """
╔══════════════════════════════════════════════════════╗
║           Volt Language v2.0 - Quick Reference       ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  VARIABLES & ASSIGNMENT                              ║
║    set name = "Alice"                                ║
║    set user = {name: "Alice", age: 25}               ║
║    set [a, b, c] = [1, 2, 3]                        ║
║                                                      ║
║  OUTPUT / INPUT                                      ║
║    show f"Hello {name}!"                             ║
║    ask "Prompt: " -> variable                        ║
║                                                      ║
║  CONDITIONALS                                        ║
║    if / else if / else { ... }                       ║
║    match value { case 1 {...} default {...} }         ║
║                                                      ║
║  LOOPS                                               ║
║    for 5 { ... }                                     ║
║    for i in 1 to 10 { ... }                          ║
║    for item in list { ... }                          ║
║    for key, val in dict { ... }                      ║
║    while cond { ... }                                ║
║                                                      ║
║  FUNCTIONS                                           ║
║    func greet(name = "World") { ... }                ║
║    set double = (x) => x * 2                        ║
║                                                      ║
║  CLASSES                                             ║
║    class Dog extends Animal {                        ║
║      func init(name) { set this.name = name }        ║
║      func speak() { show this.name + " barks" }     ║
║    }                                                 ║
║    set d = new Dog("Rex")                            ║
║                                                      ║
║  ERROR HANDLING                                      ║
║    try { ... } catch err { ... } finally { ... }     ║
║    throw "error message"                             ║
║                                                      ║
║  MODULES                                             ║
║    use "math"   use "random"                         ║
║    use "time"   use "file"                           ║
║                                                      ║
║  STRING METHODS                                      ║
║    .upper() .lower() .trim() .replace() .split()     ║
║    .startsWith() .endsWith() .indexOf() .slice()     ║
║    .contains() .repeat() .reverse() .length          ║
║                                                      ║
║  LIST METHODS                                        ║
║    .push() .pop() .map() .filter() .find()           ║
║    .forEach() .reduce() .sort() .reverse()           ║
║    .includes() .join() .slice() .flat() .length      ║
║                                                      ║
║  DICT METHODS                                        ║
║    .keys() .values() .entries() .has() .merge()      ║
║    .remove() .size .forEach() .map() .filter()       ║
║                                                      ║
║  COMMENTS                                            ║
║    -- this is a comment                              ║
╚══════════════════════════════════════════════════════╝
"""


def run_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    interpreter = Interpreter()
    try:
        interpreter.run_file(filepath)
    except LexerError as e:
        print(f"⚡ {e}")
        sys.exit(1)
    except ParserError as e:
        print(f"⚡ {e}")
        sys.exit(1)
    except VoltRuntimeError as e:
        print(f"⚡ {e}")
        sys.exit(1)


def repl():
    print(BANNER)
    interpreter = Interpreter()

    while True:
        try:
            line = input("volt> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye! ⚡")
            break

        line = line.strip()
        if not line:
            continue
        if line in ('exit', 'quit'):
            print("Goodbye! ⚡")
            break
        if line == 'help':
            print(HELP_TEXT)
            continue

        # Multi-line: if line ends with '{', keep reading until braces balance
        if line.endswith('{') or line.count('{') > line.count('}'):
            brace_count = line.count('{') - line.count('}')
            while brace_count > 0:
                try:
                    continuation = input("  ... ")
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                line += '\n' + continuation
                brace_count += continuation.count('{') - continuation.count('}')

        try:
            interpreter.run(line)
        except LexerError as e:
            print(f"⚡ {e}")
        except ParserError as e:
            print(f"⚡ {e}")
        except VoltRuntimeError as e:
            print(f"⚡ {e}")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ('--help', '-h'):
            print(__doc__)
            sys.exit(0)
        if sys.argv[1] in ('--version', '-v'):
            print(f"Volt v{VOLT_VERSION}")
            sys.exit(0)
        run_file(sys.argv[1])
    else:
        repl()


if __name__ == '__main__':
    main()
