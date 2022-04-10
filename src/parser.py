from keyring import set_keyring
import pydot
import ply.yacc as yacc
import lexer
import sys
import re
from lexer import lexer
import copy
import json
import pandas as pd

counter = 0
cur_num = 0
var_cnt = 0
funcReturntype = ''
# def AST(p):
#     global counter
#     calling_func_name = sys._getframe(1).f_code.co_name
#     calling_rule_name = calling_func_name[2:]

#     counter = counter + 1
#     tmp = counter
#     if(len(p) == 2):
#         return p[1]
#     with open('graph.dot', 'a') as file:
#         file.write("\n" + str(counter) + "[label=\"" + calling_rule_name.replace('"',"") + "\"]")
#         for i in range(1, len(p)):
#             if(type(p[i]) is tuple):
#                 file.write("\n" + str(tmp) + " -> " + str(p[i][1]))
#             else :
#                 counter = counter + 1
#                 p[i] = (p[i], counter)
#                 file.write("\n" + str(counter) + "[label=\"" + str(p[i][0]).replace('"',"") + "\"]")
#                 file.write("\n" + str(tmp) + " -> " + str(p[i][1]))
    
#     return (calling_rule_name,tmp)
def conv(s):
    return '' if s is None else str(s)
    
def ignore_1(s):
    ignore_list = ["{", "}", "(", ")", "[", "]", ";", ","]
    if s in ignore_list:
        return True
    return False
def parse_format_string(format_str):
  # parse the format string of printf and return the
  # corresponding option used after '%'
  c_reg_exp='''\
  %                                  # literal "%"
  (?:                                # first option
  (?:[-+0 #]{0,5})                   # optional flags
  (?:\d+|\*)?                        # width
  (?:\.(?:\d+|\*))?                  # precision
  (?:h|l|ll|w|I|I32|I64)?            # size
  ([cCdiouxXeEfgGaAnpsSZ])             # type
  ) |                                # OR
  %%                                # literal "%%"
  '''
  types=[]
  for match in re.finditer(c_reg_exp, format_str, flags = re.X):
      types.append(match.group(1))
  types = [type for type in types if type is not None]
  return types

def int_or_real(dtype):
  arr = conv(dtype).split()
  if ('*' in arr):
    return 'int'
  if 'long' in arr:
    return 'int' 
  elif ( ('int' in arr) or ('char' in arr) or ('short' in arr) ):
    return 'int'
  else:
    return 'int'
def extract_if_tuple(p2):
  if (type(p2) is tuple):
    return str(p2[0])
  else:
    return str(p2)

def _new_var():#done
  # define new temporary variable
  global var_cnt
  s = "__temp_" + str(var_cnt)
  var_cnt += 1
  return s

def check_func_call(func_argument,call_argument):
    if(func_argument == call_argument):
        return 1
    # if(func_argument)
    if(func_argument in ['int','float','char']):
        if(call_argument in ['int','char','float']):
            return 1
        return 0
    elif(func_argument.endswith('*')):
        if(not call_argument.endswith('*')):
            return 0
        else:
            return 1
    else:
        return 0

def AST(p):#done
    global cur_num
    calling_func_name = sys._getframe(1).f_code.co_name
    calling_rule_name = calling_func_name[2:]
    length = len(p)
    if(length == 2):
        if(isinstance(p[1], Node)):
        # print(p[1].ast,p[0].name)
            # if(p[1].val == 'main'):
            #     print(p[1].ast, "line 50")
            return p[1].ast
        else:
        # print(p[1],p[0].name)
            return p[1]
    else:
        cur_num += 1
        p_count = cur_num
        open('./graph1.dot','a').write("\n" + str(p_count) + "[label=\"" + calling_rule_name.replace('"',"") + "\"]") ## make new vertex in dot file
        for child in range(1,length,1):
            # if(length==3 and isinstance(p[child], Node)):
            #     print(p[child].val)

            if(isinstance(p[child], Node) and p[child].ast is None):
                # if(isinstance(p[child], Node) and p[child].val == 'Point'):
                #     print(" ehhh line 62")
                continue
            global child_num 
            global child_val
            if(not isinstance(p[child], Node)):
                if(isinstance(p[child], tuple)):
                    if(ignore_1(p[child][0]) is False):
                        open('graph1.dot','a').write("\n" + str(p_count) + " -> " + str(p[child][1]))
                elif not isinstance(p[child], list): #if condition changed
                    if((ignore_1(p[child]) is False) & (str(p[child]).replace('"',"") != "")):
                        cur_num += 1
                        open('graph1.dot','a').write("\n" + str(cur_num) + "[label=\"" + str(p[child]).replace('"',"") + "\"]")
                        p[child] = (p[child],cur_num)
                        open('graph1.dot','a').write("\n" + str(p_count) + " -> " + str(p[child][1]))
            else:
                if(isinstance(p[child].ast, tuple)):
                    if(ignore_1(p[child].ast[0]) is False):
                        open('graph1.dot','a').write("\n" + str(p_count) + " -> " + str(p[child].ast[1]))
                else:   #if condition changed
                    if((ignore_1(p[child].ast) is False) & (str(p[child].ast).replace('"',"") != "")):
                        cur_num += 1
                        open('graph1.dot','a').write("\n" + str(cur_num) + "[label=\"" + str(p[child].ast).replace('"',"") + "\"]")
                        p[child].ast = (p[child].ast,cur_num)
                        open('graph1.dot','a').write("\n" + str(p_count) + " -> " + str(p[child].ast[1]))

    return (calling_rule_name,p_count)

class SymTable():
    def __init__(self):
        self.table = [{}]
        self.prevScope = {}
        self.prevScope[0] = 0
        self.scope = 0
        self.next = 1
        self.loopingDepth=0
        self.switchDepth = 0
        self.function_overloaded_map={}
        self.functionScope = {}
        self.scope_to_function = {}
        self.scope_to_function[0] = 'global'
        self.local_vars = {}
        self.local_vars['global'] = []
        self.func_arguments = {}    # tracks arguments of functions, required for resolving overloading functions
        self.ignore_function_ahead = []
        self.actrec = []
    
    def isPresent(self, id):
        tmp = self.scope
        while 1:
            # print(tmp)
            # print(self.table[tmp].keys())
            if id in self.table[tmp].keys():
                return (self.table[tmp][id], tmp)
            tmp = self.prevScope[tmp]
            if self.prevScope[tmp] == tmp:
                # print(self.table[tmp].keys())
                if id in self.table[tmp].keys():
                    return (self.table[tmp][id], tmp)
                break
        return None

    def data_type_size(self, __type__):
        type_size = {'char':1, 
                    'int':4,
                    'float':4,
                    'void':0, }
        if(__type__.endswith('*')):
            return 8
        if( __type__.startswith('struct')):
            tmp = self.scope
            while(1):
                if(__type__ in self.table[tmp].keys()):
                    break
                tmp = self.prevScope[tmp]
                if self.prevScope[tmp] == tmp:
                    break
            if (tmp == 0):
                if(__type__ not in self.table[tmp].keys()):
                   return -1
            return self.table[tmp][__type__]['size']

        # print(f"line 206 : __type__ = {__type__}")
        __type__ = __type__.split()[-1]
        if __type__ not in type_size.keys():
            return -1
        return type_size[__type__]

    def typecast(self, type_1, type_2):
        if(type_1.endswith('*')):
            return type_1
        if(type_2.endswith('*')):
            return type_2
        to_num = {'char':0,
                    'int':1,
                    'long':2,
                    'float':3,
                    'double':4}
        to_str = {}
        to_str[0] = 'char'
        to_str[1] = 'int'
        to_str[2] = 'long'
        to_str[3] = 'float'
        to_str[4] = 'double'
        type_1 =  type_1.split()[-1]
        type_2 =  type_2.split()[-1]
        if type_1 not in to_num or type_2 not in to_num:
            return str(-1)
        num_type_1 = to_num[type_1]
        num_type_2 = to_num[type_2]
        return to_str[max(num_type_1 , num_type_2)]

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

class emit_class():
    def __init__(self, symtable):
        self.mathFuncs = ['pow', 'fabs', 'sin', 'cos', 'sqrt']

        self.jump_mark = 0
        self.top_label = {}
        self.emit_array = []
        self.symtable = symtable
        self.nextstat = 0
        self.pre_append_in_symbol_table_list = ['pow', 'fabs', 'sin', 'cos', 'sqrt', 'strlen', 'strcpy','printf', 'scanf','malloc','free']
        self.label_count = 0

    def get_new_tmp(self, dtype, value=0, scope = -1):
        if(self.symtable.scope == -1):
            scope = self.symtable.scope
        tmp_name = _new_var()

        #insert into the symbol table
        self.symtable.table[scope][tmp_name] = {}
        self.symtable.table[scope][tmp_name]['type'] = dtype
        self.symtable.table[scope][tmp_name]['size'] = self.symtable.data_type_size(dtype)
        self.symtable.table[scope][tmp_name]['value'] = value

        return tmp_name
    def get_label(self):
    # generate a nsew label
        s = "__label_" + str(self.label_count)
        self.label_count += 1
        return s
    def emit(self, op, src1, src2, dst):#done
        if(self.jump_mark and not op.startswith('label') and not op.startswith('func')):
            return
        else :
            self.jump_mark = 0
        
        if(op.startswith('label')):
            if len(self.emit_array) > 0 and self.emit_array[-1][0].startswith('label'):
                self.top_label[dst] = self.emit_array[-1][3]
                return
            else:
                self.top_label[dst] = dst
        if(not (self.symtable.scope == 0 and not op.startswith('func') and not op.startswith('ret'))):
            # global_emit_array.append([str(op), str(s1), str(s2), str(dest)])
        # else:
            self.emit_array.append([str(op), str(dst), str(src1), str(src2)])
        self.nextstat += 1        
    

    def handle_binary_emit(self, p0, p1, p2, p3):#done
    # handles emit for all kinds of binary operators 
        operator = p2 if type(p2) is not tuple else str(p2[0])
        higher_data_type = int_or_real(self.symtable.typecast(p1.type , p3.type))
        if(operator in ["<",">","<=",">=","==","!="]):
            return_tmp = self.get_new_tmp('int')
        else:
            return_tmp = self.get_new_tmp(higher_data_type)
        p0.place = return_tmp
        if (int_or_real(p1.type) != higher_data_type):
            tmp = self.get_new_tmp(higher_data_type)
            self.emit(int_or_real(p1.type) + '_' + int_or_real(higher_data_type) + '_' + '=', p1.place, '', tmp)
            self.emit(higher_data_type + '_' + operator, tmp, p3.place, p0.place)
        elif (int_or_real(p3.type) != higher_data_type):
            tmp = self.get_new_tmp(higher_data_type)
            self.emit(int_or_real(p3.type) + '_' + int_or_real(higher_data_type) + '_' + '=', p3.place, '', tmp)
            self.emit(higher_data_type + '_' + operator, p1.place, tmp, p0.place)
        else:
            if p1.type == 'char':
                tmp1 = self.get_new_tmp('int')
                self.emit(self,int_or_real('char') + '_' + int_or_real('int') + '_' + '=', p1.place, '', tmp1)
                tmp2 = self.get_new_tmp('int')
                self.emit(int_or_real('char') + '_' + int_or_real('int') + '_' + '=', p3.place, '', tmp2)
                tmp3 = self.get_new_tmp('int')
                self.emit( 'int_' + operator, tmp1, tmp2, tmp3)
                self.emit(int_or_real('int') + '_' + int_or_real('char') + '_' + '=', tmp3, '', p0.place) 
            else: 
                self.emit(int_or_real(p1.type) + '_' + operator, p1.place, p3.place, p0.place)
        return p0, p1, p2, p3

    def handle_binary_emit_sub_add(self, p0, p1, p2, p3):#done
        operator = p2 if type(p2) is not tuple else str(p2[0])
        higher_data_type = int_or_real(self.symtable.typecast(p1.type , p3.type))
        if(p1.type.endswith('*') or p3.type.endswith('*') or p1.level > 0 or p3.level > 0):
            higher_data_type = 'int'
        return_tmp = self.get_new_tmp(higher_data_type)
        p0.place = return_tmp
        if (int_or_real(p1.type) != higher_data_type and p1.level == 0):
            tmp = self.get_new_tmp(higher_data_type)
            self.emit(int_or_real(p1.type) + '_' + int_or_real(higher_data_type) + '_' + '=', p1.place, '', tmp)
            self.emit(higher_data_type + '_' + operator, tmp, p3.place, p0.place)
        elif (int_or_real(p3.type) != higher_data_type and p3.level == 0):
            tmp = self.get_new_tmp(higher_data_type)
            self.emit(int_or_real(p3.type) + '_' + int_or_real(higher_data_type) + '_' + '=', p3.place, '', tmp)

            self.emit(higher_data_type + '_' + operator, p1.place, tmp, p0.place)
        else:
            if(p1.type.endswith('*') or p3.type.endswith('*') or p1.level > 0 or p3.level > 0):
                tmp = self.get_new_tmp('int')
                if(p1.type.endswith('*') or p1.level > 0):
                    if(p3.type.startswith('float')):
                        print("Compilation error at line " + str(p1.line_no) + ", cannot add float to pointer variable")
                        # give_error()
                    data_type = p1.type
                    if data_type.endswith('*'):
                        data_type = data_type[:-2]
                    self.emit('int_mul',p3.place,self.symtable.data_type_size(data_type),tmp)
                    self.emit('int_' + operator, p1.place, tmp, p0.place)
                else:
                    if(p1.type.startswith('float')):
                        print("Compilation error at line " + str(p1.line_no) + ", cannot add float to pointer variable")
                        # give_error()
                    data_type = p3.type
                    if data_type.endswith('*'):
                        data_type = data_type[:-2]
                    self.emit('int_mul',p1.place,self.symtable.data_type_size(data_type),tmp)
                    self.emit('int_' + operator, tmp, p3.place, p0.place)
            elif p1.type == 'char':
                tmp1 = self.get_new_tmp('int')
                self.emit(int_or_real('char') + '_' + int_or_real('int') + '_' + '=', p1.place, '', tmp1)
                tmp2 = self.get_new_tmp('int')
                self.emit(int_or_real('char') + '_' + int_or_real('int') + '_' + '=', p3.place, '', tmp2)
                tmp3 = self.get_new_tmp('int')
                self.emit( 'int_' + operator, tmp1, tmp2, tmp3)
                self.emit(int_or_real('char') + '_' + int_or_real('int') + '_' + '=', tmp3, '', p0.place)
            else: 
                self.emit(int_or_real(p1.type) + '_' + operator, p1.place, p3.place, p0.place)
        return p0, p1, p2, p3


