"""
Volt Language v2.0 - Standard Library Modules
Built-in modules: math, random, time, file
Loaded via 'use "math"' etc.
"""

import math as _math
import random as _random
import time as _time
import os as _os
import datetime as _datetime


class VoltModule:
    """A module object accessible via dot notation."""
    def __init__(self, name, properties=None, methods=None):
        self.name = name
        self.properties = properties or {}
        self.methods = methods or {}

    def get_property(self, name):
        if name in self.properties:
            return self.properties[name]
        if name in self.methods:
            return self.methods[name]
        raise KeyError(f"Module '{self.name}' has no property '{name}'")

    def call_method(self, name, args):
        if name in self.methods:
            return self.methods[name](args)
        raise KeyError(f"Module '{self.name}' has no method '{name}'")

    def __repr__(self):
        return f"<module '{self.name}'>"


def _check_args(name, args, min_count, max_count=None):
    if max_count is None:
        max_count = min_count
    if len(args) < min_count or len(args) > max_count:
        if min_count == max_count:
            raise RuntimeError(f"{name}() takes exactly {min_count} argument(s), got {len(args)}")
        raise RuntimeError(f"{name}() takes {min_count}-{max_count} arguments, got {len(args)}")


# ═══════════════════════════════════════════════════════════
#  MATH MODULE
# ═══════════════════════════════════════════════════════════

def create_math_module():
    return VoltModule("math",
        properties={
            'pi': _math.pi,
            'e': _math.e,
            'inf': _math.inf,
            'nan': _math.nan,
            'tau': _math.tau,
        },
        methods={
            'sqrt':  lambda a: (_check_args('math.sqrt', a, 1), _math.sqrt(a[0]))[1],
            'pow':   lambda a: (_check_args('math.pow', a, 2), _math.pow(a[0], a[1]))[1],
            'abs':   lambda a: (_check_args('math.abs', a, 1), abs(a[0]))[1],
            'floor': lambda a: (_check_args('math.floor', a, 1), _math.floor(a[0]))[1],
            'ceil':  lambda a: (_check_args('math.ceil', a, 1), _math.ceil(a[0]))[1],
            'round': lambda a: round(a[0]) if len(a) == 1 else round(a[0], int(a[1])),
            'min':   lambda a: min(a[0]) if len(a) == 1 and isinstance(a[0], list) else min(a),
            'max':   lambda a: max(a[0]) if len(a) == 1 and isinstance(a[0], list) else max(a),
            'sin':   lambda a: (_check_args('math.sin', a, 1), _math.sin(a[0]))[1],
            'cos':   lambda a: (_check_args('math.cos', a, 1), _math.cos(a[0]))[1],
            'tan':   lambda a: (_check_args('math.tan', a, 1), _math.tan(a[0]))[1],
            'asin':  lambda a: (_check_args('math.asin', a, 1), _math.asin(a[0]))[1],
            'acos':  lambda a: (_check_args('math.acos', a, 1), _math.acos(a[0]))[1],
            'atan':  lambda a: (_check_args('math.atan', a, 1), _math.atan(a[0]))[1],
            'log':   lambda a: _math.log(a[0]) if len(a) == 1 else _math.log(a[0], a[1]),
            'log10': lambda a: (_check_args('math.log10', a, 1), _math.log10(a[0]))[1],
            'log2':  lambda a: (_check_args('math.log2', a, 1), _math.log2(a[0]))[1],
            'exp':   lambda a: (_check_args('math.exp', a, 1), _math.exp(a[0]))[1],
            'gcd':   lambda a: (_check_args('math.gcd', a, 2), _math.gcd(int(a[0]), int(a[1])))[1],
            'radians': lambda a: (_check_args('math.radians', a, 1), _math.radians(a[0]))[1],
            'degrees': lambda a: (_check_args('math.degrees', a, 1), _math.degrees(a[0]))[1],
            'hypot': lambda a: (_check_args('math.hypot', a, 2), _math.hypot(a[0], a[1]))[1],
        }
    )


# ═══════════════════════════════════════════════════════════
#  RANDOM MODULE
# ═══════════════════════════════════════════════════════════

def create_random_module():
    rng = _random.Random()

    def rand_int(args):
        _check_args('random.int', args, 2)
        return rng.randint(int(args[0]), int(args[1]))

    def rand_float(args):
        if len(args) == 0:
            return rng.random()
        elif len(args) == 2:
            return rng.uniform(args[0], args[1])
        raise RuntimeError("random.float() takes 0 or 2 arguments")

    def rand_choice(args):
        _check_args('random.choice', args, 1)
        lst = args[0]
        if not isinstance(lst, list):
            raise RuntimeError("random.choice() requires a list")
        return rng.choice(lst)

    def rand_shuffle(args):
        _check_args('random.shuffle', args, 1)
        lst = args[0]
        if not isinstance(lst, list):
            raise RuntimeError("random.shuffle() requires a list")
        shuffled = lst[:]
        rng.shuffle(shuffled)
        return shuffled

    def rand_seed(args):
        _check_args('random.seed', args, 1)
        rng.seed(args[0])
        return None

    def rand_range(args):
        if len(args) == 1:
            return rng.randrange(int(args[0]))
        elif len(args) == 2:
            return rng.randrange(int(args[0]), int(args[1]))
        elif len(args) == 3:
            return rng.randrange(int(args[0]), int(args[1]), int(args[2]))
        raise RuntimeError("random.range() takes 1-3 arguments")

    return VoltModule("random",
        methods={
            'int':     rand_int,
            'float':   rand_float,
            'choice':  rand_choice,
            'shuffle': rand_shuffle,
            'seed':    rand_seed,
            'range':   rand_range,
            'bool':    lambda a: rng.choice([True, False]),
        }
    )


