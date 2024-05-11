import ply.yacc as yacc
import sys
from forth_lexer import tokens, literals

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

stack_elements = 0
number_of_ifs = 0
number_of_loops = 0
loop_stack = []
functions  = {}

reservedWords = {
    'mod' : 'MOD',
    'cr' : 'WRITELN',
    'emit' : 'WRITECHR',
    'swap' : 'SWAP'
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
    "Operacao : DO"
    global number_of_loops, loop_stack, stack_elements
    nol = number_of_loops
    number_of_loops += 1
    loop_stack.append(f'loop{nol}')
    p[0] = f"WHILE{nol}:\nPUSHG {stack_elements - 1}\nPUSHG {stack_elements - 2}\nINF\nJZ ENDWHILE{nol}\nPUSHG {stack_elements - 3}\n"
    stack_elements += 1

def p_LOOPEND_OPERATION(p):
    "Operacao : LoopEnd "
    p[0] = p[1]

def p_LOOP_END_OPERATION(p):
    "LoopEnd : LOOP"
    global loop_stack, stack_elements
    loopN = loop_stack.pop()
    nol = loopN[4:]
    p[0] = f"STOREG {stack_elements - 3}\nPUSHG {stack_elements-1}\nPUSHI 1\nADD\nSTOREG {stack_elements-1}\nJUMP WHILE{nol}\nENDWHILE{nol}:\nPOP 2\n"
    stack_elements -= 3

def p_PLUSLOOP_END_OPERATION(p):
    "LoopEnd : PLUSLOOP"
    global loop_stack, stack_elements
    loopN = loop_stack.pop()
    nol = loopN[4:]
    p[0] = f"PUSHG {stack_elements-2}\nADD\nSTOREG {stack_elements-2}\nSTOREG {stack_elements - 4}\nJUMP WHILE{nol}\nENDWHILE{nol}:\nPOP 2\n"
    stack_elements -= 4

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
    global stack_elements
    stack_elements += 1
    p[0] = f"PUSHF {p[1]}\n"

def p_NUMBER_INT_PUSH_OPERATION(p):
    "Number : INT"
    global stack_elements
    stack_elements += 1
    p[0] = f"PUSHI {p[1]}\n"

def p_PRINT_INT_OPERATION(p):
    "Operacao : PRINTINT"
    global stack_elements
    stack_elements -= 1
    p[0] = "WRITEI\n"

def p_PRINT_FLOAT_OPERATION(p):
    "Operacao : PRINTFLOAT"
    global stack_elements
    stack_elements -= 1
    p[0] = "WRITEF\n"

def p_CHAR_OPERATION(p):
    "Operacao : CHAR"
    global stack_elements
    stack_elements += 1
    p[0] = f'PUSHS "{p[1]}"\nCHRCODE\n'

def p_COMPARASION_OPERATION(p):
    "Operacao : COMPARISON"
    global stack_elements
    stack_elements -= 1
    if p[1] == '>':
        p[0] = f"SUP\n"
    elif p[1] == '<':
        p[0] = f"INF\n"
    elif p[1] == '>=':
        p[0] = f"SUPEQ\n"
    elif p[1] == '<=':
        p[0] = f"INFEQ\n"
    elif p[1] == '=':
        p[0] = f"EQUAL\n"
    else:
        p[0] = ""

def p_INLINECOMMENT_OPERATION(p):
    "Operacao : LINECOMMENT"
    p[0] = ""

def p_ID_OPERATION(p):
    "Operacao : ID"
    global stack_elements
    if (p[1] == 'i' or p[1] == 'I') and loop_stack and loop_stack[-1].startswith('loop'):
        p[0] = f"PUSHG {stack_elements - 2}\n"
        stack_elements += 1
    elif p[1] in functions:
        p[0] = f"PUSHA {p[1]}\nCALL\n"
        # TODO: Verificar e alterar quantos elementos sobe ou desce a stack depois de chamada a função
    else:
        p[0] = f"{reservedWords[p[1].lower()]}\n"
        # TODO: Verificar e alterar quantos elementos sobe ou desce a stack depois de chamada a função

def p_IFELSETHEN_OPERATION(p):
    "Condicional : IF Operacoes ELSE Operacoes THEN"
    global number_of_ifs, stack_elements
    noi = number_of_ifs
    number_of_ifs += 1
    stack_elements -= 1
    p[0] = f"JZ ELSE{noi}\n{p[2]}JUMP ENDIF{noi}\nELSE{noi}:\n{p[4]}ENDIF{noi}:\n"

def p_IFTHEN_OPERATION(p):
    "Condicional : IF Operacoes THEN"
    global number_of_ifs, stack_elements
    noi = number_of_ifs
    number_of_ifs += 1
    stack_elements -= 1
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
    global stack_elements
    stack_elements -= 2
    p[0] = operations[p[1]]

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input: ", p)
 
 # Build the parser
parser = yacc.yacc() # debug=True)

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