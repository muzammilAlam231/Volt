"""
Volt Language v2.0 - Interpreter
Tree-walk interpreter with full OOP, method chaining, modules, and more.
"""

import os
from ast_nodes import *
from lexer import Lexer, LexerError
from parser import Parser, ParserError
from stdlib import VoltModule, BUILTIN_MODULES


# ═══════════════════════════════════════════════════════════
#  SIGNAL EXCEPTIONS
# ═══════════════════════════════════════════════════════════

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class BreakSignal(Exception):
    pass

class ContinueSignal(Exception):
    pass

class VoltRuntimeError(Exception):
    def __init__(self, message):
        super().__init__(f"Runtime Error: {message}")

class VoltThrowError(Exception):
    """Raised by the 'throw' statement — catchable by try/catch."""
    def __init__(self, value):
        self.value = value
        super().__init__(str(value))


# ═══════════════════════════════════════════════════════════
#  ENVIRONMENT (SCOPE)
# ═══════════════════════════════════════════════════════════

class Environment:
    def __init__(self, parent=None):
        self.variables = {}
        self.parent = parent

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise VoltRuntimeError(f"Undefined variable: '{name}'")

    def set(self, name, value):
        self.variables[name] = value

    def update(self, name, value):
        if name in self.variables:
            self.variables[name] = value
            return True
        if self.parent:
            return self.parent.update(name, value)
        return False

    def has(self, name):
        if name in self.variables:
            return True
        if self.parent:
            return self.parent.has(name)
        return False


# ═══════════════════════════════════════════════════════════
#  VOLT RUNTIME TYPES
# ═══════════════════════════════════════════════════════════

class VoltFunction:
    def __init__(self, name, params, body, closure_env):
        self.name = name
        self.params = params  # list of (name, default_ast_or_None)
        self.body = body
        self.closure_env = closure_env

    def __repr__(self):
        param_names = [p[0] for p in self.params]
        return f"<func {self.name}({', '.join(param_names)})>"


class VoltClass:
    def __init__(self, name, parent, methods, env):
        self.name = name
        self.parent = parent    # VoltClass or None
        self.methods = methods  # dict of name -> VoltFunction
        self.env = env

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.parent:
            return self.parent.find_method(name)
        return None

    def __repr__(self):
        return f"<class {self.name}>"


class VoltInstance:
    def __init__(self, klass):
        self.klass = klass
        self.properties = {}

    def get(self, name):
        if name in self.properties:
            return self.properties[name]
        method = self.klass.find_method(name)
        if method:
            return method
        raise VoltRuntimeError(f"'{self.klass.name}' has no property or method '{name}'")

    def set_property(self, name, value):
        self.properties[name] = value

    def __repr__(self):
        # If the class has a toString method, we'd call it. For repr, use simple form.
        return f"<{self.klass.name} instance>"


