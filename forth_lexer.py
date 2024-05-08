import ply.lex as lex

tokens = [
    'FLOAT',
    'INT',
    'FADD',
    'ADD',
    'FSUB',
    'SUB',
    'FMUL',
    'MUL',
    'FDIV',
    'DIV',
    'CHAR',
    'IF',
    'ELSE',
    'THEN',
    'COMPARASION',
    'ID',
    'PRINTSTRING',
    'PRINTFLOAT',
    'PRINTINT'
]

literals = [':', ';', '"']

reserved = {
    'CHAR': 'CHAR'
}

t_INT = r'\d+'

t_FLOAT = r'\d+\.\d+'

t_ADD = r'\+'

t_SUB = r'\-'

t_MUL = r'\*'

t_DIV = r'\/'

t_PRINTINT = r'\.'

t_COMPARASION = r'[<>]'

t_ignore = " \t\n"

def t_FADD(t):
    r'f\+'
    return t

def t_FSUB(t):
    r'f\-'
    return t

def t_FMUL(t):
    r'f\*'
    return t

def t_FDIV(t):
    r'f\/'
    return t

def t_PRINTFLOAT(t):
    r'f\.'
    return t

def t_IF(t):
    r'[iI][fF]'
    return t

def t_ELSE(t):
    r'[eE][lL][sS][eE]'
    return t

def t_THEN(t):
    r'[tT][hH][eE][nN]'
    return t

def t_PRINTSTRING(t):
    r'\." [^"]*"' 
    t.value = t.value[3:-1]
    return t

def t_CHAR(t):
    r'CHAR\s+([a-zA-Z])'
    t.value = t.value[-1:]
    return t

def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_\-]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_error(t):
    print("Caráter ilegal: ", t.value[0])
    t.lexer.skip(1)

# build the lexer
lexer = lex.lex()