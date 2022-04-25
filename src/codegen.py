'''
This file creates assembly code from 3AC code.
'''

from parser2 import pars
import sys
import copy
from misc import symbol_info
count1 = 0
param_off = 0
scope_all_instr_arr = []
scope0_instr_arr = []
leaders = [0]
nextuse = {}
live = {}
symbols = {}

def is_number(number):
    number = str(number)
    if (number.startswith('-')):
        return True
    if number[0] == '.' or number[0].isnumeric():
        return True
    return False

def is_symbol(var):
    if(var in pars.symtable.global_symbol_table.keys()):
        return True
    else:
        return False


def register_alloc_optim():
    sz = len(scope0_instr_arr)
    for j in range(0, sz):
        cur_instr = scope0_instr_arr[j]
        src1, src2, dest = cur_instr.src1, cur_instr.src2, cur_instr.dest
        for operand in [src1, src2, dest]:
            if (operand != None and not operand.isnumeric()):
                live[operand] = False
                nextuse[operand] = None

    for j in range(sz-1, -1, -1):
        cur_instr = scope0_instr_arr[j]
        src1, src2, dest = cur_instr.src1, cur_instr.src2, cur_instr.dest

        if (dest != None and not dest.isnumeric() and is_symbol(dest)):
            cur_instr.info['live'][dest] = live[dest]
            cur_instr.info['nextuse'][dest] = nextuse[dest]
            live[dest] = False
            nextuse[dest] = None
        if (src2 != None and not src2.isnumeric() and is_symbol(src2)):
            cur_instr.info['live'][src2] = live[src2]
            cur_instr.info['nextuse'][src2] = nextuse[src2]
            live[src2] = True
            nextuse[src2] = j
        if (src1 != None and not src1.isnumeric() and is_symbol(src1)):
            cur_instr.info['live'][src1] = live[src1]
            cur_instr.info['nextuse'][src1] = nextuse[src1]
            live[src1] = True
            nextuse[src1] = j

    for i in range(len(leaders) - 1):
        ignore_instr_list = ['param']
        block_start = leaders[i]
        block_end = leaders[i + 1] - 1
        for j in range(block_start, block_end + 1):
            cur_instr = scope_all_instr_arr[j]
            src1, src2, dest = cur_instr.src1, cur_instr.src2, cur_instr.dest
            for operand in [src1, src2, dest]:
                if (operand != None and not operand.isnumeric()):
                    live[operand] = False
                    nextuse[operand] = None

        for j in range(block_end, block_start - 1, -1):
            cur_instr = scope_all_instr_arr[j]
            src1, src2, dest = cur_instr.src1, cur_instr.src2, cur_instr.dest
            if cur_instr.op in ignore_instr_list:
                continue
            if (dest != None and not dest.isnumeric() and is_symbol(dest)):
                cur_instr.info['live'][dest] = live[dest]
                cur_instr.info['nextuse'][dest] = nextuse[dest]
                live[dest] = False
                nextuse[dest] = None
            if (src2 != None and not src2.isnumeric() and is_symbol(src2)):
                cur_instr.info['live'][src2] = live[src2]
                cur_instr.info['nextuse'][src2] = nextuse[src2]
                live[src2] = True
                nextuse[src2] = j
            if (src1 != None and not src1.isnumeric() and is_symbol(src1)):
                cur_instr.info['live'][src1] = live[src1]
                cur_instr.info['nextuse'][src1] = nextuse[src1]
                live[src1] = True
                nextuse[src1] = j

def find_basic_blocks():
    i = 1
    for quads in pars.EMIT.global_emit_array:
        instruction = Instruction(i,quads)
        scope0_instr_arr.append(instruction)
    # print('186 helper function')
    for j in pars.EMIT.emit_array:
        print(j)
    for quads in pars.EMIT.emit_array:
        instruction = Instruction(i,quads)
        scope_all_instr_arr.append(instruction)
        op = quads[0]
        extra = 0
        if(op in ["label","goto","ifgoto","ret","call","func","funcEnd"]):
            if(op != "label" and op != "func"):
                extra += 1
            leaders.append(i - 1 + extra)
        i += 1
    leaders.append(len(pars.EMIT.emit_array))

