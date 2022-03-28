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

def AST(p):
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
                else:   #if condition changed
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

        __type__ = __type__.split()[-1]
        if __type__ not in type_size.keys():
            return -1
        return type_size[__type__]


class Node():
    def __init__(self, name, val = None, line_no = 0, type = None, children = [], scope = 0, array = [], max_depth = 0, is_func = 0, parentStruct = None, level = 0, ast = None) :
        self.name = name
        self.val = val
        self.line_no = line_no

        self.type = type
        self.children = children
        self.scope = scope
        self.array = array
        self.max_depth = max_depth
        self.is_func = is_func
        self.parentStruct = parentStruct
        self.level = level
        self.ast = ast

        

class Parser():
    tokens = lexer().tokens
    lex = lexer()
    lex.build()
    current_type = []
    symtable = SymTable()
    translation_unit = Node('START')
    funcReturntype = None     #curfuncReturntype
    root = Node(name = "root")
    scope_to_function = {}
    scope_to_function[0] = 'global'

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

    def build(self):
        self.parser = yacc.yacc(module=self, start='translation_unit' ,debug=True)

    def p_identifier(self, p):
        '''
            identifier : ID
        '''
        p[0] = Node(name = "Identifier", val = p[1], line_no = p.lineno(1))
        x = self.symtable.isPresent(p[1])
        if x != None:
            p[0].type = x[0]['type']
            
            if 'array' in x[0].keys():
                p[0].level = len(x[0]['array'])
            
            if 'is_func' in x[0]:
                p[0].is_func = 1

        p[0].ast = AST(p)


    def p_primary_expression_1(self,p):
        '''
        primary_expression : identifier
        '''
        # print("i am here line 240")
        x = p[1].val
        if self.symtable.isPresent(x) == None :
            print("Compilation Error at line",p[1].line_no,"unary expression",p[1].val,"not defined") 
        p[0] = p[1]

    def p_primary_expression_2(self,p):
        '''
        primary_expression : INT_NUM
        '''
        # print("i am here line 250")
        p[0] = Node(name = "constant", val = p[1], line_no=p.lineno(1), type = 'int')
        p[0].ast = AST(p)

        
    def p_primary_expression_3(self,p):
        '''
        primary_expression : FLOAT_NUM
        '''
        p[0] = Node(name = "constant", val = p[1], line_no=p.lineno(1), type = 'float')
        p[0].ast = AST(p)


    def p_primary_expression_4(self,p):
        '''
        primary_expression : CHARACTER
        '''
        p[0] = Node(name = "constant", val = p[1], line_no=p.lineno(1), type = 'char')
        p[0].ast = AST(p)


    def p_primary_expression_5(self,p):
        '''
        primary_expression : STRING
        '''
        p[0] = Node(name = "constant", val = p[1], line_no=p.lineno(1), type = 'string')
        p[0].ast = AST(p)
    
    def p_primary_expression_6(self,p):
        '''
        primary_expression : LEFT_PAR expression RIGHT_PAR
        '''
        # p[0] = p[1]
        p[0] = p[2]
        p[0].ast = AST(p)

    def p_postfix_expression(self,p):
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
            # print(f"p[1].val : {p[1].val}, line 297")
            # primary_expression
            p[0]=p[1]
            p[0].ast = AST(p)
            return
            
        elif (len(p)==5 and p[2]=='['):
            # postfix_expression LEFT_SQ_BR expression RIGHT_SQ_BR
            # print(f"p[1].val : {p[1].val}, line 305")
            p[0]= Node(name ="ArrayExpression", val=p[1].val,line_no=p[1], type=p[1].type,children=[p[1],p[3]],is_func=p[1].is_func , parentStruct = p[1].parentStruct)
            p[0].array = copy.deepcopy(p[1].array)
            p[0].array.append(conv(p[3].val))
            p[0].level = p[1].level - 1
            # sc=  self.symtable.isPresent(self,p[1].val)[1]
            p[0].ast=AST(p)

            if (p[0].level==None):
                print("Compilation error at line", str(p[1].line_no)," : Incorrect Dimensions specified for ", p[1].val)
            #check

            if (p[3].type not in ['int','char']):
                print("Compilation Error : Array index at line ", p[3].line_no, " is of incompatible type")
            return

        elif( len(p)==4 and p[2]=='('):
            #postfix_expression LEFT_PAR RIGHT_PAR
            # print(f"p[1].val : {p[1].val}, line 324")
            p[0]= Node(name='FunctionCall',val=p[1].val,line_no=p[1].line_no,type = p[1].type,children = [p[1]],is_func=0)
            p[0].ast=AST(p)

            if(p[1].val not in self.symtable.table[0].keys() or 'is_func' not in self.symtable.table[0][p[1].val].keys()):
                print('Compilation Error at line no.' + str(p[1].line_no) + ': function with name ' + p[1].val + 'is not declared')
            elif(len(self.symtable.table[0][p[1].val]['argumentList']) != 0):
                print("Syntax Error at line no. ",p[1].line_no,"wrong number of arguments for function call")  
        
        elif ( len(p)==5 and p[2]=='(' ):
            # postfix_expression LEFT_PAR argument_expression_list RIGHT_PAR
            # print(f"p[1].val : {p[1].val}, line 335")
            p[0] = Node(name = 'FunctionCall',val = p[1].val,line_no = p[1].line_no,type = p[1].type,children = [],is_func=0)
            p[0].ast = AST(p)
            if(p[1].val not in self.symtable.table[0].keys() or 'is_func' not in self.symtable.table[0][p[1].val].keys()):
                print('Compilation Error at line no. :' + str(p[1].line_no) + ': no function declared with name ' + p[1].val )
            elif(len(self.symtable.table[0][p[1].val]['argumentList']) != len(p[3].children)):
                print("Syntax Error at line " + str(p[1].line_no) + " Incorrect number of arguments for function call")
            else:
                i = 0
                for arguments in self.symtable.table[0][p[1].val]['argumentList']:
                    curVal = p[3].children[i].val
                    if(curVal not in self.symtable.table[self.symtable.scope].keys()):
                        continue
                    # print(self.current_type," line 324")

                    self.current_type = self.symtable.table[self.symtable.scope][curVal]['type']
                    # print(self.current_type," line 324")
                    # temp = compare_types(self.current_type,arguments)
                    if(self.current_type.split()[-1] != arguments.split()[-1]):
                        print("Warning at line " + str(p[1].line_no), ": Type not match in argument " + str(i+1) + " of function call, " + 'actual type is :' + arguments + 'but called with : ' + self.current_type)
                    
                    i += 1
                    self.current_type = [self.current_type]

        elif(len(p)==3):
            # print(f"p[1].val : {p[1].val}, line 360")
            #  | postfix_expression INC
            #   | postfix_expression DEC
            p[0] = Node(name="IncOrDecExpression",val=p[1].val,line_no=p[1].line_no,type=p[1].type)
            p[0].ast=AST(p)
            if ( self.symtable.isPresent(p[1].val)!=None and ((p[1].is_func == 1) or ('struct' in p[1].type.split()))):
                    print("Compilation Error at line no.", str(p[1].line_no), ", Invalid operation on", p[1].val)
        
        elif(len(p)==4 and (p[2]=='.' or p[2]=='->')):
            # postfix_expression PTR_OP identifier
            # postfix_expression DOT identifier
            # print(f"p[1].val : {p[1].val}, line 371")

            if (not p[1].name.startswith('dot')):
                # print(f"p[1].val : {p[1].val}, line 367")

                # print(self.symtable.scope)
                # print(self.symtable.prevScope)
                # for i in self.symtable.table:
                #     print(i)
                if (self.symtable.isPresent(p[1].val) == None or p[1].val not in self.symtable.table[self.symtable.isPresent(p[1].val)[1]].keys()):
                    # print(f"p[1].val : {p[1].val}, line 367")
                    print("Compilation Error at line no. " + str(p[1].line_no) + " : " + p[1].val + " not declared")

                    # print(self.symtable.scope)
                    # print(self.symtable.prevScope)
                    # for i in self.symtable.table:
                    #     print(i)
                    
            
            # print(f"p1 is {p[1]}, p1.val is {p[1].val}, line 369")
            p[0] = Node(name = 'dotOrPointerExpression', val = p[3].val , line_no = p[1].line_no, type = p[1].type, children = [])
            p[0].ast = AST(p)
            if (p[1].type.endswith('*') and p[2][0] == '.') or (not p[1].type.endswith('*') and p[2][0] == '->') :
                print("Compilation Error at line " + str(p[1].line_no) + " : invalid operator " +  " on " + conv(p[1].type))
            if(not p[1].type.startswith('struct')):
                print("Compilation Error at line " + str(p[1].line_no) + ", " + p[1].val + " is not a struct")
                return
            flag = 0 
            if(self.symtable.isPresent(p[1].type) != None):
                scp = self.symtable.isPresent(p[1].type)[1]
            else :
                scp = -1
            
            # print(scp, p[1].type, self.symtable.table[scp][p[1].type]['field_list'], "line 382")
            # print(self.symtable.table[scp].keys(), "line 382")
            for curr_list in self.symtable.table[scp][p[1].type]['field_list']:
                # print(curr_list, p[3].val, "line 384")
                if curr_list[1] == p[3].val:
                    flag = 1 
                    p[0].type = curr_list[0]
                    p[0].parentStruct = p[1].type
                    if(len(curr_list) == 5):
                        p[0].level = len(curr_list[4])
                        
            if(p[0].level == -1):
                print("Compilation Error at  line ", str(p[1].line_no), ", number of dimensions specified for " + conv(p[1].val) , " are incorrect")
            if flag == 0 :
                print("Compilation error at line " + str(p[1].line_no) + " : field " + "not declared in " +conv(p[1].type))

                
    def p_lcur_br(self, p):
        '''
        lcur_br : LEFT_CUR_BR               
        '''
        self.symtable.prevScope[self.symtable.next] = self.symtable.scope
        self.symtable.scope = self.symtable.next
        self.symtable.table.append({})
        self.symtable.next = self.symtable.next + 1
        p[0] = p[1]

    def p_l_paren(self, p):
        '''
        l_paren : LEFT_PAR
        '''
        self.symtable.prevScope[self.symtable.next] = self.symtable.scope
        self.symtable.scope = self.symtable.next
        self.symtable.table.append({})
        self.symtable.next = self.symtable.next + 1
        p[0] = p[1]

    def p_rcur_br(self, p):
        '''
        rcur_br : RIGHT_CUR_BR
        '''
        self.symtable.scope = self.symtable.prevScope[self.symtable.scope]
        p[0] = p[1]
        
    def p_argument_expression_list(self,p):
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
        
    def p_unary_expression(self,p):
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
        elif len(p) == 3:
            if p[1] =='++' or p[1] == '--':
                node_1 = Node(name = '',val = p[1],line_no = p[2].line_no)
                p[0] = Node(name = 'Increment/Decrement Operation',val = p[2].val,line_no = p[2].line_no,type = p[2].type,children = [node_1,p[2]])
                p[0].ast = AST(p)
                x = self.symtable.isPresent(p[2].val)
                if x != None and (p[2].is_func == 1 or 'struct' in conv(p[2].type).split()):
                    print("Compilation Error encountered at line",str(p[2].line_no),":Invalid operation encountered",p[2].val)
            elif p[1] == 'sizeof':
                node_2 = Node(name = '',val = p[1],line_no = p[2].line_no)
                p[0] = Node(name = 'SizeOf Operation',val = p[2].val,line_no = p[2].line_no,type = p[2].type,children = [node_2,p[2]])
                p[0].ast = AST(p)
            else :
                if p[1].val == '&':
                    p[0] = Node(name = 'Address_Of Operator',val = p[2].val,line_no = p[2].line_no,type = p[2].type + ' *',children = [p[2]])
                    p[0].ast = AST(p)
                elif p[1].val == '*':
                    if conv(p[2].type).endswith('*') == False:
                        print("Compilation Error encountered at line",str(p[1].line_no),":Cannot dereference the variable of type",conv(p[2].type))
                        p[0] = Node(name = 'Error Node line 495')
                    else:
                        p[0] = Node(name = 'Pointer Operator',val = p[2].val,line_no = p[2].line_no,type = p[2].type[:len(p[2].type)-2],children = [p[2]])
                        p[0].ast = AST(p)
                elif p[1].val == '-':
                    p[0] = Node(name = 'Unary Minus Operator',val = p[2].val,line_no = p[2].line_no,type = p[2].type ,children = [p[2]])
                    p[0].ast = AST(p)
                else:
                    p[0] = Node(name = 'Unary Operator',val = p[2].val,line_no = p[2].line_no,type = p[2].type,children = [p[2]])
                    p[0].ast = AST(p)
        else:
            node_3 = Node(name = '',val = p[1],line_no = p[3].line_no, children = [])
            p[0] = Node(name = 'SizeOf Operation', val = p[3].val, line_no = p[3].line_no, type = p[3].type, children = [node_3,p[3]])
            p[0].ast = AST(p)
    
    def p_cast_expression(self,p):
        '''
        cast_expression : unary_expression
                        | LEFT_PAR type_name RIGHT_PAR cast_expression
        '''
        if(len(p) == 2):
            p[0] = p[1]
           
            if(p[0]!=None):
                p[0].ast = AST(p)
        else:
            p[0] = Node(name = 'Type Casting',val = p[2].val,line_no = p[2].line_no,type = p[2].type)
            p[0].ast = AST(p)

    def p_unary_operator(self,p):
        '''
        unary_operator : BIT_AND
                    | MUL
                    | ADD
                    | SUB
                    | NOT
                    | NEGATE
        '''
        p[0] = Node(name = 'unary_operator',val = p[1],line_no = p.lineno(1))
        p[0].ast = AST(p)
        
    def p_additive_expression(self,p):
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
        elif p[1].type == '' and  p[3].type == '': # diff.
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
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            p[0] = Node(name = 'Addition Or Subtraction',line_no = p[1].line_no,type = p[1].type,children = [])
            p[0].ast = AST(p)
        elif(conv(p[3].type).endswith('*') and not (conv(p[1].type).endswith('*'))):
            if(p[1].type == 'float'):
                if(p[2] is tuple):
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            p[0] = Node(name = 'Addition Or Subtraction',line_no = p[1].line_no,type = p[3].type,children = [])
            p[0].ast = AST(p)
        elif(conv(p[1].type).endswith('*') and conv(p[3].type).endswith('*')):
            if(p[2] is tuple):
                print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
            else:
                print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            p[0] = Node(name = 'Addition Or Subtraction',line_no = p[1].line_no,type = p[1].type,children = [])
            p[0].ast = AST(p)
        else :
            valid_types = ['char' , 'int' , 'float']
            if p[1].type.split()[-1] not in valid_types or conv(p[3].type).split()[-1] not in valid_types:
                if(p[2] is tuple):
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            final_type = self.typecast(p[1].type , p[3].type)
            p[0] = Node(name = 'Addition Or Subtraction',line_no = p[1].line_no,type = final_type,children = [])
            p[0].ast = AST(p)
        x = self.symtable.isPresent(p[1].val)
        if x != None and p[1].is_func == 1 :
            print('Compilation Error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
        y = self.symtable.isPresent(p[3].val)
        if y != None and p[3].is_func == 1 :
            print('Compilation Error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            

    def p_multiplicative_expression(self,p):
        '''
        multiplicative_expression : cast_expression
                                | multiplicative_expression MUL cast_expression
                                | multiplicative_expression DIV cast_expression
                                | multiplicative_expression MODULO cast_expression
        '''
        if(len(p) == 2):
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
            return
        elif(p[1].type == None and p[3].type == None):
            p[0] = Node(name = 'MulDiv',line_no = p[1].line_no, type = 'int',children = [])
            p[0].ast = AST(p)
            return
        elif(p[1].type == None):
            p[0] = Node(name = 'MulDiv',line_no = p[1].line_no, type = p[3].type,children = [])
            p[0].ast = AST(p)
            return
        elif(p[3].type == None):
            p[0] = Node(name = 'MulDiv',line_no = p[1].line_no, type = p[1].type,children = [])
            p[0].ast = AST(p)
            return
            
        else :
            tempNode = Node(name = '', val = p[2], line_no = p[1].line_no, children = [])
            type_list = ['char' , 'int' , 'long' , 'float' , 'double']

            if(conv(p[1].type).split()[-1] not in type_list or conv(p[3].type).split()[-1] not in type_list):
                if(p[2] is not tuple):
                    print(p[1].line_no , 'Compilation TIME error : Incompatible data type with ' + p[2] +  ' operator')
                else :
                    print(p[1].line_no , 'Compilation TIME error : Incompatible data type with ' + p[2][0] +  ' operator')

            scope_exists = self.symtable.isPresent(p[1].val)
            if scope_exists != None and p[3].is_func == 1:
                print(f"Compilation TIME error : Invalid operation {p[3].val} at line {p[3].line_no}")
                
            if(p[2] == '%'):
                allowed_types = ['char' , 'int' , 'long']
                typecast_type = self.typecast(p[1].type , p[3].type)
                if typecast_type not in allowed_types:
                    print(p[1].line_no , 'Compilation error : Incompatible data type with MODULO operator')
                if typecast_type == 'char':
                    typecast_type = 'int'        # ascii values of characters are taken as integers values.
                p[0] = Node(name = 'MODULO', val = p[1].val, line_no = p[1].line_no, type = typecast_type, children = [])
                p[0].ast = AST(p)
            
            else :
                typecast_type = self.typecast(p[1].type , p[3].type)
                if typecast_type == 'char':
                    typecast_type = 'int'        # ascii values of characters are taken as integers values.
                p[0] = Node(name = 'MulDiv', val = p[1].val, line_no = p[1].line_no, type = typecast_type, children = [])
                if p[0] != None :
                    p[0].ast = AST(p)


    def p_shift_expression(self,p):
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
            if p[1].type == None and p[3].type == None:
                p[0] = Node(name = 'Bit Shift Operation',line_no = p[1].line_no,type = 'int')
                if p[0] != None :
                    p[0].ast = AST(p)
                return
            valid_types = ['int']
            if conv(p[1].type).split()[-1] not in valid_types or conv(p[3].type).split()[-1] not in valid_types:
                if(p[2] is tuple):
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func == 1 :
                print('Compilation Error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func == 1 :
                print('Compilation Error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            final_type = self.typecast(p[1].type , p[3].type)
            p[0] = Node(name = 'Bit Shift Operation',line_no = p[1].line_no,type = final_type)
            if p[0] != None :
                p[0].ast = AST(p)

    def p_relational_expression(self,p):
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
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func == 1 :
                print('Compilation Error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func == 1 :
                print('Compilation Error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            final_type = self.typecast(p[1].type , p[3].type)
            p[0] = Node(name = 'Relation Operation',line_no = p[1].line_no,type = final_type)
            if p[0] != None :
                p[0].ast = AST(p)

    def p_equality_expression(self,p):
        '''
        equality_expression : relational_expression
                            | equality_expression EQ_CHECK relational_expression
                            | equality_expression NOT_EQ relational_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
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
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator')
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func == 1 :
                print('Compilation Error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func == 1 :
                print('Compilation Error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            final_type = self.typecast(p[1].type , p[3].type)
            p[0] = Node(name = 'Equality Check Operation',line_no = p[1].line_no,type = final_type)
            if p[0] != None :
                p[0].ast = AST(p)

    def p_and_expression(self,p):
        '''
        and_expression : equality_expression
                    | and_expression BIT_AND equality_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
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
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator') 
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func == 1 :
                print('Compilation Error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func == 1 :
                print('Compilation Error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            p[0].type = 'int'
        
    
    def p_exclusive_or_expression(self,p):
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
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator') 
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func == 1 :
                print('Compilation Error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func == 1 :
                print('Compilation Error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            p[0].type = 'int'
        

    def p_inclusive_or_expression(self,p):
        '''
        inclusive_or_expression : exclusive_or_expression
                                | inclusive_or_expression BIT_OR exclusive_or_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
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
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator') 
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func == 1 :
                print('Compilation Error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func == 1 :
                print('Compilation Error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            p[0].type = 'int'

    

    def p_logical_and_expression(self,p):
        '''
        logical_and_expression : inclusive_or_expression
                            | logical_and_expression AND inclusive_or_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
        else:
            if p[1].type == None and  p[3].type == None: # diff.
                p[0] = Node(name = 'Logical And Operation',line_no = p[1].line_no,type = 'int')
                p[0].ast = AST(p)
                return
            elif p[1].type == None:
                p[0] = Node(name = 'Logical And Operation',line_no = p[1].line_no, type = p[3].type)
                p[0].ast = AST(p)
                return
            elif p[3].type == None:
                p[0] = Node(name = 'Logical And Operation',line_no = p[1].line_no, type = p[1].type)
                p[0].ast = AST(p)
                return
            p[0] = Node(name = 'Logical And Operation',line_no = p[1].line_no,type = None)
            p[0].ast = AST(p)
            valid_types = ['int','char','float']
            if conv(p[1].type).split()[-1] not in valid_types or conv(p[3].type).split()[-1] not in valid_types:
                if(p[2] is tuple):
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator') 
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func == 1 :
                print('Compilation Error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func == 1 :
                print('Compilation Error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            p[0].type = 'int'
        
        

    def p_logical_or_expression(self,p):
        '''
        logical_or_expression : logical_and_expression
                            | logical_or_expression OR logical_and_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
        else:
            if p[1].type == None and  p[3].type == None: # diff.
                p[0] = Node(name = 'Logical Or Operation',line_no = p[1].line_no,type = 'int')
                p[0].ast = AST(p)
                return
            elif p[1].type == None:
                p[0] = Node(name = 'Logical Or Operation',line_no = p[1].line_no, type = p[3].type)
                p[0].ast = AST(p)
                return
            elif p[3].type == None:
                p[0] = Node(name = 'Logical Or Operation',line_no = p[1].line_no, type = p[1].type)
                p[0].ast = AST(p)
                return
            p[0] = Node(name = 'Logical Or Operation',line_no = p[1].line_no,type = None)
            p[0].ast = AST(p)
            valid_types = ['int','char','float']
            if conv(p[1].type).split()[-1] not in valid_types or conv(p[3].type).split()[-1] not in valid_types:
                if(p[2] is tuple):
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2][0] +  ' operator')  
                else:
                    print('Compilation Error encountered at line no.',p[1].line_no , ': Incompatible data type with ' + p[2] +  ' operator') 
            x = self.symtable.isPresent(p[1].val)
            if x != None and p[1].is_func == 1 :
                print('Compilation Error encountered at line no.',p[1].line_no , ': Operation is invalid on ' + p[1].val)
            y = self.symtable.isPresent(p[3].val)
            if y != None and p[3].is_func == 1 :
                print('Compilation Error encountered at line no.',p[3].line_no , ': Operation is invalid on ' + p[3].val)
            p[0].type = 'int'


    def p_conditional_expression(self,p):
        '''
        conditional_expression : logical_or_expression
                            | logical_or_expression TERNARY expression COLON conditional_expression
        '''
        if(len(p) == 6):
            p[0] = Node(name = 'ConditionalOperation', line_no = p[1].line_no, type = None, children = [])
            if p[0] != None :
                p[0].ast = AST(p)
        elif(len(p) == 2) : 
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)

    def p_assignment_expression(self,p):
        '''
        assignment_expression : conditional_expression
                            | unary_expression assignment_operator assignment_expression
        '''        
        if(len(p) == 4):
            if(p[1].type == None and p[3].type == None):
                p[0] = Node(name = 'AssignmentOperation', line_no = p[1].line_no, type = 'int',children = [])
                if p[0] != None :
                    p[0].ast = AST(p)
                return
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
                    print(f"p_assignment_expression : found scope is None, entry doesn't exist in symbol table ,line 980.")
                    return

                found_scope = found_scope[1]
                for curr_list in self.symtable.table[found_scope][p[1].parentStruct]['field_list']:
                    # print(curr_list)
                    if curr_list[1] == p[1].val:
                        if len(curr_list) < 5 and len(p[1].array) == 0:
                            break
                        if(len(curr_list) < 5 or (len(curr_list[4]) < len(p[1].array))):
                            print("Compilation error at line ", str(p[1].line_no), ", incorrect number of dimensions")
                        
            found_scope = self.symtable.isPresent(p[1].val)
            if (found_scope != None) and ((p[1].is_func == 1)):
                print("Compilation Error at line", str(p[1].line_no), ":Invalid operation on", p[1].val)

            found_scope = self.symtable.isPresent(p[3].val)
            if (found_scope != None) and ((p[3].is_func == 1)):
                print("Compilation Error at line", str(p[3].line_no), ":Invalid operation on", p[3].val)

            if p[2].val != '=':
                if ('struct' in conv(p[1].type).split()) or ('struct' in conv(p[3].type).split()):
                    print("Compilation Error at line", str(p[1].line_no), ":Invalid operation on", p[1].val)
            
            p[0] = Node(name = 'AssignmentOperation',type = p[1].type, line_no = p[1].line_no, children = [], level = p[1].level)
            if p[0] != None :
                p[0].ast = AST(p)
        
        else :
            p[0] = p[1]
            if p[0] != None :
                p[0].ast = AST(p)
        

    def p_assignment_operator(self,p):
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

        

    def p_expression(self,p):
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

    def p_constant_expression(self,p):
        '''
        constant_expression : conditional_expression
        '''
        p[0] = p[1]
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_declaration(self,p):
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
                    totalEle = 1
                    if(len(child.children[0].array) > 0):
                        self.symtable.table[self.symtable.scope][child.children[0].val]['array'] = child.children[0].array
                    for i in child.children[0].array:
                        totalEle = totalEle*i
                    if(child.children[0].type != None):
                        self.symtable.table[self.symtable.scope][child.children[0].val]['type'] = p[1].type + ' ' + child.children[0].type 
                        self.symtable.table[self.symtable.scope][child.children[0].val]['size'] = 8
                    elif(flag == 0):
                        print("Compilation error at line " + str(p[1].line_no) + ", variable " + child.children[0].val + " cannot have type void")
                    self.symtable.table[self.symtable.scope][child.children[0].val]['size'] *= totalEle

                else:
                    if(child.val in self.symtable.table[self.symtable.scope].keys()):
                        print(p.lineno(1), 'Compilation error : ' + child.val + ' already declared')
                    self.symtable.table[self.symtable.scope][child.val] = {}
                    self.symtable.table[self.symtable.scope][child.val]['type'] = p[1].type
                    self.symtable.table[self.symtable.scope][child.val]['size'] = self.symtable.data_type_size(p[1].type)
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


    def p_declaration_specifiers(self,p):
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
                self.current_type.append('')
                
            else :
                # print(self.current_type)
                self.current_type.append(conv(p[1].type))

        elif(len(p) == 3):
            # print(f"p[1].name : {p[1].name}, p[2].name : {p[2].name}, line 1134")
            if(p[1].name == 'storageClassSpecifier' and p[2].name.startswith('storageClassSpecifier')):
                print("Invalid Syntax at line " + str(p[1].line_no) + ", " + conv(p[2].type) + " not allowed after " + conv(p[1].type))
            if(p[1].name == 'type_specifier_1' and (p[2].name.startswith('type_specifier_1') or p[2].name.startswith('StorageClassSpecifier') or p[2].name.startswith('TypeQualifier'))):
                print("Invalid Syntax at line " + str(p[1].line_no) + ", " + conv(p[2].type) + " not allowed after " + conv(p[1].type))
            if(p[1].name == 'typeQualifier' and (p[2].name.startswith('storageClassSpecifier') or p[2].name.startswith('TypeQualifier'))):
                print("Invalid Syntax at line " + str(p[1].line_no) + ", " + conv(p[2].type) + " not allowed after " + conv(p[1].type))
            # if(p[1].name == '') 
            self.current_type.pop()
            self.current_type.append(conv(p[1].type) + ' ' + conv(p[2].type))
            
            temp = ""
            if p[1] != None:
                temp = conv(p[1].type) + ' ' + conv(p[2].type)
            else:
                temp = p[2].type
            self.current_type.append(conv(temp))
            
            p[0] = Node(name = p[1].name + p[2].name, val = p[1], type = temp, line_no = p[1].line_no, children = [])
            if(p[0]!=None):
                p[0].ast = AST(p)
    

    def p_init_declarator_list(self,p):
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
    

    def p_init_declarator(self,p):
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
            
            
    def p_storage_class_specifier(self,p):
        '''
        storage_class_specifier : AUTO
        '''
        p[0] = Node(name = 'storageClassSpecifier',type = p[1], line_no = p.lineno(1), children = [])

    
    def p_type_specifier_1(self,p):
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

    def p_type_specifier_2(self,p):
        '''
        type_specifier : struct_specifier
                    | class_specifier
        '''
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

        
    def p_struct_specifier(self,p):
        '''
        struct_specifier : struct identifier lcur_br struct_declaration_list rcur_br
                                | struct lcur_br struct_declaration_list rcur_br
                                | struct identifier
        '''
        p[0] = Node(name = 'Struct Specifier')
        if len(p) == 6:
            name_ = 'struct ' +  conv(p[2].val)
            if(p[0]!=None):
                p[0].ast = AST(p)
            if name_ in self.symtable.table[self.symtable.scope].keys():
                print('Compilation Error occured at line'+str(p[1].line_no)+':Struct with this name has already been declared')
            ptr_name_ = name_ + ' *'
            self.symtable.table[self.symtable.scope][name_] = {}
            self.symtable.table[self.symtable.scope][name_]['type'] = name_
            self.symtable.table[self.symtable.scope][ptr_name_] = {}
            self.symtable.table[self.symtable.scope][ptr_name_]['type'] = ptr_name_
            already_decl = []
            mem_offset = 0
            # print(p[4].children, "line 1438")
            for child in p[4].children:
                for items in already_decl:
                    if items[1] == child.val:
                        print("Compilation Error encountered at line "+str(p[4].line_no)+':'+child.val +'Child of struct already encountered')
                if self.symtable.data_type_size(child.type) == -1:
                    print("Compilation Error encountered at line "+ str(p[4].line_no)+':Data type not valid')
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
                print("Compilation Error at line ",str(p[1].line_no)+': Invalid Type',conv(p[0].type))
        
        else :
            
            if(p[0]!=None):
                p[0].ast = AST(p)  
                  
    def p_struct(self,p):
        '''
        struct : STRUCT
        '''
        p[0] = Node ( name = 'Struct', type = 'struct', line_no = p.lineno(1))
        if(p[0]!=None):
            p[0].ast = AST(p)
            
    def p_struct_declaration(self,p):
        '''
        struct_declaration : specifier_qualifier_list struct_declarator_list SEMI_COLON
        '''
        p[0] = Node(name = 'StructDeclaration', type = p[1].type, line_no = p[1].line_no)
        if(p[0]!=None):
            p[0].ast = AST(p)
        p[0].children = p[2].children
        for child in p[0].children:
            if child.type != None:
                child.type = conv(p[1].type) + ' ' + conv(child.type)
            else:
                if('void' in conv(p[1].type).split()):
                    print("Compilation error encountered at line " + str(p[1].line_no) + ", variable " + child.val + " cannot have type void")
                child.type = p[1].type
    
    def p_struct_declaration_list(self,p):
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
    
    def p_specifier_qualifier_list(self,p):
        '''
        specifier_qualifier_list : type_specifier specifier_qualifier_list  
                                | type_specifier  
                                | type_qualifier specifier_qualifier_list   
                                | type_qualifier 
        '''
        p[0] = Node(name = 'Specifier Qualifier List', type = p[1].type, line_no = p[1].line_no)
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_struct_declarator_list(self,p):
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
        if(p[0]!=None):
            p[0].ast = AST(p)
        

    def p_struct_declarator(self,p):
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
            
    def p_type_qualifier(self,p):
        '''
        type_qualifier : CONST
        '''
        p[0] = Node(name = 'typeQualifier', type = p[1], line_no = p.lineno(1), children = [])


    def p_declarator(self,p): 
        '''
        declarator : pointer direct_declarator
                | direct_declarator
        '''
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
                #curfuncReturntype = curfuncReturntype + ' ' + p[1].type
                self.funcReturntype = self.funcReturntype + ' ' + conv(p[1].type)

            p[0].val = p[2].val
            p[0].array = p[2].array

    def p_direct_declarator_1(self,p):
        '''
        direct_declarator : identifier
                        | LEFT_PAR declarator RIGHT_PAR
                        | direct_declarator l_paren parameter_type_list RIGHT_PAR
                        | direct_declarator l_paren identifier_list RIGHT_PAR
        '''
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
            if(len (p) == 5 and p[3].name == 'ParameterList'):
                p[0].children = p[3].children
                p[0].type = self.current_type[-1]
                if(p[1].val in self.symtable.table[self.symtable.prevScope[self.symtable.scope]].keys()):
                    print('Compilation error : near- line ' + str(p[1].line_no) + ' function already declared')
                    
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]][p[1].val] = {}
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]][p[1].val]['is_func'] = 1
                tempList = []
                for child in p[3].children:
                    tempList.append(conv(child.type))
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]][p[1].val]['argumentList'] = tempList
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]][p[1].val]['type'] = self.current_type[-1-len(tempList)]
                self.funcReturntype = copy.deepcopy(self.current_type[-1-len(tempList)])
                self.scope_to_function[self.symtable.scope] = p[1].val

    
    def p_direct_declarator_2(self,p):
        '''
        direct_declarator : direct_declarator LEFT_SQ_BR constant_expression RIGHT_SQ_BR
                        | direct_declarator LEFT_SQ_BR RIGHT_SQ_BR
                        | direct_declarator l_paren RIGHT_PAR
        '''
        if len(p) == 5 :
            p[0] = Node(name = 'Array Declarator', val = p[1].val, line_no = p.lineno(1))
            if(p[0]!=None):
                p[0].ast = AST(p)
                p[0].array = copy.deepcopy(p[1].array)  
                p[0].array.append(int(p[3].val))
        else : # incomplete.
            p[0] = p[1]
            if(p[0]!=None):
                p[0].ast = AST(p)
            if(p[3] == ')'):
                # print("line 1600 ", p[1].val, " ", self.symtable.scope)
                if(p[1].val in self.symtable.table[self.symtable.prevScope[self.symtable.scope]].keys()):
                    print('Compilation error : near line ' + str(p[1].line_no) + ' function already declared')
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]][p[1].val] = {}
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]][p[1].val]['type'] = self.current_type[-1]
                self.funcReturntype = copy.deepcopy(self.current_type[-1])
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]][p[1].val]['is_func'] = 1
                self.symtable.table[self.symtable.prevScope[self.symtable.scope]][p[1].val]['argumentList'] = []
                self.scope_to_function[self.symtable.scope] = p[1].val
        

    def p_pointer(self,p):
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

    def p_type_qualifier_list(self,p):
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

    def p_parameter_type_list(self,p):
        '''
        parameter_type_list : parameter_list
        '''
        p[0] = p[1]
        if(p[0]!=None):
            p[0].ast= AST(p)

    def p_parameter_list(self,p):
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
        
    def p_parameter_declaration(self,p):
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
            if(p[2].name == 'Declarator'):
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
        
    def p_identifier_list(self,p):
        '''
        identifier_list : INT_NUM
                        | identifier_list COMMA identifier
                        | identifier_list COMMA INT_NUM
        '''   
        if(len(p) == 2):
            p[0] = Node(name = 'IdentifierList',val = p[1], line_no = p.lineno(1), children = [p[1]])
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
            p[0] = Node(name = 'IdentifierList',val = p[1].val, line_no = p.lineno(1), children = [p[1]])
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
                p[0].ast = AST(p)

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
          
        

    def p_initializer(self,p):
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
            p[0] = p[2]
            p[0].name = 'Initializer'
        if(len(p) == 4):
            p[0].max_depth = p[2].max_depth + 1
            if(p[0]!=None):
                p[0].ast = AST(p)
        elif(len(p) == 5):
            if(p[0]!=None):
                p[0].ast = AST(p)

    def p_initializer_list(self,p):
        '''
        initializer_list : initializer
                        | initializer_list COMMA initializer
        '''
        if(len(p) == 2):
            p[0] = Node(name = 'Initializer List', children = [p[1]], line_no = p.lineno(1), max_depth = p[1].max_depth)
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

    def p_statement(self,p):
        '''
        statement : labeled_statement
                | compound_statement
                | expression_statement
                | selection_statement
                | iteration_statement
                | jump_statement
        '''
        p[0] = Node(name = 'statement', children = [], line_no = p.lineno(1))
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_labeled_statement(self,p):
        '''
        labeled_statement : identifier COLON statement
        '''
        p[0] = Node(name = 'labeledStatement', children = [], line_no = p.lineno(1) )
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_compound_statement(self,p):
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
            #CHECK CHECK CHECK            
                            
        
    def p_function_compound_statement(self,p):
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
                    #CHECK CHECK CHECK

    
         

    def p_block_item_list(self,p):
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

    def p_block_item(self,p):
        '''
        block_item : declaration
                    | statement
        '''
        p[0] = p[1]
        

    def p_expression_statement(self,p):
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
            #p[0].place = p[1].place

        p[0].name = 'expressionStatement'

        
    def p_selection_statement(self,p):
        '''
        selection_statement : IF LEFT_PAR expression RIGHT_PAR statement %prec IFX
                            | IF LEFT_PAR expression RIGHT_PAR statement ELSE statement
        '''
        p[0] = Node(name = 'IfElseStatment', children = [], line_no = p.lineno(1))
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_iteration_statement_1(self,p):
        '''
        iteration_statement : while LEFT_PAR expression RIGHT_PAR statement
                        
        '''
        p[0] = Node(name = 'whileStatement', line_no = p.lineno(1))
        self.symtable.loopingDepth-=1
        if(p[0]!=None):
            p[0] = AST(p)

    def p_iteration_statement_2(self,p):
        '''
        iteration_statement :  for LEFT_PAR expression_statement expression_statement RIGHT_PAR statement       
        '''
        
        p[0] = Node(name = 'ForNoStatement', line_no = p.lineno(1))
        self.symtable.loopingDepth-=1
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_iteration_statement_3(self,p):
        '''
        iteration_statement : for LEFT_PAR expression_statement expression_statement expression RIGHT_PAR statement 
        '''
        p[0] = Node(name = 'ForStatement', line_no = p.lineno(1))
        self.symtable.loopingDepth-=1
        if(p[0]!=None):
            p[0].ast = AST(p)

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


    def p_while(self,p):
        '''
        while : WHILE
        '''
        self.symtable.loopingDepth+=1
        p[0]=p[1]
        p[0]=AST(p)
        ## CHECK)
    def p_for(self, p):
        '''
        for : FOR
        '''
        self.symtable.loopingDepth+=1
        p[0]=p[1]
        p[0]=AST(p)
         ## CHECK


    def p_translation_unit(self,p):
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

    def p_external_declaration(self,p):
        '''
        external_declaration : function_definition
                            | declaration
        '''
        p[0] = p[1]
        p[0].name = 'external_declaration'
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_function_definition(self,p):
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
    
    def p_function_definition2(self,p):
        '''
        function_definition : declaration_specifiers declarator function_compound_statement
        '''
        p[0] = Node(name = 'FuncDecl',val = p[2].val,type = p[1].type, line_no = p.lineno(1))
        
        if(p[0]!=None):
            p[0].ast = AST(p)

    def p_declaration_list(self,p):
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
    
    def p_jump_statement(self,p):
        '''
        jump_statement : RETURN SEMI_COLON
                        | RETURN expression SEMI_COLON
        '''
        if(len(p) == 3):
            p[0] = Node(name = 'jump_statement', line_no = p.lineno(1))
            if(p[0]!=None):
                p[0].ast = AST(p)
            if(self.funcReturntype != 'void'):
                print('Compilation error at line ' + str(p.lineno(1)) + ': function return type is not void')
        else:
            if(p[2].type != None and self.funcReturntype != p[2].type):
                # print(curfuncReturntype)
                print('warning at line ' + str(p.lineno(1)) + ': function return type is not ' + conv(p[2].type))
                # print(f"return type is {self.funcReturntype}")
            p[0] = Node(name = 'jump_statement',line_no = p.lineno(1))
            # print(p[1], "line 2080")
            if(p[0]!=None):
                p[0].ast = AST(p) 


    def p_error(self,p):
        print('Error found while parsing!')
        print(p)
        x = p.lexpos - self.lex.lexer.lexdata.rfind('\n', 0, p.lexpos)
        print(f"Error!!!, Unknown lexeme encountered! {p.value[0]} at line no. {p.lineno}, column no. {x}")
        global error_present
        error_present = 1

if __name__ == '__main__':
    pars = Parser()
    pars.build()

    for filename in sys.argv[1:] :
        with open(filename, 'r') as f:
            content = f.read()
            pars.lex.lexer.input(content)

            open('graph1.dot','w').write("digraph G {")
            pars.parser.parse(content, debug=False)
            open('graph1.dot','a').write("\n}")

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