class Parser():
    tokens = lexer().tokens
    lex = lexer()
    lex.build()
    curType = []
    symtable = SymTable()
    EMIT = emit_class(symtable)
    translation_unit = Node('START')
    
    # print("line 396 : ", funcReturntype)
    root = Node(name = "root")
    scope_to_function = {}
    scope_to_function[0] = 'global'
    continueStack = []
    breakStack = []
    strings = {}
    offset = {}
    offset[0] = 0
    precedence = (
        ('left', 'ADD', 'SUB'),
        ('left', 'DIV', 'MUL', 'MODULO'),
        ('left', 'INC', 'DEC'),
        ('nonassoc', 'IFX'),
        ('nonassoc', 'ELSE'),
        ('nonassoc', 'IFX1'),
        ('nonassoc', 'IFX2'),
        # ('nonassoc', 'IFX3'),
        # ('nonassoc', 'IFX4'),
        # ('nonassoc', 'IFX5'),
        # ('nonassoc', 'IFX6'),
        # ('nonassoc', 'IFX7'),
        ('nonassoc', 'IFX8')
    )

    # def typecast(self, type_1, type_2):
    #     if(type_1.endswith('*')):
    #         return type_1
    #     if(type_2.endswith('*')):
    #         return type_2
    #     to_num = {'char':0,
    #                 'int':1,
    #                 'long':2,
    #                 'float':3,
    #                 'double':4}
    #     to_str = {}
    #     to_str[0] = 'char'
    #     to_str[1] = 'int'
    #     to_str[2] = 'long'
    #     to_str[3] = 'float'
    #     to_str[4] = 'double'
    #     type_1 =  type_1.split()[-1]
    #     type_2 =  type_2.split()[-1]
    #     if type_1 not in to_num or type_2 not in to_num:
    #         return str(-1)
    #     num_type_1 = to_num[type_1]
    #     num_type_2 = to_num[type_2]
    #     return to_str[max(num_type_1 , num_type_2)]

    def check_invalid_operation_on_function(self, p):
        found_scope = self.symtable.isPresent(p.val)
        if(found_scope!=None):
            found_scope = found_scope[1]
        if (found_scope != -1) and (p.is_func >= 1):
            print("Compilation error at line", str(p.line_no), ":Invalid operation on", p.val, "line no : 389")
        return

    def array_init(self, base_addr, offset, dtype, arr, p, lev, line_no): # done
        '''
        handle array initialization of type "int arr[2] = {1,2}"
        '''
        if(len(p.children)  > arr[lev]):
            print("Compilation error at " + str(p.line_no) + ", incorrect initializer")
            return
        i = 0
        for child in p.children:
            if(lev == len(arr) - 1 and len(child.children) > 0 and not (dtype.startswith('struct') or dtype.startswith('union'))):
                print("Compilation error at " + str(p.line_no) + ", incorrect initializer")
                return
            elif(lev < len(arr) - 1 and len(child.children) == 0):
                print("Compilation error at " + str(p.line_no) + ", incorrect initializer")
                return
            tmp = self.EMIT.get_new_tmp(dtype)
            self.EMIT.emit('int_mul', offset, arr[lev], tmp)
            self.EMIT.emit('int_add', tmp, i, tmp)
            if(lev == len(arr) - 1):
                self.EMIT.emit('int_mul', tmp, self.symtable.data_type_size(dtype), tmp)
                self.EMIT.emit('int_add', tmp, base_addr, tmp)
                if((dtype.startswith('struct') or dtype.startswith('union'))):
                    found_scope = self.symtable.isPresent(dtype)
                    if(found_scope!=None):
                        found_scope = found_scope[1]
                    self.struct_init(tmp, '',found_scope, dtype, child, line_no)
                else:
                    tmp2 = child.place
                    if(dtype != child.type):
                        tmp2 = self.EMIT.get_new_tmp(dtype)
                        self.EMIT.emit(int_or_real(child.type) + '_' + int_or_real(dtype) + '_' + '=', child.place, '', tmp2)
                    self.EMIT.emit(int_or_real(dtype) + '_=', tmp2, '*', tmp)  
            else:
                self.array_init(base_addr, tmp, dtype, arr, child, lev+1, line_no)
            i += 1

    def struct_init(self, base_addr, name, scope, struct_name, p, line_no): # done
        ''' 
        handle struct initialization of the type "struct point x = {1,2}"
        '''
        # print("line 495 :", self.symtable.scope)
        lst = self.symtable.table[scope][struct_name]['field_list']
        if(struct_name == p.type):
            if(len(name) > 0):
                if(len(p.addr) > 0):
                    self.EMIT.emit('*', p.addr, '', name)
                else:
                    self.EMIT.emit('int_assignment', p.place, '', name)
            else:
                self.EMIT.emit('int_assignment', p.place, '*', base_addr)
            return
        if(len(lst) != len(p.children)):
            print("Compilation error at " + str(p.line_no) + ", incorrect initializer")
            return
        i = 0
        for child in p.children:
            if(len(lst[i]) == 5):
                self.array_init(base_addr, 0, lst[i][0], lst[i][4], child, 0, line_no)
            elif(lst[i][0].startswith('struct') or lst[i][0].startswith('union')):
                found_scope = self.symtable.isPresent(lst[i][0])
                if(found_scope!=None):
                    found_scope = found_scope[1]
                tmp = self.EMIT.get_new_tmp('int')
                self.EMIT.emit('int_assignment', base_addr, '', tmp)
                self.struct_init(tmp, '', found_scope, lst[i][0], child, line_no)
            else:
                tmp2 = child.place
                if(lst[i][0] != child.type):
                    tmp2 = self.EMIT.get_new_tmp(lst[i][0])
                    self.EMIT.emit(int_or_real(child.type) + '_' + int_or_real(lst[i][0]) + '_' + '=', child.place, '', tmp2)
                self.EMIT.emit(int_or_real(lst[i][0]) + '_=', tmp2, '*', base_addr)
            self.EMIT.emit('int_add', base_addr, lst[i][2], base_addr)
            i = i+1

    def build(self):#done
        # insert/pre-append entries in the symbol table
        for symbol in ['printf', 'scanf','malloc','free','strlen', 'strcpy']:
            self.symtable.table[0][symbol] = {}
            self.symtable.table[0][symbol]['is_func'] = 1
            self.symtable.table[0][symbol]['argumentList'] = ['int']
            self.symtable.table[0][symbol]['type'] = 'int'
        
        for symbol in ['pow', 'fabs', 'sin', 'cos', 'sqrt']:
            self.symtable.table[0][symbol] = {}
            self.symtable.table[0][symbol]['is_func'] = 1
            self.symtable.table[0][symbol]['argumentList'] = ['int']
            self.symtable.table[0][symbol]['type'] = 'float'

        self.parser = yacc.yacc(module=self, start='translation_unit' ,debug=True)
        
        self.symtable.table[0]['NULL'] = {}
        self.symtable.table[0]['NULL']['type'] = 'void *'
        self.symtable.table[0]['NULL']['value'] = '0'
    
    def p_identifier(self, p): # done
        '''
            identifier : ID
        '''
        p[0] = Node(name = "Identifier", val = p[1], line_no = p.lineno(1), place=p[1])
        x = self.symtable.isPresent(p[1])
        if x != None:
            p[0].place = p[0].place + '_' + str(x[1])
            p[0].type = x[0]['type']
            
            if 'array' in x[0].keys():
                p[0].level = len(x[0]['array'])
            
            if 'is_func' in x[0]:
                p[0].is_func = 1

        p[0].ast = AST(p)


    def p_primary_expression_1(self,p): #done
        '''
        primary_expression : identifier
        '''
        x = p[1].val
        if self.symtable.isPresent(x) == None :
            print("Compilation error at line",p[1].line_no,"unary expression",p[1].val,"not defined") 
        p[0] = p[1]
        # print(p[0].val)

    def p_primary_expression_2(self,p): #done 
        '''
        primary_expression : INT_NUM
        '''
        # print("i am here line 250")
        p[0] = Node(name = "constant", val = p[1], line_no=p.lineno(1), type = 'int', place = p[1])
        tempVar = self.EMIT.get_new_tmp(dtype='int', scope=0)
        p[0].place = tempVar
        p[0].ast = AST(p)

        
    def p_primary_expression_3(self,p): #done 
        '''
        primary_expression : FLOAT_NUM
        '''
        p[0] = Node(name = "constant", val = p[1], line_no=p.lineno(1), type = 'float',place = p[1])
        tempVar =  self.EMIT.get_new_tmp(dtype='float', scope=0)
        p[0].place = tempVar
        p[0].ast = AST(p)


    def p_primary_expression_4(self,p): #done 
        '''
        primary_expression : CHARACTER
        '''
        p[0] = Node(name = "constant", val = p[1], line_no=p.lineno(1), type = 'char', place = p[1])
        tempVar = self.EMIT.get_new_tmp(dtype='char', scope=0)
        p[0].place = tempVar
        p[0].ast = AST(p)


    def p_primary_expression_5(self,p): #done 
        '''
        primary_expression : STRING
        '''
        p[0] = Node(name = "constant", val = p[1], line_no=p.lineno(1), type = 'string', place = self.EMIT.get_new_tmp('char *'))
        self.strings[p[0].place] = p[1]
        p[0].ast = AST(p)
    
    def p_primary_expression_6(self,p): #done
        '''
        primary_expression : LEFT_PAR expression RIGHT_PAR
        '''
        # p[0] = p[1]
        p[0] = p[2]
        p[0].ast = AST(p)

    def p_postfix_expression(self,p):  #done #catch have changed last rule; postfix_expression changed to identifier
        '''
        postfix_expression : primary_expression
                        | postfix_expression INC
                        | postfix_expression DEC
                        | postfix_expression DOT identifier
                        | postfix_expression LEFT_PAR RIGHT_PAR
                        | postfix_expression PTR_OP identifier
                        | postfix_expression LEFT_SQ_BR expression RIGHT_SQ_BR
                        | postfix_expression LEFT_PAR argument_expression_list RIGHT_PAR
        '''
        # if len(p) == 5 && p[2] == '[':
        if (len(p) == 2):
            # print(f"p[1].val : {p[1].val}, line 639")
            # primary_expression
            p[0]=p[1]
            p[0].ast = AST(p)
            # print("here1")
            return    
        elif (len(p)==5 and p[2]=='['):  #done 
            # print("here2")
            # postfix_expression LEFT_SQ_BR expression RIGHT_SQ_BR
            # print(f"p[1].val : {p[1].val}, line 305")
            p[0]= Node(name ="ArrayExpression", val=p[1].val,line_no=p[1], type=p[1].type,children=[p[1],p[3]],is_func=p[1].is_func , parentStruct = p[1].parentStruct, place = p[1].place)
            # 
            if(conv(p[1].type).endswith('*') and p[1].level == 0):
                p[0].type = p[1].type[:-2]
                tmp = p[1].place
                tmp1 = self.EMIT.get_new_tmp('int')
                tmp2 = self.EMIT.get_new_tmp('int')
                self.EMIT.emit('int_mul', p[3].place, self.symtable.data_type_size(p[0].type), tmp2)
                self.EMIT.emit('int_add', tmp, tmp2, tmp1)
                tmp3 = self.EMIT.get_new_tmp(p[0].type)
                self.EMIT.emit('deref', tmp1, '', tmp3)
                p[0].place = tmp3
                p[0].addr = tmp1
                return
            # 
            p[0].array = copy.deepcopy(p[1].array)
            p[0].array.append(conv(p[3].val))
            p[0].level = p[1].level - 1
            # sc=  self.symtable.isPresent(self,p[1].val)[1]
            p[0].ast=AST(p)
            if (p[0].level==None):
                print("Compilation error at line", str(p[1].line_no)," : Incorrect Dimensions specified for ", p[1].val)
            #check
                            
            if (p[3].type not in ['int','char']):
                print("Compilation error : Array index at line ", p[3].line_no, " is of incompatible type")
                return 

            tempScope = self.symtable.isPresent(p[1].val)
            temp_ind = self.EMIT.get_new_tmp('int')
            if(p[0].parentStruct != None and len(p[0].parentStruct)):
                found_scope = self.symtable.isPresent(p[0].parentStruct)[1]
                for curr_list in self.symtable.table[found_scope][p[0].parentStruct]['field_list']:
                    if curr_list[1] == p[0].val:
                        d = len(curr_list[4]) - 1 - p[0].level
                        if d == 0:
                            self.EMIT.emit('int_assignment', p[3].place, '', temp_ind)
                        else:
                            v1 = self.EMIT.get_new_tmp('int')
                            self.EMIT.emit('int_mul', p[1].tind, curr_list[4][d], v1)
                            self.EMIT.emit('int_add', v1, p[3].place, temp_ind)
            elif(tempScope != None):
                # print("line 690: ",p[0].val)
                # print("line 691: ",tempScope[1])
                # print("line 691: ",self.symtable.table[tempScope[1]][p[0].val])
                d = len(self.symtable.table[tempScope[1]][p[0].val]['array']) - 1 - p[0].level
                if d == 0:
                    self.EMIT.emit('int_assignment', p[3].place, '', temp_ind)
                else:
                    v1 = self.EMIT.get_new_tmp('int')
                    self.EMIT.emit('int_mul', p[1].tind, self.symtable.table[tempScope[1]][p[0].val]['array'][d], v1)
                    self.EMIT.emit('int_add', v1, p[3].place, temp_ind)
                    

            if(p[0].level == 0 and len(p[0].array) > 0):
                v1 = self.EMIT.get_new_tmp('int')
                self.EMIT.emit('int_mul', temp_ind, self.symtable.data_type_size(p[1].type), v1)
                v2 = self.EMIT.get_new_tmp('int')
                if(len(p[1].addr) > 0):
                    self.EMIT.emit('int_assignment', p[1].addr, '', v2)
                else:
                    self.EMIT.emit('addr', p[0].place, '', v2)
                v3 = self.EMIT.get_new_tmp('int')
                self.EMIT.emit('int_add', v2, v1, v3)
                v4 = self.EMIT.get_new_tmp(p[1].type)
                self.EMIT.emit('deref', v3, '', v4)
                p[0].place = v4
                p[0].addr = v3
            elif(len(p[0].array) > 0):
                p[0].tind = temp_ind

        elif( len(p)==4 and p[2]=='('):  #done 
            # print("here3")
            #postfix_expression LEFT_PAR RIGHT_PAR
            # print(f"p[1].val : {p[1].val}, line 324")
            p[0]= Node(name='FunctionCall',val=p[1].val,line_no=p[1].line_no,type = p[1].type,children = [p[1]],is_func=0, place = p[1].place)
            p[0].ast=AST(p) 
            func_to_be_called = ''
            if(p[1].val in ['printf', 'scanf','malloc','free', 'pow', 'fabs', 'sin', 'cos', 'sqrt', 'strlen', 'strcpy']):
                func_to_be_called = p[1].val
            if(p[1].val not in self.symtable.table[0].keys() or 'is_func' not in self.symtable.table[0][p[1].val].keys()):
                print('Compilation error at line ' + str(p[1].line_no) + ': no function with name ' + p[1].val + ' declared')
            
            elif(p[1].val not in  self.symtable.function_overloaded_map.keys() and func_to_be_called == ''):
                print('Compilation error at line ' + str(p[1].line_no) + ': no function with name ' + p[1].val + ' declared')

            elif(p[1].val not in self.EMIT.pre_append_in_symbol_table_list):
                for i in range(self.symtable.function_overloaded_map[p[1].val] + 1):  
                    cur_func_name = p[1].val + '_' + str(i)

                    if(len(self.symtable.table[0][cur_func_name]['argumentList']) == 0):
                        func_to_be_called = cur_func_name
                        break
                
            if(func_to_be_called == ''):
                print('Compilation error at line : ' + str(p[1].line_no) + ': incorrect arguments for function call')
            else:
                p[0].type = self.symtable.table[0][func_to_be_called]['type']
            retVal = ''
            if(p[0].type != 'void'):
                retVal = self.EMIT.get_new_tmp(p[0].type)
            self.EMIT.emit('call', 0, retVal, func_to_be_called)
            p[0].place = retVal
            p[0].is_unary = 1
            
        elif ( len(p)==5 and p[2]=='(' ):  #done 
            # print("here4")
            # postfix_expression LEFT_PAR argument_expression_list RIGHT_PAR
            # print(f"p[1].val : {p[1].val}, line 335")
            p[0] = Node(name = 'FunctionCall',val = p[1].val,line_no = p[1].line_no,type = p[1].type,children = [],is_func=0,place = p[1].place)
            p[0].ast = AST(p)
            func_to_be_called = ''
            if(p[1].val in self.EMIT.pre_append_in_symbol_table_list):
              func_to_be_called = p[1].val
            if (p[1].val == 'printf'):
              if (p[3].children[0].type != "char *"):
                print("Compilation error at line :" + str(p[1].line_no) + " Incompatible first argument to printf")
              type_dict = {"x": ["int", "int *", "char *", "float *"],\
                        "d": ["int", "int *", "char *", "float *"],\
                        "f": ["float"],\
                        "c": ["char"] }
              types_children = parse_format_string(p[3].children[0].val)
              if (len(types_children) != len(p[3].children) - 1):
                print("Compilation error at line " + str(p[1].line_no) + " Incorrect number of arguments for function call")
                
              for i in range(len(p[3].children)):
                if (i == 0):
                  continue
                if(types_children[i-1] not in type_dict.keys()):
                  continue
                if(p[3].children[i].type not in type_dict[types_children[i - 1]]):
                  if(p[3].children[i].level > 0 and types_children[i-1] in ["x", "d"]):
                    continue
                  tmp = self.EMIT.get_new_tmp(type_dict[types_children[i - 1]][0])
                  self.EMIT.emit(int_or_real(p[3].children[i].type) + '_' + int_or_real(type_dict[types_children[i - 1]][0]) + '_' + '=', p[3].children[i].place, '', tmp)
                  p[3].children[i].place = tmp

            if(p[1].val not in self.symtable.table[0].keys()):
              print('Compilation error at line :' + str(p[1].line_no) + ': no function with name ' + p[1].val + ' declared')
            elif(p[1].val not in self.symtable.function_overloaded_map.keys() and func_to_be_called == ''):
              print('Compilation error at line :' + str(p[1].line_no) + ': no function with name ' + p[1].val + ' declared')
            elif(p[1].val not in self.EMIT.pre_append_in_symbol_table_list):
              actual_len = len(p[3].children)
              for i in range(self.symtable.function_overloaded_map[p[1].val] + 1):

                cur_func_name = p[1].val + '_' + str(i)
                j = 0
                flag = 0

                if(len(self.symtable.table[0][cur_func_name]['argumentList']) != actual_len):
                  continue

                for arguments in self.symtable.table[0][cur_func_name]['argumentList']:
                  current_type = p[3].children[j].type
                  if(current_type == ''):
                    j += 1
                    continue
                  if(arguments != current_type):
                    flag = 1
                    break
                  j += 1
                if(flag == 0):
                  func_to_be_called = cur_func_name
                  break

              if(func_to_be_called == ''):  
                for i in range(self.symtable.function_overloaded_map[p[1].val] + 1):
                  cur_func_name = p[1].val + '_' + str(i)
                  j = 0
                  flag = 0
                  if(actual_len != len(self.symtable.table[0][cur_func_name]['argumentList'])):
                    continue
                  for arguments in self.symtable.table[0][cur_func_name]['argumentList']:
                    current_type = p[3].children[j].type
                    if(current_type == ''):
                      j += 1
                      continue
                    if(check_func_call(arguments,current_type) == 0):
                      flag = 1
                      break
                    j += 1

                  if(flag == 0):
                    func_to_be_called = cur_func_name
                    break

            if(func_to_be_called == ''):
              print('Compilation error at line : ' + str(p[1].line_no) + ': incorrect arguments for function call')

            else:
              len_arg_list = len(self.symtable.table[0][func_to_be_called]['argumentList'])-1
              p[0].type = self.symtable.table[0][func_to_be_called]['type']
              for param in reversed(p[3].children):
                if(p[1].val in self.EMIT.mathFuncs):
                  if(param.type != 'float'):
                    tmp = self.EMIT.get_new_tmp('float')
                    self.EMIT.emit(int_or_real(param.type) + '_' + int_or_real('float') + '_' + '=', param.place, '', tmp)
                    param.place = tmp
                elif(func_to_be_called not in self.EMIT.pre_append_in_symbol_table_list):
                  if(param.type != self.symtable.table[0][func_to_be_called]['argumentList'][len_arg_list]):
                    tmp = self.EMIT.get_new_tmp(self.symtable.table[0][func_to_be_called]['argumentList'][len_arg_list])
                    self.EMIT.emit(int_or_real(param.type) + '_' + int_or_real(self.symtable.table[0][func_to_be_called]['argumentList'][len_arg_list]) + '_' + '=', param.place, '', tmp)
                    param.place = tmp
                  len_arg_list -= 1
                self.EMIT.emit('param', '', func_to_be_called, param.place)
              retVal = ''
              if(p[0].type != 'void'):
                retVal = self.EMIT.get_new_tmp(p[0].type)
              self.EMIT.emit('call', len(p[3].children), retVal, func_to_be_called)
              p[0].place = retVal
              p[0].is_unary = 1

            if(p[1].val not in self.symtable.table[0].keys() or 'is_func' not in self.symtable.table[0][p[1].val].keys()):
                print('Compilation error at line no. :' + str(p[1].line_no) + ': no function declared with name ' + p[1].val )
            elif(p[1].val not in self.symtable.function_overloaded_map.keys() and func_to_be_called == ''):
                print('Compilation error at line ' + str(p[1].line_no) + ': no function with name ' + p[1].val + ' declared')
            # elif(len(self.symtable.table[0][p[1].val]['argumentList']) != len(p[3].children)):
            #     print("Syntax error at line " + str(p[1].line_no) + " Incorrect number of arguments for function call")

            # else:
            #     i = 0
            #     print(f"line 864 : {self.symtable.table[0][p[1].val]}")
            #     for arguments in self.symtable.table[0][p[1].val]['argumentList']:
            #         curVal = p[3].children[i].val
            #         if(curVal not in self.symtable.table[self.symtable.scope].keys()):
            #             continue
            #         # print(self.curType," line 324")

            #         self.curType = self.symtable.table[self.symtable.scope][curVal]['type']
            #         # print(self.curType," line 324")
            #         # temp = compare_types(self.curType,arguments)
            #         if(self.curType.split()[-1] != arguments.split()[-1]):
            #             print("Warning at line " + str(p[1].line_no), ": Type not match in argument " + str(i+1) + " of function call, " + 'actual type is :' + arguments + 'but called with : ' + self.curType)
                    
            #         i += 1
            #         self.curType = [self.curType]
