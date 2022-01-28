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
        'return'    : 'RETURN',
        'void'      : 'VOID',
        'sizeof'    : 'SIZEOF',
        'unsigned'  : 'UNSIGNED',
        'main'      : 'MAIN',
        
    }

    tokens = list(reserved.values()) + [
            'STRING',
            'ID',
            'ADD', # "+"
            'SUB', # "-"
            'MUL', # "*"
            'DIV', # "/"
            'XOR', # "^"
            'AND', # "&"
            'OR', # "|"
            'MODULO', # "%"
            'ASSIGNMENT', #"="
            'LEFT_SHIFT', # "<<"
            'RIGHT_SHIFT', # ">>"
            ]
    
    # def __init__():

    def build(self, **kwargs):
        self.lexer = lex.lex(self)
    
    num = r'([0-9])'
    alph = r'([a-zA-Z_])'
    exp = r'([Ee][+-]?' + num + r'+)'
    exponent = r'(' + num + r'+' + exp + r')'
    dec = r'(' + num + r'*[.]' + num + r'+' + exp + r'?)'
    flt = r'(' + exponent + r'|' + dec + r')'
    nline = r'\n+'
    
    t_ADD = r'\+'
    t_SUB = r'-'
    t_MUL = r'\*'
    t_DIV = r'/'
    t_XOR = r'\^'
    t_AND = r'&&'
    t_OR  = r'\|\|'
    t_LEFT_SHIFT = r'<<'
    t_RIGHT_SHIFT = r'>>'
    t_ASSIGNMENT = r'=' 

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        if t.value in self.reserved.keys():
            t.type = self.reserved[t.value]
        else :
            t.type = 'ID'

        return t

    @TOKEN(flt)
    def t_FLOAT(self, t):
        t.type = 'FLOAT'
        t.value = float(t.value)
        return t
    
    def t_INT(self, t):
        r'(([0-9])+)'
        t.type = 'INT'
        t.value = int(t.value)
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
    
lexee = lexer()
lexee.build()

data = "99.3+64\"hehe\""

sample_program = '''
int main()
{
    int a = 1;
    return 0;
}
'''
 
# Give the lexer some input
lexee.lexer.input(data)

# Tokenize
while True:
    token = lexee.lexer.token()
    if not token: 
        break      # No more input
    print(token)