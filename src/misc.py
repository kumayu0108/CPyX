import sys
import re
from NodeClass import Node

cur_num = 0
var_cnt = 0
def conv(s):
    return '' if s is None else str(s)

def ignore_1(s):
    ignore_list = ["{", "}", "(", ")", "[", "]", ";", ","]
    if s in ignore_list:
        return True
    return False

# def parse_format_string(format_str):
#   c_reg_exp='''\
#   %                                  # literal "%"
#   (?:                                # first option
#   (?:[-+0 #]{0,5})                   # optional flags
#   (?:\d+|\*)?                        # width
#   (?:\.(?:\d+|\*))?                  # precision
#   (?:h|l|ll|w|I|I32|I64)?            # size
#   ([cCdiouxXeEfgGaAnpsSZ])             # type
#   ) |                                # OR
#   %%                                # literal "%%"
#   '''
#   types=[]
#   for match in re.finditer(c_reg_exp, format_str, flags = re.X):
#       types.append(match.group(1))
#   types = [type for type in types if type is not None]
#   return types

def int_or_real(dtype):
  arr = conv(dtype).split()
  if ('*' in arr):
    return 'int'
  if('struct' in arr ):
    return 'int'
  if 'long' in arr:
    return 'int' 
  elif ( ('int' in arr) or ('short' in arr) ):
    return 'int'
  elif ('char' in arr):
    return 'char'
  else:
    return 'float'

def extract_if_tuple(p2):
  if (type(p2) is tuple):
    return str(p2[0])
  else:
    return str(p2)

def new_var():
  global var_cnt
  s = "__t_" + str(var_cnt)
  var_cnt += 1
  return s

def AST(p):
    global cur_num
    calling_func_name = sys._getframe(1).f_code.co_name
    rule_calling = calling_func_name[2:]
    length = len(p)
    if(length == 2):
        if(isinstance(p[1], Node)):
            return p[1].ast
        else:
            return p[1]
    else:
        cur_num += 1
        p_count = cur_num
        open('./graph1.dot','a').write("\n" + str(p_count) + "[label=\"" + rule_calling.replace('"',"") + "\"]")
        for child in range(1,length,1):

            if(isinstance(p[child], Node) and p[child].ast is None):
                continue
            global child_num 
            global child_val
            if(not isinstance(p[child], Node)):
                if(isinstance(p[child], tuple)):
                    if(ignore_1(p[child][0]) is False):
                        open('graph1.dot','a').write("\n" + str(p_count) + " -> " + str(p[child][1]))
                elif not isinstance(p[child], list):
                    if((ignore_1(p[child]) is False) & (str(p[child]).replace('"',"") != "")):
                        cur_num += 1
                        open('graph1.dot','a').write("\n" + str(cur_num) + "[label=\"" + str(p[child]).replace('"',"") + "\"]")
                        p[child] = (p[child],cur_num)
                        open('graph1.dot','a').write("\n" + str(p_count) + " -> " + str(p[child][1]))
            else:
                if(isinstance(p[child].ast, tuple)):
                    if(ignore_1(p[child].ast[0]) is False):
                        open('graph1.dot','a').write("\n" + str(p_count) + " -> " + str(p[child].ast[1]))
                else:
                    if((ignore_1(p[child].ast) is False) & (str(p[child].ast).replace('"',"") != "")):
                        cur_num += 1
                        open('graph1.dot','a').write("\n" + str(cur_num) + "[label=\"" + str(p[child].ast).replace('"',"") + "\"]")
                        p[child].ast = (p[child].ast,cur_num)
                        open('graph1.dot','a').write("\n" + str(p_count) + " -> " + str(p[child].ast[1]))

    return (rule_calling,p_count)

class symbol_info:
    def __init__(self, isArray = False, length = 0, isStruct = False, size = 0, pointsTo = ''):
        self.isArray = isArray
        self.isStruct = isStruct
        self.size = ((size + 3)//4)*4
        self.length = length
        self.address_desc_mem = []
        self.pointsTo = pointsTo
        self.address_desc_reg = set()