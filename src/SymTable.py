from multiprocessing.spawn import import_main_path
from misc import conv

class SymTable():
    def __init__(self):
        self.table = [{}]
        self.global_symbol_table = {}
        self.prevScope = {}
        self.prevScope[0] = 0
        self.scope = 0
        self.next = 1
        self.float_reverse_map={}
        self.float_constant_values = []
        self.loopingDepth=0
        self.switchDepth = 0
        self.function_overloaded_map={}
        self.functionScope = {}
        self.scope_to_function = {}
        self.strings = {}
        self.scope_to_function[0] = 'global'
        self.local_vars = {}
        self.local_vars['global'] = []
        self.func_arguments = {}
        self.ignore_function_ahead = []
        self.actrec = []
        self.funcReturntype = ''
    
    def isPresent(self, id):
        tmp = self.scope
        while 1:
            if id in self.table[tmp].keys():
                return (self.table[tmp][id], tmp)
            tmp = self.prevScope[tmp]
            if self.prevScope[tmp] == tmp:
                if id in self.table[tmp].keys():
                    return (self.table[tmp][id], tmp)
                break
        return None

    def data_type_size(self, __type__):
        __type__ = conv(__type__)
        if (__type__ == '' or __type__ == 'virtual_func'):
            return 0

        type_size = {'char':1, 
                    'int':4,
                    'float':4,
                    'bool':1,
                    'void':0, }

        if(__type__.endswith('*')):
            return 4
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
            val = ((self.table[tmp][__type__]['size'] + 3) // 4)*4
            return val

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
                    'float':2,
                    'double':3}
        to_str = {}
        to_str[0] = 'char'
        to_str[1] = 'int'
        to_str[2] = 'float'
        to_str[3] = 'double'
        type_1 =  type_1.split()[-1]
        type_2 =  type_2.split()[-1]
        if type_1 not in to_num or type_2 not in to_num:
            return str(-1)
        num_type_1 = to_num[type_1]
        num_type_2 = to_num[type_2]
        return to_str[max(num_type_1 , num_type_2)]
    
    def update_local_vars(self):
        for i in range (self.next):
            if(len(self.table[i]) > 0 and i in self.scope_to_function.keys()):
                temp_list = {}
                for key in self.table[i].keys():
                    if(not (key.startswith('struct'))):
                        temp_list[key] = self.table[i][key]

                    if(not ((key.startswith('struct')) or ('is_func' in self.table[i][key].keys()) or (key.startswith('__')) )):
                        newkey = key + "_" + str(i)
                        self.global_symbol_table[key + "_" + str(i)] = self.table[i][key]
                        if(newkey not in self.local_vars[self.scope_to_function[i]]):
                            self.local_vars[self.scope_to_function[i]].append(newkey)
                        if i > 0:
                            if key in self.func_arguments[self.scope_to_function[i]]:
                                self.func_arguments[self.scope_to_function[i]].append(newkey)
                                self.func_arguments[self.scope_to_function[i]].remove(key)

                    elif key.startswith('__'):
                        if(key not in self.strings.keys()):
                            self.local_vars[self.scope_to_function[i]].append(key)
                        self.global_symbol_table[key] = self.table[i][key]