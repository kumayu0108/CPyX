import pydot
import ply.yacc as yacc
import lexer
import sys
from lexer import lexer
counter = 0

def AST(p):
    global counter
    calling_func_name = sys._getframe(1).f_code.co_name
    calling_rule_name = calling_func_name[2:]

    counter = counter + 1
    tmp = counter
    if(len(p) == 2):
        return p[1]
    with open('graph.dot', 'a') as file:
        file.write("\n" + str(counter) + "[label=\"" + calling_rule_name.replace('"',"") + "\"]")
        for i in range(1, len(p)):
            if(type(p[i]) is tuple):
                file.write("\n" + str(tmp) + " -> " + str(p[i][1]))
            else :
                counter = counter + 1
                p[i] = (p[i], counter)
                file.write("\n" + str(counter) + "[label=\"" + str(p[i][0]).replace('"',"") + "\"]")
                file.write("\n" + str(tmp) + " -> " + str(p[i][1]))
    
    return (calling_rule_name,tmp)
    

class Parser():
    tokens = lexer().tokens
    lex = lexer()
    lex.build()

    def build(self):
        self.parser = yacc.yacc(module=self, start='translation_unit' ,debug=False)

    def p_primary_expression(self,p):
        '''
        primary_expression : ID
                        | INT_NUM
                        | FLOAT_NUM
                        | CHARACTER
                        | STRING
                        | LEFT_PAR expression RIGHT_PAR
        '''
        p[0] = AST(p)
        

    def p_postfix_expression(self,p):
        '''
        postfix_expression : primary_expression
                        | postfix_expression INC
                        | postfix_expression DEC
                        | postfix_expression DOT ID
                        | postfix_expression LEFT_PAR RIGHT_PAR
                        | postfix_expression PTR_OP ID
                        | postfix_expression LEFT_SQ_BR expression RIGHT_SQ_BR
                        | postfix_expression LEFT_PAR argument_expression_list RIGHT_PAR
        '''
        p[0] = AST(p)

        
        
    def p_argument_expression_list(self,p):
        '''
        argument_expression_list : assignment_expression
                                | argument_expression_list COMMA assignment_expression
        '''
        p[0] = AST(p)
        
    def p_unary_expression(self,p):
        '''
        unary_expression : postfix_expression
                        | INC unary_expression
                        | DEC unary_expression
                        | SIZEOF unary_expression
                        | unary_operator cast_expression
                        | SIZEOF LEFT_PAR type_name RIGHT_PAR
        '''
        p[0] = AST(p)
        
    def p_cast_expression(self,p):
        '''
        cast_expression : unary_expression
                        | LEFT_PAR type_name RIGHT_PAR cast_expression
        '''
        p[0] = AST(p)

    def p_unary_operator(self,p):
        '''
        unary_operator : BIT_AND
                    | MUL
                    | ADD
                    | SUB
                    | NOT
                    | NEGATE
        '''
        p[0] = AST(p)

    def p_additive_expression(self,p):
        '''
        additive_expression : multiplicative_expression
                            | additive_expression ADD multiplicative_expression
                            | additive_expression SUB multiplicative_expression
        '''
        p[0] = AST(p)

    def p_mulitplicative_expression(self,p):
        '''
        multiplicative_expression : cast_expression
                                | multiplicative_expression MUL cast_expression
                                | multiplicative_expression DIV cast_expression
                                | multiplicative_expression MODULO cast_expression
        '''
        p[0] = AST(p)


    def p_shift_expression(self,p):
        '''
        shift_expression : additive_expression
                        | shift_expression LEFT_SHIFT additive_expression
                        | shift_expression RIGHT_SHIFT additive_expression
        '''
        p[0] = AST(p)
        

    def p_relational_expression(self,p):
        '''
        relational_expression : shift_expression
                            | relational_expression LESS shift_expression
                            | relational_expression GREATER shift_expression
                            | relational_expression LEQ shift_expression
                            | relational_expression GEQ shift_expression
        '''
        p[0] = AST(p)

    def p_equality_expression(self,p):
        '''
        equality_expression : relational_expression
                            | equality_expression EQ_CHECK relational_expression
                            | equality_expression NOT_EQ relational_expression
        '''
        p[0] = AST(p)

    def p_and_expression(self,p):
        '''
        and_expression : equality_expression
                    | and_expression BIT_AND equality_expression
        '''
        p[0] = AST(p)
    

    def p_exclusive_or_expression(self,p):
        '''
        exclusive_or_expression : and_expression
                                | exclusive_or_expression XOR and_expression
        '''
        p[0] = AST(p)
        

    def p_inclusive_or_expression(self,p):
        '''
        inclusive_or_expression : exclusive_or_expression
                                | inclusive_or_expression BIT_OR exclusive_or_expression
        '''
        p[0] = AST(p)
    

    def p_logical_and_expression(self,p):
        '''
        logical_and_expression : inclusive_or_expression
                            | logical_and_expression AND inclusive_or_expression
        '''
        p[0] = AST(p)
        
        

    def p_logical_or_expression(self,p):
        '''
        logical_or_expression : logical_and_expression
                            | logical_or_expression OR logical_and_expression
        '''
        p[0] = AST(p)


    def p_conditional_expression(self,p):
        '''
        conditional_expression : logical_or_expression
                            | logical_or_expression TERNARY expression COLON conditional_expression
        '''
        p[0] = AST(p)

    def p_assignment_expression(self,p):
        '''
        assignment_expression : conditional_expression
                            | unary_expression assignment_operator assignment_expression
        '''
        p[0] = AST(p)
        

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
        p[0] = AST(p)

    def p_expression(self,p):
        '''
        expression : assignment_expression
                | expression COMMA assignment_expression
        '''
        p[0] = AST(p)

    def p_constant_expression(self,p):
        '''
        constant_expression : conditional_expression
        '''
        p[0] = AST(p)

    def p_declaration(self,p):
        '''
        declaration : declaration_specifiers SEMI_COLON
                    | declaration_specifiers init_declarator_list SEMI_COLON
        '''
        p[0] = AST(p)
    

    def p_declaration_specifiers(self,p):
        '''
        declaration_specifiers : storage_class_specifier
                            | storage_class_specifier declaration_specifiers
                            | type_specifier
                            | type_specifier declaration_specifiers
                            | type_qualifier
                            | type_qualifier declaration_specifiers
        '''
        p[0] = AST(p)

    

    def p_init_declarator_list(self,p):
        '''
        init_declarator_list : init_declarator
                            | init_declarator_list COMMA init_declarator
        '''
        p[0] = AST(p)
    

    def p_init_declarator(self,p):
        '''
        init_declarator : declarator
                        | declarator ASSIGNMENT initializer
        '''
        p[0] = AST(p)
    

    def p_storage_class_specifier(self,p):
        '''
        storage_class_specifier : AUTO
        '''
        p[0] = AST(p)


    def p_type_specifier(self,p):
        '''
        type_specifier : VOID
                    | CHAR
                    | INT
                    | FLOAT
                    | BOOL
                    | struct_specifier
        '''
        p[0] = AST(p)

    def p_struct_specifier(self,p):
        '''
        struct_specifier : struct ID LEFT_CUR_BR struct_declaration_list RIGHT_CUR_BR
                                | struct LEFT_CUR_BR struct_declaration_list RIGHT_CUR_BR
                                | struct ID
        '''
        p[0] = AST(p)
        

    def p_struct(self,p):
        '''
        struct : STRUCT
        '''
        p[0] = AST(p)

    def p_struct_declaration_list(self,p):
        '''
        struct_declaration_list : struct_declaration
                                | struct_declaration_list struct_declaration
        '''
        p[0] = AST(p)


    def p_struct_declaration(self,p):
        '''
        struct_declaration : specifier_qualifier_list struct_declarator_list SEMI_COLON
        '''
        p[0] = AST(p)
        

    def p_specifier_qualifier_list(self,p):
        '''
        specifier_qualifier_list : type_specifier specifier_qualifier_list
                                | type_specifier
                                | type_qualifier specifier_qualifier_list
                                | type_qualifier
        '''
        p[0] = AST(p)

    def p_struct_declarator_list(self,p):
        '''
        struct_declarator_list : struct_declarator
                            | struct_declarator_list COMMA struct_declarator
        '''
        p[0] = AST(p)
        

    def p_struct_declarator(self,p):
        '''
        struct_declarator : declarator
                        | COLON constant_expression
                        | declarator COLON constant_expression
        '''
        p[0] = AST(p)


    def p_type_qualifier(self,p):
        '''
        type_qualifier : CONST
        '''
        p[0] = AST(p)

 

    def p_declarator(self,p):
        '''
        declarator : pointer direct_declarator
                | direct_declarator
        '''
        p[0] = AST(p)
        

    def p_direct_declarator(self,p):
        '''
        direct_declarator : ID
                        | LEFT_PAR declarator RIGHT_PAR
                        | direct_declarator LEFT_SQ_BR RIGHT_SQ_BR
                        | direct_declarator LEFT_PAR RIGHT_PAR
                        | direct_declarator LEFT_SQ_BR constant_expression RIGHT_SQ_BR
                        | direct_declarator LEFT_PAR parameter_type_list RIGHT_PAR
                        | direct_declarator LEFT_PAR identifier_list RIGHT_PAR
        '''
        p[0] = AST(p)
        
    def p_pointer(self,p):
        '''
        pointer : MUL
                | MUL type_qualifier_list
                | MUL pointer
                | MUL type_qualifier_list pointer
        '''
        p[0] = AST(p)

    def p_type_qualifier_list(self,p):
        '''
        type_qualifier_list : type_qualifier
                            | type_qualifier_list type_qualifier
        '''
        p[0] = AST(p)

    def p_parameter_type_list(self,p):
        '''
        parameter_type_list : parameter_list
        '''
        p[0] = AST(p)

    def p_parameter_list(self,p):
        '''
        parameter_list : parameter_declaration
                    | parameter_list COMMA parameter_declaration
        '''
        p[0] = AST(p)
        
    def p_parameter_declaration(self,p):
        '''
        parameter_declaration : declaration_specifiers declarator
                            | declaration_specifiers abstract_declarator
                            | declaration_specifiers
        '''
        p[0] = AST(p)
        
    def p_identifier_list(self,p):
        '''
        identifier_list : ID
                        | identifier_list COMMA ID
        '''   
        p[0] = AST(p)

    def p_type_name(self,p):
        '''
        type_name : specifier_qualifier_list
                | specifier_qualifier_list abstract_declarator
        '''
        p[0] = AST(p)

    def p_abstract_declarator(self,p):
        '''
        abstract_declarator : pointer
                            | direct_abstract_declarator
                            | pointer direct_abstract_declarator
        '''
        p[0] = AST(p)
        

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
        p[0] = AST(p)

    def p_initializer(self,p):
        '''
        initializer : assignment_expression
                    | LEFT_CUR_BR initializer_list RIGHT_CUR_BR
                    | LEFT_CUR_BR initializer_list COMMA RIGHT_CUR_BR
        '''
        p[0] = AST(p)

    def p_initializer_list(self,p):
        '''
        initializer_list : initializer
                        | initializer_list COMMA initializer
        '''
        p[0] = AST(p)

    def p_statement(self,p):
        '''
        statement : labeled_statement
                | compound_statement
                | expression_statement
                | selection_statement
                | iteration_statement
                | jump_statement
        '''
        p[0] = AST(p)

    def p_labeled_statement(self,p):
        '''
        labeled_statement : ID COLON statement
        '''
        p[0] = AST(p) 

    def p_compound_statement(self,p):
        '''
        compound_statement : LEFT_CUR_BR RIGHT_CUR_BR
                        | LEFT_CUR_BR block_item_list RIGHT_CUR_BR
        '''
        p[0] = AST(p)
        
    def p_block_item_list(self,p):
        '''
        block_item_list : block_item
                        | block_item_list block_item
        '''
        p[0] = AST(p)

    def p_block_item(self,p):
        '''
        block_item : declaration
                    | statement
        '''
        p[0] = AST(p)

    def p_expression_statement(self,p):
        '''
        expression_statement : SEMI_COLON
                            | expression SEMI_COLON
        '''
        p[0] = AST(p)

    def p_selection_statement(self,p):
        '''
        selection_statement : IF LEFT_PAR expression RIGHT_PAR statement
                            | IF LEFT_PAR expression RIGHT_PAR statement ELSE statement
        '''
        p[0] = AST(p)
    def p_iteration_statement(self,p):
        '''
        iteration_statement : WHILE LEFT_PAR expression RIGHT_PAR statement
                            | FOR LEFT_PAR expression_statement expression_statement RIGHT_PAR statement
                            | FOR LEFT_PAR expression_statement expression_statement expression RIGHT_PAR statement
                            | FOR LEFT_PAR declaration expression_statement RIGHT_PAR statement
                            | FOR LEFT_PAR declaration expression_statement expression RIGHT_PAR statement
        '''
        p[0] = AST(p)

    def p_translation_unit(self,p):
        '''
        translation_unit : external_declaration
                        | translation_unit external_declaration
        '''
        p[0] = AST(p)

    def p_external_declaration(self,p):
        '''
        external_declaration : function_definition
                            | declaration
        '''
        p[0] = AST(p)

    def p_function_definition(self,p):
        '''
        function_definition : declaration_specifiers declarator declaration_list compound_statement
                            | declaration_specifiers declarator compound_statement
                            | declarator declaration_list compound_statement
                            | declarator compound_statement
        '''
        p[0] = AST(p)
    
    def p_declaration_list(self,p):
        '''
        declaration_list : declaration
                        | declaration_list declaration
        '''
        p[0] = AST(p)
    
    def p_jump_statement(self,p):
        '''
        jump_statement : RETURN SEMI_COLON
                        | RETURN expression SEMI_COLON
        '''
        p[0] = AST(p)

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
        print(f"Parsing file {filename}\n")
        with open(filename, 'r') as f:
            content = f.read()
            pars.lex.lexer.input(content)

            open('graph.dot','w').write("digraph G {")
            pars.parser.parse(content, debug=False)

            open('graph.dot','a').write("\n}")
            graphs = pydot.graph_from_dot_file('graph.dot')
            graph = graphs[0]
            name = f.name[f.name.rfind('/')+1:]
            graph.write_png(f'./plots/pydot_graph_{name}.png')
            f.close()