# done till here A







        elif(len(p)==3):  #done 
            # print("here5")
            # print(f"p[1].val : {p[1].val}, line 360")
            #  | postfix_expression INC
            #   | postfix_expression DEC
            tmp = self.EMIT.get_new_tmp(p[1].type)
            p[0] = Node(name = 'IncrementOrDecrementExpression',val = p[1].val,line_no = p[1].line_no,type = p[1].type,children = [], place = tmp)
            p[0].ast = AST(p)
            found_scope = -1 if(self.symtable.isPresent(p[1].val) ==None) else self.symtable.isPresent(p[1].val)[1]
            
            if (found_scope != -1) and ((p[1].is_func >= 1) or ('struct' in p[1].type.split())):
              print("Compilation error at line", str(p[1].line_no), ":Invalid operation on", p[1].val)
           
            
            self.EMIT.emit(int_or_real(p[1].type) + '_=', p[1].place, '', tmp)
            if (extract_if_tuple(p[2]) == '++'):
              if(len(p[1].addr) == 0):
                self.EMIT.emit('inc', '', '', p[1].place)
              else:
                tmp2 = self.EMIT.get_new_tmp(p[1].type)
                self.EMIT.emit(int_or_real(p[1].type) + "_+", p[1].place, '1', tmp2)
                self.EMIT.emit(int_or_real(p[1].type) + "_=", tmp2, '*', p[1].addr)
            if (extract_if_tuple(p[2]) == '--'):
              if(len(p[1].addr) == 0):
                self.EMIT.emit('dec', '', '', p[1].place)
              else:
                tmp2 = self.EMIT.get_new_tmp(p[1].type)
                self.EMIT.emit(int_or_real(p[1].type) + "_-", p[1].place, '1', tmp2)
                self.EMIT.emit(int_or_real(p[1].type) + "_=", tmp2, '*', p[1].addr)
            p[0].is_unary = 1        

            


            
        elif(len(p)==4 and (p[2]=='.' or p[2]=='->')):  #done 
            # print("here6`")
            # postfix_expression PTR_OP identifier
            # postfix_expression DOT identifier
            # print(f"p[1].val : {p[1].val}, line 371")

            if (not p[1].name.startswith('dot')):
              struct_scope = -1 if(self.symtable.isPresent(p[1].val) ==None) else self.symtable.isPresent(p[1].val)[1]
              if (struct_scope == -1 or p[1].val not in self.symtable.table[struct_scope].keys()) and len(p[1].array) == 0:
                print("Compilation error at line " + str(p[1].line_no) + " : " + p[1].val + " not declared " )
            tmp = self.EMIT.get_new_tmp(p[1].type)

            p[0] = Node(name = 'PeriodOrArrowExpression',val = p[3],line_no = p[1].line_no,type = p[1].type,children = [],place = tmp)
            p[0].ast = AST(p)
            struct_name = p[1].type
            if (struct_name.endswith('*') and p[2][0] == '.') or (not struct_name.endswith('*') and p[2][0] == '->') :
              print("Compilation error at line " + str(p[1].line_no) + " : invalid operator " +  " on " + struct_name)
              return
            if(not (struct_name.startswith('struct') or struct_name.startswith('union'))):
              print("Compilation error at line " + str(p[1].line_no) + ", " + p[1].val + " is not a struct")
              return

            found_scope = -1 if(self.symtable.isPresent(struct_name) ==None) else self.symtable.isPresent(struct_name)[1]
            flag = 0 
            for curr_list in self.symtable.table[found_scope][struct_name]['field_list']:

              if curr_list[1] == p[3].val:
                flag = 1 
                p[0].type = curr_list[0]
                p[0].parentStruct = struct_name
                if(len(curr_list) == 5):
                  p[0].level = len(curr_list[4])
            if(p[0].level == -1):
              print("Compilation error at line ", str(p[1].line_no), ", incorrect number of dimensions specified for " + p[1].val)
              return
            if flag == 0 :
              print("Compilation error at line " + str(p[1].line_no) + " : field " + " not declared in " + struct_name)
              return

            # 3AC Code Handling
            if(extract_if_tuple(p[2]) == '.'): 
              for curr_list in self.symtable.table[found_scope][struct_name]['field_list']:
                if curr_list[1] == p[3].val:
                  tmp = self.EMIT.get_new_tmp('int')
                  if(len(p[1].addr) > 0):
                    self.EMIT.emit('int_assignment',p[1].addr, '', tmp)  
                  else:
                    self.EMIT.emit('addr',p[1].place, '', tmp)
                  tmp2 = self.EMIT.get_new_tmp(curr_list[0])
                  self.EMIT.emit('int_add',tmp, curr_list[3], tmp2)
                  tmp3 = self.EMIT.get_new_tmp(curr_list[0])
                  self.EMIT.emit('deref',tmp2,'',tmp3)
                  p[0].place = tmp3
                  p[0].addr = tmp2
                  break
            else:
              for curr_list in self.symtable.table[found_scope][struct_name]['field_list']:
                if curr_list[1] == p[3].val:
                  tmp = self.EMIT.get_new_tmp('int')
                  self.EMIT.emit('int_add', p[1].place, curr_list[3], tmp)
                  tmp2 = self.EMIT.get_new_tmp(curr_list[0])
                  self.EMIT.emit('deref',tmp,'',tmp2)
                  p[0].place = tmp2
                  p[0].addr = tmp
                  break
                
    def p_lcur_br(self, p): #done 
        '''
        lcur_br : LEFT_CUR_BR               
        '''
        self.symtable.prevScope[self.symtable.next] = self.symtable.scope
        self.symtable.scope = self.symtable.next
        self.symtable.table.append({})
        self.offset[self.symtable.next] = 0
        self.symtable.next = self.symtable.next + 1
        p[0] = p[1]

    def p_l_paren(self, p): #done 
        '''
        l_paren : LEFT_PAR
        '''
        self.symtable.prevScope[self.symtable.next] = self.symtable.scope
        self.symtable.scope = self.symtable.next
        self.symtable.table.append({})
        self.offset[self.symtable.next] = 0
        self.symtable.next = self.symtable.next + 1
        p[0] = p[1]

    def p_rcur_br(self, p): #done
        '''
        rcur_br : RIGHT_CUR_BR
        '''
        self.symtable.scope = self.symtable.prevScope[self.symtable.scope]
        p[0] = p[1]
        
    def p_argument_expression_list(self,p): #done 
        '''
        argument_expression_list : assignment_expression
                                | argument_expression_list COMMA assignment_expression
        '''
        if len(p) == 4:
            p[0] = p[1]
            if p[0] != None :
                p[0].children.append(p[3])
                p[0].ast = AST(p)
        else :
            p[0] = Node(name = 'argument_expression_list',line_no = p[1].line_no,type = p[1].type,children = [p[1]])
            p[0].ast = AST(p)
        
    def p_unary_expression(self,p): #done 
        '''
        unary_expression : postfix_expression
                        | INC unary_expression
                        | DEC unary_expression
                        | SIZEOF unary_expression
                        | unary_operator cast_expression
                        | SIZEOF LEFT_PAR type_name RIGHT_PAR
        '''
        if len(p) == 2:
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
            # print("yoyo1")
        elif len(p) == 3:
            # print("yoyo2")
            if p[1] =='++' or p[1] == '--':
                node_1 = Node(name = '',val = p[1],line_no = p[2].line_no)
                p[0] = Node(name = 'Increment/Decrement Operation',val = p[2].val,line_no = p[2].line_no,type = p[2].type,children = [node_1,p[2]],place = p[2].place)
                p[0].ast = AST(p)
                x = self.symtable.isPresent(p[2].val)
                if x != None and (p[2].is_func == 1 or 'struct' in conv(p[2].type).split()):
                    print("Compilation error encountered at line",str(p[2].line_no),":Invalid operation encountered",p[2].val)
                y = p[1] if type(p[1]) is not tuple else str(p[1][0])
                if y == '++':
                    if len(p[2].addr) == 0:
                        self.EMIT.emit('inc','','',p[2].place)
                    else:
                        tmpVar2 = self.EMIT.get_new_tmp(p[2].type)
                        self.EMIT.emit(int_or_real(p[2].type) + "_+", p[2].place, '1', tmp2)
                        self.EMIT.emit(int_or_real(p[2].type) + "_=", tmp2, '*', p[2].addr)
                        p[0].place = tmpVar2

                elif y == '--':
                    if len(p[2].addr) == 0:
                        self.EMIT.emit('dec','','',p[2].place)
                    else:
                        tmpVar2 = self.EMIT.get_new_tmp(p[2].type)
                        self.EMIT.emit(int_or_real(p[2].type) + "_-", p[2].place, '1', tmp2)
                        self.EMIT.emit(int_or_real(p[2].type) + "_=", tmp2, '*', p[2].addr)
                        p[0].place = tmpVar2
            elif p[1] == 'sizeof':
                # print("This rule followed at line 1077")
                node_2 = Node(name = '',val = p[1],line_no = p[2].line_no)
                p[0] = Node(name = 'SizeOf Operation',val = p[2].val,line_no = p[2].line_no,type = p[2].type,children = [node_2,p[2]])
                p[0].ast = AST(p)
                tmpVar = self.EMIT.get_new_tmp('int')
                p[0].place = tmpVar
                p[0].is_unary = 1
                self.EMIT.emit('int_assignment',self.symtable.data_type_size(p[2].type),'',p[0].place)
            else :
                if p[1].val == '&':
                    p[0] = Node(name = 'Address_Of Operator',val = p[2].val,line_no = p[2].line_no,type = conv(p[2].type) + ' *',children = [p[2]])
                    p[0].ast = AST(p)
                    tmp = self.EMIT.get_new_tmp(p[0].type)
                    if len(p[2].addr) > 0:
                        self.EMIT.emit('int_assignment', p[2].addr, '', tmp)
                    else:
                        self.EMIT.emit('addr', p[2].place, '', tmp)
                    p[0].place = tmp
                    p[0].is_unary = 1
                elif p[1].val == '*':
                    if conv(p[2].type).endswith('*') == False and p[2].level == 0:
                        print("Compilation error encountered at line",str(p[1].line_no),":Cannot dereference the variable of type",conv(p[2].type))
                        # p[0] = Node(name = 'Error Node line 495')
                    p[0] = Node(name = 'Pointer Operator',val = p[2].val,line_no = p[2].line_no,type = p[2].type[:len(p[2].type)-2],children = [p[2]])
                    p[0].ast = AST(p)
                    tmp = self.EMIT.get_new_tmp(p[0].type)
                    self.EMIT.emit('deref', p[2].place, '', tmp)
                    p[0].place = tmp
                    p[0].addr = p[2].place
                elif p[1].val == '-':
                    tmp = self.EMIT.get_new_tmp(p[2].type)
                    p[0] = Node(name = 'Unary Minus Operator',val = p[2].val,line_no = p[2].line_no,type = p[2].type ,children = [p[2]],place = tmp)
                    p[0].ast = AST(p)
                    if p[2].type == 'char':
                        tmp = self.EMIT.get_new_tmp('int')
                        self.EMIT.emit(int_or_real('char') + '_' + int_or_real('int') +
                             '_' + '=', p[2].place, '', tmp)
                        tmp2 = self.EMIT.get_new_tmp('int')
                        self.EMIT.emit('int_' + 'uminus', tmp, '', tmp2)
                        self.EMIT.emit(int_or_real('int') + '_' + int_or_real('char') +
                        '_' + '=', tmp , '', p[0].place)

                    else:
                        self.EMIT.emit(int_or_real(p[2].type) + '_' + 'uminus', p[2].place, '', p[0].place)
                    p[0].is_unary = 1
                else:
                    tmp = self.EMIT.get_new_tmp(p[2].type)
                    p[0] = Node(name = 'Unary Negation Operator',val = p[2].val,line_no = p[2].line_no,type = p[2].type,children = [p[2]], place = tmp)
                    p[0].ast = AST(p)
                    if p[2].type == 'char':

                        tmp = self.EMIT.get_new_tmp('int')
                        self.EMIT.emit(int_or_real('char') + '_' + int_or_real('int') +
                        '_' + '=', p[2].place, '', tmp)
                        self.EMIT.emit('int_' + 'bitwisenot', tmp, '', tmp2)
                        self.EMIT.emit(int_or_real('int') + '_' + int_or_real('char') + '_' + '=', tmp , '', p[0].place)                    
                    else:
                        self.EMIT.emit(int_or_real(p[2].type) + '_' + 'bitwisenot', p[2].place,'', p[0].place)
        else:
            # print("yoyo3")
            node_3 = Node(name = '',val = p[1],line_no = p[3].line_no, children = [])
            #print("line 1125: ",p[2])
            p[0] = Node(name = 'SizeOf Operation', val = p[3].val, line_no = p[3].line_no, type = 'int', children = [node_3,p[3]])
            tmp = self.EMIT.get_new_tmp('int')
            p[0].place = tmp
            p[0].is_unary = 1
            p[0].ast = AST(p)
        # print("line 1131 :", p[0].type)
    
    def p_cast_expression(self,p):  #done
        '''
        cast_expression : unary_expression
                        | LEFT_PAR type_name RIGHT_PAR cast_expression
        '''
        if(len(p) == 2):
            p[0] = p[1]
            # print("line 1138 : ", p[0].val)
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            tmp = self.EMIT.get_new_tmp(p[2].type)
            p[0] = Node(name = 'Type Casting',val = p[2].val,line_no = p[2].line_no,type = p[2].type, place=tmp)
            p[0].ast = AST(p)
            self.EMIT.emit(int_or_real(p[4].type) + '_' + int_or_real(p[2].type) + '_' + '=', p[4].place, '', p[0].place)
            # print("line 1143 :", p[0].type)

    def p_unary_operator(self,p): #done 
        '''
        unary_operator : BIT_AND
                    | MUL
                    | ADD
                    | SUB
                    | NOT
                    | NEGATE
        '''
        p[0] = Node(name = 'unary_operator',val = p[1],line_no = p.lineno(1), place = p[1])
        p[0].ast = AST(p)
        
    def p_additive_expression(self,p):  #done
        '''
        additive_expression : multiplicative_expression
                            | additive_expression ADD multiplicative_expression
                            | additive_expression SUB multiplicative_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
            return
        elif p[1].type == None and  p[3].type == None: 
            p[0] = Node(name = 'Addition Or Subtraction',line_no = p[1].line_no,type = 'int',children = [])
            p[0].ast = AST(p)
            return
        elif p[1].type == None:
            p[0] = Node(name = 'Addition Or Subtraction',line_no = p[1].line_no, type = p[3].type,children = [])
            p[0].ast = AST(p)
            return
        elif p[3].type == None:
            p[0] = Node(name = 'Addition Or Subtraction',line_no = p[1].line_no, type = p[1].type,children = [])
            p[0].ast = AST(p)
            return
        elif conv(p[1].type).endswith('*') and not (conv(p[3].type).endswith('*')):
            if p[3].type == 'float':
                if p[2] is tuple:
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            p[0] = Node(name = 'Addition Or Subtraction',line_no = p[1].line_no,type = p[1].type,children = [])
            p[0].ast = AST(p)
        elif(conv(p[3].type).endswith('*') and not (conv(p[1].type).endswith('*'))):
            if(p[1].type == 'float'):
                if(p[2] is tuple):
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            p[0] = Node(name = 'Addition Or Subtraction',line_no = p[1].line_no,type = p[3].type,children = [])
            p[0].ast = AST(p)
        elif(conv(p[1].type).endswith('*') and conv(p[3].type).endswith('*')):
            if(p[2] is tuple):
                print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
            else:
                print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            p[0] = Node(name = 'Addition Or Subtraction',line_no = p[1].line_no,type = p[1].type,children = [])
            p[0].ast = AST(p)
        else :
            valid_types = ['char' , 'int' , 'float', 'long', 'double']
            if conv(p[1].type).split()[-1] not in valid_types or conv(p[3].type).split()[-1] not in valid_types:
                if(p[2] is tuple):
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            final_type = self.symtable.typecast(p[1].type , p[3].type)
            p[0] = Node(name = 'Addition Or Subtraction',line_no = p[1].line_no,type = final_type,children = [])
            p[0].ast = AST(p)
        x = self.symtable.isPresent(p[1].val)
        if x != None and p[1].is_func >= 1 :
            print('Compilation error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
        y = self.symtable.isPresent(p[3].val)
        if y != None and p[3].is_func >= 1 :
            print('Compilation error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
        p[0], p[1], p[2], p[3] = self.EMIT.handle_binary_emit_sub_add(p[0], p[1], p[2], p[3])
        if(p[1].level > 0 or p[3].level > 0):
            p[0].type = p[0].type + ' *'
            

    def p_multiplicative_expression(self,p):    #done
        '''
        multiplicative_expression : cast_expression
                                | multiplicative_expression MUL cast_expression
                                | multiplicative_expression DIV cast_expression
                                | multiplicative_expression MODULO cast_expression
        '''
        # print("blabla")
        if(len(p) == 2):
            # print("blabla1")
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
            return
        elif(p[1].type == None and p[3].type == None):
            # print("blabla2")
            p[0] = Node(name = 'MulDiv',line_no = p[1].line_no, type = 'int',children = [])
            p[0].ast = AST(p)
            return
        elif(p[1].type == None):
            # print("blabla3")
            p[0] = Node(name = 'MulDiv',line_no = p[1].line_no, type = p[3].type,children = [])
            p[0].ast = AST(p)
            return
        elif(p[3].type == None):
            # print("blabla4")
            p[0] = Node(name = 'MulDiv',line_no = p[1].line_no, type = p[1].type,children = [])
            p[0].ast = AST(p)
            return
            
        else :
            print("blabla5")
            tempNode = Node(name = '', val = p[2], line_no = p[1].line_no, children = [])
            type_list = ['char' , 'int' , 'long' , 'float' , 'double']
            # print("line 1254 :", p[1].type, "p[3].type : ", p[3].type)
            if(conv(p[1].type).split()[-1] not in type_list or conv(p[3].type).split()[-1] not in type_list):
                # print("line 1268 :", p[3].type)
                if(p[2] is not tuple):
                    print(p[1].line_no , 'Compilation TIME error : Incompatible data type with ' + p[2] +  ' operator')
                else :
                    print(p[1].line_no , 'Compilation TIME error : Incompatible data type with ' + p[2][0] +  ' operator')

            scope_exists = self.symtable.isPresent(p[1].val)
            if scope_exists != None and p[3].is_func == 1:
                print(f"Compilation TIME error : Invalid operation {p[3].val} at line {p[3].line_no}")
                
            if(p[2] == '%'):
                # print("line 1286 :", p[2])
                allowed_types = ['char' , 'int' , 'long']
                typecast_type = self.symtable.typecast(p[1].type , p[3].type)
                if typecast_type not in allowed_types:
                    print(p[1].line_no , 'Compilation error : Incompatible data type with MODULO operator')
                if typecast_type == 'char':
                    typecast_type = 'int'        # ascii values of characters are taken as integers values.
                p[0] = Node(name = 'MODULO', val = p[1].val, line_no = p[1].line_no, type = typecast_type, children = [])
                p[0].ast = AST(p)
            
            else :
                typecast_type = self.symtable.typecast(p[1].type , p[3].type)
                if typecast_type == 'char':
                    typecast_type = 'int'        # ascii values of characters are taken as integers values.
                p[0] = Node(name = 'MulDiv', val = p[1].val, line_no = p[1].line_no, type = typecast_type, children = [])
                if p[0] != None :
                    p[0].ast = AST(p)
            p[0], p[1], p[2], p[3] = self.EMIT.handle_binary_emit(p[0], p[1], p[2], p[3])


    def p_shift_expression(self,p): #done
        '''
        shift_expression : additive_expression
                        | shift_expression LEFT_SHIFT additive_expression
                        | shift_expression RIGHT_SHIFT additive_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            if p[1].type == None or p[3].type == None:
                p[0] = Node(name = 'Bit Shift Operation',line_no = p[1].line_no,type = 'int')
                if p[0] != None :
                    p[0].ast = AST(p)
                return
            valid_types = ['int']
            if conv(p[1].type).split()[-1] not in valid_types or conv(p[3].type).split()[-1] not in valid_types:
                if(p[2] is tuple):
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func >= 1 :
                print('Compilation error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func >= 1 :
                print('Compilation error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            final_type = self.symtable.typecast(p[1].type , p[3].type)
            p[0] = Node(name = 'Bit Shift Operation',line_no = p[1].line_no,type = final_type)
            if p[0] != None :
                p[0].ast = AST(p)
            p[0], p[1], p[2], p[3] = self.EMIT.handle_binary_emit(p[0], p[1], p[2], p[3])

    def p_relational_expression(self,p):    #done
        '''
        relational_expression : shift_expression
                            | relational_expression LESS shift_expression
                            | relational_expression GREATER shift_expression
                            | relational_expression LEQ shift_expression
                            | relational_expression GEQ shift_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
        else :
            if p[1].type == None and  p[3].type == None: # diff.
                p[0] = Node(name = 'Relational Operation',line_no = p[1].line_no,type = 'int')
                if p[0] != None :
                    p[0].ast = AST(p)
                return
            elif p[1].type == None:
                p[0] = Node(name = 'Relation Operation',line_no = p[1].line_no, type = p[3].type)
                if p[0] != None :
                    p[0].ast = AST(p)
                return
            elif p[3].type == None:
                p[0] = Node(name = 'Relation Operation',line_no = p[1].line_no, type = p[1].type)
                if p[0] != None :
                    p[0].ast = AST(p)
                return
            valid_types = ['char','int','float'] 
            if conv(p[1].type).split()[-1] not in valid_types or conv(p[3].type).split()[-1] not in valid_types:
                if(p[2] is tuple):
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func >= 1 :
                print('Compilation error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func >= 1 :
                print('Compilation error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            final_type = self.symtable.typecast(p[1].type , p[3].type)
            p[0] = Node(name = 'Relation Operation',line_no = p[1].line_no,type = final_type)
            if p[0] != None :
                p[0].ast = AST(p)
            p[0], p[1], p[2], p[3] = self.EMIT.handle_binary_emit(p[0], p[1], p[2], p[3])

    def p_equality_expression(self,p):  #done
        '''
        equality_expression : relational_expression
                            | equality_expression EQ_CHECK relational_expression
                            | equality_expression NOT_EQ relational_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
            # print("line 1394 :", p[0].val)
        else:
            if p[1].type == None and  p[3].type == None: # diff.
                p[0] = Node(name = 'Equality Check Operation',line_no = p[1].line_no,type = 'int')
                if p[0] != None :
                    p[0].ast = AST(p)
                return
            elif p[1].type == None:
                p[0] = Node(name = 'Equality Check Operation',line_no = p[1].line_no, type = p[3].type)
                if p[0] != None :
                    p[0].ast = AST(p)
                return
            elif p[3].type == None:
                p[0] = Node(name = 'Equality Check Operation',line_no = p[1].line_no, type = p[1].type)
                if p[0] != None :
                    p[0].ast = AST(p)
                return
            valid_types = ['char','int','float'] 
            if conv(p[1].type).split()[-1] not in valid_types or conv(p[3].type).split()[-1] not in valid_types:
                if(p[2] is tuple):
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func >= 1 :
                print('Compilation error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func >= 1 :
                print('Compilation error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            final_type = self.symtable.typecast(p[1].type , p[3].type)
            p[0] = Node(name = 'Equality Check Operation',line_no = p[1].line_no,type = final_type)
            if p[0] != None :
                p[0].ast = AST(p)
            p[0], p[1], p[2], p[3] = self.EMIT.handle_binary_emit(p[0], p[1], p[2], p[3])

    def p_and_expression(self,p):   #done
        '''
        and_expression : equality_expression
                    | and_expression BIT_AND equality_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
            # print("line 1437 :", p[0].val)
        else:
            if p[1].type == None and  p[3].type == None: # diff.
                p[0] = Node(name = 'And Operation',line_no = p[1].line_no,type = 'int')
                p[0].ast = AST(p)
                return
            elif p[1].type == None:
                p[0] = Node(name = 'And Operation',line_no = p[1].line_no, type = p[3].type)
                p[0].ast = AST(p)
                return
            elif p[3].type == None:
                p[0] = Node(name = 'And Operation',line_no = p[1].line_no, type = p[1].type)
                p[0].ast = AST(p)
                return
            p[0] = Node(name = 'And Operation',line_no = p[1].line_no)
            p[0].ast = AST(p)
            valid_types = ['int','char']
            if conv(p[1].type).split()[-1] not in valid_types or conv(p[3].type).split()[-1] not in valid_types:
                if(p[2] is tuple):
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator') 
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func >= 1 :
                print('Compilation error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func >= 1 :
                print('Compilation error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            p[0].type = 'int'
            p[0], p[1], p[2], p[3] = self.EMIT.handle_binary_emit(p[0], p[1], p[2], p[3])
        
    
    def p_exclusive_or_expression(self,p):  #done
        '''
        exclusive_or_expression : and_expression
                                | exclusive_or_expression XOR and_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
        else:
            if p[1].type == None and  p[3].type == None: # diff.
                p[0] = Node(name = 'XOR Operation',line_no = p[1].line_no,type = 'int')
                p[0].ast = AST(p)
                return
            elif p[1].type == None:
                p[0] = Node(name = 'XOR Operation',line_no = p[1].line_no, type = p[3].type)
                p[0].ast = AST(p)
                return
            elif p[3].type == None:
                p[0] = Node(name = 'XOR Operation',line_no = p[1].line_no, type = p[1].type)
                p[0].ast = AST(p)
                return
            p[0] = Node(name = 'XOR Operation',line_no = p[1].line_no)
            p[0].ast = AST(p)
            valid_types = ['int','char']
            if conv(p[1].type).split()[-1] not in valid_types or conv(p[3].type).split()[-1] not in valid_types:
                if(p[2] is tuple):
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator') 
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func >= 1 :
                print('Compilation error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func >= 1 :
                print('Compilation error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            p[0].type = 'int'
            p[0], p[1], p[2], p[3] = self.EMIT.handle_binary_emit(p[0], p[1], p[2], p[3])
        

    def p_inclusive_or_expression(self,p):  #done
        '''
        inclusive_or_expression : exclusive_or_expression
                                | inclusive_or_expression BIT_OR exclusive_or_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
            # print("line 1517:", p[0].val)
        else:
            if p[1].type == None and  p[3].type == None: # diff.
                p[0] = Node(name = 'OR Operation',line_no = p[1].line_no,type = 'int')
                p[0].ast = AST(p)
                return
            elif p[1].type == None:
                p[0] = Node(name = 'OR Operation',line_no = p[1].line_no, type = p[3].type)
                p[0].ast = AST(p)
                return
            elif p[3].type == None:
                p[0] = Node(name = 'OR Operation',line_no = p[1].line_no, type = p[1].type)
                p[0].ast = AST(p)
                return
            p[0] = Node(name = 'OR Operation',line_no = p[1].line_no,type = None)
            p[0].ast = AST(p)
            valid_types = ['int','char']
            if conv(p[1].type).split()[-1] not in valid_types or conv(p[3].type).split()[-1] not in valid_types:
                if(p[2] is tuple):
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator') 
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func >= 1 :
                print('Compilation error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func >= 1 :
                print('Compilation error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            p[0].type = 'int'
            p[0], p[1], p[2], p[3] = self.EMIT.handle_binary_emit(p[0], p[1], p[2], p[3])
    

    def p_logical_and_expression(self,p): #done 
        '''
        logical_and_expression : inclusive_or_expression
                            | logical_and_expression AndMark1 AND inclusive_or_expression 
        '''
        if len(p) == 2:
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
        else:
            l3 = self.EMIT.get_label()
            self.EMIT.emit('ifgoto', p[4].place, 'neq 0', l3)
            self.EMIT.emit('int_assignment', '0', '', p[2][1])
            self.EMIT.emit('goto', '', '', p[2][0])
            self.EMIT.emit('label', '', '', l3)
            self.EMIT.emit('int_assignment', '1', '', p[2][1])
            self.EMIT.emit('label', '', '', p[2][0])
            if p[1].type == None and  p[4].type == None: # diff.
                p[0] = Node(name = 'Logical And Operation',line_no = p[1].line_no,type = 'int')
                p[0].ast = AST(p)
                return
            elif p[1].type == None:
                p[0] = Node(name = 'Logical And Operation',line_no = p[1].line_no, type = p[4].type)
                p[0].ast = AST(p)
                return
            elif p[4].type == None:
                p[0] = Node(name = 'Logical And Operation',line_no = p[1].line_no, type = p[1].type)
                p[0].ast = AST(p)
                return
            p[0] = Node(name = 'Logical And Operation',line_no = p[1].line_no,type = None)
            p[0].ast = AST(p)
            valid_types = ['int','char','float']
            if conv(p[1].type).split()[-1] not in valid_types or conv(p[4].type).split()[-1] not in valid_types:
                if(p[3] is tuple):
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[3][0] +  ' operator')  
                else:
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[3] +  ' operator') 
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func == 1 :
                print('Compilation error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[4].val)
            if y != None and p[4].is_func == 1 :
                print('Compilation error encountered at line no.',p[4].line_no , ': Operation is invalid on ' + p[4].val)
            p[0].type = 'int'
            p[0] = Node(name = 'Logical And Operation',line_no = p[1].line_no,type = 'int',place = p[2][1])
        
        
    def p_AndMark1(self,p): #done
        '''AndMark1 : '''
        l1 = self.EMIT.get_label()
        l2 = self.EMIT.get_label()
        tmp = self.EMIT.get_new_tmp('int')
        self.EMIT.emit('ifgoto', p[-1].place, 'neq 0', l2)
        self.EMIT.emit('int_assignment', '0', '', tmp)
        self.EMIT.emit('goto', '', '', l1)
        self.EMIT.emit('label', '', '', l2)
        p[0] = [l1, tmp]


    def p_logical_or_expression(self,p): #done
        '''
        logical_or_expression : logical_and_expression
                            | logical_or_expression OrMark1 OR logical_and_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
        else:
            l3 = self.EMIT.get_label()
            self.EMIT.emit('ifgoto', p[4].place, 'eq 0', l3)
            self.EMIT.emit('int_assignment', '1', '', p[2][1])
            self.EMIT.emit('goto', '', '', p[2][0])
            self.EMIT.emit('label', '', '', l3)
            self.EMIT.emit('int_assignment', '0', '', p[2][1])
            self.EMIT.emit('label', '', '', p[2][0])
            if p[1].type == None and  p[4].type == None: # diff.
                p[0] = Node(name = 'Logical Or Operation',line_no = p[1].line_no,type = 'int')
                p[0].ast = AST(p)
                return
            elif p[1].type == None:
                p[0] = Node(name = 'Logical Or Operation',line_no = p[1].line_no, type = p[4].type)
                p[0].ast = AST(p)
                return
            elif p[4].type == None:
                p[0] = Node(name = 'Logical Or Operation',line_no = p[1].line_no, type = p[1].type)
                p[0].ast = AST(p)
                return
            p[0] = Node(name = 'Logical Or Operation',line_no = p[1].line_no,type = None)
            p[0].ast = AST(p)
            valid_types = ['int','char','float']
            if conv(p[1].type).split()[-1] not in valid_types or conv(p[4].type).split()[-1] not in valid_types:
                if(p[3] is tuple):
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[3][0] +  ' operator')  
                else:
                    print('Compilation error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[3] +  ' operator') 
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func == 1 :
                print('Compilation error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[4].val)
            if y != None and p[4].is_func == 1 :
                print('Compilation error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            p[0].type = 'int'
            p[0].place = p[2][1]
    
    def p_OrMark1(self,p): #done
        '''OrMark1 : '''
        l1 = self.EMIT.get_label()
        l2 = self.EMIT.get_label()
        tmp = self.EMIT.get_new_tmp('int')
        self.EMIT.emit('ifgoto', p[-1].place, 'eq 0', l2)
        self.EMIT.emit('int_assignment', '1', '', tmp)
        self.EMIT.emit('goto', '', '', l1)
        self.EMIT.emit('label', '', '', l2)
        p[0] = [l1, tmp]

    def p_conditional_expression(self,p): #done
        '''
        conditional_expression : logical_or_expression
                            | logical_or_expression CondMark1 TERNARY expression COLON CondMark2 conditional_expression
        '''
        if(len(p) == 6):
            self.symtable.table[p[2][2]][p[2][1]]['type'] = int_or_real(p[7].type)
            self.symtable.table[p[2][2]][p[2][1]]['size'] = self.symtable.data_type_size(int_or_real(p[7].type))
            self.EMIT.emit(int_or_real(p[7].type) + '_=', p[7].place, '', p[2][1])
            self.EMIT.emit('label', '', '', p[6][0])

            p[0] = Node(name = 'ConditionalOperation', line_no = p[1].line_no, type = None, children = [],place = p[2][1])
            if p[0] != None :
                p[0].ast = AST(p)
        elif(len(p) == 2) : 
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
            # print("line 1682 :", p[0].val)
    def p_CondMark1(self,p): #done
        '''CondMark1 : '''
        l1 = self.EMIT.get_label()
        tmp = self.EMIT.get_new_tmp('')
        self.EMIT.emit('ifgoto', p[-1].place, 'eq 0', l1)
        p[0] = [l1, tmp, self.symtable.scope]

    def p_CondMark2(self,p): #done
        '''CondMark2 : '''
        l2 = self.EMIT.get_label()
        self.symtable.table[p[-4][2]][p[-4][1]]['type'] = int_or_real(p[-2].type)
        self.symtable.table[p[-4][2]][p[-4][1]]['size'] = self.symtable.data_type_size(int_or_real(p[-2].type))
        self.EMIT.emit(int_or_real(p[-2].type) + '_=', p[-2].place, '', p[-4][1])
        self.EMIT.emit('.oto', '', '', l2)
        self.EMIT.emit('label', '', '', p[-4][0])
        p[0] = [l2]

    def p_assignment_expression(self,p):#done
        '''
        assignment_expression : conditional_expression
                            | unary_expression assignment_operator assignment_expression
        '''        
        if(len(p) == 4):
            if p[1].is_unary == 1:
                print('Compilation error at line ' + str(p[1].line_no) + ', left side of an assignment expression can\'t be an expression')
            if(p[1].type == None and p[3].type == None):
                p[0] = Node(name = 'AssignmentOperation', line_no = p[1].line_no, type = 'int',children = [])
                if p[0] != None :
                    p[0].ast = AST(p)
                return
            
            # use higher type
            elif p[1].type == None: 
                # print(p[1].type, p[3].type, "line 947")
                p[0] = Node(name = 'AssignmentOperation', line_no = p[1].line_no, type = p[3].type, children = [])
                if p[0] != None :
                    p[0].ast = AST(p)
                return
            elif p[3].type == None:
                p[0] = Node(name = 'AssignmentOperation', line_no = p[1].line_no, type = p[1].type, children = [])
                if p[0] != None :
                    p[0].ast = AST(p)
                return

            if p[1].type == '-1' or p[3].type == '-1':
                return
            if('const' in conv(p[1].type).split()):
                print('Error, modifying a variable declared with const keyword at line ' + str(p[1].line_no))
            if('struct' in conv(p[1].type).split() and 'struct' not in conv(p[3].type).split()):
                print('Compilation error at line ' + str(p[1].line_no) + ', cannot assign variable of type ' + p[3].type + ' to ' + p[1].type)
            elif('struct' not in conv(p[1].type).split() and 'struct' in conv(p[3].type).split()):
                print('Compilation error at line ' + str(p[1].line_no) + ', cannot assign variable of type ' + p[3].type + ' to ' + p[1].type)
            elif(conv(p[1].type).split()[-1] != conv(p[3].type).split()[-1]):
                print('Warning at line ' + str(p[2].line_no) + ': type mismatch in assignment')

            tempScope = self.symtable.isPresent(p[1].val)
            if(p[1].level != p[3].level):
                # print(p.lineno(1))
                print("Compilation error at line ", str(p.lineno(1)), ", type mismatch in assignment")
            if(p[1].level != 0 or p[3].level != 0):
                print("Compilation error at line ", str(p[1].line_no), ", cannot assign array pointer")
            if(p[1].parentStruct != None and len(p[1].parentStruct) > 0):
                found_scope = self.symtable.isPresent(p[1].parentStruct)
                if(found_scope == None):
                    print(f"p_assignment_expression : found scope is None, entry doesn't exist in symbol table ,line 1655.")
                    return
                found_scope = found_scope[1]
                for curr_list in self.symtable.table[found_scope][p[1].parentStruct]['field_list']:
                    # print(curr_list)
                    if curr_list[1] == p[1].val:
                        if len(curr_list) < 5 and len(p[1].array) == 0:
                            break
                        if(len(curr_list) < 5 or (len(curr_list[4]) < len(p[1].array))):
                            print("Compilation error at line ", str(p[1].line_no), ", incorrect number of dimensions")

            if p[2].val != '=':
                if('struct' in p[1].type.split() or ('struct' in p[3].type.split())):
                    print("Compilation error at line", str(p[1].line_no), ":Invalid operation on", p[1].val)
            
            p[0] = Node(name = 'AssignmentOperation',type = p[1].type, line_no = p[1].line_no, children = [], level = p[1].level)
            if p[0] != None :
                p[0].ast = AST(p)
            
            if('struct' in p[1].type.split() and 'struct' in p[3].type.split()):
                if(p[1].type != p[3].type):
                    print("Compilation error at line ", str(p[1].line_no), ", type mismatch in assignment")
                else:
                    if(len(p[1].addr) == 0  ):
                        self.EMIT.emit(int_or_real(p[1].type) + '_=', p[3].place, '', p[1].place)
                    else:
                        self.EMIT.emit(int_or_real(p[1].type) + '_=', p[3].place, '*', p[1].addr)
                return
            
            if p[2].val == '=':
                operator = '='
                data_type = int_or_real(p[1].type)
                if(p[1].level > 0):
                    data_type = 'int'
                type2 = int_or_real(p[3].type)
                if(p[3].level > 0):
                    type2 = 'int'
                if (type2 != data_type):
                    tmp = self.EMIT.get_new_tmp(data_type)
                    self.EMIT.emit(int_or_real(p[3].type) + '_' + int_or_real(data_type) + '_' + '=', p[3].place, '', tmp)
                    if(len(p[1].addr) == 0  ):
                        self.EMIT.emit(data_type + '_' + operator, tmp, '', p[1].place)
                    else:
                        self.EMIT.emit(data_type + '_' + operator, tmp, '*', p[1].addr)
                else:
                    if(len(p[1].addr) == 0  ):
                        self.EMIT.emit(int_or_real(p[1].type) + '_' + operator, p[3].place, '', p[1].place)
                    else:
                        self.EMIT.emit(int_or_real(p[1].type) + '_' + operator, p[3].place, '*', p[1].addr)

            else :
                operator = p[2].val[:-1]
                higher_data_type = int_or_real(self.symtable.typecast(p[1].type , p[3].type))
                if (int_or_real(p[1].type) != higher_data_type):
                    tmp = self.EMIT.get_new_tmp(higher_data_type)
                    self.EMIT.emit(int_or_real(p[1].type) + '_' + int_or_real(higher_data_type) + '_' + '=', p[1].place, '', tmp)
                    self.EMIT.emit(higher_data_type + '_' + operator, tmp, p[3].place, tmp)
                    if(len(p[1].addr) == 0):
                        self.EMIT.emit(int_or_real(higher_data_type) + '_' + int_or_real(p[1].type) + '_' + '=', tmp, '', p[1].place)
                    else:
                        tmp2 = self.EMIT.get_new_tmp(higher_data_type)
                        self.EMIT.emit(int_or_real(higher_data_type) + '_' + int_or_real(p[1].type) + '_' + '=', tmp, '', tmp2)
                        self.EMIT.emit(int_or_real(p[1].type) + '_=', tmp2, '*', p[1].addr)
                        tmp = tmp2
                elif (int_or_real(p[3].type) != higher_data_type):
                    tmp = self.EMIT.get_new_tmp(higher_data_type)
                    self.EMIT.emit(int_or_real(p[3].type) + '_' + int_or_real(higher_data_type) + '_' + '=', p[3].place, '', tmp)

                    if(len(p[1].addr) == 0  ):
                        self.EMIT.emit(higher_data_type + '_' + operator, p[1].place, tmp, p[1].place)
                    else:
                        self.EMIT.emit(int_or_real(p[1].type) + '_' + operator, tmp, p[1].place, tmp)
                        self.EMIT.emit(int_or_real(p[1].type) + '_=' , tmp, '*', p[1].addr)
                else:
                    if((operator == '+' or operator == '-') and p[1].type.endswith('*')):
                        tmp = self.EMIT.get_new_tmp('int')
                        self.EMIT.emit('int_mul',p[3].place,self.symtable.data_type_size(p[1].type[:-2]), tmp)
                        if(len(p[1].addr) == 0  ):
                            self.EMIT.emit(int_or_real(p[1].type) + '_' + operator, tmp, p[1].place, p[1].place)
                        else:
                            tmp2 = self.EMIT.get_new_tmp(p[0].type)
                            self.EMIT.emit(int_or_real(p[1].type) + '_' + operator, tmp, p[1].place, tmp2)
                            self.EMIT.emit(int_or_real(p[1].type) + '_=' , tmp2, '*', p[1].addr)
                    else:
                        if(len(p[1].addr) == 0  ):
                            self.EMIT.emit(int_or_real(p[1].type) + '_' + operator, p[3].place, p[1].place, p[1].place)
                        else:
                            tmp = self.EMIT.get_new_tmp(p[0].type)
                            self.EMIT.emit(int_or_real(p[1].type) + '_' + operator, p[3].place, p[1].place, tmp)
                            self.EMIT.emit(int_or_real(p[1].type) + '_=' , tmp, '*', p[1].addr)

            if(len(p[1].addr) == 0):
                p[0].place = p[1].place
            else:
                tmp = self.EMIT.get_new_tmp(p[0].type)
                self.EMIT.emit('deref', p[1].addr, '', tmp)
                p[0].place = tmp
        
        else :
            p[0] = p[1]
            p[0].ast = AST(p)

    def p_assignment_operator(self,p): #done
        '''
        assignment_operator : ASSIGNMENT
                            | SHORT_ADD
                            | SHORT_SUB
                            | SHORT_MUL
                            | SHORT_DIV
                            | SHORT_XOR
                            | SHORT_AND
                            | SHORT_OR
                            | SHORT_MOD
                            | SHORT_LEFT_SHIFT
                            | SHORT_RIGHT_SHIFT
        '''
        p[0] = Node(name = 'assignment_operator',val = p[1], line_no = p.lineno(1), children = [p[1]])
        if p[0] != None :
            p[0].ast = AST(p)
        # print(p.lineno(1))

        

    def p_expression(self,p):   #done
        '''
        expression : assignment_expression
                | expression COMMA assignment_expression
        '''
        if(len(p) == 2):
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            p[0] = p[1]
            
            if(p[0]!=None):
                p[0].children.append(p[3])
                p[0].ast = AST(p)
                p[0].is_unary = 1

    def p_constant_expression(self,p):  #done
        '''
        constant_expression : conditional_expression
        '''
        p[0] = p[1]
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_declaration(self,p):  #done
        '''
        declaration : declaration_specifiers SEMI_COLON
                    | declaration_specifiers init_declarator_list SEMI_COLON
                    | CLASS_OBJ identifier init_declarator_list SEMI_COLON
        '''
        if(len(p) == 3):
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)

        elif(len(p) == 4):
            if(p[2].is_func > 0):
                self.symtable.scope = self.symtable.prevScope[self.symtable.scope]
            p[0] = Node(name = 'Declaration', val = p[1], type = p[1].type, line_no = p.lineno(1), children = [])
            if(p[0]!=None):
                p[0].ast = AST(p)

            flag = 1
            if('void' in p[1].type.split()):
                flag = 0
            for child in p[2].children:
                if(child.name == 'InitDeclarator'):
                    if(conv(p[1].type).startswith('typedef')):
                        print("Compilation error at line " + str(p[1].line_no) + ": typedef intialized")
                        continue
                    if(child.children[0].val in self.symtable.table[self.symtable.scope].keys()):
                      print(p.lineno(1), 'Compilation error : ' + child.children[0].val + ' already declared')
                    # print(child.children[0].val,child.children[1].val)
                    self.symtable.table[self.symtable.scope][child.children[0].val] = {}
                    self.symtable.table[self.symtable.scope][child.children[0].val]['type'] = p[1].type
                    self.symtable.table[self.symtable.scope][child.children[0].val]['value'] = child.children[1].val
                    self.symtable.table[self.symtable.scope][child.children[0].val]['size'] = self.symtable.data_type_size(p[1].type)
                    self.symtable.table[self.symtable.scope][child.children[0].val]['offset'] = self.offset[self.symtable.scope]
                    totalEle = 1
                    act_data_type=p[1].type
                    if(len(child.children[0].array) > 0):
                        self.symtable.table[self.symtable.scope][child.children[0].val]['array'] = child.children[0].array
                        for i in child.children[0].array:
                            totalEle = totalEle*i
                    if(child.children[0].type != None):
                        self.symtable.table[self.symtable.scope][child.children[0].val]['type'] = p[1].type + ' ' + child.children[0].type 
                        self.symtable.table[self.symtable.scope][child.children[0].val]['type'] = act_data_type 
                        self.symtable.table[self.symtable.scope][child.children[0].val]['size'] = 8
                    elif(flag == 0):
                        print("Compilation error at line " + str(p[1].line_no) + ", variable " + child.children[0].val + " cannot have type void")
                    self.symtable.table[self.symtable.scope][child.children[0].val]['size'] *= totalEle
                    self.offset[self.symtable.scope] += self.symtable.table[self.symtable.scope][child.children[0].val]['size']

                    # 3AC Code
                    child.children[0].place = child.children[0].val + '_' + str(self.symtable.scope)
                    operator = '='
                    data_type = int_or_real(act_data_type)
                    type2 = int_or_real(child.children[1].type)
                    if(child.children[1].level > 0):
                        type2 = 'int'
                    if act_data_type.endswith('*') and not (child.children[1].type.endswith('*') or child.children[1].level > 0):
                        print("Compilation error at line " + str(p[1].line_no) + ", variable " + child.children[1].val + " is not a pointer")
                    elif(len(child.children[0].array) > 0):
                        base_addr = ''
                        if(conv(child.children[1].type).endswith('*')):
                            self.EMIT.emit('int_assignment', child.children[1].place, '', child.children[0].place)
                        elif(len(child.children[0].addr) == 0):
                            base_addr = self.EMIT.get_new_tmp(p[1].type)
                            self.EMIT.emit('addr', child.children[0].place, '', base_addr)
                        else:
                            base_addr = child.children[0].addr
                            self.array_init(base_addr, 0, act_data_type, child.children[0].array, child.children[1], 0, p.lineno(1))
                    elif((p[1].type.startswith('struct') or p[1].type.startswith('union')) and not act_data_type.endswith('*')):
                        found_scope = self.symtable.isPresent(p[1].type)
                        if(found_scope!=None):
                            found_scope = found_scope[1]
                        base_addr = ''
                        if(len(child.children[0].addr) == 0):
                            base_addr = self.EMIT.get_new_tmp('int')
                            self.EMIT.emit('addr', child.children[0].place, '', base_addr)
                        else:
                            base_addr = child.children[0].addr
                        # print("line 1949 :", found_scope, "type :", p[1].type, "table :", self.symtable.table[found_scope][p[1].type])
                        self.struct_init(base_addr, child.children[0].place, found_scope, p[1].type, child.children[1], p.lineno(1))
                    elif (type2 != data_type):
                        tmp = self.EMIT.get_new_tmp(data_type)
                        self.EMIT.emit(int_or_real(type2) + '_' + int_or_real(data_type) + '_' + '=', child.children[1].place, '', tmp)
                        self.EMIT.emit(data_type + '_' + operator, tmp, '', child.children[0].place)
                    else:
                        self.EMIT.emit(data_type + '_' + operator, child.children[1].place, '', child.children[0].place)

                else:
                    if(child.val in self.symtable.table[self.symtable.scope].keys() and 'is_func' in self.symtable.table[self.symtable.scope][child.val]):
                        continue
                    if(child.val in self.symtable.table[self.symtable.scope].keys() and 'is_func' not in self.symtable.table[self.symtable.scope][child.val]):
                        print(p.lineno(1), 'Compilation error : ' + child.val + ' already declared')
                    self.symtable.table[self.symtable.scope][child.val] = {}
                    self.symtable.table[self.symtable.scope][child.val]['type'] = p[1].type
                    self.symtable.table[self.symtable.scope][child.val]['size'] = self.symtable.data_type_size(p[1].type)
                    self.symtable.table[self.symtable.scope][child.val]['offset'] = self.offset[self.symtable.scope]
                    totalEle = 1
                    if(len(child.array) > 0):
                        self.symtable.table[self.symtable.scope][child.val]['array'] = child.array
                        for i in child.array:
                            totalEle = totalEle*i
                    if(child.type != None):
                        self.symtable.table[self.symtable.scope][child.val]['type'] = p[1].type + ' ' + child.type
                        self.symtable.table[self.symtable.scope][child.val]['size'] = 8
                    elif(flag == 0):
                        print("Compilation error at line " + str(p[1].line_no) + ", variable " + child.val + " cannot have type void")
                    self.symtable.table[self.symtable.scope][child.val]['size'] *= totalEle
                    self.offset[self.symtable.scope] += self.symtable.table[self.symtable.scope][child.val]['size']

    def p_declaration_specifiers(self,p):   #done
        '''
        declaration_specifiers : storage_class_specifier %prec IFX1
                            | declaration_specifiers storage_class_specifier %prec IFX8 
                            | type_specifier %prec IFX1
                            | declaration_specifiers type_specifier %prec IFX8
                            | type_qualifier %prec IFX1
                            | declaration_specifiers type_qualifier %prec IFX8
                            | VIRTUAL %prec IFX1
                            | FRIEND %prec IFX1
        '''
        # storage_class_specifier, type_specifier, type_qualifier done
        # !!! implement virtual, friend rules
        if(len(p) == 2):
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
            if p[1].type ==None:
                self.curType.append('')
                
            else :
                # print(self.curType)
                self.curType.append(conv(p[1].type))

        elif(len(p) == 3):
            # print(f"p[1].name : {p[1].name}, p[2].name : {p[2].name}, line 1134")
            if(p[1].name == 'storageClassSpecifier' and p[2].name.startswith('storageClassSpecifier')):
                print("Invalid Syntax at line " + str(p[1].line_no) + ", " + conv(p[2].type) + " not allowed after " + conv(p[1].type))
            if(p[1].name == 'type_specifier_1' and (p[2].name.startswith('type_specifier_1') or p[2].name.startswith('StorageClassSpecifier') or p[2].name.startswith('TypeQualifier'))):
                print("Invalid Syntax at line " + str(p[1].line_no) + ", " + conv(p[2].type) + " not allowed after " + conv(p[1].type))
            if(p[1].name == 'typeQualifier' and (p[2].name.startswith('storageClassSpecifier') or p[2].name.startswith('TypeQualifier'))):
                print("Invalid Syntax at line " + str(p[1].line_no) + ", " + conv(p[2].type) + " not allowed after " + conv(p[1].type))
            # if(p[1].name == '') 
            self.curType.pop()
            self.curType.append(conv(p[1].type) + ' ' + conv(p[2].type))
            
            temp = ""
            if p[1] != None:
                temp = conv(p[1].type) + ' ' + conv(p[2].type)
            else:
                temp = p[2].type
            self.curType.append(conv(temp))
            
            p[0] = Node(name = p[1].name + p[2].name, val = p[1], type = temp, line_no = p[1].line_no, children = [])
            if(p[0]!=None):
                p[0].ast = AST(p)
    

    def p_init_declarator_list(self,p): #done
        '''
        init_declarator_list : init_declarator
                            | init_declarator_list COMMA init_declarator
        '''
        if(len(p) == 2):
            p[0] = Node(name = 'InitDeclaratorList', line_no = p.lineno(1), children = [p[1]])
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            p[0] = p[1]
            p[0].children.append(p[3])
            if(p[0]!=None):
                p[0].ast = AST(p)
    

    def p_init_declarator(self,p):  #done
        '''
        init_declarator : declarator
                        | declarator ASSIGNMENT initializer
        '''
        if(len(p) == 4):
            # print(p[1]," line ")
            p[0] = Node(name = 'InitDeclarator', type = p[1].type, line_no = p.lineno(1), children = [p[1],p[3]], array = p[1].array)
            if(p[0]!=None):
                p[0].ast = AST(p)
            if(len(p[1].array) > 0 and (p[3].max_depth == 0 or p[3].max_depth > len(p[1].array))):
                print('Compilation error at line ' + str(p.lineno(1)) + ' , invalid initializer')
            if(p[1].level != p[3].level):
                print("Compilation error at line ", str(p[3].line_no), ",  type mismatch")
            
        else : 
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
            
            
    def p_storage_class_specifier(self,p):  #done
        '''
        storage_class_specifier : AUTO
        '''
        p[0] = Node(name = 'storageClassSpecifier',type = p[1], line_no = p.lineno(1), children = [])

    
    def p_type_specifier_1(self,p): #done
        ''' 
        type_specifier : VOID  
                    | CHAR  
                    | INT  
                    | FLOAT  
                    | BOOL  
                    | STRING_KEY
        '''
        p[0] = Node(name = 'type_specifier_1',type = p[1], line_no = p.lineno(1))
        # print(p[1])

    def p_type_specifier_2(self,p): #done
        '''
        type_specifier : struct_specifier
                    | class_specifier
        '''
        # print("line 2088:",p[1])
        p[0] = p[1]
        if(p[0]!=None):
            p[0].ast = AST(p)


    # def p_simple_type_specifier(self, p):
    #     '''
    #     simple_type_specifier : COLONCOLON nested_name_specifier class_name
    #                         | nested_name_specifier class_name
    #                         | COLONCOLON class_name
    #                         | class_name
    #     '''
    #     pass


    def p_class_specifier(self,p):
        '''
        class_specifier : class_head lcur_br member_specification rcur_br
                        | class_head lcur_br rcur_br
        '''
        pass
   

    
    def p_class_head(self,p):
        '''
        class_head : class_key
                   | class_key identifier
                   | class_key base_clause
                   | class_key identifier base_clause
                   | class_key nested_name_specifier identifier
                   | class_key nested_name_specifier identifier base_clause
        '''
        pass
        # catch
        
    def p_class_key(self, p):
        '''
        class_key : CLASS
        '''
        if(p[0]!=None):
            p[0] = Node(name = p[1], line_no = p.lineno(1))

    def p_base_clause(self,p):
        '''
        base_clause : COLON base_specifier_list
        '''
        pass
        # catch
    
    def p_base_specifier_list(self,p):
        '''
        base_specifier_list : base_specifier
                            | base_specifier_list COMMA base_specifier
        '''
        pass
        # catch

    def p_base_specifier(self,p):
        '''
        base_specifier :  class_name
                        | nested_name_specifier class_name
                        | COLONCOLON class_name
                        | COLONCOLON nested_name_specifier class_name
                        | VIRTUAL COLONCOLON class_name
                        | VIRTUAL access_specifier COLONCOLON class_name
                        | VIRTUAL COLONCOLON nested_name_specifier class_name
                        | VIRTUAL access_specifier COLONCOLON nested_name_specifier class_name
	                    | access_specifier VIRTUAL COLONCOLON nested_name_specifier class_name
                        | access_specifier COLONCOLON class_name
                        | access_specifier COLONCOLON nested_name_specifier class_name
                        | access_specifier VIRTUAL COLONCOLON  class_name
                        | VIRTUAL access_specifier nested_name_specifier class_name
                        | VIRTUAL access_specifier class_name
                        | VIRTUAL class_name
                        | VIRTUAL nested_name_specifier class_name
	                    | access_specifier VIRTUAL nested_name_specifier class_name
                        | access_specifier nested_name_specifier class_name
                        | access_specifier VIRTUAL class_name
                        | access_specifier class_name
        '''
        pass
        # catch
    
    def p_member_specification(self,p):
        '''
        member_specification : member_declaration member_specification
                             | member_declaration
                             | access_specifier COLON member_specification
                             | access_specifier COLON
        '''
        pass
        # print("....")
        # catch

    def p_nested_name_specifier(self,p):
        '''
        nested_name_specifier : ID COLONCOLON %prec IFX8
                              | ID COLONCOLON nested_name_specifier %prec IFX1 
        '''
        pass

    def p_class_name(self,p):
        '''
        class_name : identifier
        '''
        p[0] = p[1]
        if(p[0]!=None):
            p[0] = AST(p)

    def p_access_specifier(self,p):
        '''
        access_specifier : PRIVATE
                         | PROTECTED
                         | PUBLIC
        '''
        p[0] = Node (name = 'Access Specifier',line_no = p.lineno(1),children = [])
        if(p[0]!=None):
            p[0] = AST(p)

    def p_member_declaration(self,p):
        '''
        member_declaration : declaration_specifiers member_declarator_list SEMI_COLON
                            | member_declarator_list SEMI_COLON
                            | decl_specifier_seq SEMI_COLON
                            | SEMI_COLON 
                            | function_definition %prec IFX1
	                        | function_definition SEMI_COLON %prec IFX2
                            | VIRTUAL function_definition
	                        | qualified_id SEMI_COLON
                            | NOT class_name LEFT_PAR RIGHT_PAR compound_statement
        '''
        pass
        # print(".....")
        # catch
    
    def p_qualified_id(self,p):
        '''
        qualified_id : nested_name_specifier unqualified_id
        '''
        pass
        # catch
    
    def p_unqualified_id(self,p):
        # removed the rule "NOT class_name" here.
        '''
        unqualified_id : identifier
        ''' 
        p[0] = p[1]
        p[0].ast = AST(p)
        #catch
    
    def p_member_declarator(self, p):
        # check for eps rule
        '''
        member_declarator : declarator
                        | declarator pure_specifier
                        | declarator constant_initializer
                        | COLON constant_expression
                        | identifier COLON constant_expression
        '''
        pass
        #catch



    # catch : maybe error in  
    def p_pure_specifier(self, p):
        '''
        pure_specifier : ASSIGNMENT '0'
        '''
        pass


    def p_constant_initializer(self, p):
        '''
        constant_initializer : ASSIGNMENT constant_expression
        '''
        pass


    def p_member_declarator_list(self,p):
        '''
        member_declarator_list : member_declarator
	                          | member_declarator_list COMMA member_declarator
        '''
        pass
        # print("....")
        #catch

    # def p_function_specifier(self, p):
    #     '''
    #     function_specifier : VIRTUAL
    #     '''
    #     pass
        #catch 
        
    # def p_decl_specifier(self, p):        
    #     '''
    #     decl_specifier : storage_class_specifier
    #                     | type_specifier
    #                     | function_specifier
    #                     | FRIEND
    #     '''
    #     pass


    def p_decl_specifier_seq(self,p): # incomplete
        '''
            decl_specifier_seq : declaration_specifiers %prec IFX1
                                | decl_specifier_seq declaration_specifiers %prec IFX8
        '''
        if(len(p) == 2):
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)

    
    def p_struct_id_decl(self, p):  #introduced to handle case where struct pointer is introduced within a struct
        '''
        struct_id_decl : struct identifier
        '''
        p[0] = p[1]
        p[1].type = conv(p[1].type) + ' ' + conv(p[2].val)
        p[0].type = p[1].type
        p[0].val = p[1].type
        p[0].name = conv(p[0].name) + '+'
        # print("line 2315 :", p[0].name)

        name_ = p[1].type
        # print("line 2318 :", name_, "scope = ", self.symtable.scope)
        if(p[0]!=None):
            p[0].ast = AST(p)
        if name_ in self.symtable.table[self.symtable.scope].keys():
            print('Compilation error occured at line'+str(p[1].line_no)+':Struct with this name has already been declared')
        ptr_name_ = name_ + ' *'
        self.symtable.table[self.symtable.scope][name_] = {}
        self.symtable.table[self.symtable.scope][name_]['type'] = name_
        self.symtable.table[self.symtable.scope][ptr_name_] = {}
        self.symtable.table[self.symtable.scope][ptr_name_]['type'] = ptr_name_

    def p_struct_specifier(self,p): #done
        '''
        struct_specifier : struct_id_decl lcur_br struct_declaration_list rcur_br
                                | struct lcur_br struct_declaration_list rcur_br
                                | struct identifier
        '''
        p[0] = Node(name = 'Struct Specifier')
        # print("line 2336 :", p[1].name)
        if len(p) == 5 and p[1].name.endswith('+'):
            # print("line 2339 : ___________________________________________")
            name_ = p[1].type
            # name_ = 'struct ' +  conv(p[2].val)
            # if(p[0]!=None):
            #     p[0].ast = AST(p)
            # if name_ in self.symtable.table[self.symtable.scope].keys():
            #     print('Compilation error occured at line'+str(p[1].line_no)+':Struct with this name has already been declared')
            ptr_name_ = name_ + ' *'
            # self.symtable.table[self.symtable.scope][name_] = {}
            # self.symtable.table[self.symtable.scope][name_]['type'] = name_
            # self.symtable.table[self.symtable.scope][ptr_name_] = {}
            # self.symtable.table[self.symtable.scope][ptr_name_]['type'] = ptr_name_
            already_decl = []
            mem_offset = 0
            #print(p[4].children, "line 2352")
            for child in p[3].children:
                for items in already_decl:
                    if items[1] == child.val:
                        print("Compilation error encountered at line "+str(p[4].line_no)+':'+child.val +'Child of struct already encountered')
                if self.symtable.data_type_size(child.type) == -1:
                    print("Compilation error encountered at line "+ str(p[4].line_no)+':Data type not valid')
                mem_size = self.symtable.data_type_size(child.type)
                temp_arr = [child.type, child.val, mem_size, mem_offset]
                num_of_elements = 1
                if len(child.array)>0 :
                    temp_arr.append(child.array)
                    for elems in child.array:
                        num_of_elements *= elems
                mem_offset += (self.symtable.data_type_size(child.type))* num_of_elements
                temp_arr[2] *= num_of_elements
                mem_size *= num_of_elements
                # print(temp_arr, "line 1454")
                already_decl.append(temp_arr)
            # print("line 2367: ", name_, " scope : ", self.symtable.scope, "table : ", self.symtable.table[self.symtable.scope])
            self.symtable.table[self.symtable.scope][name_]['field_list'] = already_decl
            self.symtable.table[self.symtable.scope][name_]['size'] = mem_offset
            self.symtable.table[self.symtable.scope][ptr_name_]['field_list'] = already_decl
            self.symtable.table[self.symtable.scope][ptr_name_]['size'] = 8
        
        elif len(p) == 3:
            if(p[0]!=None):
                p[0].type = 'struct ' + conv(p[2].val)
                p[0].ast = AST(p)
            x = self.symtable.isPresent(conv(p[0].type))
            if x== None :
                print("Compilation error at line ",str(p[1].line_no)+': Invalid Type',conv(p[0].type))
        
        else :
            if(p[0]!=None):
                p[0].ast = AST(p)
        # print("line 2383 : ", self.symtable.table)
                  
    def p_struct(self,p):   #done
        '''
        struct : STRUCT
        '''
        p[0] = Node ( name = 'Struct', type = 'struct', line_no = p.lineno(1))
        if(p[0]!=None):
            p[0].ast = AST(p)
            
    def p_struct_declaration(self,p):   #done
        '''
        struct_declaration : specifier_qualifier_list struct_declarator_list SEMI_COLON
        '''
        p[0] = Node(name = 'StructDeclaration', type = p[1].type, line_no = p[1].line_no)
        p[0].ast = AST(p)
        p[0].children = p[2].children
        for child in p[0].children:
            if child.type != None:
                child.type = conv(p[1].type) + ' ' + conv(child.type)
            else:
                if('void' in conv(p[1].type).split()):
                    print("Compilation error encountered at line " + str(p[1].line_no) + ", variable " + child.val + " cannot have type void")
                child.type = p[1].type
    
    def p_struct_declaration_list(self,p):  #done
        '''
        struct_declaration_list : struct_declaration
                                | struct_declaration_list struct_declaration
        '''
        p[0] = Node(name = 'Struct Declaration List', type = p[1].type, line_no = p[1].line_no)
        if(p[0]!=None):
            p[0].ast = AST(p)
        if len(p) == 2:
            p[0].children = p[1].children
        else :
            p[0].children = p[1].children
            p[0].children.extend(p[2].children)
        # print(p[1].children, "line 1506")
    
    def p_specifier_qualifier_list(self,p): #done
        '''
        specifier_qualifier_list : type_specifier specifier_qualifier_list  
                                | type_specifier  
                                | type_qualifier specifier_qualifier_list   
                                | type_qualifier 
        '''
        p[0] = Node(name = 'Specifier Qualifier List', type = p[1].type, line_no = p[1].line_no)
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_struct_declarator_list(self,p):   #done
        '''
        struct_declarator_list : struct_declarator
                            | struct_declarator_list COMMA struct_declarator
        '''
        p[0] = Node(name = 'Struct Declarator List',type = p[1].type, line_no = p[1].line_no)
        if len(p) == 2:
            p[0].children = [p[1]]
        else :
            p[0].children = p[1].children

            # error : changed here, catch
            if(isinstance(p[3], list)):
                p[0].children.extend(p[3])
            else :
                p[0].children.append(p[3])
        p[0].ast = AST(p)
        

    def p_struct_declarator(self,p):    #done
        '''
        struct_declarator : declarator
                        | COLON constant_expression
                        | declarator COLON constant_expression
        '''
        if len(p) == 3:
            p[0] = p[2]
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            p[0] = p[1] 
            if(p[0]!=None):
                p[0].ast = AST(p)
            
    def p_type_qualifier(self,p):#done
        '''
        type_qualifier : CONST
        '''
        p[0] = Node(name = 'typeQualifier', type = p[1], line_no = p.lineno(1), children = [])


    def p_declarator(self,p):#done
        '''
        declarator : pointer direct_declarator
                | direct_declarator
        '''
        global funcReturntype
        # print("line 2480 : ", funcReturntype)
        if(len(p) == 2):
            p[0] = p[1]
            if(p[0]!=None):
                p[0].name = 'Declarator'
                p[0].val = p[1].val
                p[0].array = p[1].array
                p[0].ast = AST(p)
        else :
            p[0] = p[2]
            p[0].name = 'Declarator'
            p[0].type = p[1].type
            if(p[0]!=None):
                p[0].ast = AST(p)
            if(p[2].val in self.symtable.table[self.symtable.prevScope[self.symtable.scope]] and 'is_func' in self.symtable.table[self.symtable.prevScope[self.symtable.scope]][p[2].val].keys()):
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]
                                    ][p[2].val]['type'] = self.symtable.table[self.symtable.prevScope[self.symtable.scope]][p[2].val]['type'] + ' ' + p[1].type
                funcReturntype = funcReturntype + ' ' + conv(p[1].type)
                # print("line 2501 : ", funcReturntype)

            p[0].val = p[2].val
            p[0].array = p[2].array

    def p_direct_declarator_1(self,p): #done
        '''
        direct_declarator : identifier
                        | LEFT_PAR declarator RIGHT_PAR
                        | direct_declarator l_paren parameter_type_list RIGHT_PAR
                        | direct_declarator l_paren identifier_list RIGHT_PAR
        '''
        global funcReturntype
        # print("line 2511 : ", funcReturntype)
        if len(p) == 2:
            p[0] = Node(name = 'ID', val = p[1].val, line_no = p.lineno(1), children = [])
            # p[0].ast = AST(p)
            AST(p)
            if(p[0]!=None):
                p[0].ast = p[1].val
            # print("||", p[0].ast, "||", p[1].name , p[1].val , " line 1570")

        elif len(p) == 4:
            p[0] = p[2]
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
                p[0].children = p
            
        if(len(p)== 5 and p[3].name == 'ParameterList'):
            p[0].children = p[3].children
            p[0].type = self.curType[-1]
            prev_func_name = ''
            if(p[1].val in self.symtable.function_overloaded_map.keys()):
                prev_func_name = p[1].val + '_' + str(self.symtable.function_overloaded_map[p[1].val])
            
            if(prev_func_name != ''):
                if('is_func' not in self.symtable.table[0][prev_func_name] or self.symtable.table[0][prev_func_name]['is_func'] == 1):
                    tempList = []
                    for child in p[3].children:
                        tempList.append(child.type)
                    for i in range(int(self.symtable.function_overloaded_map[p[1].val]) + 1):
                        prev_name = p[1].val + '_' + str(i)
                        prevList = copy.deepcopy(self.symtable.table[0][prev_name]['argumentList'])
                        if(len(prevList) != len(tempList)):
                            continue
                        else:
                            if(prevList == tempList):
                                print('Compilation error : near line ' + str(p[1].line_no) + ' function already declared, line 2502')
                                return
                                
                else :
                    if(prev_func_name in self.symtable.functionScope.keys()):
                        self.symtable.scope_to_function.pop(self.symtable.functionScope[prev_func_name])
                    self.symtable.functionScope[prev_func_name] = self.symtable.scope
                    self.symtable.scope_to_function[self.symtable.scope] = prev_func_name
                    self.symtable.local_vars[prev_func_name] = []
                    iterator = 0
                    for child in p[3].children:
                        if(child.type != self.symtable.table[0][prev_func_name]['argumentList'][iterator]):
                            print('Compilation error : near line ' + str(p[1].line_no) + ' argument ' + str(iterator+1) +' does not match function declaration')
                        iterator += 1
                    p[0].virtual_func_name = prev_func_name
                    self.symtable.func_arguments[prev_func_name] = [arg_node.val for arg_node in p[3].children]
                    return 
            
            cur_func_name = p[1].val + '_0'
            if(p[1].val in self.symtable.function_overloaded_map.keys()):
                cur_func_name = p[1].val + '_' + str(int(self.symtable.function_overloaded_map[p[1].val]) + 1)
            self.symtable.func_arguments[cur_func_name] = []
            
            self.symtable.func_arguments[cur_func_name] = [arg_node.val for arg_node in p[3].children]
            
            self.symtable.table[self.symtable.prevScope[self.symtable.scope]][cur_func_name] = {}
            self.symtable.table[0][p[1].val] = {}
            self.symtable.table[0][p[1].val]['type'] = 'virtual_func'
            self.symtable.table[0][p[1].val]['is_func'] = 2
            self.symtable.table[self.symtable.prevScope[self.symtable.scope]][cur_func_name]['is_func'] = 2
            self.symtable.ignore_function_ahead.append(cur_func_name)
            p[0].is_func = 2
            tempList = []
        
            for child in p[3].children:
                tempType = child.type
                tempList.append(tempType)
        
            self.symtable.table[self.symtable.prevScope[self.symtable.scope]][cur_func_name]['argumentList'] = tempList
            self.symtable.table[self.symtable.prevScope[self.symtable.scope]][cur_func_name]['type'] = self.curType[-1-len(tempList)]
            funcReturntype = copy.deepcopy(self.curType[-1-len(tempList)])
            # print("line 2593 : ", funcReturntype)
            if(cur_func_name in self.symtable.functionScope.keys()):
                self.symtable.scope_to_function.pop(self.symtable.functionScope[cur_func_name])
            self.symtable.functionScope[cur_func_name] = self.symtable.scope
            self.symtable.scope_to_function[self.symtable.scope] = cur_func_name
            self.symtable.local_vars[cur_func_name] = []
            p[0].virtual_func_name = cur_func_name
            if(p[1].val in self.symtable.function_overloaded_map):
                self.symtable.function_overloaded_map[p[1].val] += 1
            else:
                self.symtable.function_overloaded_map[p[1].val] = 0

    
    def p_direct_declarator_2(self,p):  #done
        '''
        direct_declarator : direct_declarator LEFT_SQ_BR constant_expression RIGHT_SQ_BR
                        | direct_declarator LEFT_SQ_BR RIGHT_SQ_BR
                        | direct_declarator l_paren RIGHT_PAR
        '''
        global funcReturntype
        # print("line 2610 : ", funcReturntype)
        if len(p) == 5 :
            p[0] = Node(name = 'Array Declarator', val = p[1].val, line_no = p.lineno(1), place=p[1].place)
            if(p[0]!=None):
                p[0].ast = AST(p)
                p[0].array = copy.deepcopy(p[1].array)
                # print(p[3].val," line 2619")  
                # BAD FIX
                try :
                    p[0].array.append(int(p[3].val))
                except :
                    # print(self.symtable.isPresent(p[3].val)[0])
                    p[0].array.append(int(self.symtable.isPresent(p[3].val)[0]['value']))

        else :
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
            if(p[3] == ')'):
                prev_func_name = ''
                if(p[1].val in self.symtable.function_overloaded_map.keys()):
                    prev_func_name = p[1].val + '_' + str(self.symtable.function_overloaded_map[p[1].val])
                # print("line 1600 ", p[1].val, " ", self.symtable.scope)
                if(prev_func_name != ''):
                    if('is_func' not in self.symtable.table[0][prev_func_name] or self.symtable.table[0][prev_func_name]['is_func'] == 1):
                        for i in range(int(self.symtable.function_overloaded_map[p[1].val]) + 1):
                            prev_name = p[1].val + '_' + str(i)
                            prevList = copy.deepcopy(self.symtable.table[0][prev_name]['argumentList'])
                        if(len(prevList) == 0):
                            print('Compilation error : near line ' + str(p[1].line_no) + ' function already declared')
                            return
                    else:
                        if(prev_func_name in self.functionScope.keys()):
                            self.scope_to_function.pop(self.functionScope[prev_func_name])
                        self.functionScope[prev_func_name] = self.currentScope
                        self.scope_to_function[self.symtable.scope] = prev_func_name
                        # self.symtable.local_vars[prev_func_name] = []
                        p[0].virtual_func_name = prev_func_name
                        self.symtable.func_arguments[prev_func_name] = []
                        return 
                
                if(p[1].val in self.symtable.table[self.symtable.prevScope[self.symtable.scope]].keys()):
                    print('Compilation error : near line ' + str(p[1].line_no) + ' function already declared')
                cur_func_name = p[1].val + '_0'
                if(p[1].val in self.symtable.function_overloaded_map.keys()):
                    cur_func_name = p[1].val + '_' + str(int(self.symtable.function_overloaded_map[p[1].val]) + 1)
                # func_arguments[cur_func_name] = []
                p[0].virtual_func_name = cur_func_name
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]][cur_func_name] = {}
                self.symtable.table[0][p[1].val] = {}
                self.symtable.table[0][p[1].val]['type'] = 'virtual_func'
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]][cur_func_name]['type'] = self.curType[-1]
                funcReturntype = copy.deepcopy(self.curType[-1])
                # print("line 2656 : ", funcReturntype)
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]][cur_func_name]['is_func'] = 2
                self.symtable.table[0][p[1].val]['is_func'] = 2
                self.symtable.ignore_function_ahead.append(cur_func_name)
                p[0].is_func = 2
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]][cur_func_name]['argumentList'] = []
                if(cur_func_name in self.symtable.functionScope.keys()):
                    self.symtable.scope_to_function.pop(self.symtable.functionScope[cur_func_name])
                self.symtable.functionScope[cur_func_name] = self.symtable.scope
                self.symtable.scope_to_function[self.symtable.scope] = cur_func_name
                # self.symtable.local_vars[cur_func_name] = []
                p[0].virtual_func_name = cur_func_name

                if(p[1].val in self.symtable.function_overloaded_map):
                    self.symtable.function_overloaded_map[p[1].val] += 1
                else:
                    self.symtable.function_overloaded_map[p[1].val] = 0
            else :
                p[0].array = copy.deepcopy(p[1].array)
                p[0].array.append(0)
            # print("line 2676 : ", funcReturntype)

    def p_pointer(self,p):  #do doa done
        '''
        pointer : MUL
                | MUL type_qualifier_list
                | MUL pointer
                | MUL type_qualifier_list pointer
        '''
        if(len(p) == 2):
            p[0] = Node(name = 'Pointer',type = '*', line_no = p.lineno(1))
            if(p[0]!=None):
                p[0].ast = AST(p)
        elif(len(p) == 3):
            p[0] = Node(name = 'Pointer',type = p[2].type + ' *', line_no = p.lineno(1))
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            p[0] = Node(name = 'Pointer',type = p[2].type + ' *', line_no = p[2].line_no)
            if(p[0]!=None):
                p[0].ast = AST(p)

    def p_type_qualifier_list(self,p):  #done
        '''
        type_qualifier_list : type_qualifier
                            | type_qualifier_list type_qualifier
        '''
        if(len(p) == 2):
            p[0] = p[1]
            if(p[0]!=None):
                p[0].name = 'Type Qualifier List'
                p[0].children = p[1]
                p[0].ast = AST(p)
        else:
            p[0] = p[1]
            if(p[0]!=None):
                p[0].children.append(p[2])
                p[0].type = conv(p[1].type) + " " + conv(p[2].type)
                p[0].name = 'Type Qualifier List'
                p[0].ast = AST(p)

    def p_parameter_type_list(self,p):  #done
        '''
        parameter_type_list : parameter_list
        '''
        p[0] = p[1]
        if(p[0]!=None):
            p[0].ast= AST(p)

    def p_parameter_list(self,p):    #done
        '''
        parameter_list : parameter_declaration
                    | parameter_list COMMA parameter_declaration
        '''
        p[0] = Node(name = 'ParameterList', children = [], line_no = p.lineno(1))
        if(len(p) == 2):
            if(p[0]!=None):
                p[0].ast = AST(p)
            p[0].children.append(p[1])
        else:
            p[0].ast = AST(p)
            p[0].children = p[1].children
            p[0].children.append(p[3])
        
    def p_parameter_declaration(self,p): #done
        '''
        parameter_declaration : declaration_specifiers declarator
                            | declaration_specifiers abstract_declarator
                            | declaration_specifiers
        '''
        if(len(p) == 2):
            p[0] = p[1]
            
            if(p[0]!=None):
                p[0].ast = AST(p)
            p[0].name = 'ParameterDeclaration'
        else:
            p[0] = Node(name = 'ParameterDeclaration',val = p[2].val,type = p[1].type, line_no = p[1].line_no, children = [])
            p[0].ast = AST(p)
            if(p[2].type != None):
                p[0].type = conv(p[1].type) + ' ' + conv(p[2].type)
        if( len(p) > 2 and p[2].name == 'Declarator'):
            if(p[2].val in self.symtable.table[self.symtable.scope].keys()):
                print(p.lineno(1), 'Compilation error : ' + p[2].val + ' parameter already declared')
            self.symtable.table[self.symtable.scope][p[2].val] = {}
            self.symtable.table[self.symtable.scope][p[2].val]['type'] = p[1].type
            
            if(p[2].type != None):
                self.symtable.table[self.symtable.scope][p[2].val]['type'] = conv(p[1].type) + ' ' + conv(p[2].type)
                self.symtable.table[self.symtable.scope][p[2].val]['size'] = self.symtable.data_type_size(conv(p[1].type)+ ' ' + conv(p[2].type))
            else:
                if('void' in p[1].type.split()):
                    print("Compilation error at line " + str(p[1].line_no) + ", parameter " + p[2].val + " cannot have type void")
                self.symtable.table[self.symtable.scope][p[2].val]['size'] = self.symtable.data_type_size(conv(p[1].type))
            if(len(p[2].array) > 0):
                self.symtable.table[self.symtable.scope][p[2].val]['array'] = p[2].array
            self.symtable.table[self.symtable.scope][p[2].val]['offset'] = self.offset[self.symtable.scope]
            self.offset[self.symtable.scope] += self.symtable.table[self.symtable.scope][p[2].val]['size']
            
    def p_identifier_list(self,p): #done
        '''
        identifier_list : INT_NUM
                        | identifier_list COMMA identifier
                        | identifier_list COMMA INT_NUM
        '''   
        if(len(p) == 2):
            p[0] = Node(name = 'IdentifierList',val = p[1], line_no = p.lineno(1), children = [p[1]],place= p[1])
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            p[0] = p[1]
            #catch
            if(isinstance(p[3], Node)):
                p[0].children.append(p[3].val)
            else :
                p[0].children.append(p[3])
            p[0].name = 'IdentifierList'
            if(p[0]!=None):
                p[0].ast = AST(p)
    
    # catch/added : broken above rule into int_num and identifier
    def p_identifier_list_2(self,p): 
        '''
        identifier_list : identifier
        '''
        if(len(p) == 2):
            p[0] = Node(name = 'IdentifierList',val = p[1].val, line_no = p.lineno(1), children = [p[1]], place=p[1].val)
            if(p[0]!=None):
                p[0].ast = AST(p)

    def p_type_name(self,p):
        '''
        type_name : specifier_qualifier_list
                | specifier_qualifier_list abstract_declarator
        '''
        if len(p) == 2:
            p[0] = p[1]
            p[0].name = 'Type Name'
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            p[0] = Node(name = 'Type Name', type = p[1].type, line_no = p[1].line_no)
            if(p[0]!=None):
                p[0].type = p[1].type + ' ' + p[2].type
                p[0].ast = AST(p)
            # print("hehe", p[1].type, "|",  p[2].type)
        # print("line 2846 :", p[0].type)

    def p_abstract_declarator(self,p):
        '''
        abstract_declarator : pointer
                            | direct_abstract_declarator
                            | pointer direct_abstract_declarator
        '''
        if(len(p) == 2):
            p[0] = p[1]
            p[0].name = 'Abstract Declarator'
            if(p[0]!=None):
                p[0].ast = AST(p)
        elif(len(p) == 3):
            p[0] = Node(name = 'Abstract Declarator',val = p[2].val,type = p[1].type + ' *', line_no = p[1].line_no, children = [])
            if(p[0]!=None):
                p[0].ast = AST(p)

    def p_direct_abstract_declarator(self,p):
        '''
        direct_abstract_declarator : LEFT_SQ_BR RIGHT_SQ_BR
                                | LEFT_PAR RIGHT_PAR
                                | LEFT_PAR abstract_declarator RIGHT_PAR
                                | LEFT_PAR parameter_type_list RIGHT_PAR
                                | LEFT_SQ_BR constant_expression RIGHT_SQ_BR
                                | direct_abstract_declarator LEFT_SQ_BR RIGHT_SQ_BR
                                | direct_abstract_declarator LEFT_PAR RIGHT_PAR
                                | direct_abstract_declarator LEFT_SQ_BR constant_expression RIGHT_SQ_BR
                                | direct_abstract_declarator LEFT_PAR parameter_type_list RIGHT_PAR
        '''
        if(len(p) == 3):
            if(p[1]=='('):
                p[0] = Node(name = 'directAbstractDeclarator()', line_no = p.lineno(1), children = [])
            if(p[1]=='['):
                p[0] = Node(name = 'directAbstractDeclarator[]', line_no = p.lineno(1), children = [])
        

        elif(len(p) == 4):
            p[0] = p[2]
            if(p[2]=='['):
                p[0].name='directAbstractDeclarator[]'
            if(p[2]=='('):
               p[0].name='directAbstractDeclarator()'
            if(p[0]!=None):
                p[0].ast = AST(p)
            
        else:
            if (p[2] == '('):
                p[0] = Node(name = 'directAbstractDeclarator()',val = p[1].val,type = p[1].val,  line_no = p[1].lineno(1), children = [p[3]])
            elif(p[2] == '['):
                p[0] = Node(name = 'directAbstractDeclarator[]',val = p[1].val,type = p[1].val,  line_no = p[1].lineno(1), children = [p[3]])
            if(p[0]!=None):
                p[0].ast = AST(p)
          
        

    def p_initializer(self,p): #done
        '''
        initializer : assignment_expression
                    | lcur_br initializer_list rcur_br
                    | lcur_br initializer_list COMMA rcur_br
        '''
        if(len(p) == 2):
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            p[0] = Node(name = 'Initializer',val = '',type = '', line_no = p[2].line_no, children = [])
            if(p[2].sqb or not p[2].name.startswith('Initial')):
                p[0].children = [p[2]]
            else:
                p[0] = p[2]
            p[0].name = 'Initializer'
            p[0].sqb = True
            if(len(p) == 4):
                p[0].max_depth = p[2].max_depth + 1
                p[0].ast = AST(p)
            elif(len(p) == 5):
                p[0].ast = AST(p) 

    def p_initializer_list(self,p): #done
        '''
        initializer_list : initializer
                        | initializer_list COMMA initializer
        '''
        if(len(p) == 2):
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            p[0] = Node(name = 'Initializer List', children = [], line_no = p.lineno(1))
            if(p[0]!=None):
                p[0].ast = AST(p)
            if(p[1].name != 'Initializer List'):
                p[0].children.append(p[1])
            else:
                p[0].children = p[1].children
            p[0].children.append(p[3])
            p[0].max_depth = max(p[1].max_depth, p[3].max_depth)

    def p_statement(self,p): #self
        '''
        statement : labeled_statement
                | compound_statement
                | expression_statement
                | selection_statement
                | iteration_statement
                | jump_statement
        '''
        # print("line 2932 :", p[-1])
        p[0] = Node(name = 'statement', children = [], line_no = p.lineno(1))
        if(p[0]!=None):
            p[0].ast = AST(p)
        if isinstance(p[1], Node):
          p[0].label = p[1].label
          p[0].expr = p[1].expr
        p[0].ast = AST(p)

    def p_labeled_statement(self,p): #done 
        '''
        labeled_statement : identifier COLON statement
        '''
        p[0] = Node(name = 'labeledStatement', children = [], line_no = p.lineno(1) )
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_compound_statement(self,p): #done 
        '''
        compound_statement : lcur_br rcur_br
                        | lcur_br block_item_list rcur_br
        '''
        if(len(p) == 3):
            p[0] = Node(name = 'EmptyScope', line_no = p.lineno(1), children = [])
        else :
            p[0]=p[2]
            p[0].name = 'Scope'
            if(p[0]!=None):
                p[0].ast = AST(p)          
                            
        
    def p_function_compound_statement(self,p): #done 
        '''
        function_compound_statement : LEFT_CUR_BR rcur_br
                        | LEFT_CUR_BR block_item_list rcur_br
        '''
        if(len(p) == 3):
            p[0] = Node(name = 'EmptyScope', line_no = p.lineno(1), children = [])
        else :
            p[0]=p[2]
            p[0].name = 'Scope'
            if(p[0]!=None):
                p[0].ast = AST(p)

    
         

    def p_block_item_list(self,p): #done 
        '''
        block_item_list : block_item
                        | block_item_list block_item
        '''
        if(len(p) == 2):
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            p[0] = Node(name = 'blockItemList', children = [], line_no = p.lineno(1))
            if(p[0]!=None):
                p[0].ast = AST(p)
            if(p[1].name != 'blockItemList'):
                p[0].children.append(p[1])
            else:
                p[0].children = p[1].children
            p[0].children.append(p[2])

    def p_block_item(self,p): #done 
        '''
        block_item : declaration
                    | statement
        '''
        p[0] = p[1]
        

    def p_expression_statement(self,p): #done
        '''
        expression_statement : SEMI_COLON
                            | expression SEMI_COLON
        '''
        p[0] = Node(name = 'ExpressionStatement', children = [], line_no = p.lineno(1))
        if(len(p) == 3):
            if(p[0]!=None):
                p[0].ast = AST(p)
            p[0].val = p[1].val
            p[0].type = p[1].type
            p[0].children = p[1].children
            p[0].place = p[1].place

        p[0].name = 'expressionStatement'

        
    def p_selection_statement(self,p): #done
        '''
        selection_statement : IF LEFT_PAR expression RIGHT_PAR IfMark1 statement %prec IFX
                            | IF LEFT_PAR expression RIGHT_PAR IfMark1 statement ELSE IfMark2 statement
        '''
        if(len(p) == 10):
            p[0] = Node(name = 'IfElseStatement', line_no = p.lineno(1))
            if(p[0]!=None):
                p[0].ast = AST(p)
                self.EMIT.emit('label', '', '', p[5][1])

        else:
            p[0] = Node(name = 'IfStatement', line_no = p.lineno(1))
            p[0].ast = AST(p)
            # print("line 3037 :", p[5])
            self.EMIT.emit('label', '', '', p[5][0])

    # def p_rand(self, p):
    #     '''rand : '''
    #     print("line 3042 : ", p[-2])

    def p_IfMark1(self,p): #done
        '''IfMark1 : '''
        l1 = self.EMIT.get_label()
        l2 = self.EMIT.get_label()
        self.EMIT.emit('ifgoto', p[-2].place, 'eq 0', l1)
        p[0] = [l1, l2]
        # print(f"line 3046 : ifmark1 : p[0] = {p[0]}")
        
    def p_IfMark2(self,p):
        '''IfMark2 : '''
        self.EMIT.emit('goto', '', '', p[-3][1])
        self.EMIT.emit('label', '', '', p[-3][0])

    def p_iteration_statement_1(self,p): #done
        '''
        iteration_statement : while WhMark1 LEFT_PAR expression RIGHT_PAR WhMark2 statement
                        
        '''
        # print(p[-5]," line 3054")
        # print(p[2], "line 3055")
        self.EMIT.emit('goto','','',p[2][0])
        self.EMIT.emit('label','', '', p[2][1])
        self.continueStack.pop()
        self.breakStack.pop()
        p[0] = Node(name = 'whileStatement', line_no = p.lineno(1))
        self.symtable.loopingDepth-=1
        if(p[0]!=None):
            p[0] = AST(p)

    def p_WhMark1(self,p): #done
        '''WhMark1 : '''
        # print("line 3066 : ", p)
        l1 = self.EMIT.get_label()
        l2 = self.EMIT.get_label()
        self.continueStack.append(l1)
        self.breakStack.append(l2)
        self.EMIT.emit('label', '', '', l1)
        p[0] = [l1 , l2]

    def p_WhMark2(self,p): #done
        '''WhMark2 : '''
        # print("line 3076 :", p)
        self.EMIT.emit('ifgoto', p[-2].place , 'eq 0', p[-4][1])

    # def p_WhMark3(p):
    # '''WhMark3 : '''
    #     emit('goto','','',p[-6][0])
    #     emit('label','', '', p[-6][1])
    #     continueStack.pop()
    #     breakStack.pop()
    def p_iteration_statement_2(self,p): #done
        '''
        iteration_statement :  for LEFT_PAR expression_statement forMark1 expression_statement forMark2 RIGHT_PAR statement       
        '''
        self.EMIT.emit('goto', '', '', p[4][0])
        self.EMIT.emit('label', '', '', p[4][1])
        self.breakStack.pop()
        self.continueStack.pop()
        p[0] = Node(name = 'ForNoStatement', line_no = p.lineno(1))
        self.symtable.loopingDepth-=1
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_iteration_statement_3(self,p): #done
        '''
        iteration_statement : for LEFT_PAR expression_statement forMark1 expression_statement forMark3 expression forMark4 RIGHT_PAR forMark5 statement 
        '''
        self.EMIT.emit('goto','','',p[4][3])
        self.EMIT.emit('label', '', '', p[4][1])
        self.breakStack.pop()
        self.continueStack.pop()
        p[0] = Node(name = 'ForStatement', line_no = p.lineno(1))
        self.symtable.loopingDepth-=1
        if(p[0]!=None):
            p[0].ast = AST(p)



    def p_forMark1(self,p): #done
        '''forMark1 : '''
        l1 = self.EMIT.get_label()
        l2 = self.EMIT.get_label()
        l3 = self.EMIT.get_label()
        l4 = self.EMIT.get_label()
        self.continueStack.append(l1)
        self.breakStack.append(l2)
        self.EMIT.emit('label', '', '', l1)
        p[0] = [l1, l2, l3, l4]

    def p_forMark2(self,p): #done
        '''forMark2 : '''
        if p[-1].place:
            self.EMIT.emit('ifgoto', p[-1].place, 'eq 0', p[-2][1])

    def p_forMark3(self,p): #done
        '''forMark3 : '''
        if p[-1].place:
            self.EMIT.emit('ifgoto', p[-1].place, 'eq 0', p[-2][1])
        self.EMIT.emit('goto', '', '', p[-2][2])
        self.continueStack.pop()
        self.continueStack.append(p[-2][3])
        self.EMIT.emit('label', '', '', p[-2][3])

    def p_forMark4(self,p): #done
        '''forMark4 : '''
        self.EMIT.emit('goto' , '', '', p[-4][0])

    def p_forMark5(self,p): #done 
        '''forMark5 : '''
        self.EMIT.emit('label', '', '', p[-6][2])
        # RULES LEFT ITERATION
        #catch UNSURE
