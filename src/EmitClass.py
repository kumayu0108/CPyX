from misc import new_var, int_or_real

class emit_class():
    def __init__(self, symtable):
        self.jump_mark = 0
        self.top_label = {}
        self.emit_array = []
        self.symtable = symtable
        self.nextstat = 0
        self.label_count = 0
        self.global_emit_array = []

    def get_new_tmp(self, dtype, value=0, scope = -1):
        if(scope== -1):
            scope = self.symtable.scope
        tmp_name = new_var()

        self.symtable.table[scope][tmp_name] = {}
        self.symtable.table[scope][tmp_name]['type'] = dtype
        self.symtable.table[scope][tmp_name]['size'] = self.symtable.data_type_size(dtype)
        self.symtable.table[scope][tmp_name]['value'] = value
        return tmp_name

    def get_label(self):
        s = "__l" + str(self.label_count)
        self.label_count += 1
        return s
    def emit(self, op, src1, src2, dst):
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
        if(self.symtable.scope == 0 and not op.startswith('func') and not op.startswith('ret')):
            self.global_emit_array.append([str(op), str(src1), str(src2), str(dst)])
        else:
            self.emit_array.append([str(op), str(src1), str(src2), str(dst)])
        self.nextstat += 1        
    

    def handle_binary_emit(self, p0, p1, p2, p3):
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
                self.emit(int_or_real('char') + '_' + int_or_real('int') + '_' + '=', p1.place, '', tmp1)
                tmp2 = self.get_new_tmp('int')
                self.emit(int_or_real('char') + '_' + int_or_real('int') + '_' + '=', p3.place, '', tmp2)
                tmp3 = self.get_new_tmp('int')
                self.emit( 'int_' + operator, tmp1, tmp2, tmp3)
                self.emit(int_or_real('int') + '_' + int_or_real('char') + '_' + '=', tmp3, '', p0.place) 
            else: 
                self.emit(int_or_real(p1.type) + '_' + operator, p1.place, p3.place, p0.place)
        return p0, p1, p2, p3

    def handle_binary_emit_sub_add(self, p0, p1, p2, p3):
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
                    data_type = p1.type
                    if data_type.endswith('*'):
                        data_type = data_type[:-2]
                    self.emit('int_*',p3.place,self.symtable.data_type_size(data_type),tmp)
                    self.emit('int_' + operator, p1.place, tmp, p0.place)
                else:
                    if(p1.type.startswith('float')):
                        print("Compilation error at line " + str(p1.line_no) + ", cannot add float to pointer variable")
                    data_type = p3.type
                    if data_type.endswith('*'):
                        data_type = data_type[:-2]
                    self.emit('int_*',p1.place,self.symtable.data_type_size(data_type),tmp)
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
