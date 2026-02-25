"""
Volt Language v2.0 - AST Node Definitions
Supports: OOP, dictionaries, lambdas, match/switch, try/catch,
          destructuring, method chaining, string interpolation, modules.
"""


class ASTNode:
    pass


# ── Literals ──────────────────────────────────────────────

class NumberLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

class StringLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

class BooleanLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

class NullLiteral(ASTNode):
    pass

class ListLiteral(ASTNode):
    def __init__(self, elements):
        self.elements = elements

class DictLiteral(ASTNode):
    def __init__(self, pairs):
        self.pairs = pairs  # list of (key_node, value_node)


# ── Identifiers & Access ─────────────────────────────────

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

class IndexAccess(ASTNode):
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index

class DotAccess(ASTNode):
    def __init__(self, obj, property):
        self.obj = obj
        self.property = property

class ThisExpression(ASTNode):
    pass

class SuperMethodCall(ASTNode):
    def __init__(self, method, args):
        self.method = method
        self.args = args


# ── Expressions ───────────────────────────────────────────

class BinaryOp(ASTNode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnaryOp(ASTNode):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class FunctionCall(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class MethodCall(ASTNode):
    def __init__(self, obj, method, args):
        self.obj = obj
        self.method = method
        self.args = args

class CallExpression(ASTNode):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

class NewExpression(ASTNode):
    def __init__(self, class_name, args):
        self.class_name = class_name
        self.args = args

class LambdaExpression(ASTNode):
    def __init__(self, params, body):
        self.params = params
        self.body = body

class StringInterpolation(ASTNode):
    def __init__(self, parts):
        self.parts = parts


# ── Statements ────────────────────────────────────────────

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class Assignment(ASTNode):
    def __init__(self, target, value):
        self.target = target
        self.value = value

class ShowStatement(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class AskStatement(ASTNode):
    def __init__(self, prompt, variable):
        self.prompt = prompt
        self.variable = variable

class IfStatement(ASTNode):
    def __init__(self, condition, body, elif_clauses, else_body):
        self.condition = condition
        self.body = body
        self.elif_clauses = elif_clauses
        self.else_body = else_body

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class LoopTimesStatement(ASTNode):
    def __init__(self, count, body):
        self.count = count
        self.body = body

class LoopRangeStatement(ASTNode):
    def __init__(self, variable, start, end, body):
        self.variable = variable
        self.start = start
        self.end = end
        self.body = body

class ForInStatement(ASTNode):
    def __init__(self, variable, variable2, iterable, body):
        self.variable = variable
        self.variable2 = variable2
        self.iterable = iterable
        self.body = body

class FuncDeclaration(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params  # list of (name, default_node_or_None)
        self.body = body

class ReturnStatement(ASTNode):
    def __init__(self, value):
        self.value = value

class BreakStatement(ASTNode):
    pass

class ContinueStatement(ASTNode):
    pass

class PushStatement(ASTNode):
    def __init__(self, list_expr, value):
        self.list_expr = list_expr
        self.value = value

class PopStatement(ASTNode):
    def __init__(self, list_expr):
        self.list_expr = list_expr


# ── OOP ───────────────────────────────────────────────────

class ClassDeclaration(ASTNode):
    def __init__(self, name, parent, methods):
        self.name = name
        self.parent = parent
        self.methods = methods


# ── Match / Switch ────────────────────────────────────────

class MatchStatement(ASTNode):
    def __init__(self, value, cases, default_body):
        self.value = value
        self.cases = cases
        self.default_body = default_body


# ── Try / Catch / Finally ────────────────────────────────

class TryCatchStatement(ASTNode):
    def __init__(self, try_body, catch_var, catch_body, finally_body):
        self.try_body = try_body
        self.catch_var = catch_var
        self.catch_body = catch_body
        self.finally_body = finally_body

class ThrowStatement(ASTNode):
    def __init__(self, value):
        self.value = value


# ── Destructuring ─────────────────────────────────────────

class DestructureList(ASTNode):
    def __init__(self, names, value):
        self.names = names
        self.value = value

class DestructureDict(ASTNode):
    def __init__(self, names, value):
        self.names = names
        self.value = value


# ── Import ────────────────────────────────────────────────

class UseStatement(ASTNode):
    def __init__(self, module_name):
        self.module_name = module_name