class Instruction:
    def __init__(self,lno,quad):
        self.lno = lno
        self.src1 = None
        self.src2 = None
        self.dest = None
        self.jump_label = None
        self.info = {}
        self.op = None
        self.info['nextuse'] = {}
        self.info['live'] = {}
        self.argument_list = []
        self.fill_info(quad)

    def fill_info(self,quad):
        self.op = quad[0]
        if(self.op == "ifgoto"):
            self.dest = quad[3]
            self.src1 = quad[1]
            self.src2 = quad[2]
            print("ifgoto : ", self.src1 , self.src2 , self.dest)

        elif(self.op == "goto"):
            self.dest = quad[3]
            print("goto : ", self.dest)

        elif(self.op == "inc" or self.op == "dec"):
            if(pars.symtable.global_symbol_table[quad[3]]['type'] == 'float'):
                if(self.op == 'inc'):
                    self.op = 'float_+'
                else:
                    self.op = 'float_-'
                self.src1 = quad[3]
                self.src2 = pars.symtable.float_reverse_map["1.0"]
                self.dest = quad[3]
                if(self.op == 'inc'):
                    print(self.dest, "=", self.src1, "float_+ 1.0") 
                else:
                    print(self.dest, "=", self.src1, "float_- 1.0") 
            else:    
                self.src1 = quad[3]
                print(self.op, self.dest)


        elif(self.op == "param"):
            self.src1 = quad[3]
            self.dest = quad[2]
            print(self.op, self.src1)

        elif(self.op.endswith('bitwisenot')):
            self.src1 = quad[1]
            self.dest = quad[3]
            print(self.dest, "= ~", self.src1) 

        elif(self.op == "func"):
            self.src1 = quad[3]
            print(self.op , self.src1)

        elif(self.op == "ret"):
            if(quad[3] != ""):
                self.src1 = quad[3]
            print(self.op, quad[3])

        elif(self.op == "int_float_="):
            self.op = "int2float"
            self.src1 = quad[1]
            self.dest = quad[3]
            print(self.dest, "=" , self.op , self.src1)

        elif(self.op == "call"):
            self.src1 = quad[3]
            self.src2 = quad[2]
            print(self.op, quad[1], quad[2], quad[3])


        elif(self.op == "char_int_="):
            self.op = "char2int"
            self.src1 = quad[1]
            self.dest = quad[3]
            print(self.dest, "=" , self.op , self.src1)

        elif(self.op == "float_int_="):
            self.op = "float2int"
            self.src1 = quad[1]
            self.dest = quad[3]
            print(self.dest, "=" , self.op , self.src1)


        elif(self.op == "int_char_="):
            self.op = "int2char"
            self.src1 = quad[1]
            self.dest = quad[3]
            print(self.dest, "=" , self.op , self.src1)

        elif(self.op == "char_float_="):
            self.op = "char2float"
            self.src1 = quad[1]
            self.dest = quad[3]
            print(self.dest, "=" , self.op , self.src1)


        elif(self.op == "int_=" or self.op == "int_int_=" or self.op == "float_=" or self.op == "char_=" or self.op == "char_char_="):
            self.dest = quad[3]
            self.src1 = quad[1]
            if (quad[2] != ''):
                self.src2 = quad[2]
                print(self.dest, self.op, self.src2, self.src1)
            else:
                print(self.dest, self.op , self.src1)

        elif(self.op == "float_char_="):
            self.op = "float2char"
            self.src1 = quad[1]
            self.dest = quad[3]
            print(self.dest, "=" , self.op , self.src1)


        elif(self.op == "int_uminus"):
            self.dest = quad[3]
            self.src1 = quad[1]
            print(self.dest, "int_= -", self.src1)

        elif(self.op == "label"):
            self.src1 = quad[3]
            print(self.op, self.src1)

        elif(self.op == "float_uminus"):
            self.dest = quad[3]
            self.src1 = quad[1]
            self.src2 = pars.symtable.float_reverse_map["-1.0"]
            self.op = "float_*"
            print(self.dest, "float_= -", self.src1)

        elif(self.op.startswith("int_") or self.op.startswith("float_") or self.op.startswith("char_")):
            self.dest = quad[3]
            self.src1 = quad[1]
            self.src2 = quad[2]
            print(self.dest, "=", self.src1 , self.op , self.src2)

        elif(self.op == "*"):
            self.op = "deref"
            self.dest = quad[3]
            self.src1 = quad[1]
            print(self.dest, "= deref", self.src1)

        elif(self.op == "addr"):
            self.dest = quad[3]
            self.src1 = quad[1]
            print(self.dest, "= addr", self.src1)


        elif(self.op == "funcEnd"):
            self.dest = quad[3]
            print(self.op) 

class register:
    def __init__(self):
        self.register_descriptor = {}
        self.byte__translator = {}
        self.register_descriptor["eax"] = set()
        self.register_descriptor["ebx"] = set()
        self.register_descriptor["ecx"] = set()
        self.register_descriptor["edx"] = set()
        self.register_descriptor["esi"] = set()
        self.register_descriptor["edi"] = set()
        self.register_descriptor["xmm0"] = set()
        self.register_descriptor["xmm1"] = set()
        self.register_descriptor["xmm2"] = set()
        self.register_descriptor["xmm3"] = set()
        self.register_descriptor["xmm4"] = set()
        self.register_descriptor["xmm5"] = set()
        self.register_descriptor["xmm6"] = set()
        self.register_descriptor["xmm7"] = set()
        self.byte__translator["eax"] = "al"
        self.byte__translator["ebx"] = "bl"
        self.byte__translator["ecx"] = "cl"
        self.byte__translator["edx"] = "dl"
        self.byte__translator["esi"] = "sil"
        self.byte__translator["edi"] = "dil"

    def free_registers(self,instr):
       to_free = [instr.src1, instr.src2]
       for operand in to_free:
           if (operand != None and is_symbol(operand) and instr.info['nextuse'][operand] == None
               and instr.info['live'][operand] == False):
               temp_reg=''
               for reg in symbols[operand].address_desc_reg:
                   self.register_descriptor[reg].remove(operand)
                   temp_reg = reg
               symbols[operand].address_desc_reg.clear()
               if temp_reg != '':
                   if temp_reg.startswith('xmm'):
                       print("\tmovss dword " + self.get_location_in_memory(operand) + ", " + temp_reg)
                   else:
                       print("\tmov dword " + self.get_location_in_memory(operand) + ", " + temp_reg) 

    def get_register(self,instr, compulsory = True, exclude_reg = [],is_float = False):
        if(is_float == False):
            if is_symbol(instr.src1): 
                for reg in symbols[instr.src1].address_desc_reg:
                    if reg not in exclude_reg:
                        if((not reg.startswith('xmm')) and len(self.register_descriptor[reg]) == 1 and instr.info['nextuse'][instr.src1] == None and not instr.info['live'][instr.src1]):
                            self.save_in_memory(reg)
                            return reg

            for reg in self.register_descriptor.keys():
                if(reg not in exclude_reg and (not reg.startswith('xmm'))):
                    if(len(self.register_descriptor[reg]) == 0):
                        self.save_in_memory(reg)
                        return reg

            if(instr.info['nextuse'][instr.dest] != None or compulsory == True):
                R = None
                for reg in self.register_descriptor.keys():
                    if(reg not in exclude_reg and (not reg.startswith('xmm'))):
                        if(R == None):
                            R = reg
                        elif(len(self.register_descriptor[reg]) < len(self.register_descriptor[R])):
                            R = reg
                self.save_in_memory(R)
                return R

            else:
                return self.get_location_in_memory(instr.dest)
        else:
            if is_symbol(instr.src1): 
                for reg in symbols[instr.src1].address_desc_reg:
                    if reg not in exclude_reg:
                        if((reg.startswith('xmm')) and len(self.register_descriptor[reg]) == 1 and instr.info['nextuse'][instr.src1] == None\
                        and not instr.info['live'][instr.src1]):
                            self.save_in_memory(reg)
                            return reg

            for reg in self.register_descriptor.keys():
                if(reg not in exclude_reg and (reg.startswith('xmm'))):
                    if(len(self.register_descriptor[reg]) == 0):
                        self.save_in_memory(reg)
                        return reg

            if(instr.info['nextuse'][instr.dest] != None or compulsory == True):
                R = None
                for reg in self.register_descriptor.keys():
                    if(reg not in exclude_reg and (reg.startswith('xmm'))):
                        if(R == None):
                            R = reg
                        elif(len(self.register_descriptor[reg]) < len(self.register_descriptor[R])):
                            R = reg
                self.save_in_memory(R)
                return R

            else:
                return self.get_location_in_memory(instr.dest)


    def save_in_memory(self,reg):
        saved_loc = set()
        for symbol in self.register_descriptor[reg]:
            location = self.get_location_in_memory(symbol)
            if location not in saved_loc:
                if(reg.startswith('xmm')):
                    print("\tmovss dword " + self.get_location_in_memory(symbol) + ", " + reg)
                else:
                    print("\tmov dword " + self.get_location_in_memory(symbol) + ", " + reg)
                saved_loc.add(location)
            symbols[symbol].address_desc_reg.remove(reg)
        self.register_descriptor[reg].clear()


    
    def get_location_in_memory(self,symbol, sqb = True):
        if not is_symbol(symbol):
            return symbol
        if (symbol in pars.symtable.strings.keys() or symbol in pars.symtable.local_vars['global']):
            if(sqb):
                return "[" + str(symbol) + "]"
            else:
                return str(symbol)

        if(len(symbols[symbol].address_desc_mem) == 0):
            return symbol
        location = symbols[symbol].address_desc_mem[-1]
        if(not sqb):
            prefix_string = ""
            if(is_number(location)):
                prefix_string = "ebp"
                if(location >= 0):
                    prefix_string = "ebp+"    

            return prefix_string+str(location)
        prefix_string = "["
        if(is_number(location)):
            prefix_string = "[ebp"
            if(location >= 0):
                prefix_string = "[ebp+"

        return prefix_string+str(location)+"]"

    def get_best_location(self,symbol, exclude_reg = [], byte = False):
        if not is_symbol(symbol):
            return symbol
        if(symbol in pars.symtable.strings.keys()):
            return symbol
        if is_symbol(symbol):
            for reg in symbols[symbol].address_desc_reg:
                if (reg not in exclude_reg):
                    if byte:
                        return self.byte__translator[reg]
                    else:
                        return reg
        if(byte):
            return "byte " + self.get_location_in_memory(symbol)
        else:
            return "dword " + self.get_location_in_memory(symbol)

    def check_type_location(self,location):
        if is_number(location):
            return 'number'
        elif (location.startswith('[')):
            return "memory"
        elif(location.startswith("dword")):
            return "data"
        else:
            return "register"

    def del_symbol_reg_exclude(self,symbol, exclude = []):
        to_keep = set()
        if len(exclude) == 0:
            for reg in symbols[symbol].address_desc_reg:
                self.save_in_memory(reg)
                break
        for reg in symbols[symbol].address_desc_reg:
            if reg not in exclude:
                self.register_descriptor[reg].remove(symbol)
                tmp = reg
            else:
                to_keep.add(reg)
        symbols[symbol].address_desc_reg.clear()
        symbols[symbol].address_desc_reg = copy.deepcopy(to_keep)


    def upd_register_descriptor(self,reg, symbol):
        if(symbol in pars.symtable.strings):
            return
        self.save_in_memory(reg)
        if not is_symbol(symbol):
            return
        for register in symbols[symbol].address_desc_reg:
            if register != reg:
                self.register_descriptor[register].remove(symbol)
        symbols[symbol].address_desc_reg.clear()
        symbols[symbol].address_desc_reg.add(reg)
        self.register_descriptor[reg].add(symbol)

    def save_caller_status(self):
        saved = set()
        for reg in self.register_descriptor.keys():
            for symbol in self.register_descriptor[reg]:
                if symbol not in saved:
                    if(reg.startswith('xmm')):
                        print("\tmovss dword " +  self.get_location_in_memory(symbol) + ", " + reg)
                    else:
                        print("\tmov dword " +  self.get_location_in_memory(symbol) + ", " + reg)

                    saved.add(symbol)
                    symbols[symbol].address_desc_reg.clear()
            self.register_descriptor[reg].clear()
    
    
    