# | for LEFT_PAR declaration expression_statement RIGHT_PAR statement 
# | for LEFT_PAR declaration expression_statement expression RIGHT_PAR statement 
#####################
    def p_iteration_statement_4(self, p):
        #catch changed l_paren with LEFT_PAR
        '''
        iteration_statement : for LEFT_PAR declaration expression_statement RIGHT_PAR statement
        '''
        p[0] = Node(name = 'ForStatement', line_no = p.lineno(1))
        self.symtable.loopingDepth-=1
        self.symtable.scope = self.symtable.prevScope[self.symtable.scope]
        if(p[0]!=None):
            p[0].ast = AST(p)
      
    def p_iteration_statement_5(self, p):
        #catch changed l_paren with LEFT_PAR
        '''
        iteration_statement : for LEFT_PAR declaration expression_statement expression RIGHT_PAR statement
        '''
        p[0] = Node(name = 'ForStatement', line_no = p.lineno(1))
        self.symtable.loopingDepth-=1
        self.symtable.scope = self.symtable.prevScope[self.symtable.scope]
        if(p[0]!=None):
            p[0].ast = AST(p)

    # def p_scopeDecM(self, p):
    #     '''
    #     scopeDecM :
    #     '''
    #     self.symtable.scope = self.symtable.prevScope[self.symtable.scope]
