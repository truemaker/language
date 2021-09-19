# IMPORTS
from strings_with_arrows import *
from errors import *
from parser import Parser
from tokens import *
from constants import *
import math
import os
# Runtime Result
class RuntimeResult:
    def __init__(self):
        self.value = None
        self.error = None
    def register(self, res):
        if res.error: self.error = res.error
        return res.value
    def success(self, value):
        self.value = value
        return self
    def failure(self, error):
        self.error = error
        return self

# CONTEXT
class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

# Values
class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation()

    def execute(self, args):
        return RuntimeResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other: other = self
        return RTError(
            self.pos_start, other.pos_end,
            'Illegal operation',
            self.context
        )

class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Number):
            try:
                return Number(self.value + other.value).set_context(self.context), None
            except TypeError:
                return None, self.illegal_operation(other)
        else:
            return None, Value.illegal_operation(self, other)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0
    
    def __repr__(self):
        return str(self.value)
class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous function>"
    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    def check_args(self, arg_names, args, context):
        res = RuntimeResult()
        if len(args) > len(arg_names):
            return res.failure(RTError(self.pos_start, self.pos_end, 'Too many arguments',context))
        if len(args) < len(arg_names):
            return res.failure(RTError(self.pos_start, self.pos_end, 'Too few arguments',context))
        return res.success(None)
    def populate_args(self, arg_names, args, context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(context)
            context.symbol_table.set(arg_name, arg_value)
    def check_and_populate_args(self, arg_names, args, context):
        res = RuntimeResult()
        res.register(self.check_args(arg_names, args, context))
        if res.error: return res
        self.populate_args(arg_names, args, context)
        return res.success(None)
class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names):
        super.__init__(super())
        self.name = name or '<anonymous function>'
        self.body_node = body_node
        self.arg_names = arg_names
    def execute(self, args):
        res = RuntimeResult()
        interpreter = Interpreter()
        new_context = self.generate_new_context()
        res.register(self.check_and_populate_args(self.arg_names, args, new_context))
        if res.error: return res
        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error: return res
        return res.success(value)
    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    def __repr__(self):
        return f"<Function {self.name}>"
class BuiltinFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
    def execute(self, args):
        res = RuntimeResult()
        exec_context = self.generate_new_context()
        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)
        res.register(self.check_and_populate_args(method.arg_names, args, exec_context))
        if res.error: return res
        return_value = res.register(method(exec_context))
        if res.error: return res
        return res.success(return_value)
    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} found')
    def copy(self):
        copy = BuiltinFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    def __repr__(self):
        return f"<BuiltinFunction {self.name}>"
    def execute_print(self, context):
        print(str(context.symbol_table.get("value")))
        return RuntimeResult().success(Number.null)
    execute_print.arg_names =["value"]
    def execute_print_ret(self, context):
        return RuntimeResult().success(String(str(context.symbol_table.get("value"))))
    execute_print_ret.arg_names =["value"]
    def execute_input(self, context):
        text = input()
        return RuntimeResult().success(String(text))
    execute_input.arg_names = []
    def execute_input_int(self, context):
        while True:
            try:
                num = int(input())
                break
            except:
                print(f'user input is not an integer')
        return RuntimeResult().success(Number(num))
    execute_input_int.arg_names = []
    def execute_clear(self, context):
        os.system("cls" if os.name == "nt" else "clear")
        return RuntimeResult().success(Number(0))
    execute_clear.arg_names = []
    def execute_is_number(self, context):
        if isinstance(context.symbol_table.get("value"), Number):
            return RuntimeResult().success(Number.true)
        else:
            return RuntimeResult().success(Number.false)
    execute_is_number.arg_names = ["value"]
    def execute_is_string(self, context):
        if isinstance(context.symbol_table.get("value"), String):
            return RuntimeResult().success(Number.true)
        else:
            return RuntimeResult().success(Number.false)
    execute_is_string.arg_names = ["value"]
    def execute_is_list(self, context):
        if isinstance(context.symbol_table.get("value"), List):
            return RuntimeResult().success(Number.true)
        else:
            return RuntimeResult().success(Number.false)
    execute_is_list.arg_names = ["value"]
    def execute_is_function(self, context):
        if isinstance(context.symbol_table.get("value"), BaseFunction):
            return RuntimeResult().success(Number.true)
        else:
            return RuntimeResult().success(Number.false)
    execute_is_function.arg_names = ["value"]
    def execute_append(self, context):
        list = context.symbol_table.get("list")
        value = context.symbol_table.get("value")
        if not isinstance(list,List):
            return RuntimeResult().failure(RTError(self.pos_start, self.pos_end,"First argument must be a list"))
        list.elements.append(value)
        return RuntimeResult().success(Number.null)
    execute_append.arg_names = ["list", "value"]
    def execute_pop(self, context):
        list = context.symbol_table.get("list")
        index = context.symbol_table.get("index")
        if not isinstance(list,List):
            return RuntimeResult().failure(RTError(self.pos_start, self.pos_end,"First argument must be a list"))
        if not isinstance(index,Number):
            return RuntimeResult().failure(RTError(self.pos_start, self.pos_end,"Second argument must be a number"))
        try:
            element = list.elements.pop(index)
        except:
            return RuntimeResult().failure(RTError(self.pos_start, self.pos_end,f"Index out of range"))
        return RuntimeResult().success(element)
    execute_pop.arg_names = ["list", "index"]
    def execute_extend(self, context):
        list = context.symbol_table.get("list")
        value = context.symbol_table.get("value")
        if not isinstance(list,List):
            return RuntimeResult().failure(RTError(self.pos_start, self.pos_end,"First argument must be a list"))
        if not isinstance(value,List):
            return RuntimeResult().failure(RTError(self.pos_start, self.pos_end,"Second argument must be a list"))
        list.elements.extend(value.elements)
        return RuntimeResult().success(Number.null)
    execute_append.arg_names = ["list", "value"]
    def execute_exit(self, context):
        os.system("cls" if os.name == "nt" else "clear")
        exit()
    execute_exit.arg_names = []

