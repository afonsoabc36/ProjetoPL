import ply.yacc as yacc
import sys
from forth_lexer import tokens, literals

# Mudar isto no lexer
operations = {
    '+' : 'ADD',
    'f+' : 'FADD',
    '-' : 'SUB',
    'f-' : 'FSUB',
    '*' : 'MUL',
    'f*' : 'FMUL',
    '/' : 'DIV',
    'f/' : 'FDIV'
}

number_of_ifs = 0
number_of_loops = 0
loop_stack = []

reservedWords = {
    'mod' : 'MOD',
    'cr' : 'WRITELN',
    'emit' : 'WRITECHR'
}

functions  = {

}

def p_OPERATIONS_MULTIPLE(p):
    "Operacoes : Operacoes Operacao"
    p[0] = p[1] + p[2]

def p_OPERATIONS_SINGLE(p):
    "Operacoes : Operacao"
    p[0] = p[1]

def p_DEFINITION_OPERATION(p):
    "Operacao : ':' ID Operacoes ';'"
    functions[p[2]] = p[3]
    p[0] = ""

def p_LOOP_OPERATION(p):
    "Operacao : DO "
    global number_of_loops, loop_stack
    nol = number_of_loops
    number_of_loops += 1
    loop_stack.append(f'loop{nol}')
    p[0] = f"WHILE{nol}:\nPUSHG 0\nPUSHG 1\nINF\nJZ ENDWHILE{nol}\n"

def p_LOOPEND_OPERATION(p):
    "Operacao : LoopEnd "
    p[0] = p[1]

def p_LOOP_END_OPERATION(p):
    "LoopEnd : LOOP"
    global loop_stack
    loopN = loop_stack.pop()
    nol = loopN[4:]
    p[0] = f"PUSHG 0\nPUSHI 1\nADD\nSTOREG 0\nJUMP WHILE{nol}\nENDWHILE{nol}:\n"

def p_PLUSLOOP_END_OPERATION(p):
    "LoopEnd : PLUSLOOP"
    global loop_stack
    loopN = loop_stack.pop()
    nol = loopN[4:]
    p[0] = f"PUSHG 0\nADD\nSTOREG 0\nJUMP WHILE{nol}\nENDWHILE{nol}:\n"

def p_ARITHMETIC_OPERATION(p):
    "Operacao : ArithmeticOperation"
    p[0] = f"{p[1]}\n"

def p_CONDITIONAL_OPERATION(p):
    "Operacao : Condicional"
    p[0] = p[1]

def p_PRINTSTRING_OPERATION(p):
    "Operacao : PRINTSTRING"
    p[0] = f'PUSHS "{p[1]}"\nWRITES\n'

def p_NUM_OPERATION(p):
    "Operacao : Number"
    p[0] = p[1]

def p_NUMBER_FLOAT_PUSH_OPERATION(p):
    "Number : FLOAT"
    p[0] = f"PUSHF {p[1]}\n"

def p_NUMBER_INT_PUSH_OPERATION(p):
    "Number : INT"
    p[0] = f"PUSHI {p[1]}\n"

def p_PRINT_INT_OPERATION(p):
    "Operacao : PRINTINT"
    p[0] = "WRITEI\n"

def p_PRINT_FLOAT_OPERATION(p):
    "Operacao : PRINTFLOAT"
    p[0] = "WRITEF\n"

def p_CHAR_OPERATION(p):
    "Operacao : CHAR"
    intValue = ord(p[1])
    p[0] = f"PUSHI {intValue}\n"

def p_COMPARASION_OPERATION(p):
    "Operacao : COMPARASION"
    if p[1] == '>':
        p[0] = f"SUP\n"
    elif p[1] == '<':
        p[0] = f"INF\n"
    else:
        pass

def p_INLINECOMMENT_OPERATION(p):
    "Operacao : LINECOMMENT"
    p[0] = ""

def p_ID_OPERATION(p):
    "Operacao : ID"
    if (p[1] == 'i' or p[1] == 'I') and loop_stack and loop_stack[-1].startswith('loop'):
        p[0] = "PUSHG 0\n"
    elif p[1] in functions:
        p[0] = f"PUSHA {p[1]}\nCALL\n"
    else:
        p[0] = f"{reservedWords[p[1].lower()]}\n"

def p_IFELSETHEN_OPERATION(p):
    "Condicional : IF Operacoes ELSE Operacoes THEN"
    global number_of_ifs
    noi = number_of_ifs
    number_of_ifs += 1
    p[0] = f"JZ ELSE{noi}\n{p[2]}JUMP ENDIF{noi}\nELSE{noi}:\n{p[4]}ENDIF{noi}:\n"

def p_IFTHEN_OPERATION(p):
    "Condicional : IF Operacoes THEN"
    global number_of_ifs
    noi = number_of_ifs
    number_of_ifs += 1
    p[0] = f"JZ ENDIF{noi}\n{p[2]}ENDIF{noi}:\n"

def p_ArithmeticOperation(p):
    """
    ArithmeticOperation : ADD
                        | FADD
                        | SUB
                        | FSUB
                        | MUL
                        | FMUL
                        | DIV
                        | FDIV
    """
    p[0] = operations[p[1]]

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input: ", p)
 
 # Build the parser
parser = yacc.yacc() # , debug=True)

# reading input
with open('input.fs', 'r') as file:
    # START
    print("START\n")
    result = parser.parse(file.read()) # , debug=True)
    print(result)
    # STOP
    print("STOP\n")
    # Print das funções
    for key,function in functions.items():
        print(f"{key}:")
        print(f"{function}", end='')
        # RETURN
        print("RETURN\n")