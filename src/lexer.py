import sys
import ply.lex as lex
from ply.lex import TOKEN

class lexer():
    
    reserved = {
        'auto'      : 'AUTO',
        'int'       : 'INT',
        'char'      : 'CHAR',
        'float'     : 'FLOAT',
        'bool'      : 'BOOL',
        'struct'    : 'STRUCT',
        'const'     : 'CONST', 
        'for'       : 'FOR',
        'while'     : 'WHILE',
        'if'        : 'IF',
        'else'      : 'ELSE',
        # 'return'    : 'RETURN',
        'void'      : 'VOID',
        'sizeof'    : 'SIZEOF',
        # 'main'      : 'MAIN',
        'printf'    : 'PRINTF',
        'scanf'     : 'SCANF',
        'malloc'    : 'MALLOC',
        'calloc'    : 'CALLOC',
        'free'      : 'FREE',
        'true'      : 'TRUE',
        'false'     : 'FALSE'
    }

    tokens = list(reserved.values()) + [
            'ID',
            'INT_NUM',
            'FLOAT_NUM',
            'CHARACTER',
            'STRING',
            'ADD',          # "+"
            'SUB',          # "-"
            'MUL',          # "*"
            'DIV',          # "/"
            'XOR',          # "^"
            'BIT_AND',      # "&"
            'BIT_OR',       # "|"
            'AND',          # "&&"
            'OR',           # "||" 

            'MODULO',       # "%"
            'ASSIGNMENT',   # "="
            'NOT',          # "~"
            'NEGATE',       # "!"
            'BACKSLASH',    # "\"          \\EXTRA
            

            'LEFT_SHIFT',   # "<<"
            'RIGHT_SHIFT',  # ">>"
            'LEFT_PAR',     # "("
            'RIGHT_PAR',    # ")"
            'LEFT_CUR_BR',  # "{"
            'RIGHT_CUR_BR', # "}"
            'LEFT_SQ_BR',   # "["     
            'RIGHT_SQ_BR',  # "]"     
            'SEMI_COLON',   # ";"  
            'COLON',        # ":" 
            'DOT',          # "."
            'COMMA',        # ","     
            'PTR_OP',       # "->"    

            'INC',          # "++"    
            'DEC',          # "--"   
            
            #SHORTHANDS 
            'SHORT_ADD',   # "+="
            'SHORT_SUB',   # "-="
            'SHORT_MUL',   # "*="
            'SHORT_DIV',   # "/="
            'SHORT_XOR',   # "^="
            'SHORT_AND',   # "&="
            'SHORT_OR',    # "|="
            'SHORT_MOD',   # "%="
            'SHORT_LEFT_SHIFT',    # "<<="
            'SHORT_RIGHT_SHIFT',   # ">>="
            


            'NOT_EQ',       # "!="
            'EQ_CHECK',     # "=="
            'GEQ',          # ">="
            'LEQ',          # "<="
            'GREATER',      # ">"    
            'LESS',         # "<"     
            'TERNARY'       # "?"     //

            ]
    
    # def __init__(self):

    def build(self, **kwargs):
        self.lexer = lex.lex(self)
    
    num = r'([0-9])'
    alph = r'([a-zA-Z_])'
    exp = r'([Ee][+-]?' + num + r'+)'
    exponent = r'(' + num + r'+' + exp + r')'
    dec = r'(' + num + r'*[.]' + num + r'+' + exp + r'?)'
    flt = r'(' + exponent + r'|' + dec + r')'
    nline = r'\n+'
    
    t_SHORT_ADD = r'\+='
    t_SHORT_SUB = r'-='
    t_SHORT_MUL = r'\*='
    t_SHORT_DIV = r'/='
    t_SHORT_XOR = r'\^='
    t_SHORT_AND = r'&='
    t_SHORT_OR = r'\|='
    t_SHORT_MOD = r'%='
    t_SHORT_LEFT_SHIFT = r'<<='
    t_SHORT_RIGHT_SHIFT = r'>>='
    t_ADD = r'\+'
    t_INC = r'\+\+'
    t_SUB = r'-'
    t_DEC = r'--'
    t_MUL = r'\*'
    t_DIV = r'/'
    t_XOR = r'\^'
    t_AND = r'&&'
    t_OR  = r'\|\|'
    t_BIT_AND = r'&'
    t_BIT_OR = r'\|'
    t_LEFT_SHIFT = r'<<'
    t_RIGHT_SHIFT = r'>>'
    t_LEFT_PAR = r'\('
    t_RIGHT_PAR = r'\)'
    t_LEFT_CUR_BR = r'\{'
    t_RIGHT_CUR_BR = r'\}' 
    t_LEFT_SQ_BR = r'\['
    t_RIGHT_SQ_BR = r'\]'
    t_SEMI_COLON = r';'
    t_NOT_EQ = r'!='
    t_EQ_CHECK = r'=='
    t_ASSIGNMENT = r'='
    t_GEQ = r'>='
    t_LEQ = r'<='
    t_GREATER = r'>'
    t_LESS = r'<'
    t_COLON = r':'
    t_DOT = r'\.'
    t_NOT = r'~'
    t_NEGATE = r'!'
    t_BACKSLASH = r'\\'
    t_COMMA = r','
    t_PTR_OP = r'\->'

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        if t.value in self.reserved.keys():
            t.type = self.reserved[t.value]
        else :
            t.type = 'ID'
        return t

    @TOKEN(flt)
    def t_FLOAT_NUM(self, t):
        t.type = 'FLOAT_NUM'
        t.value = float(t.value)
        return t
    
    def t_INT_NUM(self, t):
        r'(([0-9])+)'
        t.type = 'INT_NUM'
        t.value = int(t.value)
        return t
    
    def t_CHARACTER(self, t):
        r'(\'(\\.|[^\\\'])+\')'
        t.type = 'CHARACTER'
        if(len(t.value) == 3):
            t.value = t.value[1]
        elif(len(t.value) == 4 and t.value[1] == '\\'):
            t.value = t.value[1:3]
        else :
            x = t.lexpos - self.lexer.lexdata.rfind('\n', 0, t.lexpos)
            print(f"Error!!!, Invalid single quote character encountered at line no. {t.lineno}, column no. {x} ")
            t.lexer.skip(1)
            pass
        
        return t
       
    string_regex = r'(\"(\\.|[^\\"])*\")'
    @TOKEN(string_regex) 
    def t_STRING(self, t):
        return t
        
    @TOKEN(nline)
    def t_NEWLINE(self, t):
        t.lexer.lineno += len(t.value)
        pass
    
    def t_wspace(self, t):
        r'[ \t]+'
        pass
    
    def t_INLINE_COMMENT(self, t):
        r'//.*'
        pass

    def t_BLOCK_COMMENT(self, t):
        r'/\*(.|\n)*?\*/'   # ? is to identify the closing *
        t.lexer.lineno += t.value.count('\n')
        pass
    
    def t_COMMENT_NOT_END(self, t):
        r'/\*(.|\n)*$'
        x = t.lexpos - self.lexer.lexdata.rfind('\n', 0, t.lexpos)
        print(f"Error!!!, Comment Block not ended! {t.value[0]} at line no. {t.lineno}, column no. {x} ")
        t.lexer.skip(1)
        pass
    
    def t_INV_SINGLE_QUOTE(self,t):
        r'(\'(\\.|[^\\\'])+$)'
        x = t.lexpos - self.lexer.lexdata.rfind('\n', 0, t.lexpos)
        print(f"Error!!!, Invalid single quote encountered at line no. {t.lineno}, column no. {x} ")
        t.lexer.skip(1)
        pass

    def t_INV_DOUBLE_QUOTE(self,t):
        r'(\"(\\.|[^\\"])*$)'
        x = t.lexpos - self.lexer.lexdata.rfind('\n', 0, t.lexpos)
        print(f"Error!!!, Invalid double quote encountered at line no. {t.lineno}, column no. {x} ")
        t.lexer.skip(1)
        pass
    
    def t_error(self, t):
        x = t.lexpos - self.lexer.lexdata.rfind('\n', 0, t.lexpos)
        print(f"Error!!!, Unknown lexeme encountered! {t.value[0]} at line no. {t.lineno}, column no. {x}")
        t.lexer.skip(1)
        pass

def output_token(input):
    # Give the lexer some input
    lexee.lexer.input(input)

    # Tokenize
    print(f"{'token.type':>16} {'token.value':>16} {'token.lineno':>16} {'token.lexpos':>16}")

    while True:
        token = lexee.lexer.token()
        if not token: 
            break      # No more input
        x = token.lexpos - input.rfind('\n', 0, token.lexpos)
        print(f"{token.type:>16} {token.value:>16} {token.lineno:>16} {x:>16}")


if __name__ == "__main__":
    lexee = lexer()
    lexee.build()

    for filename in sys.argv[1:] :
        print(f"Lexer output for file {filename}\n")

        with open(filename,'r') as file:
            output_token(file.read())
            
        print('\n')
        print(''.join(['_']*70))
        print('\n')