#####################


    def p_while(self,p): #done 
        '''
        while : WHILE
        '''
        self.symtable.loopingDepth+=1
        p[0]=p[1]
        p[0]=AST(p)
        ## CHECK)
    def p_for(self, p): #done 
        '''
        for : FOR
        '''
        self.symtable.loopingDepth+=1
        p[0]=p[1]
        p[0]=AST(p)
         ## CHECK


    def p_translation_unit(self,p): #done
        '''
        translation_unit : external_declaration
                        | translation_unit external_declaration
        '''
        p[0] = Node(name = 'JumpStatement', line_no = p.lineno(1))
        if(len(p) == 2):
            p[0].children.append(p[1])
        else:
            p[0].children.append(p[2])
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_external_declaration(self,p): #done
        '''
        external_declaration : function_definition
                            | declaration
        '''
        p[0] = p[1]
        p[0].name = 'external_declaration'
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_function_definition(self,p): # do we want to remove the bottom two grammars?
        '''
        function_definition : declaration_specifiers declarator declaration_list compound_statement
                            | declarator declaration_list function_compound_statement
                            | declarator function_compound_statement
        '''
        if(len(p) == 3):
            p[0] = Node(name = 'FuncDeclWithoutType',val = p[1].val,type = 'int', line_no = p[1].line_no)
        elif(len(p) == 4):
            p[0] = Node(name = 'FuncDeclWithoutType',val = p[1].val,type = 'int', line_no = p[1].line_no)
        else:
            p[0] = Node(name = 'FuncDecl',val = p[2].val,type = p[1].type, line_no = p[1].line_no)

        if(p[0]!=None):
            p[0].ast = AST(p)
    
    def p_function_definition2(self,p): # done 
        '''
        function_definition : declaration_specifiers declarator FuncMark1 function_compound_statement
        '''
        p[0] = Node(name = 'FuncDecl',val = p[2].val,type = p[1].type, line_no = p.lineno(1))
        cur_func_name = p[2].val + '_' + str(self.symtable.function_overloaded_map[p[2].val])

        self.symtable.table[0][cur_func_name]['is_func'] = 1
        if(p[0]!=None):
            p[0].ast = AST(p)
        if p[1].type == 'void' and self.EMIT.emit_array[-1][0] != 'ret':
          self.EMIT.emit('ret','','','')
        elif p[1].type != 'void' and self.EMIT.emit_array[-1][0] != 'ret':
          print("Compilation error at line "+str(p[1].line_no)+": Function reaches end of control without return statement")
        self.EMIT.emit('funcEnd', '', '', p[2].virtual_func_name)
        
    def p_FuncMark1(self,p): #done 
        '''FuncMark1 : '''
        self.EMIT.emit('func', '', '', p[-1].virtual_func_name)

    def p_declaration_list(self,p): #done 
        '''
        declaration_list : declaration
                        | declaration_list declaration
        '''
        if(len(p) == 2):
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            p[0] = Node(name = 'DeclarationList', children = [], line_no = p.lineno(1))
            if(p[0]!=None):
                p[0].ast = AST(p)
            if(p[1].name != 'DeclarationList'):
                p[0].children.append(p[1])
            else:
                p[0].children = p[1].children
            p[0].children.append(p[2])
    
    def p_jump_statement1(self,p): #done
        '''
        jump_statement : RETURN SEMI_COLON
                        | RETURN expression SEMI_COLON
        '''
        global funcReturntype
        # print("line 3263 : ", funcReturntype)
        if(len(p) == 3):
            p[0] = Node(name = 'jump_statement', line_no = p.lineno(1))
            if(p[0]!=None):
                p[0].ast = AST(p)
            if(funcReturntype != 'void'):
                print('Compilation error at line ' + str(p.lineno(1)) + ': function return type is not void')
            self.EMIT.emit('ret','','','')
        else:
            if(p[2].type != None and funcReturntype != p[2].type):
                # print("line 3289 : ", funcReturntype)
                print('warning at line ' + str(p.lineno(1)) + ': function return type is not ' + conv(p[2].type))
                # print(f"return type is {funcReturntype}")
            p[0] = Node(name = 'jump_statement',line_no = p.lineno(1))
            # print(p[1], "line 2080")
            if(p[0]!=None):
                p[0].ast = AST(p) 
            tmp = p[2].place
            if funcReturntype != p[2].type :
                tmp = self.EMIT.get_new_tmp(funcReturntype)
                self.EMIT.emit(int_or_real(p[2].type) + '_' + int_or_real(funcReturntype) + '_' + '=', p[2].place, '', tmp)
            self.EMIT.emit('ret', '', '', tmp)
            self.EMIT.jump_mark  = 1
    def p_jump_statement2(self,p): #done 
        '''
            jump_statement : BREAK SEMI_COLON
                            | CONTINUE SEMI_COLON
                            | GOTO identifier SEMI_COLON
        '''
        if p[1] == 'BREAK':
            p[0] = Node(name = 'Break Statement',val = '',type = '', line_no = p.lineno(1), children = [])
            p[0].ast = AST(p)
            if self.symtable.loopingDepth == 0 and self.symtable.switchDepth == 0:
                print("Error at line no.",p[0].line_no," :Break is not inside any loop")
            self.EMIT.emit('goto','','',self.breakStack[-1])
            self.EMIT.jump_mark = 1
        elif p[1] == 'CONTINUE':
            p[0] = Node(name = 'JumpStatement',val = '',type = '', line_no = p.lineno(1), children = [])
            p[0].ast = AST(p)

            if(self.symtable.loopingDepth == 0):
              print("Error at line no.",p[0].line_no," :Continue is not inside any loop")
            self.EMIT.emit('goto','','',self.continueStack[-1])
            self.EMIT.jump_mark = 1
        else:
            p[0] = Node(name = 'JumpStatement',val = '',type = '', line_no = p.lineno(1), children = []) 
            p[0].ast = AST(p)   
            self.EMIT.emit('goto', '', '', p[2])
            self.EMIT.jump_mark = 1
    def p_error(self,p): #done
        print('Error found while parsing!')
        print(p)
        x = p.lexpos - self.lex.lexer.lexdata.rfind('\n', 0, p.lexpos)
        print(f"Error!!!, Unknown lexeme encountered! {p.value[0]} at line no. {p.lineno}, column no. {x}")
        global error_present
        error_present = 1

