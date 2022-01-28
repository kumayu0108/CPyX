import ply.lex as lex

class lexer():
    
    tokens = ['INT', 'FLOAT', 'BOOL', 'CHAR','STRUCT','VOID'  #data types
            'ID',
            'MAIN',
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
            'FOR','WHILE','IF',
            'RETURN']
    
    # def __init__():

    def build(self, **kwargs):
        self.lexer = lex.lex(self)
    
    num = r'([0-9])'
    alph = r'([a-zA-Z_])'
    exp = r'([Ee][+-]?' + num + r'+)'
    exponent = r'(' + num + r'+' + exp + r')'
    dec = r'(' + num + r'*[.]' + num + r'+' + exp + r'?)'
    float = r'(' + exponent + r'|' + dec + r')'
    
    t_ADD = r'\+'
    t_SUB = r'-'
    t_MUL = r'\*'
    t_DIV = r'/'
    t_XOR = r'\^'
    t_AND = r'&&'
    t_OR  = r'\|\|'
    t_LEFT_SHIFT = r'<<'
    t_RIGHT_SHIFT = r'>>'
    
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = 'ID'
        return t

    def t_INT(self, t):
        r'(([0-9])+)'
        t.type = 'INT'
        t.value = int(t.value)
        return t

    # def t_FLOAT(self, t):
    #     pass

    # def t_STRING(self, t):
    #     pass
    
    # def t_NEWLINE(self, t):
    #     pass
      
    
lexee = lexer()
lexee.build()

data = "99+64"
 
# Give the lexer some input
lexee.lexer.input(data)

# Tokenize
while True:
    token = lexee.lexer.token()
    if not token: 
        break      # No more input
    print(token)