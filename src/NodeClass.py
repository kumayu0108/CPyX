class Node():
    def __init__(self, name, val = None, expr=[],label=[], line_no = 0,sqb = False, type = None, children = [], place = None, quad = None, scope = 0, array = [], max_depth = 0, is_func = 0, tind=0,parentStruct = None, level = 0, ast = None, addr = '', virtual_function_name = '',is_unary = 0) :
        self.name = name
        self.sqb=sqb
        self.val = val
        self.line_no = line_no
        self.tind=tind
        self.type = type
        self.children = children
        self.scope = scope
        self.array = array
        self.expr = expr
        self.label = label
        self.max_depth = max_depth
        self.is_func = is_func
        self.parentStruct = parentStruct
        self.level = level
        self.ast = ast
        self.place = place
        self.quad = quad
        self.addr = addr
        self.is_unary = is_unary
        self.virtual_function_name = virtual_function_name
