from errors import *
from tokens import *


# NODES
class NumberNode:
    def __init__(self, tok, pos_start=None, pos_end=None):
        self.tok = tok
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'{self.tok}'


class StringNode:
    def __init__(self, tok, pos_start=None, pos_end=None):
        self.tok = tok
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'{self.tok}'


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.pos_start = left_node.pos_start
        self.pos_end = right_node.pos_end
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class VarAssingNode:
    def __init__(self, name, value):
        self.name_tok = name
        self.value = value
        self.pos_start = value.pos_start
        self.pos_end = value.pos_end
    def __repr__(self):
        return f'({self.name_tok} = {self.value})'


class VarAccessNode:
    def __init__(self, name):
        self.name_tok = name
        self.pos_start = name.pos_start
        self.pos_end = name.pos_end
    def __repr__(self):
        return f'({self.name_tok})'


class IfNode:
    def __init__(self, cases, else_case, should_return_null):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end


class ForNode:
    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null
        self.pos_start = var_name_tok.pos_start
        self.pos_end = body_node.pos_end


class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null


class FunctionDefinitionNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node, should_auto_return):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node

        if self.var_name_tok:
            self.pos_start = self.body_node.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start
        self.pos_end = self.body_node.pos_end
        self.should_auto_return = should_auto_return
    def __repr__(self):
        return f'({self.var_name_tok} : {self.body_node.__repr__()})'