def dprint(str):
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    print(str)
    sys.stdout = open('out.asm', 'a')


class CodeGen:
    REG = register()
    def gen_top_headers(self):
        for func in ['printf', 'scanf','malloc','free','strlen', 'strcpy','pow', 'fabs', 'sin', 'cos', 'sqrt']:
            print("extern " + func)
        print("section .text")
        print("\tglobal main")
        print("main:")
        print("\tpush ebp")
        print("\tmov ebp, esp")

        for var in pars.symtable.local_vars['global']:
            if(symbols[var].isArray):
                quad = Instruction(0, ['', '', '', ''])
                reg = self.REG.get_register(quad, compulsory = True)
                print("\tmov " + reg + ", " + str(symbols[var].length))
                print("\timul " + reg + ", " + str(max(4, pars.symtable.data_type_size(pars.symtable.global_symbol_table[var]['type']))))
                print("\tpush " + reg)
                print("\tcall malloc")
                print("\tadd esp, 4")
                print("\tmov [" + str(var) + "] , eax")

        for quad in scope0_instr_arr:
            self.generate_assembly_code(quad)
        self.REG.save_caller_status()
        print("\tcall _main")
        print("\tmov esp, ebp")
        print("\tpop ebp")
        print("\tret")


    def data_section(self):
        print("section\t.data")
        float_tmp_vars = [lis[1] for lis in pars.symtable.float_constant_values]
        for vars in pars.symtable.local_vars['global']:
            if vars not in pars.symtable.strings.keys() and vars not in float_tmp_vars and vars not in pars.symtable.ignore_function_ahead:
                if(symbols[vars].isStruct):
                    print("\t" + vars + "\ttimes\t" + str(symbols[vars].size) + "\tdb\t0")
                elif('value' in pars.symtable.global_symbol_table[vars].keys() and not symbols[vars].isArray):
                    print("\t" + vars + "\tdd\t" + str(pars.symtable.global_symbol_table[vars]['value']))
                else:
                    print("\t" + vars + "\tdd\t0")
        for name in pars.symtable.strings.keys():
            temp_string = (pars.symtable.strings[name])[1:-1]
            print("\t" + name + ":\tdb\t`" + temp_string + "`, 0")
        for name in pars.symtable.float_constant_values:
            print("\t" + name[1] + "\tdd\t" + str(name[0]))


    def bin_operations(self, quad, op):
        best_location = self.REG.get_best_location(quad.src1)
        reg1 = self.REG.get_register(quad, compulsory=True)
        self.REG.save_in_memory(reg1)
        if best_location != reg1:
            print("\tmov " + reg1 + ", " + best_location)
        reg2 = self.REG.get_best_location(quad.src2)
        print("\t" + op + ' ' + reg1 + ", " + reg2)
        self.REG.free_registers(quad)
        self.REG.upd_register_descriptor(reg1, quad.dest)

    def real_bin_operations(self,quad,op):
        best_location = self.REG.get_best_location(quad.src1)
        reg1 = self.REG.get_register(quad, compulsory=True,is_float=True)
        self.REG.save_in_memory(reg1)
        if best_location != reg1:
            print("\tmovss " + reg1 + ", " + best_location)
        reg2 = self.REG.get_best_location(quad.src2)
        print("\t" + op + ' ' + reg1 + ", " + reg2)
        self.REG.free_registers(quad)
        self.REG.upd_register_descriptor(reg1, quad.dest)

    def add(self,quad):
        self.bin_operations(quad, 'add')

    def sub(self, quad):
        self.bin_operations(quad, 'sub')

    def real_add(self,quad):
        self.real_bin_operations(quad,'addss')

    def real_sub(self,quad):
        self.real_bin_operations(quad,'subss')

    def mul(self, quad):
        self.bin_operations(quad, 'imul')

    def real_mul(self,quad):
        self.real_bin_operations(quad, 'mulss')

    def real_div(self,quad):
        self.real_bin_operations(quad, 'divss')

    def band(self, quad):
        self.bin_operations(quad, 'and')

    def bor(self, quad):
        self.bin_operations(quad, 'or')

    def bxor(self, quad):
        self.bin_operations(quad, 'xor')

    def div(self, quad):
        best_location = self.REG.get_best_location(quad.src1)
        self.REG.save_in_memory('eax')
        self.REG.save_in_memory('edx')
        if best_location != 'eax':
            print("\tmov " + 'eax' + ", " + best_location)
        reg = self.REG.get_register(quad, exclude_reg=['eax','edx'])
        best_location = self.REG.get_best_location(quad.src2)
        self.REG.upd_register_descriptor(reg, quad.src2)
        if best_location != reg:
            print("\tmov " + reg + ", " + best_location)
        print("\tcdq")
        print('\tidiv ' + reg)
        self.REG.upd_register_descriptor('eax', quad.dest)
        self.REG.free_registers(quad)


    def mod(self, quad):
        best_location = self.REG.get_best_location(quad.src1)
        self.REG.save_in_memory('eax')
        self.REG.save_in_memory('edx')
        if best_location != 'eax':
            print("\tmov " + 'eax' + ", " + best_location)
        reg = self.REG.get_register(quad, exclude_reg=['eax', 'edx'])
        best_location = self.REG.get_best_location(quad.src2)
        self.REG.upd_register_descriptor(reg, quad.src2)
        if best_location != reg:
            print("\tmov " + reg + ", " + best_location)
        print("\tcdq")
        print('\tidiv ' + reg)
        self.REG.upd_register_descriptor('edx', quad.dest)
        self.REG.free_registers(quad)


    def increment(self, quad):
        best_location = self.REG.get_best_location(quad.src1)
        if self.REG.check_type_location(best_location) == "register":
            self.REG.upd_register_descriptor(best_location, quad.src1)
        print("\tinc " + best_location)

    def decrement(self, quad):
        best_location = self.REG.get_best_location(quad.src1)
        if self.REG.check_type_location(best_location) == "register":
            self.REG.upd_register_descriptor(best_location,quad.src1)
        print("\tdec " + best_location)

    def bitwisenot(self, quad):
        best_location = self.REG.get_best_location(quad.dest)
        if self.REG.check_type_location(best_location) == "register":
            self.REG.upd_register_descriptor(best_location, quad.dest)
        print("\tnot " + best_location)

    def uminus(self, quad):
        best_location = self.REG.get_best_location(quad.dest)
        if self.REG.check_type_location(best_location) == "register":
            self.REG.upd_register_descriptor(best_location, quad.dest)
        print("\tneg " + best_location)


    def lshift(self, quad):
        best_location = self.REG.get_best_location(quad.src1)
        reg1 = self.REG.get_register(quad, compulsory=True)
        self.REG.upd_register_descriptor(reg1, quad.dest)
        if best_location != reg1:
            print("\tmov " + reg1 + ", " + best_location)
        best_location = self.REG.get_best_location(quad.src2)
        if self.REG.check_type_location(best_location) == "number":
            print("\tshl " + reg1 +  ', ' + best_location)
        else:
            if best_location != "ecx":
                self.REG.upd_register_descriptor("ecx",quad.src2)
                print("\tmov " + "ecx" + ", " + best_location)
            print("\tshl " + reg1 + ", cl")
        self.REG.free_registers(quad)


    def rshift(self, quad):
        best_location = self.REG.get_best_location(quad.src1)
        reg1 = self.REG.get_register(quad, compulsory=True)
        self.REG.upd_register_descriptor(reg1, quad.dest)
        if best_location != reg1:
            print("\tmov " + reg1 + ", " + best_location)
        best_location = self.REG.get_best_location(quad.src2)
        if self.REG.check_type_location(best_location) == "number":
            print("\tshr " + reg1 + ', ' + best_location)
        else:
            if best_location != "ecx":
                self.REG.upd_register_descriptor("ecx", quad.src2)
                print("\tmov " + "ecx" + ", " + best_location)
            print("\tshr " + reg1 + ", cl")
        self.REG.free_registers(quad)


    def relational_op(self,quad):
        best_location = self.REG.get_best_location(quad.src1)
        reg1 = self.REG.get_register(quad, compulsory=True)
        self.REG.save_in_memory(reg1)
        op = quad.op.split("_")[-1]
        if best_location != reg1:
            print("\tmov " + reg1 + ", " + best_location)
        reg2 = self.REG.get_best_location(quad.src2)
        print("\t" + "cmp" + ' ' + reg1 + ", " + reg2)
        lbl = pars.EMIT.get_label()
        if(op == "<"):
            print("\tjl " + lbl)
        elif(op == ">"):
            print("\tjg " + lbl)
        elif(op == "=="):
            print("\tje " + lbl)
        elif(op == "!="):
            print("\tjne " + lbl)
        elif(op == "<="):
            print("\tjle " + lbl)
        elif(op == ">="):
            print("\tjge " + lbl)
        print("\tmov " + reg1 + ", 0")
        lbl2 = pars.EMIT.get_label()
        print("\tjmp " + lbl2)
        print(lbl + ":") 
        print("\tmov " + reg1 + ", 1")
        print(lbl2 + ":")
        self.REG.upd_register_descriptor(reg1, quad.dest)
        self.REG.free_registers(quad)


    def relational_float(self,quad):
        best_location = self.REG.get_best_location(quad.src1)
        reg1 = self.REG.get_register(quad, compulsory=True,is_float=True)
        self.REG.save_in_memory(reg1)
        op = quad.op.split("_")[-1]
        if best_location != reg1:
            print("\tmovss " + reg1 + ", " + best_location)
        reg2 = self.REG.get_best_location(quad.src2)
        reg3 = self.REG.get_register(quad,compulsory=True)
        print("\t" + "ucomiss" + ' ' + reg1 + ", " + reg2)
        lbl = pars.EMIT.get_label()
        if(op == "<"):
            print("\tjb " + lbl)
        elif(op == ">"):
            print("\tja " + lbl)
        elif(op == "=="):
            print("\tje " + lbl)
        elif(op == "!="):
            print("\tjne " + lbl)
        elif(op == "<="):
            print("\tjbe " + lbl)
        elif(op == ">="):
            print("\tjae " + lbl)
        print("\tmov " + reg3 + ", 0")
        lbl2 = pars.EMIT.get_label()
        print("\tjmp " + lbl2)
        print(lbl + ":") 
        print("\tmov " + reg3 + ", 1")
        print(lbl2 + ":")
        self.REG.upd_register_descriptor(reg3, quad.dest)
        self.REG.free_registers(quad)


    def real_assign(self,quad):
        if(quad.src2 is not None):
            best_location = self.REG.get_best_location(quad.dest)
            if(best_location not in self.REG.register_descriptor.keys()):
                reg = self.REG.get_register(quad, compulsory = True)
                print("\tmov " + reg + ", " + best_location)
                best_location = reg
            symbols[quad.dest].address_desc_reg.add(best_location)
            self.REG.register_descriptor[best_location].add(quad.dest)

            if(not is_number(quad.src1)):
                loc = self.REG.get_best_location(quad.src1)
                if(loc not in self.REG.register_descriptor.keys()):
                    reg = self.REG.get_register(quad, compulsory = True, exclude_reg = [best_location],is_float = True)
                    self.REG.upd_register_descriptor(reg, quad.src1)
                    print("\tmovss " + reg + ", " + loc)
                    loc = reg
                symbols[quad.src1].address_desc_reg.add(loc)
                self.REG.register_descriptor[loc].add(quad.src1)
                print("\tmovss [" + best_location + "], " + loc)
            else:
                print("\tmovss dword [" + best_location + "], " + quad.src1)

        elif (is_number(quad.src1)):
            best_location = self.REG.get_best_location(quad.dest)
            if (self.REG.check_type_location(best_location) == "register"):
                self.REG.upd_register_descriptor(best_location, quad.dest)
            print("\tmovss " + best_location + ", " + quad.src1)

        else:
            symbols[quad.dest].pointsTo = symbols[quad.src1].pointsTo
            if(symbols[quad.dest].size <= 4):
                best_location = self.REG.get_best_location(quad.src1)
                if (best_location not in self.REG.register_descriptor.keys()):
                    reg =self.REG.get_register(quad, compulsory = True,is_float=True)
                    self.REG.upd_register_descriptor(reg, quad.src1)
                    print("\tmovss " + reg + ", " + best_location)
                    best_location = reg
                symbols[quad.dest].address_desc_reg.add(best_location)
                self.REG.register_descriptor[best_location].add(quad.dest)
                self.REG.del_symbol_reg_exclude(quad.dest, [best_location])
            else:
                loc1 = self.REG.get_location_in_memory(quad.dest, sqb = False)
                loc2 = self.REG.get_location_in_memory(quad.src1, sqb = False)
                reg = self.REG.get_register(quad, compulsory = True,is_float=True)
                for i in range(0, symbols[quad.dest].size, 4):
                    print("\tmovss " + reg + ", dword [" + loc2 + " + " + str(i) + "]" )
                    print("\tmovss dword [" + loc1 + " + " + str(i) + "], " + reg )


    def assign(self, quad):
        if (quad.src2 is not None):
            if(quad.src1 in symbols.keys() and symbols[quad.src1].size > 4):
                loc1 = self.REG.get_best_location(quad.dest)
                loc2 = self.REG.get_location_in_memory(quad.src1, sqb = False)
                if(loc1 not in self.REG.register_descriptor.keys()):
                    reg2 = self.REG.get_register(quad)
                    print("\tmov " + reg2 + ", "+ loc1)
                    loc1 = reg2
                reg = self.REG.get_register(quad, exclude_reg = [loc1])
                for i in range(0, symbols[quad.src1].size, 4):
                    print("\tmov " + reg +  ", dword [" + loc2 + " + " + str(i) + "] " )
                    print("\tmov dword [" + loc1 + " + " + str(i) + "], " + reg)

            else:
                best_location = self.REG.get_best_location(quad.dest)
                if(best_location not in self.REG.register_descriptor.keys()):
                    reg = self.REG.get_register(quad, compulsory = True)
                    print("\tmov " + reg + ", " + best_location)
                    best_location = reg
                symbols[quad.dest].address_desc_reg.add(best_location)
                self.REG.register_descriptor[best_location].add(quad.dest)

                if(not is_number(quad.src1)):
                    loc = self.REG.get_best_location(quad.src1)
                    if(loc not in self.REG.register_descriptor.keys()):
                        reg = self.REG.get_register(quad, compulsory = True, exclude_reg = [best_location])
                        self.REG.upd_register_descriptor(reg, quad.src1)
                        print("\tmov " + reg + ", " + loc)
                        loc = reg
                    if(quad.src1 not in pars.symtable.strings):
                        symbols[quad.src1].address_desc_reg.add(loc)
                        self.REG.register_descriptor[loc].add(quad.src1)

                    print("\tmov [" + best_location + "], " + loc)
                else:
                    print("\tmov dword [" + best_location + "], " + quad.src1)

        elif (is_number(quad.src1)):
            best_location = self.REG.get_best_location(quad.dest)
            if (self.REG.check_type_location(best_location) == "register"):
                self.REG.upd_register_descriptor(best_location, quad.dest)
            print("\tmov " + best_location + ", " + quad.src1)

        else:
            symbols[quad.dest].pointsTo = symbols[quad.src1].pointsTo
            if(symbols[quad.dest].size <= 4):
                best_location = self.REG.get_best_location(quad.src1)
                if (best_location not in self.REG.register_descriptor.keys()):
                    reg = self.REG.get_register(quad, compulsory = True)
                    self.REG.upd_register_descriptor(reg, quad.src1)
                    print("\tmov " + reg + ", " + best_location)
                    best_location = reg

                symbols[quad.dest].address_desc_reg.add(best_location)
                self.REG.register_descriptor[best_location].add(quad.dest)
                self.REG.del_symbol_reg_exclude(quad.dest, [best_location])
            else:
                loc1 = self.REG.get_location_in_memory(quad.dest, sqb = False)
                loc2 = self.REG.get_location_in_memory(quad.src1, sqb = False)
                reg = self.REG.get_register(quad, compulsory = True)

                for i in range(0, symbols[quad.dest].size, 4):
                    print("\tmov " + reg + ", dword [" + loc2 + " + " + str(i) + "]" )
                    print("\tmov dword [" + loc1 + " + " + str(i) + "], " + reg )


    def char_assign(self, quad):
        if(quad.src2 is not None):
            best_location = self.REG.get_best_location(quad.dest)
            if(best_location not in self.REG.register_descriptor.keys()):
                reg = self.REG.get_register(quad, compulsory = True)
                print("\tmov " + reg + ", " + best_location)
                best_location = reg

            symbols[quad.dest].address_desc_reg.add(best_location)
            self.REG.register_descriptor[best_location].add(quad.dest)

            if(is_symbol(quad.src1)):
                loc = self.REG.get_best_location(quad.src1)
                if(loc not in self.REG.register_descriptor.keys()):
                    loc = self.REG.get_best_location(quad.src1, byte = True)
                    reg = self.REG.get_register(quad, compulsory = True, exclude_reg = [best_location, "esi", "edi"])
                    self.REG.upd_register_descriptor(reg, quad.src1)
                    print("\txor " + reg + ", " + reg)
                    print("\tmov " + self.REG.byte__translator[reg] + ", " + loc)
                    loc = reg

                if(quad.src1 not in pars.symtable.strings):
                    symbols[quad.src1].address_desc_reg.add(loc)
                    self.REG.register_descriptor[loc].add(quad.src1)
                print("\tmov byte [" + best_location + "], " + self.REG.byte__translator[loc])
            else:
                print("\tmov byte [" + best_location + "], " + quad.src1)

        else:
            symbols[quad.dest].pointsTo = symbols[quad.src1].pointsTo
            best_location = self.REG.get_best_location(quad.src1)
            if (best_location not in self.REG.register_descriptor.keys()):
                best_location = self.REG.get_best_location(quad.src1, byte = True)
                reg = self.REG.get_register(quad, compulsory = True, exclude_reg = ["esi", "edi"])
                self.REG.upd_register_descriptor(reg, quad.src1)
                print("\txor " + reg + ", " + reg)
                print("\tmov " + self.REG.byte__translator[reg] + ", " + best_location)
                best_location = reg

            symbols[quad.dest].address_desc_reg.add(best_location)
            self.REG.register_descriptor[best_location].add(quad.dest)
            self.REG.del_symbol_reg_exclude(quad.dest, [best_location])


    def int2float(self, quad):
        best_location = self.REG.get_best_location(quad.src1)
        reg = self.REG.get_register(quad, is_float=True)
        self.REG.upd_register_descriptor(reg,quad.dest)
        print("\tcvtsi2ss " + reg + ", " + best_location)


    def float2int(self, quad):
        best_location = self.REG.get_best_location(quad.src1)
        reg = self.REG.get_register(quad)
        self.REG.upd_register_descriptor(reg, quad.dest)
        print("\tcvttss2si " + reg + ", " + best_location)


    def char2int(self, quad):
        reg = self.REG.get_register(quad, exclude_reg = ["esi", "edi"])
        loc = self.REG.get_best_location(quad.src1, byte = True)
        print("\txor " + reg  + ", " + reg)
        print("\tmov " + self.REG.byte__translator[reg] + ", " + loc)
        self.REG.upd_register_descriptor(reg, quad.dest)


    def char2float(self, quad):
        reg = self.REG.get_register(quad,  exclude_reg = ["esi", "edi"])
        loc = self.REG.get_best_location(quad.src1, byte = True)
        print("\txor " + reg + ", " + reg)
        print("\tmov " + self.REG.byte__translator[reg] +", " + loc)
        dest_reg = self.REG.get_register(quad, is_float = True)
        self.REG.upd_register_descriptor(dest_reg, quad.dest)
        print("\tcvtsi2ss " + dest_reg + ", " + reg)


    def int2char(self, quad):
        reg1 = self.REG.get_register(quad,  exclude_reg = ["esi", "edi"])
        reg2 = self.REG.get_register(quad, exclude_reg = [reg1, "esi", "edi"])
        print("\tmov " + reg1 +", " + self.REG.get_best_location(quad.src1))
        self.REG.upd_register_descriptor(reg2, quad.dest)
        print("\txor " + reg2 + ", " + reg2)
        print("\tmov " + self.REG.byte__translator[reg2] + ", " + self.REG.byte__translator[reg1])


    def float2char(self, quad):
        reg = self.REG.get_register(quad, is_float=True)
        print("\tmovss " + reg + ", " + self.REG.get_best_location(quad.src1))
        reg1 = self.REG.get_register(quad)
        print("\tcvttss2si " + reg1  + ", " + reg)
        reg2 = self.REG.get_register(quad, exclude_reg = [reg1, "esi", "edi"])
        print("\txor " + reg2 + ", " + reg2)
        print("\tmov " + self.REG.byte__translator[reg2] + ", " + self.REG.byte__translator[reg1])
        self.REG.upd_register_descriptor(reg2, quad.dest)


    def deref(self, quad):
        if(len(symbols[quad.src1].pointsTo)> 0):
            self.REG.del_symbol_reg_exclude(symbols[quad.src1].pointsTo)
        sym = symbols[quad.src1].pointsTo
        if(len(sym) > 0):
            symbols[quad.dest].pointsTo = symbols[sym].pointsTo
        else:
            symbols[quad.dest].pointsTo = ''

        best_location = self.REG.get_best_location(quad.src1)
        if (self.REG.check_type_location(best_location) in ["memory", "data", "number"]):
            reg = self.REG.get_register(quad, compulsory = True)
            self.REG.upd_register_descriptor(reg, quad.src1)
            print("\tmov " + reg + ", " + best_location)
            best_location = reg

        if(symbols[quad.dest].size > 4):
            loc1 = self.REG.get_location_in_memory(quad.dest, sqb = False)
            loc2 = best_location
            reg = self.REG.get_register(quad, compulsory = True, exclude_reg = [loc2])

            for i in range(0, symbols[quad.dest].size, 4):
                print("\tmov " + reg + ", dword [" + loc2 + " + " + str(i) + "]" )
                print("\tmov dword [" + loc1 + " + " + str(i) + "], " + reg )
            return

        reg2 = self.REG.get_register(quad, compulsory  = True, exclude_reg = [best_location])
        print("\tmov " + reg2 + ", [" + best_location + "] ")
        dest_loc = self.REG.get_best_location(quad.dest)
        if(dest_loc in self.REG.register_descriptor.keys()):
            self.REG.upd_register_descriptor(dest_loc, quad.dest)
        print("\tmov " + dest_loc + ", " + reg2 )


    def param(self, quad):
        global count1
        global param_off
        if(count1 == 0):
            self.REG.save_caller_status()
        count1 += 1
        param_off += 4
        if(is_symbol(quad.src1) and symbols[quad.src1].size > 4):
            param_off += symbols[quad.src1].size - 4
            loc = self.REG.get_location_in_memory(quad.src1, sqb = False)
            for i in range(symbols[quad.src1].size - 4, -1, -4):
                print("\tpush dword [" + loc + "+" + str(i) + "]")
            return
        location = self.REG.get_best_location(quad.src1)
        if((is_symbol(quad.src1) and pars.symtable.global_symbol_table[quad.src1]['type'] == 'float' and quad.dest == 'printf') or quad.dest in ['pow', 'fabs', 'sin', 'cos', 'sqrt']):
            if(location.startswith('xmm')):
                self.REG.save_in_memory(location)
            print("\tsub\tesp, 8")
            reg1 = self.REG.get_register(quad,compulsory=True)
            if(is_symbol(quad.src1)):
                print("\tlea " + reg1 + ", " + self.REG.get_location_in_memory(quad.src1))
            else:
                print("\tmov " + reg1 + ", " + pars.symtable.float_reverse_map[quad.src1])
            print("\tfld dword [" + reg1 + "]")
            print("\tfstp qword [esp]")
        else:  
            if(location.startswith('xmm')):
                self.REG.del_symbol_reg_exclude(quad.src1)
            print("\tpush " + self.REG.get_best_location(quad.src1))

    def function_call(self, quad):
        global count1, param_off
        self.REG.save_caller_status()
        if(len(quad.src2) and symbols[quad.src2].size > 4):
            print("\tmov ecx, ebp")
            print("\tsub ecx, esp")
            print("\tadd ecx, " + str(symbols[quad.src2].address_desc_mem[-1]+ 12))
            print("\tpush ecx")
            param_off += 4
            count1 += 1
        print("\tcall " + quad.src1)
        if(quad.src1 in ['pow', 'fabs', 'sin', 'cos', 'sqrt']):
            self.REG.del_symbol_reg_exclude(quad.src2)
            print("\tfstp dword " + self.REG.get_location_in_memory(quad.src2))
        elif(len(quad.src2) and symbols[quad.src2].size <= 4):
            print("\tmov " + self.REG.get_best_location(quad.src2) + ", eax")
        print("\tadd esp, " + str(param_off))
        count1 = 0
        param_off = 0


    def function_end(self, quad):
        for var in pars.symtable.local_vars[quad.dest]:
            symbols[var].address_desc_mem.pop()
        for key in self.REG.register_descriptor.keys():
            self.REG.register_descriptor[key].clear()

    def alloc_stack(self,quad):
        if(quad.src1 == 'main_0'):
            print("_main:")
        else:
            print(quad.src1 + ":")
        offset = 0
        for var in pars.symtable.local_vars[quad.src1]:
            if var not in pars.symtable.func_arguments[quad.src1]:
                offset += max(pars.symtable.data_type_size(pars.symtable.global_symbol_table[var]['type']), 4)
                symbols[var].address_desc_mem.append(-offset) 
        print("\tpush ebp")
        print("\tmov ebp, esp")
        print("\tsub esp, " + str(offset))

        for var in pars.symtable.local_vars[quad.src1]:
            if var not in pars.symtable.func_arguments[quad.src1]:
                if(symbols[var].isArray):
                    reg = self.REG.get_register(quad, compulsory = True)
                    print("\tmov " + reg + ", " + str(symbols[var].length))
                    print("\timul " + reg + ", " + str(max(4, pars.symtable.data_type_size(pars.symtable.global_symbol_table[var]['type']))))
                    print("\tpush " + reg)
                    print("\tcall malloc")
                    print("\tadd esp, 4")
                    print("\tmov " + self.REG.get_location_in_memory(var) + ", eax")

        counter = 0
        if(pars.symtable.data_type_size(pars.symtable.table[0][quad.src1]['type']) > 4):
            counter += 4
        for var in pars.symtable.func_arguments[quad.src1]:
            symbols[var].address_desc_mem.append(counter + 8)
            if(symbols[var].isArray):
                counter += 4
            else:
                counter += symbols[var].size


    def function_return(self, quad):
        self.REG.save_caller_status()
        if(quad.src1):
            if(is_symbol(quad.src1) and symbols[quad.src1].size > 4):
                loc2 = self.REG.get_location_in_memory(quad.src1, sqb = False)
                print("\tmov eax, dword [ebp + 8]")
                loc1 = "ebp + eax"
                reg = self.REG.get_register(quad, exclude_reg = ["eax"])

                for i in range(0, symbols[quad.src1].size, 4):
                    print("\tmov " + reg + ", dword [" + loc2 + " + " + str(i) + "]" )
                    print("\tmov dword [" + loc1 + " + " + str(i) + "], " + reg )
            else:
                location = self.REG.get_best_location(quad.src1)
                self.REG.save_in_memory("eax")
                if(location != "eax"):
                    print("\tmov eax, " + str(location))
        print("\tmov esp, ebp")
        print("\tpop ebp")
        print("\tret")

    def ifgoto(self,quad):
        if pars.symtable.global_symbol_table[quad.src1]['type'] == 'int':
            best_location = self.REG.get_best_location(quad.src1)
            reg1 = self.REG.get_register(quad, compulsory=True)
            self.REG.save_in_memory(reg1)
            if best_location != reg1:
                print("\tmov " + reg1 + ", " + best_location)
            print("\tcmp " + reg1 + ", 0")
            self.REG.save_caller_status()
            if(quad.src2.startswith("n")):
                print("\tjne " + quad.dest)
            else:
                print("\tje " + quad.dest)
        elif pars.symtable.global_symbol_table[quad.src1]['type'] == 'char':
            best_location = self.REG.get_best_location(quad.src1, byte=True)
            reg1 = self.REG.byte__translator[self.REG.get_register(quad, compulsory=True)]
            if best_location != reg1:
                print("\tmov " + reg1 + ", " + best_location)
            print("\tcmp " + reg1 + ", 0")
            self.REG.save_caller_status()
            if(quad.src2.startswith("n")):
                print("\tjne " + quad.dest)
            else:
                print("\tje " + quad.dest)
        else:
            best_location = self.REG.get_best_location(quad.src1)
            reg1 = self.REG.get_register(quad, compulsory=True, is_float=True)
            if best_location != reg1:
                print("\tmovss " + reg1 + ", " + best_location)
            print("\tucomiss " + reg1 + ", " + self.REG.get_location_in_memory(pars.symtable.float_reverse_map['0.0']))
            self.REG.save_caller_status()
            if(quad.src2.startswith("n")):
                print("\tjne " + quad.dest)
            else:
                print("\tje " + quad.dest)


    def goto(self,quad):
        self.REG.save_caller_status()
        print("\tjmp " + quad.dest)

    def label(self,quad):
        self.REG.save_caller_status()
        print(quad.src1 + ":")

    def addr(self, quad):
        reg = self.REG.get_register(quad)
        if(symbols[quad.src1].isArray):
            if(reg != self.REG.get_best_location(quad.src1)):
                print("\tmov " + reg + ", " + self.REG.get_best_location(quad.src1))
        else:
            if(len(symbols[quad.src1].address_desc_reg)):
                self.REG.del_symbol_reg_exclude(quad.src1)
            print("\tlea " + reg + ", " + self.REG.get_location_in_memory(quad.src1))
        symbols[quad.dest].pointsTo = quad.src1
        self.REG.register_descriptor[reg].add(quad.dest)
        symbols[quad.dest].address_desc_reg.add(reg)

    def generate_assembly_code(self, quad):
        if(quad.op == "func"):
            self.alloc_stack(quad)
        elif(quad.op == "param"):
            self.param(quad)
        elif(quad.op == "call"):
            self.function_call(quad)
        elif(quad.op == "int2float"):
            self.int2float(quad)
        elif(quad.op == "float2int"):
            self.float2int(quad)
        elif(quad.op == "char2int"):
            self.char2int(quad)
        elif(quad.op == "int2char"):
            self.int2char(quad)
        elif(quad.op == "char2float"):
            self.char2float(quad)
        elif(quad.op == "float2char"):
            self.float2char(quad)
        elif(quad.op == "float_="):
            self.real_assign(quad)
        elif(quad.op == "char_="):
            self.char_assign(quad)
        elif(quad.op.endswith("_=")):
            self.assign(quad)
        elif(quad.op == "ret"):
            self.function_return(quad)
        elif(quad.op == "float_+"):
            self.real_add(quad)
        elif(quad.op.endswith("+")):
            self.add(quad)
        elif(quad.op == "float_-"):
            self.real_sub(quad)
        elif(quad.op == "float_*"):
            self.real_mul(quad)
        elif(quad.op == "float_/"):
            self.real_div(quad)
        elif(quad.op.endswith("-")):
            self.sub(quad)
        elif(quad.op.endswith("*")):
            self.mul(quad)
        elif(quad.op.endswith("/")):
            self.div(quad)
        elif(quad.op.endswith("%")):
            self.mod(quad)
        elif(quad.op.endswith("inc")):
            self.increment(quad)
        elif(quad.op.endswith("dec")):
            self.decrement(quad)
        elif(quad.op.endswith("bitwisenot")):
            self.assign(quad)
            self.bitwisenot(quad)
        elif(quad.op == "float_uminus"):
            self.assign(quad)
            self.real_uminus(quad)
        elif(quad.op.endswith("uminus")):
            self.assign(quad)
            self.uminus(quad)
        elif(quad.op.split("_")[-1] in ["<",">","<=",">=","==","!="]
 and quad.op.startswith("int")):
            self.relational_op(quad)
        elif(quad.op.split("_")[-1] in ["<",">","<=",">=","==","!="]
 and quad.op.startswith("float")):
            self.relational_float(quad)
        elif(quad.op == "ifgoto"):
            self.ifgoto(quad)
        elif(quad.op == "label"):
            self.label(quad)
        elif(quad.op == "goto"):
            self.goto(quad)
        elif(quad.op == "funcEnd"):
            self.function_end(quad)
        elif(quad.op.endswith("<<")):
            self.lshift(quad)
        elif(quad.op.endswith(">>")):
            self.rshift(quad)
        elif(quad.op == "addr"):
            self.addr(quad)
        elif(quad.op == "deref"):
            self.deref(quad)
        elif(quad.op.endswith("&")):
            self.band(quad)
        elif(quad.op.endswith("|")):
            self.bor(quad)
        elif(quad.op.endswith("^")):
            self.bxor(quad)