BuiltinFunction.print       = BuiltinFunction("print")
BuiltinFunction.print_ret   = BuiltinFunction("print_ret")
BuiltinFunction.input       = BuiltinFunction("input")
BuiltinFunction.input_int   = BuiltinFunction("input_int")
BuiltinFunction.clear       = BuiltinFunction("clear")
BuiltinFunction.is_number   = BuiltinFunction("is_number")
BuiltinFunction.is_string   = BuiltinFunction("is_string")
BuiltinFunction.is_list     = BuiltinFunction("is_list")
BuiltinFunction.is_function = BuiltinFunction("is_function")
BuiltinFunction.append      = BuiltinFunction("append")
BuiltinFunction.pop         = BuiltinFunction("pop")
BuiltinFunction.extend      = BuiltinFunction("extend")
BuiltinFunction.exit        = BuiltinFunction("exit")

class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
    def added_to(self, other):
        if isinstance(other,String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
    def multed_by(self, other):
        if isinstance(other,Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self,other)
    def is_true(self):
        return len(self.value) > 0
    def copy(self):
        copy = String(self.value)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    def __repr__(self):
        return f'"{self.value}"'
    def __str__(self):
        return f'{self.value}'
class List(Value):
    def __init__(self, elements):
        self.elements = elements
    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None
    def subbed_by(self, other):
        if isinstance(other,Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RTError(other.pos_start, other.pos_end, "Element %s does not exist" % other.value, self.context)
        else:
            return None, Value.illegal_operation(self, other)
    def multed_by(self, other):
        if isinstance(other,List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)
    def divided_by(self, other):
        if isinstance(other,Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RTError(other.pos_start, other.pos_end, "Element %s does not exist" % other.value, self.context)
        else:
            return None, Value.illegal_operation(self, other)
    def copy(self):
        copy = List(self.elements)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'
    def __str__(self):
        return f'{", ".join([str(x) for x in self.elements])}'

# SYMBOL TABLE
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent
    def get(self, symbol):
        value = self.symbols.get(symbol, None)
        if value is None and self.parent:
            return self.parent.get(symbol)
        return value
    def set(self, symbol, value):
        self.symbols[symbol] = value
    def remove(self, symbol):
        del self.symbols[symbol]


# Interpreter
class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit)
        return method(node, context)
    def no_visit(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    def visit_IfNode(self, node, context):
        res = RuntimeResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error: return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error: return res
                return res.success(expr_value)

        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error: return res
            return res.success(else_value)

        return res.success(None)
    def visit_NumberNode(self, node, context):
        #print("Found Number")
        return RuntimeResult().success(
            Number(node.tok.value).set_pos(node.tok.pos_start,node.tok.pos_end).set_context(context))
    def visit_BinOpNode(self, node, context):
        #print("Found BinOp")
        res = RuntimeResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res
        error = None
        result = None
        if node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.divided_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.powed_by(right)
        elif node.op_tok.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, 'and'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD, 'or'):
            result, error = left.ored_by(right)
        else:
            error = RTError(node.tok.pos_start, node.tok.pos_end, "Unknown Operator")
        if error: return res.failure(error)
        else:
            return res.success(result.set_pos(node.op_tok.pos_start,node.op_tok.pos_end))
    def visit_UnaryOpNode(self, node, context):
        #print("Found UnaryOp")
        res = RuntimeResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res
        error = None
        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(TT_KEYWORD, 'NOT'):
            number, error = number.notted()
        if error: return res.failure(error)
        else:
            return res.success(number.set_pos(node.op_tok.pos_start,node.op_tok.pos_end))
    def visit_VarAccessNode(self, node, context):
        res = RuntimeResult()
        var_name = node.name_tok.value
        value = context.symbol_table.get(var_name)

        if not value: return res.failure(RTError(node.pos_start, node.pos_end, f"Variable '{var_name}' is not defined.",context))
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)
    def visit_VarAssingNode(self, node, context):
        res = RuntimeResult()
        var_name = node.name_tok.value
        value = res.register(self.visit(node.value, context))
        if res.error: return res
        context.symbol_table.set(var_name, value)
        return res.success(value)
    def visit_ForNode(self, node, context):
        res = RuntimeResult()
        elements = []
        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error: return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error: return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error: return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value
        
        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            elements.append(res.register(self.visit(node.body_node, context)))
            if res.error: return res

        return res.success(List(elements).set_pos(node.pos_start, node.pos_end).set_context(context))

    def visit_WhileNode(self, node, context):
        res = RuntimeResult()
        elements = []
        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error: return res

            if not condition.is_true(): break

            elements.append(res.register(self.visit(node.body_node, context)))
            if res.error: return res

        return res.success(List(elements).set_pos(node.pos_start, node.pos_end).set_context(context))
    def visit_FunctionDefinitionNode(self, node, context):
        res = RuntimeResult()
        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)
        if node.var_name_tok:
            context.symbol_table.set(node.var_name_tok.value, func_value)
        return res.success(func_value)
    def visit_CallNode(self, node, context):
        res = RuntimeResult()
        args = []
        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error: return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)
        for arg_node in node.arg_toks:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error: return res
        return_value = res.register(value_to_call.execute(args))
        if res.error: return res
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(return_value)
    def visit_StringNode(self, node, context):
        res = RuntimeResult()
        return res.success(
            String(node.tok.value).set_pos(node.pos_start, node.pos_end).set_context(context)
        )
    def visit_ListNode(self, node, context):
        res = RuntimeResult()
        elements = []
        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
        return res.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