class CallNode:
    def __init__(self, node_to_call, arg_toks, name=None):
        self.name = name
        self.node_to_call = node_to_call
        self.arg_toks = arg_toks
        self.pos_start = self.node_to_call.pos_start
        if len(self.arg_toks) > 0:
            self.pos_end = self.arg_toks[len(self.arg_toks) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end
    def __repr__(self):
        return f'({self.node_to_call.__repr__()} : {self.arg_toks})'


class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end
    def __str__(self):
        return self.element_nodes
    def __repr__(self):
        return self.element_nodes.__repr__()

class ReturnNode:
    def __init__(self,node_to_return,pos_start,pos_end):
        self.node_to_return = node_to_return
        self.pos_start = pos_start
        self.pos_end = pos_end
    def __repr__(self):
        return f'({self.node_to_return})'

class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

# PARSE RESULT
class ParseResult:
    def __init__(self):
        self.advance_count = 0
        self.error = None
        self.node = None

    def register_advance(self):
        self.advance_count += 1

    def register(self, res):
        if res.error: self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = self.advance_count
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0: self.error = error
        return self


# PARSER
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_token = self.tokens[self.tok_idx]
        return self.current_token

    def reverse(self, amount=1):
        self.tok_idx -= amount
        if self.tok_idx < len(self.tokens):
            self.current_token = self.tokens[self.tok_idx]
        return self.current_token

    def parse(self):
        res = self.statements()
        if not res.error and self.current_token.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '+', '-', '*', '/' or '^'"
            ))
        return res

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_token.pos_start.copy()
        while self.current_token.type == TT_NEWLINE:
            res.register_advance()
            self.advance()
        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)
        more_statements = True
        while True:
            new_line_count = 0
            while self.current_token.type == TT_NEWLINE:
                res.register_advance()
                self.advance()
                new_line_count += 1
            if new_line_count == 0:
                more_statements = False
            if not more_statements:
                break
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)
        return res.success(ListNode(statements, pos_start, self.current_token.pos_end.copy()))
    def statement(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        if self.current_token.matches(TT_KEYWORD, "return"):
            res.register_advance()
            self.advance()
            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_token.pos_start.copy()))
        if self.current_token.matches(TT_KEYWORD, "continue"):
            res.register_advance()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_token.pos_start.copy()))
        if self.current_token.matches(TT_KEYWORD, "break"):
            res.register_advance()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_token.pos_start.copy()))
        expr = res.register(self.expr())
        if res.error:
            return res.failure(InvalidSyntaxError(pos_start, self.current_token.pos_end.copy(), "Expected Expression, 'return', 'break' or 'continue'"))
        return res.success(expr)
    def atom(self):
        res = ParseResult()
        tok = self.current_token

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advance()
            self.advance()
            return res.success(NumberNode(tok))
        elif tok.type == TT_STRING:
            res.register_advance()
            self.advance()
            return res.success(StringNode(tok))
        elif tok.type == TT_IDENTIFIER:
            res.register_advance()
            self.advance()
            return res.success(VarAccessNode(tok))
        elif tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(list_expr)
        elif tok.type == TT_LPAREN:
            res.register_advance()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_token.type == TT_RPAREN:
                res.register_advance()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ')'"
                ))
        elif tok.matches(TT_KEYWORD, 'if'):
            if_expr = res.register(self.if_expr())
            if res.error: return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "If expression invalid"))
            return res.success(if_expr)
        elif tok.matches(TT_KEYWORD, 'for'):
            for_expr = res.register(self.for_expr())
            if res.error: return res.failure(
                InvalidSyntaxError(tok.pos_start, tok.pos_end, "For loop expression invalid"))
            return res.success(for_expr)
        elif tok.matches(TT_KEYWORD, 'while'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)
        elif tok.matches(TT_KEYWORD, 'func'):
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)
        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, '+', '-', '('"
        ))

    def for_expr(self):
        res = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'for'):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'for'"
            ))

        res.register_advance()
        self.advance()

        if self.current_token.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected identifier"
            ))

        var_name = self.current_token
        res.register_advance()
        self.advance()

        if self.current_token.type != TT_EQUALS:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '='"
            ))

        res.register_advance()
        self.advance()

        start_value = res.register(self.expr())
        if res.error: return res

        if not self.current_token.matches(TT_KEYWORD, 'to'):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'to'"
            ))

        res.register_advance()
        self.advance()

        end_value = res.register(self.expr())
        if res.error: return res

        if self.current_token.matches(TT_KEYWORD, 'step'):
            res.register_advance()
            self.advance()

            step_value = res.register(self.expr())
            if res.error: return res
        else:
            step_value = None

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'then'"
            ))

        res.register_advance()
        self.advance()

        if self.current_token.matches(TT_NEWLINE):
            res.register_advance()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_token.matches(TT_KEYWORD, 'end'):
                return res.failure(
                    InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, 'Expected end'))
            res.register_advance()
            self.advance()
            return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))
        body = res.register(self.statement())
        if res.error: return res
        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def while_expr(self):
        res = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'while'):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'while'"
            ))

        res.register_advance()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'then'"
            ))

        res.register_advance()
        self.advance()
        if self.current_token.matches(TT_NEWLINE):
            res.register_advance()
            self.advance()
            body = res.register(self.statements())
            if res.error: return res
            if not self.current_token.matches(TT_KEYWORD, 'end'):
                return res.failure(
                    InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, 'Expected end'))
            res.register_advance()
            self.advance()
            return res.success(WhileNode(condition, body, True))
        body = res.register(self.statement())
        if res.error: return res

        return res.success(WhileNode(condition, body, False))

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases("if"))
        if res.error: return res
        cases, else_case = all_cases
        print(else_case)
        return res.success(IfNode(cases, else_case, True))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(TT_KEYWORD, case_keyword):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '{case_keyword}'"
            ))

        res.register_advance()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'then'"
            ))

        res.register_advance()
        self.advance()

        if self.current_token.type == TT_NEWLINE:
            res.register_advance()
            self.advance()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_token.matches(TT_KEYWORD, 'end'):
                res.register_advance()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error: return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.statement())
            if res.error: return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def if_expr_elif(self):
        return self.if_expr_cases("elif")

    def if_expr_else(self):
        res = ParseResult()
        else_case = None
        if self.current_token.matches(TT_KEYWORD, 'else'):
            res.register_advance()
            self.advance()
            if self.current_token.type == TT_NEWLINE:
                res.register_advance()
                self.advance()
            statements = res.register(self.statements())
            if res.error: return res
            else_case = (statements, True)
            if self.current_token.matches(TT_KEYWORD, 'end'):
                res.register_advance()
                self.advance()
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected 'end'"
                ))
        else:
            expr = res.register(self.statement())
            if res.error: return res
            else_case = (expr, False)
        return res.success(else_case)

    def power(self):
        return self.bin_op(self.call, (TT_POW,), self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.current_token

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advance()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV, TT_MODULO))

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def comp_expr(self):
        res = ParseResult()

        if self.current_token.matches(TT_KEYWORD, 'not'):
            op_tok = self.current_token
            res.register_advance()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected int, float, identifier, '+', '-', '(' or 'not'"
            ))

        return res.success(node)

    def expr(self):
        res = ParseResult()
        if self.current_token.matches(TT_KEYWORD, 'var'):
            res.register_advance()
            self.advance()

            if self.current_token.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected identifier"
                ))

            var_name = self.current_token
            res.register_advance()
            self.advance()

            if self.current_token.type != TT_EQUALS:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '='"
                ))

            res.register_advance()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssingNode(var_name, expr))

        node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))

        if res.error:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end,"Expected 'var', int, float, identifier, '+', '-', '(' or 'not'"))

        return res.success(node)

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a
        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
            op_tok = self.current_token
            res.register_advance()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)

    def func_def(self):
        res = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'func'):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'FUN'"
            ))

        res.register_advance()
        self.advance()

        if self.current_token.type == TT_IDENTIFIER:
            var_name_tok = self.current_token
            res.register_advance()
            self.advance()
            if self.current_token.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected '('"
                ))
        else:
            var_name_tok = None
            if self.current_token.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected identifier or '('"
                ))

        res.register_advance()
        self.advance()
        arg_name_toks = []

        if self.current_token.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_token)
            res.register_advance()
            self.advance()

            while self.current_token.type == TT_COMMA:
                res.register_advance()
                self.advance()

                if self.current_token.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Expected identifier"
                    ))

                arg_name_toks.append(self.current_token)
                res.register_advance()
                self.advance()

            if self.current_token.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.current_token.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected identifier or ')'"
                ))

        res.register_advance()
        self.advance()

        if self.current_token.type == TT_ARROW:
            res.register_advance()
            self.advance()

            body = res.register(self.expr())
            if res.error: return res

            return res.success(FunctionDefinitionNode(
                var_name_tok,
                arg_name_toks,
                body,
                True
            ))

        if self.current_token.type != TT_NEWLINE:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '->' or NEWLINE"
            ))

        res.register_advance()
        self.advance()

        body = res.register(self.statements())
        if res.error: return res

        if not self.current_token.matches(TT_KEYWORD, 'end'):
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'END'"
            ))

        res.register_advance()
        self.advance()

        return res.success(FunctionDefinitionNode(
            var_name_tok,
            arg_name_toks,
            body,
            False
        ))

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_token.type == TT_LPAREN:
            res.register_advance()
            self.advance()
            arg_nodes = []

            if self.current_token.type == TT_RPAREN:
                res.register_advance()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(' or 'NOT'"
                    ))

                while self.current_token.type == TT_COMMA:
                    res.register_advance()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_token.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Expected ',' or ')'"
                    ))

                res.register_advance()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_token.pos_start.copy()
        if self.current_token.type != TT_LSQUARE:
            return res.failure(InvalidSyntaxError(pos_start, self.current_token.pos_end, "Expected '['"))
        res.register_advance()
        self.advance()
        if self.current_token.type == TT_RSQUARE:
            res.register_advance()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ']', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(' or 'NOT'"
                ))

            while self.current_token.type == TT_COMMA:
                res.register_advance()
                self.advance()

                element_nodes.append(res.register(self.expr()))
                if res.error: return res

            if self.current_token.type != TT_RSQUARE:
                return res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected ',' or ']'"
                ))

            res.register_advance()
            self.advance()
        return res.success(ListNode(element_nodes, pos_start, self.current_token.pos_end.copy()))

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None
        if self.current_token.matches(TT_KEYWORD, "elif"):
            all_cases = res.register(self.if_expr_elif())
            if res.error: return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_else())
            if res.error: return res
        return res.success((cases, else_case))
