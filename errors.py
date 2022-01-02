from strings_with_arrows import *
# ERRORS
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}: \n'
        result += '' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)
class UnexpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Unexpected Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)
class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context
    def as_string(self):
        result = f'{self.generate_stack_trace(self.context)}\n'
        result += f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}: \n'
        result += '' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result
    def generate_stack_trace(self, context):
        result = ''
        pos = self.pos_start
        ctx = context

        while ctx:
            if pos:
                result += f'    File {pos.fn}, line {str(pos.ln + 1)}, in Function {ctx.display_name}\n'
            else:
                result += f'    In Built-In Function {ctx.display_name}\n'
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        return "Stacktrace:\n" + result