Number.true = Number(1)
Number.false = Number(0)
Number.null = Number(None)
Number.NaN = Number(math.nan)
Number.Infinity = Number(math.inf)
Number.PI = Number(math.pi)

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number.null)
global_symbol_table.set("true", Number.true)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("Math_PI", Number.PI)
global_symbol_table.set("Infinity", Number.Infinity)
global_symbol_table.set("NaN", Number.NaN)
global_symbol_table.set("print", BuiltinFunction.print)
global_symbol_table.set("print_ret", BuiltinFunction.print_ret)
global_symbol_table.set("input", BuiltinFunction.input)
global_symbol_table.set("input_int", BuiltinFunction.input_int)
global_symbol_table.set("clear", BuiltinFunction.clear)
global_symbol_table.set("cls", BuiltinFunction.clear)
global_symbol_table.set("is_num", BuiltinFunction.is_number)
global_symbol_table.set("is_str", BuiltinFunction.is_string)
global_symbol_table.set("is_list", BuiltinFunction.is_list)
global_symbol_table.set("is_function", BuiltinFunction.is_function)
global_symbol_table.set("append", BuiltinFunction.append)
global_symbol_table.set("pop", BuiltinFunction.pop)
global_symbol_table.set("extend", BuiltinFunction.extend)
global_symbol_table.set("exit", BuiltinFunction.exit)

# RUN
def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error
    interpreter = Interpreter()
    context = Context("<program>")
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    return result.value, result.error