def runmain():
    # quad_op = [quad.op for quad in scope_all_instr_arr]
    # sys.stdout = open('quad_op2.txt', 'w')
    # print(quad_op)
    sys.stdout = open('./TAC.txt', 'w')
    find_basic_blocks()
    register_alloc_optim()
    for key in pars.symtable.global_symbol_table.keys():
        if key not in symbols.keys():
            if('array' in pars.symtable.global_symbol_table[key].keys()):
                len = pars.symtable.global_symbol_table[key]['size']//pars.symtable.data_type_size(pars.symtable.global_symbol_table[key]['type'])
                symbols[key] = symbol_info(isArray = True, length = len)
            elif(pars.symtable.global_symbol_table[key]['type'].startswith('struct') or pars.symtable.global_symbol_table[key]['type'].startswith('union')):
                symbols[key] = symbol_info(isStruct = True, size = pars.symtable.data_type_size(pars.symtable.global_symbol_table[key]['type']))
            else:
                symbols[key] = symbol_info(size = pars.symtable.data_type_size(pars.symtable.global_symbol_table[key]['type']))
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    sys.stdout = open('out.asm', 'w')
    codegen = CodeGen()
    codegen.gen_top_headers()
    __temp = [i.op for i in scope_all_instr_arr]
    for quad in scope_all_instr_arr:
        codegen.generate_assembly_code(quad)
    codegen.data_section()
    sys.stdout.close()