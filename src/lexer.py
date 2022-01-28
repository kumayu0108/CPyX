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
            'ADD',          # "+"
            'SUB',          # "-"
            'MUL',          # "*"
            'DIV',          # "/"
            'XOR',          # "^"
            'AND',          # "&"
            'OR',           # "|"
            'MODULO',       # "%"
            'ASSIGNMENT',   #"="
            'LEFT_SHIFT',   # "<<"
            'RIGHT_SHIFT',  # ">>"
            'LEFT_PAR',  # "("
            'RIGHT_PAR', # ")"
            'LEFT_CUR_BR',  # "{"
            'RIGHT_CUR_BR', # "}"
            'SEMI_COLON',    # ";"
            ]
    
    # def __init__(self):
    #     self.col = 0

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
    t_LEFT_PAR = r'\('
    t_RIGHT_PAR = r'\)'
    t_LEFT_CUR_BR = r'\{'
    t_RIGHT_CUR_BR = r'\}' 
    t_SEMI_COLON = r';'
    
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
    
    def t_error(self, t):
        x = t.lexpos - self.lexer.lexdata.rfind('\n', 0, t.lexpos)
        print(f"Error!!!, unknown lexeme {t.value[0]} at line no. {t.lineno}, column no. {x} ")
        t.lexer.skip(1)

def output_token(input):
    # Give the lexer some input
    lexee.lexer.input(input)

    # Tokenize
    print(f"{'token.type':>12} {'token.value':>12} {'token.lineno':>12} {'token.lexpos':>12}")

    while True:
        token = lexee.lexer.token()
        if not token: 
            break      # No more input
        x = token.lexpos - input.rfind('\n', 0, token.lexpos)
        print(f"{token.type:>12} {token.value:>12} {token.lineno:>12} {x:>12}")


if __name__ == "__main__":
    lexee = lexer()
    lexee.build()

    data = "99.3+64\"hehe\""

    sample_program_1 = '''
int main()
{
    int a = 1;
    return 0;
}
    '''

    sample_program_2 = '''
int main()
{
    int a = 1;
    if(b==1)
    {
        c=1;
    }
    else {c=3;}
    return 0;
    $$$$$$
}
    '''

    output_token(sample_program_2)