# ═══════════════════════════════════════════════════════════
#  INTERPRETER
# ═══════════════════════════════════════════════════════════

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self._setup_builtins()

    def _setup_builtins(self):
        self.builtins = {
            'len':      self._bi_len,
            'str':      self._bi_str,
            'int':      self._bi_int,
            'float':    self._bi_float,
            'type':     self._bi_type,
            'range':    self._bi_range,
            'abs':      self._bi_abs,
            'min':      self._bi_min,
            'max':      self._bi_max,
            'round':    self._bi_round,
            'upper':    self._bi_upper,
            'lower':    self._bi_lower,
            'split':    self._bi_split,
            'join':     self._bi_join,
            'contains': self._bi_contains,
            'reverse':  self._bi_reverse,
            'sort':     self._bi_sort,
            'keys':     self._bi_keys,
            'values':   self._bi_values,
            'print':    self._bi_print,
            'input':    self._bi_input,
            'number':   self._bi_number,
            'string':   self._bi_string,
            'bool':     self._bi_bool,
            'isinstance': self._bi_isinstance,
            'char':     self._bi_char,
            'ord':      self._bi_ord,
        }

    # ── Built-in Functions ────────────────────────────────

    def _bi_len(self, args):
        if len(args) != 1: raise VoltRuntimeError("len() takes 1 argument")
        v = args[0]
        if isinstance(v, (list, str, dict)): return len(v)
        raise VoltRuntimeError(f"len() not supported for {self._type_name(v)}")

    def _bi_str(self, args):
        if len(args) != 1: raise VoltRuntimeError("str() takes 1 argument")
        return self._to_string(args[0])

    def _bi_int(self, args):
        if len(args) != 1: raise VoltRuntimeError("int() takes 1 argument")
        try: return int(args[0])
        except: raise VoltRuntimeError(f"Cannot convert to int: {args[0]!r}")

    def _bi_float(self, args):
        if len(args) != 1: raise VoltRuntimeError("float() takes 1 argument")
        try: return float(args[0])
        except: raise VoltRuntimeError(f"Cannot convert to float: {args[0]!r}")

    def _bi_type(self, args):
        if len(args) != 1: raise VoltRuntimeError("type() takes 1 argument")
        return self._type_name(args[0])

    def _bi_range(self, args):
        if len(args) == 1: return list(range(int(args[0])))
        elif len(args) == 2: return list(range(int(args[0]), int(args[1])))
        elif len(args) == 3: return list(range(int(args[0]), int(args[1]), int(args[2])))
        raise VoltRuntimeError("range() takes 1-3 arguments")

    def _bi_abs(self, args):
        if len(args) != 1: raise VoltRuntimeError("abs() takes 1 argument")
        return abs(args[0])

    def _bi_min(self, args):
        if len(args) == 1 and isinstance(args[0], list): return min(args[0])
        return min(args)

    def _bi_max(self, args):
        if len(args) == 1 and isinstance(args[0], list): return max(args[0])
        return max(args)

    def _bi_round(self, args):
        if len(args) == 1: return round(args[0])
        elif len(args) == 2: return round(args[0], int(args[1]))
        raise VoltRuntimeError("round() takes 1-2 arguments")

    def _bi_upper(self, args):
        if len(args) != 1 or not isinstance(args[0], str):
            raise VoltRuntimeError("upper() takes 1 string argument")
        return args[0].upper()

    def _bi_lower(self, args):
        if len(args) != 1 or not isinstance(args[0], str):
            raise VoltRuntimeError("lower() takes 1 string argument")
        return args[0].lower()

    def _bi_split(self, args):
        if len(args) == 1 and isinstance(args[0], str): return args[0].split()
        elif len(args) == 2: return args[0].split(args[1])
        raise VoltRuntimeError("split() takes 1-2 string arguments")

    def _bi_join(self, args):
        if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], list):
            return args[0].join(self._to_string(x) for x in args[1])
        raise VoltRuntimeError("join() takes a separator and a list")

    def _bi_contains(self, args):
        if len(args) != 2: raise VoltRuntimeError("contains() takes 2 arguments")
        container, item = args
        if isinstance(container, (list, str)): return item in container
        if isinstance(container, dict): return item in container
        raise VoltRuntimeError("contains() requires a list, string, or dict")

    def _bi_reverse(self, args):
        if len(args) != 1: raise VoltRuntimeError("reverse() takes 1 argument")
        if isinstance(args[0], list): return args[0][::-1]
        if isinstance(args[0], str): return args[0][::-1]
        raise VoltRuntimeError("reverse() requires a list or string")

    def _bi_sort(self, args):
        if len(args) != 1 or not isinstance(args[0], list):
            raise VoltRuntimeError("sort() takes 1 list argument")
        return sorted(args[0])

    def _bi_keys(self, args):
        if len(args) != 1 or not isinstance(args[0], dict):
            raise VoltRuntimeError("keys() takes 1 dict argument")
        return list(args[0].keys())

    def _bi_values(self, args):
        if len(args) != 1 or not isinstance(args[0], dict):
            raise VoltRuntimeError("values() takes 1 dict argument")
        return list(args[0].values())

    def _bi_print(self, args):
        print(' '.join(self._to_string(a) for a in args))
        return None

    def _bi_input(self, args):
        prompt = self._to_string(args[0]) if args else ""
        return input(prompt)

    def _bi_number(self, args):
        if len(args) != 1: raise VoltRuntimeError("number() takes 1 argument")
        try:
            v = args[0]
            if '.' in str(v): return float(v)
            return int(v)
        except: raise VoltRuntimeError(f"Cannot convert to number: {args[0]!r}")

    def _bi_string(self, args):
        if len(args) != 1: raise VoltRuntimeError("string() takes 1 argument")
        return self._to_string(args[0])

    def _bi_bool(self, args):
        if len(args) != 1: raise VoltRuntimeError("bool() takes 1 argument")
        return self._is_truthy(args[0])

    def _bi_isinstance(self, args):
        if len(args) != 2: raise VoltRuntimeError("isinstance() takes 2 arguments")
        obj, klass = args
        if not isinstance(klass, VoltClass):
            raise VoltRuntimeError("Second argument to isinstance() must be a class")
        if not isinstance(obj, VoltInstance):
            return False
        check = obj.klass
        while check:
            if check is klass:
                return True
            check = check.parent
        return False

    def _bi_char(self, args):
        if len(args) != 1: raise VoltRuntimeError("char() takes 1 argument")
        return chr(int(args[0]))

    def _bi_ord(self, args):
        if len(args) != 1 or not isinstance(args[0], str) or len(args[0]) != 1:
            raise VoltRuntimeError("ord() takes a single character string")
        return ord(args[0])

    # ═══════════════════════════════════════════════════════
    #  STRING METHODS
    # ═══════════════════════════════════════════════════════

    def _call_string_method(self, s, method, args):
        methods = {
            'upper':      lambda: s.upper(),
            'lower':      lambda: s.lower(),
            'trim':       lambda: s.strip(),
            'trimStart':  lambda: s.lstrip(),
            'trimEnd':    lambda: s.rstrip(),
            'replace':    lambda: s.replace(args[0], args[1]) if len(args) >= 2 else self._err("replace() needs 2 args"),
            'split':      lambda: s.split() if not args else s.split(args[0]),
            'startsWith': lambda: s.startswith(args[0]) if args else self._err("startsWith() needs 1 arg"),
            'endsWith':   lambda: s.endswith(args[0]) if args else self._err("endsWith() needs 1 arg"),
            'indexOf':    lambda: s.find(args[0]) if args else self._err("indexOf() needs 1 arg"),
            'lastIndexOf': lambda: s.rfind(args[0]) if args else self._err("lastIndexOf() needs 1 arg"),
            'slice':      lambda: s[int(args[0]):int(args[1])] if len(args) >= 2 else s[int(args[0]):] if args else s,
            'charAt':     lambda: s[int(args[0])] if args else self._err("charAt() needs 1 arg"),
            'repeat':     lambda: s * int(args[0]) if args else self._err("repeat() needs 1 arg"),
            'reverse':    lambda: s[::-1],
            'contains':   lambda: args[0] in s if args else self._err("contains() needs 1 arg"),
            'includes':   lambda: args[0] in s if args else self._err("includes() needs 1 arg"),
            'length':     lambda: len(s),
            'toInt':      lambda: int(s),
            'toFloat':    lambda: float(s),
            'toNumber':   lambda: float(s) if '.' in s else int(s),
            'toList':     lambda: list(s),
            'isDigit':    lambda: s.isdigit(),
            'isAlpha':    lambda: s.isalpha(),
            'isSpace':    lambda: s.isspace(),
            'isEmpty':    lambda: len(s) == 0,
            'count':      lambda: s.count(args[0]) if args else self._err("count() needs 1 arg"),
            'padStart':   lambda: s.rjust(int(args[0]), args[1] if len(args) > 1 else ' '),
            'padEnd':     lambda: s.ljust(int(args[0]), args[1] if len(args) > 1 else ' '),
            'format':     lambda: s.format(*args),
            'join':       lambda: s.join(self._to_string(x) for x in args[0]) if args and isinstance(args[0], list) else self._err("join() needs a list"),
        }
        if method not in methods:
            raise VoltRuntimeError(f"String has no method '{method}'")
        return methods[method]()

    # ═══════════════════════════════════════════════════════
    #  LIST METHODS
    # ═══════════════════════════════════════════════════════

    def _call_list_method(self, lst, method, args, env):
        if method == 'push' or method == 'append':
            if not args: raise VoltRuntimeError(f"{method}() needs 1 argument")
            lst.append(args[0])
            return lst

        elif method == 'pop':
            if not lst: raise VoltRuntimeError("Cannot pop from empty list")
            return lst.pop(int(args[0]) if args else -1)

        elif method == 'shift':
            if not lst: raise VoltRuntimeError("Cannot shift from empty list")
            return lst.pop(0)

        elif method == 'unshift':
            if not args: raise VoltRuntimeError("unshift() needs 1 argument")
            lst.insert(0, args[0])
            return lst

        elif method == 'insert':
            if len(args) < 2: raise VoltRuntimeError("insert() needs 2 arguments")
            lst.insert(int(args[0]), args[1])
            return lst

        elif method == 'remove':
            if not args: raise VoltRuntimeError("remove() needs 1 argument")
            lst.remove(args[0])
            return lst

        elif method == 'length':
            return len(lst)

        elif method == 'indexOf':
            if not args: raise VoltRuntimeError("indexOf() needs 1 argument")
            try: return lst.index(args[0])
            except ValueError: return -1

        elif method == 'lastIndexOf':
            if not args: raise VoltRuntimeError("lastIndexOf() needs 1 argument")
            for i in range(len(lst) - 1, -1, -1):
                if lst[i] == args[0]: return i
            return -1

        elif method == 'includes' or method == 'contains':
            if not args: raise VoltRuntimeError(f"{method}() needs 1 argument")
            return args[0] in lst

        elif method == 'join':
            sep = self._to_string(args[0]) if args else ","
            return sep.join(self._to_string(x) for x in lst)

        elif method == 'slice':
            if len(args) >= 2: return lst[int(args[0]):int(args[1])]
            elif args: return lst[int(args[0]):]
            return lst[:]

        elif method == 'sort':
            return sorted(lst)

        elif method == 'reverse':
            return lst[::-1]

        elif method == 'flat':
            result = []
            for item in lst:
                if isinstance(item, list): result.extend(item)
                else: result.append(item)
            return result

        elif method == 'fill':
            if not args: raise VoltRuntimeError("fill() needs 1 argument")
            val = args[0]
            start = int(args[1]) if len(args) > 1 else 0
            end = int(args[2]) if len(args) > 2 else len(lst)
            for i in range(start, min(end, len(lst))):
                lst[i] = val
            return lst

        elif method == 'clear':
            lst.clear()
            return lst

        elif method == 'copy':
            return lst[:]

        elif method == 'count':
            if not args: raise VoltRuntimeError("count() needs 1 argument")
            return lst.count(args[0])

        elif method == 'isEmpty':
            return len(lst) == 0

        elif method == 'first':
            if not lst: raise VoltRuntimeError("Cannot get first of empty list")
            return lst[0]

        elif method == 'last':
            if not lst: raise VoltRuntimeError("Cannot get last of empty list")
            return lst[-1]

        elif method == 'unique':
            seen = []
            for item in lst:
                if item not in seen: seen.append(item)
            return seen

        elif method == 'sum':
            return sum(lst)

        elif method == 'min':
            return min(lst)

        elif method == 'max':
            return max(lst)

        # Higher-order methods (take function arguments)
        elif method == 'map':
            if not args: raise VoltRuntimeError("map() needs a function argument")
            fn = args[0]
            return [self._call_volt_function(fn, [item], env) for item in lst]

        elif method == 'filter':
            if not args: raise VoltRuntimeError("filter() needs a function argument")
            fn = args[0]
            return [item for item in lst if self._is_truthy(self._call_volt_function(fn, [item], env))]

        elif method == 'find':
            if not args: raise VoltRuntimeError("find() needs a function argument")
            fn = args[0]
            for item in lst:
                if self._is_truthy(self._call_volt_function(fn, [item], env)):
                    return item
            return None

        elif method == 'findIndex':
            if not args: raise VoltRuntimeError("findIndex() needs a function argument")
            fn = args[0]
            for i, item in enumerate(lst):
                if self._is_truthy(self._call_volt_function(fn, [item], env)):
                    return i
            return -1

        elif method == 'forEach':
            if not args: raise VoltRuntimeError("forEach() needs a function argument")
            fn = args[0]
            for item in lst:
                self._call_volt_function(fn, [item], env)
            return None

        elif method == 'every':
            if not args: raise VoltRuntimeError("every() needs a function argument")
            fn = args[0]
            return all(self._is_truthy(self._call_volt_function(fn, [item], env)) for item in lst)

        elif method == 'some':
            if not args: raise VoltRuntimeError("some() needs a function argument")
            fn = args[0]
            return any(self._is_truthy(self._call_volt_function(fn, [item], env)) for item in lst)

        elif method == 'reduce':
            if not args: raise VoltRuntimeError("reduce() needs a function argument")
            fn = args[0]
            acc = args[1] if len(args) > 1 else lst[0]
            start_idx = 0 if len(args) > 1 else 1
            for i in range(start_idx, len(lst)):
                acc = self._call_volt_function(fn, [acc, lst[i]], env)
            return acc

        elif method == 'zip':
            if not args or not isinstance(args[0], list):
                raise VoltRuntimeError("zip() needs a list argument")
            other = args[0]
            return [[lst[i], other[i]] for i in range(min(len(lst), len(other)))]

        elif method == 'enumerate':
            return [[i, lst[i]] for i in range(len(lst))]

        raise VoltRuntimeError(f"List has no method '{method}'")

    # ═══════════════════════════════════════════════════════
    #  DICT METHODS
    # ═══════════════════════════════════════════════════════

    def _call_dict_method(self, d, method, args, env):
        if method == 'keys':
            return list(d.keys())
        elif method == 'values':
            return list(d.values())
        elif method == 'entries':
            return [[k, v] for k, v in d.items()]
        elif method == 'has':
            if not args: raise VoltRuntimeError("has() needs 1 argument")
            return args[0] in d
        elif method == 'get':
            if not args: raise VoltRuntimeError("get() needs 1-2 arguments")
            key = args[0]
            default = args[1] if len(args) > 1 else None
            return d.get(key, default)
        elif method == 'remove' or method == 'delete':
            if not args: raise VoltRuntimeError(f"{method}() needs 1 argument")
            key = args[0]
            if key in d:
                val = d[key]
                del d[key]
                return val
            return None
        elif method == 'size' or method == 'length':
            return len(d)
        elif method == 'merge':
            if not args or not isinstance(args[0], dict):
                raise VoltRuntimeError("merge() needs a dict argument")
            result = dict(d)
            result.update(args[0])
            return result
        elif method == 'clear':
            d.clear()
            return d
        elif method == 'copy':
            return dict(d)
        elif method == 'isEmpty':
            return len(d) == 0
        elif method == 'contains':
            if not args: raise VoltRuntimeError("contains() needs 1 argument")
            return args[0] in d
        elif method == 'forEach':
            if not args: raise VoltRuntimeError("forEach() needs a function argument")
            fn = args[0]
            for k, v in d.items():
                self._call_volt_function(fn, [k, v], env)
            return None
        elif method == 'map':
            if not args: raise VoltRuntimeError("map() needs a function argument")
            fn = args[0]
            result = {}
            for k, v in d.items():
                new_val = self._call_volt_function(fn, [k, v], env)
                result[k] = new_val
            return result
        elif method == 'filter':
            if not args: raise VoltRuntimeError("filter() needs a function argument")
            fn = args[0]
            result = {}
            for k, v in d.items():
                if self._is_truthy(self._call_volt_function(fn, [k, v], env)):
                    result[k] = v
            return result
        elif method == 'toList':
            return [[k, v] for k, v in d.items()]

        raise VoltRuntimeError(f"Dict has no method '{method}'")

    # ═══════════════════════════════════════════════════════
    #  CALL HELPERS
    # ═══════════════════════════════════════════════════════

    def _call_volt_function(self, fn, args, env):
        """Call a VoltFunction or lambda with given args."""
        if isinstance(fn, VoltFunction):
            func_env = Environment(parent=fn.closure_env)
            self._bind_params(fn, args, func_env, env)
            try:
                self._exec_block(fn.body, func_env)
            except ReturnSignal as ret:
                return ret.value
            return None
        raise VoltRuntimeError(f"Not a callable function")

    def _bind_params(self, fn, args, func_env, caller_env):
        """Bind arguments to parameters, handling defaults."""
        for i, (param_name, default_node) in enumerate(fn.params):
            if i < len(args):
                func_env.set(param_name, args[i])
            elif default_node is not None:
                func_env.set(param_name, self.execute(default_node, caller_env))
            else:
                raise VoltRuntimeError(
                    f"Missing argument '{param_name}' in call to {fn.name}()"
                )

    def _err(self, msg):
        raise VoltRuntimeError(msg)

    # ═══════════════════════════════════════════════════════
    #  EXECUTION
    # ═══════════════════════════════════════════════════════

    def run(self, source, filename=None):
        """Lex, parse, and interpret source code."""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        tree = parser.parse()
        self.execute(tree, self.global_env)

    def run_file(self, filepath):
        """Run a .volt file."""
        if not os.path.exists(filepath):
            raise VoltRuntimeError(f"File not found: '{filepath}'")
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        self.run(source, filename=filepath)

    def execute(self, node, env):
        method_name = f'_exec_{type(node).__name__}'
        method = getattr(self, method_name, None)
        if method is None:
            raise VoltRuntimeError(f"Unknown AST node: {type(node).__name__}")
        return method(node, env)

    # ── Literals ──────────────────────────────────────────

    def _exec_Program(self, node, env):
        result = None
        for stmt in node.statements:
            result = self.execute(stmt, env)
        return result

    def _exec_NumberLiteral(self, node, env):
        return node.value

    def _exec_StringLiteral(self, node, env):
        return node.value

    def _exec_BooleanLiteral(self, node, env):
        return node.value

    def _exec_NullLiteral(self, node, env):
        return None

    def _exec_ListLiteral(self, node, env):
        return [self.execute(el, env) for el in node.elements]

    def _exec_DictLiteral(self, node, env):
        d = {}
        for key_node, value_node in node.pairs:
            key = self.execute(key_node, env)
            value = self.execute(value_node, env)
            d[key] = value
        return d

    def _exec_StringInterpolation(self, node, env):
        parts = []
        for part in node.parts:
            val = self.execute(part, env)
            parts.append(self._to_string(val))
        return ''.join(parts)

    # ── Identifiers & Access ──────────────────────────────

    def _exec_Identifier(self, node, env):
        return env.get(node.name)

    def _exec_ThisExpression(self, node, env):
        return env.get('this')

    def _exec_IndexAccess(self, node, env):
        obj = self.execute(node.obj, env)
        index = self.execute(node.index, env)
        if isinstance(obj, list):
            idx = int(index)
            if idx < -len(obj) or idx >= len(obj):
                raise VoltRuntimeError(f"Index {idx} out of range (length {len(obj)})")
            return obj[idx]
        elif isinstance(obj, str):
            idx = int(index)
            if idx < -len(obj) or idx >= len(obj):
                raise VoltRuntimeError(f"Index {idx} out of range (length {len(obj)})")
            return obj[idx]
        elif isinstance(obj, dict):
            if index not in obj:
                raise VoltRuntimeError(f"Key {index!r} not found in dict")
            return obj[index]
        raise VoltRuntimeError(f"Cannot index {self._type_name(obj)}")

    def _exec_DotAccess(self, node, env):
        obj = self.execute(node.obj, env)
        prop = node.property

        if isinstance(obj, VoltInstance):
            return obj.get(prop)
        elif isinstance(obj, VoltModule):
            return obj.get_property(prop)
        elif isinstance(obj, VoltClass):
            # Class-level access (for static-like behavior)
            method = obj.find_method(prop)
            if method: return method
            raise VoltRuntimeError(f"Class '{obj.name}' has no method '{prop}'")
        elif isinstance(obj, dict):
            # Dict dot access for convenience
            if prop == 'size': return len(obj)
            if prop in obj: return obj[prop]
            raise VoltRuntimeError(f"Key '{prop}' not found in dict")
        elif isinstance(obj, str):
            if prop == 'length': return len(obj)
            raise VoltRuntimeError(f"String has no property '{prop}'. Use .{prop}() for methods")
        elif isinstance(obj, list):
            if prop == 'length': return len(obj)
            raise VoltRuntimeError(f"List has no property '{prop}'. Use .{prop}() for methods")
        raise VoltRuntimeError(f"Cannot access property '{prop}' on {self._type_name(obj)}")

    # ── Expressions ───────────────────────────────────────

    def _exec_BinaryOp(self, node, env):
        if node.op == 'and':
            left = self.execute(node.left, env)
            return self.execute(node.right, env) if self._is_truthy(left) else left
        if node.op == 'or':
            left = self.execute(node.left, env)
            return left if self._is_truthy(left) else self.execute(node.right, env)

        left = self.execute(node.left, env)
        right = self.execute(node.right, env)

        if node.op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return self._to_string(left) + self._to_string(right)
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            if isinstance(left, dict) and isinstance(right, dict):
                result = dict(left); result.update(right); return result
            return left + right
        elif node.op == '-': return left - right
        elif node.op == '*':
            if isinstance(left, str) and isinstance(right, (int, float)):
                return left * int(right)
            if isinstance(right, str) and isinstance(left, (int, float)):
                return right * int(left)
            return left * right
        elif node.op == '/':
            if right == 0: raise VoltRuntimeError("Division by zero")
            return left / right
        elif node.op == '%':
            if right == 0: raise VoltRuntimeError("Modulo by zero")
            return left % right
        elif node.op == '==': return left == right
        elif node.op == '!=': return left != right
        elif node.op == '<': return left < right
        elif node.op == '>': return left > right
        elif node.op == '<=': return left <= right
        elif node.op == '>=': return left >= right
        raise VoltRuntimeError(f"Unknown operator: {node.op}")

    def _exec_UnaryOp(self, node, env):
        operand = self.execute(node.operand, env)
        if node.op == '-': return -operand
        if node.op == 'not': return not self._is_truthy(operand)
        raise VoltRuntimeError(f"Unknown unary operator: {node.op}")

    def _exec_LambdaExpression(self, node, env):
        return VoltFunction('<lambda>', node.params, [ReturnStatement(node.body)], env)

    # ── Function / Method Calls ───────────────────────────

    def _exec_FunctionCall(self, node, env):
        args = [self.execute(arg, env) for arg in node.args]

        # Built-in functions
        if node.name in self.builtins:
            return self.builtins[node.name](args)

        # User-defined function or class
        val = env.get(node.name)

        if isinstance(val, VoltClass):
            # Constructor call: ClassName(args) - same as new ClassName(args)
            return self._instantiate_class(val, args, env)

        if isinstance(val, VoltFunction):
            func_env = Environment(parent=val.closure_env)
            self._bind_params(val, args, func_env, env)
            try:
                self._exec_block(val.body, func_env)
            except ReturnSignal as ret:
                return ret.value
            return None

        raise VoltRuntimeError(f"'{node.name}' is not a function")

    def _exec_CallExpression(self, node, env):
        callee = self.execute(node.callee, env)
        args = [self.execute(arg, env) for arg in node.args]

        if isinstance(callee, VoltFunction):
            return self._call_volt_function(callee, args, env)
        if isinstance(callee, VoltClass):
            return self._instantiate_class(callee, args, env)
        raise VoltRuntimeError("Expression is not callable")

    def _exec_MethodCall(self, node, env):
        obj = self.execute(node.obj, env)
        method = node.method
        args = [self.execute(arg, env) for arg in node.args]

        # VoltInstance method call
        if isinstance(obj, VoltInstance):
            return self._call_instance_method(obj, method, args, env)

        # VoltModule method call
        if isinstance(obj, VoltModule):
            try:
                return obj.call_method(method, args)
            except (KeyError, RuntimeError) as e:
                raise VoltRuntimeError(str(e))

        # String method
        if isinstance(obj, str):
            return self._call_string_method(obj, method, args)

        # List method
        if isinstance(obj, list):
            return self._call_list_method(obj, method, args, env)

        # Dict method
        if isinstance(obj, dict):
            return self._call_dict_method(obj, method, args, env)

        # Number methods
        if isinstance(obj, (int, float)):
            return self._call_number_method(obj, method, args)

        raise VoltRuntimeError(f"Cannot call method '{method}' on {self._type_name(obj)}")

    def _call_number_method(self, n, method, args):
        if method == 'toStr' or method == 'toString':
            return self._to_string(n)
        elif method == 'toInt':
            return int(n)
        elif method == 'toFloat':
            return float(n)
        elif method == 'abs':
            return abs(n)
        elif method == 'isEven':
            return int(n) % 2 == 0
        elif method == 'isOdd':
            return int(n) % 2 != 0
        elif method == 'isPositive':
            return n > 0
        elif method == 'isNegative':
            return n < 0
        elif method == 'isZero':
            return n == 0
        elif method == 'clamp':
            if len(args) < 2: raise VoltRuntimeError("clamp() needs 2 arguments (min, max)")
            return max(args[0], min(n, args[1]))
        raise VoltRuntimeError(f"Number has no method '{method}'")

    def _exec_NewExpression(self, node, env):
        klass = env.get(node.class_name)
        if not isinstance(klass, VoltClass):
            raise VoltRuntimeError(f"'{node.class_name}' is not a class")
        args = [self.execute(arg, env) for arg in node.args]
        return self._instantiate_class(klass, args, env)

    def _instantiate_class(self, klass, args, env):
        instance = VoltInstance(klass)
        init_method = klass.find_method('init')
        if init_method:
            method_env = Environment(parent=init_method.closure_env)
            method_env.set('this', instance)
            method_env.set('__class__', klass)
            self._bind_params(init_method, args, method_env, env)
            try:
                self._exec_block(init_method.body, method_env)
            except ReturnSignal:
                pass
        elif args:
            raise VoltRuntimeError(f"Class '{klass.name}' constructor takes no arguments")
        return instance

    def _call_instance_method(self, instance, method_name, args, env):
        # Check if property is a function
        if method_name in instance.properties:
            val = instance.properties[method_name]
            if isinstance(val, VoltFunction):
                return self._call_volt_function(val, args, env)
            raise VoltRuntimeError(f"'{method_name}' is not a method")

        # Look up method on class
        method_fn = instance.klass.find_method(method_name)
        if method_fn is None:
            # Check for toString special method
            raise VoltRuntimeError(f"'{instance.klass.name}' has no method '{method_name}'")

        method_env = Environment(parent=method_fn.closure_env)
        method_env.set('this', instance)
        method_env.set('__class__', instance.klass)
        self._bind_params(method_fn, args, method_env, env)
        try:
            self._exec_block(method_fn.body, method_env)
        except ReturnSignal as ret:
            return ret.value
        return None

    def _exec_SuperMethodCall(self, node, env):
        this = env.get('this')
        current_class = env.get('__class__')
        if not isinstance(current_class, VoltClass) or current_class.parent is None:
            raise VoltRuntimeError("'super' used outside of a subclass method")

        parent = current_class.parent
        method_fn = parent.find_method(node.method)
        if method_fn is None:
            raise VoltRuntimeError(f"Parent class has no method '{node.method}'")

        args = [self.execute(arg, env) for arg in node.args]
        method_env = Environment(parent=method_fn.closure_env)
        method_env.set('this', this)
        method_env.set('__class__', parent)
        self._bind_params(method_fn, args, method_env, env)
        try:
            self._exec_block(method_fn.body, method_env)
        except ReturnSignal as ret:
            return ret.value
        return None

    # ── Statements ────────────────────────────────────────

    def _exec_Assignment(self, node, env):
        value = self.execute(node.value, env)
        target = node.target

        if isinstance(target, Identifier):
            if not env.update(target.name, value):
                env.set(target.name, value)
            return value

        elif isinstance(target, DotAccess):
            obj = self.execute(target.obj, env)
            if isinstance(obj, VoltInstance):
                obj.set_property(target.property, value)
            elif isinstance(obj, dict):
                obj[target.property] = value
            else:
                raise VoltRuntimeError(f"Cannot set property on {self._type_name(obj)}")
            return value

        elif isinstance(target, IndexAccess):
            obj = self.execute(target.obj, env)
            index = self.execute(target.index, env)
            if isinstance(obj, list):
                idx = int(index)
                if idx < -len(obj) or idx >= len(obj):
                    raise VoltRuntimeError(f"Index {idx} out of range")
                obj[idx] = value
            elif isinstance(obj, dict):
                obj[index] = value
            else:
                raise VoltRuntimeError(f"Cannot index-assign on {self._type_name(obj)}")
            return value

        elif isinstance(target, ThisExpression):
            raise VoltRuntimeError("Cannot assign directly to 'this'. Use 'set this.property = value'")

        raise VoltRuntimeError(f"Invalid assignment target")

    def _exec_ShowStatement(self, node, env):
        value = self.execute(node.expression, env)
        print(self._to_string(value))
        return None

    def _exec_AskStatement(self, node, env):
        prompt = self.execute(node.prompt, env)
        user_input = input(self._to_string(prompt))
        # Auto-convert
        try:
            if '.' in user_input: value = float(user_input)
            else: value = int(user_input)
        except ValueError:
            if user_input.lower() == 'true': value = True
            elif user_input.lower() == 'false': value = False
            else: value = user_input
        env.set(node.variable, value)
        return value

    def _exec_IfStatement(self, node, env):
        if self._is_truthy(self.execute(node.condition, env)):
            return self._exec_block(node.body, env)
        for elif_cond, elif_body in node.elif_clauses:
            if self._is_truthy(self.execute(elif_cond, env)):
                return self._exec_block(elif_body, env)
        if node.else_body is not None:
            return self._exec_block(node.else_body, env)
        return None

    def _exec_WhileStatement(self, node, env):
        result = None
        while self._is_truthy(self.execute(node.condition, env)):
            try: result = self._exec_block(node.body, env)
            except BreakSignal: break
            except ContinueSignal: continue
        return result

    def _exec_LoopTimesStatement(self, node, env):
        count = self.execute(node.count, env)
        if not isinstance(count, (int, float)):
            raise VoltRuntimeError("Loop count must be a number")
        result = None
        for _ in range(int(count)):
            try: result = self._exec_block(node.body, env)
            except BreakSignal: break
            except ContinueSignal: continue
        return result

    def _exec_LoopRangeStatement(self, node, env):
        start = self.execute(node.start, env)
        end = self.execute(node.end, env)
        result = None
        for i in range(int(start), int(end) + 1):
            env.set(node.variable, i)
            try: result = self._exec_block(node.body, env)
            except BreakSignal: break
            except ContinueSignal: continue
        return result

    def _exec_ForInStatement(self, node, env):
        iterable = self.execute(node.iterable, env)
        result = None

        if isinstance(iterable, dict):
            for k in iterable:
                env.set(node.variable, k)
                if node.variable2:
                    env.set(node.variable2, iterable[k])
                try: result = self._exec_block(node.body, env)
                except BreakSignal: break
                except ContinueSignal: continue

        elif isinstance(iterable, list):
            for i, item in enumerate(iterable):
                if node.variable2:
                    env.set(node.variable, i)
                    env.set(node.variable2, item)
                else:
                    env.set(node.variable, item)
                try: result = self._exec_block(node.body, env)
                except BreakSignal: break
                except ContinueSignal: continue

        elif isinstance(iterable, str):
            for i, ch in enumerate(iterable):
                if node.variable2:
                    env.set(node.variable, i)
                    env.set(node.variable2, ch)
                else:
                    env.set(node.variable, ch)
                try: result = self._exec_block(node.body, env)
                except BreakSignal: break
                except ContinueSignal: continue
        else:
            raise VoltRuntimeError(f"Cannot iterate over {self._type_name(iterable)}")
        return result

    def _exec_FuncDeclaration(self, node, env):
        func = VoltFunction(node.name, node.params, node.body, env)
        env.set(node.name, func)
        return func

    def _exec_ReturnStatement(self, node, env):
        value = None
        if node.value is not None:
            value = self.execute(node.value, env)
        raise ReturnSignal(value)

    def _exec_BreakStatement(self, node, env):
        raise BreakSignal()

    def _exec_ContinueStatement(self, node, env):
        raise ContinueSignal()

    def _exec_PushStatement(self, node, env):
        lst = self.execute(node.list_expr, env)
        value = self.execute(node.value, env)
        if not isinstance(lst, list):
            raise VoltRuntimeError("push requires a list")
        lst.append(value)
        return None

    def _exec_PopStatement(self, node, env):
        lst = self.execute(node.list_expr, env)
        if not isinstance(lst, list):
            raise VoltRuntimeError("pop requires a list")
        if not lst:
            raise VoltRuntimeError("Cannot pop from empty list")
        return lst.pop()

    # ── Classes ───────────────────────────────────────────

    def _exec_ClassDeclaration(self, node, env):
        parent = None
        if node.parent:
            parent = env.get(node.parent)
            if not isinstance(parent, VoltClass):
                raise VoltRuntimeError(f"'{node.parent}' is not a class")

        methods = {}
        for method_node in node.methods:
            fn = VoltFunction(method_node.name, method_node.params, method_node.body, env)
            methods[method_node.name] = fn

        klass = VoltClass(node.name, parent, methods, env)
        env.set(node.name, klass)
        return klass

    # ── Match / Switch ────────────────────────────────────

    def _exec_MatchStatement(self, node, env):
        value = self.execute(node.value, env)
        for case_expr, case_body in node.cases:
            case_val = self.execute(case_expr, env)
            if value == case_val:
                return self._exec_block(case_body, env)
        if node.default_body:
            return self._exec_block(node.default_body, env)
        return None

    # ── Try / Catch / Finally ─────────────────────────────

    def _exec_TryCatchStatement(self, node, env):
        result = None
        caught = False
        try:
            result = self._exec_block(node.try_body, env)
        except VoltThrowError as e:
            caught = True
            if node.catch_var and node.catch_body:
                catch_env = Environment(parent=env)
                catch_env.set(node.catch_var, e.value)
                result = self._exec_block(node.catch_body, catch_env)
        except VoltRuntimeError as e:
            caught = True
            if node.catch_var and node.catch_body:
                catch_env = Environment(parent=env)
                catch_env.set(node.catch_var, str(e))
                result = self._exec_block(node.catch_body, catch_env)
        finally:
            if node.finally_body:
                self._exec_block(node.finally_body, env)
        return result

    def _exec_ThrowStatement(self, node, env):
        value = self.execute(node.value, env)
        raise VoltThrowError(value)

    # ── Destructuring ─────────────────────────────────────

    def _exec_DestructureList(self, node, env):
        value = self.execute(node.value, env)
        if not isinstance(value, list):
            raise VoltRuntimeError("Cannot destructure non-list into list pattern")
        if len(node.names) > len(value):
            raise VoltRuntimeError(
                f"Not enough values to destructure: expected {len(node.names)}, got {len(value)}"
            )
        for i, name in enumerate(node.names):
            env.set(name, value[i])
        return None

    def _exec_DestructureDict(self, node, env):
        value = self.execute(node.value, env)
        if isinstance(value, VoltInstance):
            # Destructure from instance properties
            for name in node.names:
                if name in value.properties:
                    env.set(name, value.properties[name])
                else:
                    raise VoltRuntimeError(f"Property '{name}' not found on instance")
        elif isinstance(value, dict):
            for name in node.names:
                if name not in value:
                    raise VoltRuntimeError(f"Key '{name}' not found in dict")
                env.set(name, value[name])
        else:
            raise VoltRuntimeError("Cannot destructure non-dict into dict pattern")
        return None

    # ── Import / Use ──────────────────────────────────────

    def _exec_UseStatement(self, node, env):
        module_name = node.module_name

        # Built-in module
        if module_name in BUILTIN_MODULES:
            module = BUILTIN_MODULES[module_name]()
            env.set(module_name, module)
            return module

        # Import a .volt file
        filepath = module_name
        if not filepath.endswith('.volt'):
            filepath += '.volt'

        if not os.path.exists(filepath):
            raise VoltRuntimeError(f"Module not found: '{module_name}'")

        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        # Execute in a new environment (module scope)
        module_env = Environment(parent=self.global_env)
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        tree = parser.parse()

        for stmt in tree.statements:
            self.execute(stmt, module_env)

        # Create a module from the exported symbols
        base_name = os.path.splitext(os.path.basename(module_name))[0]
        module = VoltModule(base_name,
            properties=dict(module_env.variables),
            methods={k: (lambda fn: lambda args: self._call_volt_function(fn, args, module_env))(v)
                     for k, v in module_env.variables.items()
                     if isinstance(v, VoltFunction)}
        )
        env.set(base_name, module)
        return module

    # ═══════════════════════════════════════════════════════
    #  HELPERS
    # ═══════════════════════════════════════════════════════

    def _exec_block(self, statements, env):
        result = None
        for stmt in statements:
            result = self.execute(stmt, env)
        return result

    def _is_truthy(self, value):
        if value is None: return False
        if isinstance(value, bool): return value
        if isinstance(value, (int, float)): return value != 0
        if isinstance(value, str): return len(value) > 0
        if isinstance(value, list): return len(value) > 0
        if isinstance(value, dict): return len(value) > 0
        return True

    def _type_name(self, value):
        if value is None: return "null"
        if isinstance(value, bool): return "boolean"
        if isinstance(value, int): return "int"
        if isinstance(value, float): return "float"
        if isinstance(value, str): return "string"
        if isinstance(value, list): return "list"
        if isinstance(value, dict): return "dict"
        if isinstance(value, VoltFunction): return "function"
        if isinstance(value, VoltClass): return "class"
        if isinstance(value, VoltInstance): return value.klass.name
        if isinstance(value, VoltModule): return "module"
        return "unknown"

    def _to_string(self, value):
        if value is None: return "null"
        if isinstance(value, bool): return "true" if value else "false"
        if isinstance(value, float):
            if value == int(value): return str(int(value))
            return str(value)
        if isinstance(value, list):
            items = ", ".join(self._to_string(x) for x in value)
            return f"[{items}]"
        if isinstance(value, dict):
            pairs = ", ".join(
                f"{self._to_string(k)}: {self._to_string(v)}" for k, v in value.items()
            )
            return "{" + pairs + "}"
        if isinstance(value, VoltFunction): return repr(value)
        if isinstance(value, VoltClass): return repr(value)
        if isinstance(value, VoltInstance):
            # Check for toString method
            to_str = value.klass.find_method('toString')
            if to_str:
                method_env = Environment(parent=to_str.closure_env)
                method_env.set('this', value)
                method_env.set('__class__', value.klass)
                try:
                    self._exec_block(to_str.body, method_env)
                except ReturnSignal as ret:
                    return self._to_string(ret.value)
            return repr(value)
        if isinstance(value, VoltModule): return repr(value)
        return str(value)