# class symbol_info:

if __name__ == '__main__':
    pars = Parser()
    pars.build()

    for filename in sys.argv[1:] :
        with open(filename, 'r') as f:
            content = f.read()
            pars.lex.lexer.input(content)

            open('graph1.dot','w').write("digraph G {")
            pars.parser.parse(content, debug=False)
            open('graph1.dot','a').write("\n }")
            # save symbol table
            save_table = pars.symtable.table
            save_table = [i for i in save_table if len(i) != 0]

            for scope, entry in enumerate(save_table):
                for i in entry:
                    entry[i]['scope'] = scope

            temp = {}
            for i in save_table:
                temp.update(i)
            save_table= temp

            with open('./symbol_table_dump.json', 'w') as f:
                json.dump(save_table, f, indent = 2)
                f.close()

            df = pd.read_json('./symbol_table_dump.json')
            df = df.T
            # print(df)
            # for i in range(df.shape[0]):
            #     temp_dict = df.iloc[i].values[0]
            #     print(f"temp_dict is {temp_dict}")
            #     if(not isinstance(temp_dict, dict)):
            #         continue
            #     for field in temp_dict:
            #         df.iloc[i][field] = temp_dict[field]
            # # print(df)
            df.to_csv('./symbol_table_dump.csv')

            # new_df = pd.DataFrame()
            # for i in range(df.shape[0]):
            #     # print(f"df.iloc[i].values[0] : {df.iloc[i].values[0]}")
            #     # print(f"df.index.iloc[i].value : {df.index}")
            #     if(not isinstance(df.iloc[i].values[0], dict)):
            #         continue
            #     new_df = new_df.append(df.iloc[i].values[0], ignore_index=True)

            # new_df.to_csv('./symbol_table_dump.csv')

            graphs = pydot.graph_from_dot_file('graph1.dot')
            graph = graphs[0]
            # name = f.name[f.name.rfind('/')+1:]
            # graph.write_png(f'./plots/pydot_graph.png')
            f.close()
            # with open('./src/parser.out', 'r') as f:
            #     content = f.readlines()
            #     f.close()

            # outfile = ''

            # i=0
            # state_count = -1
            # while i < len(content):
            #     if(len(re.findall(r'^state \d+', content[i])) > 0):
            #         # is of the form 'state {num}'
            #         state_count = state_count + 1
                    
            #     else :
            #         gotoState = re.findall(r'go to state \d+', content[i])
            #         if(len(gotoState) > 0):
            #             numState = int(re.findall(r'\d+', gotoState[0])[-1])
            #             label = content[i].lstrip().split()[0]

            #             to_write = f'I{state_count} -> I{numState} [label={label}]\n'
            #             outfile += to_write
                
            #     i+=1

            # header = 'digraph "LR Automata" {\n'
            # for state_num in range(state_count):
            #     header += f' I{state_num}\n'

            # outfile = header + outfile + '}'

            # with open('./bin/outfile.dot', 'w') as f:
            #     f.write(outfile)
            #     f.close()
            for i in pars.EMIT.emit_array:
                print(i)