# ═══════════════════════════════════════════════════════════
#  TIME MODULE
# ═══════════════════════════════════════════════════════════

def create_time_module():
    def time_now(args):
        return _time.time()

    def time_sleep(args):
        _check_args('time.sleep', args, 1)
        _time.sleep(args[0])
        return None

    def time_clock(args):
        return _time.perf_counter()

    def time_date(args):
        if len(args) == 0:
            return _datetime.datetime.now().strftime('%Y-%m-%d')
        _check_args('time.date', args, 0, 1)
        return _datetime.datetime.fromtimestamp(args[0]).strftime('%Y-%m-%d')

    def time_timestamp(args):
        return _time.time()

    def time_year(args):
        return _datetime.datetime.now().year

    def time_month(args):
        return _datetime.datetime.now().month

    def time_day(args):
        return _datetime.datetime.now().day

    def time_hour(args):
        return _datetime.datetime.now().hour

    def time_minute(args):
        return _datetime.datetime.now().minute

    def time_second(args):
        return _datetime.datetime.now().second

    def time_format(args):
        if len(args) == 1:
            return _datetime.datetime.now().strftime(args[0])
        elif len(args) == 2:
            return _datetime.datetime.fromtimestamp(args[0]).strftime(args[1])
        raise RuntimeError("time.format() takes 1-2 arguments")

    def time_datetime(args):
        now = _datetime.datetime.now()
        return {
            "year": now.year, "month": now.month, "day": now.day,
            "hour": now.hour, "minute": now.minute, "second": now.second
        }

    def time_elapsed(args):
        """Measure elapsed time. Call with no args to start, call with start time to get elapsed."""
        if len(args) == 0:
            return _time.perf_counter()
        return _time.perf_counter() - args[0]

    return VoltModule("time",
        methods={
            'now':       time_now,
            'sleep':     time_sleep,
            'clock':     time_clock,
            'date':      time_date,
            'timestamp': time_timestamp,
            'year':      time_year,
            'month':     time_month,
            'day':       time_day,
            'hour':      time_hour,
            'minute':    time_minute,
            'second':    time_second,
            'format':    time_format,
            'datetime':  time_datetime,
            'elapsed':   time_elapsed,
        }
    )


# ═══════════════════════════════════════════════════════════
#  FILE MODULE
# ═══════════════════════════════════════════════════════════

def create_file_module():
    def file_read(args):
        _check_args('file.read', args, 1)
        path = str(args[0])
        if not _os.path.exists(path):
            raise RuntimeError(f"File not found: '{path}'")
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def file_write(args):
        _check_args('file.write', args, 2)
        path, data = str(args[0]), str(args[1])
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
        return None

    def file_append(args):
        _check_args('file.append', args, 2)
        path, data = str(args[0]), str(args[1])
        with open(path, 'a', encoding='utf-8') as f:
            f.write(data)
        return None

    def file_exists(args):
        _check_args('file.exists', args, 1)
        return _os.path.exists(str(args[0]))

    def file_delete(args):
        _check_args('file.delete', args, 1)
        path = str(args[0])
        if _os.path.exists(path):
            _os.remove(path)
        return None

    def file_list(args):
        _check_args('file.list', args, 1)
        path = str(args[0])
        if not _os.path.isdir(path):
            raise RuntimeError(f"Not a directory: '{path}'")
        return _os.listdir(path)

    def file_readlines(args):
        _check_args('file.readlines', args, 1)
        path = str(args[0])
        if not _os.path.exists(path):
            raise RuntimeError(f"File not found: '{path}'")
        with open(path, 'r', encoding='utf-8') as f:
            return [line.rstrip('\n') for line in f.readlines()]

    def file_size(args):
        _check_args('file.size', args, 1)
        path = str(args[0])
        if not _os.path.exists(path):
            raise RuntimeError(f"File not found: '{path}'")
        return _os.path.getsize(path)

    def file_isdir(args):
        _check_args('file.isdir', args, 1)
        return _os.path.isdir(str(args[0]))

    def file_isfile(args):
        _check_args('file.isfile', args, 1)
        return _os.path.isfile(str(args[0]))

    def file_mkdir(args):
        _check_args('file.mkdir', args, 1)
        _os.makedirs(str(args[0]), exist_ok=True)
        return None

    def file_copy(args):
        _check_args('file.copy', args, 2)
        import shutil
        shutil.copy2(str(args[0]), str(args[1]))
        return None

    def file_rename(args):
        _check_args('file.rename', args, 2)
        _os.rename(str(args[0]), str(args[1]))
        return None

    return VoltModule("file",
        methods={
            'read':      file_read,
            'write':     file_write,
            'append':    file_append,
            'exists':    file_exists,
            'delete':    file_delete,
            'list':      file_list,
            'readlines': file_readlines,
            'size':      file_size,
            'isdir':     file_isdir,
            'isfile':    file_isfile,
            'mkdir':     file_mkdir,
            'copy':      file_copy,
            'rename':    file_rename,
        }
    )


# ═══════════════════════════════════════════════════════════
#  MODULE REGISTRY
# ═══════════════════════════════════════════════════════════

BUILTIN_MODULES = {
    'math':   create_math_module,
    'random': create_random_module,
    'time':   create_time_module,
    'file':   create_file_module,
}
