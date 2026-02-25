"""
Volt Language v2.0 - Parser
Converts a token stream into an Abstract Syntax Tree (AST).
Supports: OOP, dicts, lambdas, match, try/catch, destructuring, etc.
"""

from lexer import Lexer, TokenType
from ast_nodes import *


class ParserError(Exception):
    def __init__(self, message, token):
        self.token = token
        line = token.line if token else '?'
        col = token.column if token else '?'
        super().__init__(f"Parse Error at line {line}, col {col}: {message}")


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ── Helpers ───────────────────────────────────────────

    def current(self):
        return self.tokens[self.pos]

    def peek(self):
        return self.current().type

    def peek_ahead(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx].type
        return TokenType.EOF

    def at_end(self):
        return self.peek() == TokenType.EOF

    def advance(self):
        token = self.current()
        self.pos += 1
        return token

    def expect(self, token_type, message=None):
        if self.peek() != token_type:
            msg = message or f"Expected {token_type}, got {self.peek()}"
            raise ParserError(msg, self.current())
        return self.advance()

    def match(self, *types):
        if self.peek() in types:
            return self.advance()
        return None

    def skip_newlines(self):
        while not self.at_end() and self.peek() == TokenType.NEWLINE:
            self.advance()

    def _expect_property_name(self):
        """Accept IDENTIFIER or any keyword token as a property/method name after '.'."""
        tok = self.current()
        if tok.type == TokenType.IDENTIFIER:
            self.advance()
            return tok.value
        # Allow keywords to be used as property/method names
        from lexer import KEYWORDS
        keyword_types = set(KEYWORDS.values())
        if tok.type in keyword_types:
            self.advance()
            # For keywords, the value is the string form
            val = tok.value
            if isinstance(val, bool) or val is None:
                # true/false/null stored as Python bool/None, convert back
                return {True: 'true', False: 'false', None: 'null'}.get(val, str(val))
            return str(val)
        raise ParserError("Expected property name after '.'", tok)

    # ── Program ───────────────────────────────────────────

    def parse(self):
        statements = []
        self.skip_newlines()
        while not self.at_end():
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()
        return Program(statements)

    # ── Statements ────────────────────────────────────────

    def parse_statement(self):
        tt = self.peek()

        if tt == TokenType.SET:
            return self.parse_set()
        elif tt == TokenType.SHOW:
            return self.parse_show()
        elif tt == TokenType.ASK:
            return self.parse_ask()
        elif tt == TokenType.IF:
            return self.parse_if()
        elif tt == TokenType.WHILE:
            return self.parse_while()
        elif tt == TokenType.FOR:
            return self.parse_for()
        elif tt == TokenType.FUNC:
            return self.parse_func()
        elif tt == TokenType.RETURN:
            return self.parse_return()
        elif tt == TokenType.BREAK:
            self.advance()
            return BreakStatement()
        elif tt == TokenType.CONTINUE:
            self.advance()
            return ContinueStatement()
        elif tt == TokenType.PUSH:
            return self.parse_push()
        elif tt == TokenType.POP:
            return self.parse_pop()
        elif tt == TokenType.CLASS:
            return self.parse_class()
        elif tt == TokenType.MATCH:
            return self.parse_match()
        elif tt == TokenType.TRY:
            return self.parse_try()
        elif tt == TokenType.THROW:
            return self.parse_throw()
        elif tt == TokenType.USE:
            return self.parse_use()
        elif tt == TokenType.NEWLINE:
            self.advance()
            return None
        else:
            # Expression statement (function call, method call, etc.)
            expr = self.parse_expression()
            return expr

    # ── Set / Assignment ──────────────────────────────────

    def parse_set(self):
        self.expect(TokenType.SET)

        # Destructuring: set [a, b, c] = expr
        if self.peek() == TokenType.LBRACKET:
            return self._parse_destructure_list()

        # Destructuring: set {a, b} = expr
        if self.peek() == TokenType.LBRACE:
            return self._parse_destructure_dict()

        # Normal assignment: set target = value
        target = self._parse_assign_target()
        self.expect(TokenType.ASSIGN, "Expected '=' in assignment")
        value = self.parse_expression()
        return Assignment(target, value)

    def _parse_assign_target(self):
        """Parse the left-hand side of an assignment (identifier, dot, index chain)."""
        if self.peek() == TokenType.THIS:
            self.advance()
            result = ThisExpression()
        else:
            name = self.expect(TokenType.IDENTIFIER, "Expected variable name")
            result = Identifier(name.value)

        while self.peek() in (TokenType.DOT, TokenType.LBRACKET):
            if self.match(TokenType.DOT):
                prop_name = self._expect_property_name()
                result = DotAccess(result, prop_name)
            elif self.peek() == TokenType.LBRACKET:
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET, "Expected ']'")
                result = IndexAccess(result, index)
        return result

    def _parse_destructure_list(self):
        self.advance()  # consume [
        names = []
        names.append(self.expect(TokenType.IDENTIFIER).value)
        while self.match(TokenType.COMMA):
            names.append(self.expect(TokenType.IDENTIFIER).value)
        self.expect(TokenType.RBRACKET, "Expected ']' in destructuring")
        self.expect(TokenType.ASSIGN, "Expected '=' in destructuring")
        value = self.parse_expression()
        return DestructureList(names, value)

    def _parse_destructure_dict(self):
        self.advance()  # consume {
        names = []
        names.append(self.expect(TokenType.IDENTIFIER).value)
        while self.match(TokenType.COMMA):
            if self.peek() == TokenType.RBRACE:
                break
            names.append(self.expect(TokenType.IDENTIFIER).value)
        self.expect(TokenType.RBRACE, "Expected '}' in destructuring")
        self.expect(TokenType.ASSIGN, "Expected '=' in destructuring")
        value = self.parse_expression()
        return DestructureDict(names, value)

    # ── Simple Statements ─────────────────────────────────

    def parse_show(self):
        self.expect(TokenType.SHOW)
        expr = self.parse_expression()
        return ShowStatement(expr)

    def parse_ask(self):
        self.expect(TokenType.ASK)
        prompt = self.parse_expression()
        self.expect(TokenType.ARROW, "Expected '->' after prompt")
        name = self.expect(TokenType.IDENTIFIER, "Expected variable name after '->'")
        return AskStatement(prompt, name.value)

    def parse_push(self):
        self.expect(TokenType.PUSH)
        list_expr = self.parse_primary()
        # Handle dot/index access on the list target
        while self.peek() in (TokenType.DOT, TokenType.LBRACKET):
            if self.match(TokenType.DOT):
                prop_name = self._expect_property_name()
                list_expr = DotAccess(list_expr, prop_name)
            elif self.peek() == TokenType.LBRACKET:
                self.advance()
                idx = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                list_expr = IndexAccess(list_expr, idx)
        value = self.parse_expression()
        return PushStatement(list_expr, value)

    def parse_pop(self):
        self.expect(TokenType.POP)
        list_expr = self.parse_primary()
        while self.peek() in (TokenType.DOT, TokenType.LBRACKET):
            if self.match(TokenType.DOT):
                prop_name = self._expect_property_name()
                list_expr = DotAccess(list_expr, prop_name)
            elif self.peek() == TokenType.LBRACKET:
                self.advance()
                idx = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                list_expr = IndexAccess(list_expr, idx)
        return PopStatement(list_expr)

    def parse_throw(self):
        self.expect(TokenType.THROW)
        value = self.parse_expression()
        return ThrowStatement(value)

    def parse_use(self):
        self.expect(TokenType.USE)
        name_token = self.expect(TokenType.STRING, "Expected module name string after 'use'")
        return UseStatement(name_token.value)

    # ── If / Elif / Else ──────────────────────────────────

    def parse_if(self):
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        body = self.parse_block()

        elif_clauses = []
        self.skip_newlines()
        while not self.at_end() and self.peek() == TokenType.ELSE:
            # Check if it's 'else if' (not plain 'else')
            next_idx = self.pos + 1
            # Skip newlines after 'else' to find 'if'
            while next_idx < len(self.tokens) and self.tokens[next_idx].type == TokenType.NEWLINE:
                next_idx += 1
            if next_idx < len(self.tokens) and self.tokens[next_idx].type == TokenType.IF:
                self.advance()  # consume 'else'
                # skip newlines between else and if
                self.skip_newlines()
                self.advance()  # consume 'if'
                elif_cond = self.parse_expression()
                elif_body = self.parse_block()
                elif_clauses.append((elif_cond, elif_body))
                self.skip_newlines()
            else:
                break

        else_body = None
        if not self.at_end() and self.peek() == TokenType.ELSE:
            self.advance()
            else_body = self.parse_block()

        return IfStatement(condition, body, elif_clauses, else_body)

    # ── Loops ─────────────────────────────────────────────

    def parse_while(self):
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        body = self.parse_block()
        return WhileStatement(condition, body)

    def parse_for(self):
        self.expect(TokenType.FOR)

        # Case 1: for <ident> ... (could be range, iterate, or N-times via ident)
        if self.peek() == TokenType.IDENTIFIER:
            saved_pos = self.pos
            name_token = self.advance()

            # for name in ... (range or iterate)
            if self.peek() == TokenType.IN:
                self.advance()  # consume 'in'
                expr1 = self.parse_expression()

                # for i in <start> to <end> { ... }  (range)
                if self.peek() == TokenType.TO:
                    self.advance()  # consume 'to'
                    expr2 = self.parse_expression()
                    body = self.parse_block()
                    return LoopRangeStatement(name_token.value, expr1, expr2, body)

                # for item in <iterable> { ... }  (iterate)
                body = self.parse_block()
                return ForInStatement(name_token.value, None, expr1, body)

            # for name, name2 in <iterable> { ... }  (iterate with index/key)
            if self.peek() == TokenType.COMMA:
                self.advance()  # consume comma
                name2_tok = self.expect(TokenType.IDENTIFIER, "Expected second variable name")
                self.expect(TokenType.IN, "Expected 'in' after variables in for loop")
                iterable = self.parse_expression()
                body = self.parse_block()
                return ForInStatement(name_token.value, name2_tok.value, iterable, body)

            # Not a range or iterate — backtrack and parse as N-times
            self.pos = saved_pos

        # Case 2: for <expr> { ... }  (repeat N times)
        count = self.parse_expression()
        body = self.parse_block()
        return LoopTimesStatement(count, body)

    # ── Functions ─────────────────────────────────────────

    def parse_func(self):
        self.expect(TokenType.FUNC)
        name_val = self._expect_property_name()  # Allow keywords as function names (e.g. push, pop)
        self.expect(TokenType.LPAREN, "Expected '(' after function name")
        params = self._parse_param_list()
        self.expect(TokenType.RPAREN, "Expected ')' after parameters")
        body = self.parse_block()
        return FuncDeclaration(name_val, params, body)

    def _parse_param_list(self):
        """Parse function parameters with optional default values."""
        params = []
        if self.peek() == TokenType.RPAREN:
            return params

        params.append(self._parse_single_param())
        while self.match(TokenType.COMMA):
            params.append(self._parse_single_param())
        return params

    def _parse_single_param(self):
        name = self.expect(TokenType.IDENTIFIER, "Expected parameter name").value
        default = None
        if self.match(TokenType.ASSIGN):
            default = self.parse_expression()
        return (name, default)

    def parse_return(self):
        self.expect(TokenType.RETURN)
        value = None
        if self.peek() not in (TokenType.NEWLINE, TokenType.EOF, TokenType.RBRACE):
            value = self.parse_expression()
        return ReturnStatement(value)

    # ── Classes ───────────────────────────────────────────

    def parse_class(self):
        self.expect(TokenType.CLASS)
        name = self.expect(TokenType.IDENTIFIER, "Expected class name")
        parent = None
        if self.match(TokenType.EXTENDS):
            parent = self.expect(TokenType.IDENTIFIER, "Expected parent class name").value

        self.skip_newlines()
        self.expect(TokenType.LBRACE, "Expected '{' in class declaration")
        self.skip_newlines()

        methods = []
        while not self.at_end() and self.peek() != TokenType.RBRACE:
            if self.peek() == TokenType.FUNC:
                methods.append(self.parse_func())
            elif self.peek() == TokenType.NEWLINE:
                self.advance()
            else:
                raise ParserError("Expected method declaration in class body", self.current())
            self.skip_newlines()

        self.expect(TokenType.RBRACE, "Expected '}' after class body")
        return ClassDeclaration(name.value, parent, methods)

    # ── Match / Switch ────────────────────────────────────

    def parse_match(self):
        self.expect(TokenType.MATCH)
        value = self.parse_expression()

        self.skip_newlines()
        self.expect(TokenType.LBRACE, "Expected '{' after match expression")
        self.skip_newlines()

        cases = []
        default_body = None

        while not self.at_end() and self.peek() != TokenType.RBRACE:
            if self.peek() == TokenType.CASE:
                self.advance()
                case_value = self.parse_expression()
                case_body = self.parse_block()
                cases.append((case_value, case_body))
            elif self.peek() == TokenType.DEFAULT:
                self.advance()
                default_body = self.parse_block()
            elif self.peek() == TokenType.NEWLINE:
                self.advance()
            else:
                raise ParserError("Expected 'case' or 'default' in match", self.current())
            self.skip_newlines()

        self.expect(TokenType.RBRACE, "Expected '}' after match body")
        return MatchStatement(value, cases, default_body)

    # ── Try / Catch / Finally ─────────────────────────────

    def parse_try(self):
        self.expect(TokenType.TRY)
        try_body = self.parse_block()

        self.skip_newlines()
        catch_var = None
        catch_body = None
        finally_body = None

        if not self.at_end() and self.peek() == TokenType.CATCH:
            self.advance()
            catch_var = self.expect(TokenType.IDENTIFIER, "Expected variable name after 'catch'").value
            catch_body = self.parse_block()

        self.skip_newlines()
        if not self.at_end() and self.peek() == TokenType.FINALLY:
            self.advance()
            finally_body = self.parse_block()

        if catch_body is None and finally_body is None:
            raise ParserError("Expected 'catch' or 'finally' after try block", self.current())

        return TryCatchStatement(try_body, catch_var, catch_body, finally_body)

    # ── Block ─────────────────────────────────────────────

    def parse_block(self):
        self.skip_newlines()
        self.expect(TokenType.LBRACE, "Expected '{'")
        self.skip_newlines()

        statements = []
        while not self.at_end() and self.peek() != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()

        self.expect(TokenType.RBRACE, "Expected '}'")
        return statements

    # ═══════════════════════════════════════════════════════
    #  EXPRESSION PARSING (Precedence Climbing)
    # ═══════════════════════════════════════════════════════

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.match(TokenType.OR):
            right = self.parse_and()
            left = BinaryOp('or', left, right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.match(TokenType.AND):
            right = self.parse_not()
            left = BinaryOp('and', left, right)
        return left

    def parse_not(self):
        if self.match(TokenType.NOT):
            operand = self.parse_not()
            return UnaryOp('not', operand)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_addition()
        while self.peek() in (TokenType.EQ, TokenType.NEQ, TokenType.LT,
                               TokenType.GT, TokenType.LTE, TokenType.GTE):
            op = self.advance().value
            right = self.parse_addition()
            left = BinaryOp(op, left, right)
        return left

    def parse_addition(self):
        left = self.parse_multiplication()
        while self.peek() in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplication()
            left = BinaryOp(op, left, right)
        return left

    def parse_multiplication(self):
        left = self.parse_unary()
        while self.peek() in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.advance().value
            right = self.parse_unary()
            left = BinaryOp(op, left, right)
        return left

    def parse_unary(self):
        if self.match(TokenType.MINUS):
            operand = self.parse_unary()
            return UnaryOp('-', operand)
        return self.parse_postfix()

    def parse_postfix(self):
        """Handle dot access, method calls, indexing, and function calls."""
        expr = self.parse_primary()

        while True:
            if self.peek() == TokenType.DOT:
                self.advance()  # consume .
                prop_name = self._expect_property_name()

                if self.peek() == TokenType.LPAREN:
                    # Method call: obj.method(args)
                    self.advance()
                    args = self._parse_arg_list()
                    expr = MethodCall(expr, prop_name, args)
                else:
                    # Property access: obj.property
                    expr = DotAccess(expr, prop_name)

            elif self.peek() == TokenType.LBRACKET:
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET, "Expected ']'")
                expr = IndexAccess(expr, index)

            elif self.peek() == TokenType.LPAREN:
                if isinstance(expr, Identifier):
                    self.advance()
                    args = self._parse_arg_list()
                    expr = FunctionCall(expr.name, args)
                elif isinstance(expr, (IndexAccess, CallExpression, DotAccess)):
                    # Calling result of expression: expr(args)
                    self.advance()
                    args = self._parse_arg_list()
                    expr = CallExpression(expr, args)
                else:
                    break
            else:
                break

        return expr

    def _parse_arg_list(self):
        """Parse comma-separated arguments until ')'. Expects '(' already consumed."""
        args = []
        if self.peek() != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                args.append(self.parse_expression())
        self.expect(TokenType.RPAREN, "Expected ')'")
        return args

    # ── Primary Expressions ───────────────────────────────

    def parse_primary(self):
        # Number
        if self.peek() == TokenType.NUMBER:
            return NumberLiteral(self.advance().value)

        # String
        if self.peek() == TokenType.STRING:
            return StringLiteral(self.advance().value)

        # Interpolated string
        if self.peek() == TokenType.INTERP_STRING:
            return self._parse_interp_string()

        # Boolean
        if self.peek() == TokenType.TRUE:
            self.advance()
            return BooleanLiteral(True)
        if self.peek() == TokenType.FALSE:
            self.advance()
            return BooleanLiteral(False)

        # Null
        if self.peek() == TokenType.NULL:
            self.advance()
            return NullLiteral()

        # This
        if self.peek() == TokenType.THIS:
            self.advance()
            return ThisExpression()

        # Super
        if self.peek() == TokenType.SUPER:
            self.advance()
            self.expect(TokenType.DOT, "Expected '.' after 'super'")
            method = self.expect(TokenType.IDENTIFIER, "Expected method name after 'super.'")
            self.expect(TokenType.LPAREN, "Expected '(' after super method name")
            args = self._parse_arg_list()
            return SuperMethodCall(method.value, args)

        # New
        if self.peek() == TokenType.NEW:
            self.advance()
            class_name = self.expect(TokenType.IDENTIFIER, "Expected class name after 'new'")
            self.expect(TokenType.LPAREN, "Expected '(' after class name")
            args = self._parse_arg_list()
            return NewExpression(class_name.value, args)

        # Identifier (or lambda without parens - handled after)
        if self.peek() == TokenType.IDENTIFIER:
            return Identifier(self.advance().value)

        # List literal [...]
        if self.peek() == TokenType.LBRACKET:
            return self._parse_list_literal()

        # Dict literal {...}
        if self.peek() == TokenType.LBRACE:
            return self._parse_dict_literal()

        # Grouped expression or lambda: (...) or (params) => expr
        if self.peek() == TokenType.LPAREN:
            return self._parse_paren_or_lambda()

        raise ParserError(
            f"Unexpected token: {self.current().type} ({self.current().value!r})",
            self.current()
        )

    def _parse_interp_string(self):
        """Parse an interpolated string into a chain of concatenation."""
        token = self.advance()
        parts_data = token.value  # list of ('text', str) or ('expr', str)
        nodes = []

        for ptype, pvalue in parts_data:
            if ptype == 'text':
                if pvalue:
                    nodes.append(StringLiteral(pvalue))
            elif ptype == 'expr':
                sub_lexer = Lexer(pvalue)
                sub_tokens = sub_lexer.tokenize()
                sub_parser = Parser(sub_tokens)
                expr_node = sub_parser.parse_expression()
                nodes.append(expr_node)

        if not nodes:
            return StringLiteral("")

        result = nodes[0]
        for node in nodes[1:]:
            result = BinaryOp('+', result, node)
        return StringInterpolation([result] if len(nodes) == 1 else nodes)

    def _parse_list_literal(self):
        self.advance()  # consume [
        elements = []
        self.skip_newlines()
        if self.peek() != TokenType.RBRACKET:
            elements.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.skip_newlines()
                if self.peek() == TokenType.RBRACKET:
                    break
                elements.append(self.parse_expression())
        self.skip_newlines()
        self.expect(TokenType.RBRACKET, "Expected ']'")
        return ListLiteral(elements)

    def _parse_dict_literal(self):
        self.advance()  # consume {
        self.skip_newlines()
        pairs = []
        if self.peek() != TokenType.RBRACE:
            pairs.append(self._parse_dict_entry())
            while self.match(TokenType.COMMA):
                self.skip_newlines()
                if self.peek() == TokenType.RBRACE:
                    break
                pairs.append(self._parse_dict_entry())
        self.skip_newlines()
        self.expect(TokenType.RBRACE, "Expected '}'")
        return DictLiteral(pairs)

    def _parse_dict_entry(self):
        self.skip_newlines()
        # Bare identifier as key: {name: "Alice"}
        if self.peek() == TokenType.IDENTIFIER and self.peek_ahead() == TokenType.COLON:
            key = StringLiteral(self.advance().value)
        else:
            key = self.parse_expression()
        self.expect(TokenType.COLON, "Expected ':' in dictionary entry")
        value = self.parse_expression()
        return (key, value)

    def _parse_paren_or_lambda(self):
        """Distinguish between (expr), () => expr, and (params) => expr."""
        saved_pos = self.pos
        self.advance()  # consume (

        # () => expr (empty lambda)
        if self.peek() == TokenType.RPAREN:
            self.advance()  # consume )
            if self.peek() == TokenType.FAT_ARROW:
                self.advance()  # consume =>
                body = self.parse_expression()
                return LambdaExpression([], body)
            # Not a lambda, restore and parse as grouped
            self.pos = saved_pos
            self.advance()
            self.advance()  # skip ()
            # Actually this is just () which is weird, let's restore fully
            self.pos = saved_pos
            self.advance()  # consume (
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN, "Expected ')'")
            return expr

        # Check if this looks like a lambda: (ident, ident, ...) =>
        if self.peek() == TokenType.IDENTIFIER:
            # Try parsing as lambda parameter list
            try:
                return self._try_parse_lambda(saved_pos)
            except (ParserError, IndexError):
                self.pos = saved_pos
                self.advance()  # consume (
                expr = self.parse_expression()
                self.expect(TokenType.RPAREN, "Expected ')'")
                return expr

        # Regular grouped expression
        expr = self.parse_expression()
        self.expect(TokenType.RPAREN, "Expected ')'")
        return expr

    def _try_parse_lambda(self, saved_pos):
        """Try to parse (params) => expr. Raises if not a lambda."""
        # We've consumed '(' and next is IDENTIFIER
        params = []
        param = self._parse_single_param()
        params.append(param)

        while self.peek() == TokenType.COMMA:
            self.advance()
            params.append(self._parse_single_param())

        if self.peek() != TokenType.RPAREN:
            raise ParserError("Not a lambda", self.current())

        self.advance()  # consume )

        if self.peek() != TokenType.FAT_ARROW:
            raise ParserError("Not a lambda", self.current())

        self.advance()  # consume =>

        # Lambda body: single expression
        body = self.parse_expression()
        return LambdaExpression(params, body)
