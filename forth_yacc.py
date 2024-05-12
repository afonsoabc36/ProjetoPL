import ply.yacc as yacc
import re
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
function_arguments = {}

reservedWords = {
    'mod' : {
            'function': 'MOD',
            'arguments': 2,
            'net_effect': -1
        },
    'cr' : {
            'function': 'WRITELN',
            'arguments': 0,
            'net_effect': 0
        },
    'emit' : {
            'function': 'WRITECHR',
            'arguments': 1,
            'net_effect': -1
        },
    'swap' : {
            'function': 'SWAP',
            'arguments': 2,
            'net_effect': 0
        },
    'dup' : {
            'function': 'DUP 1',
            'arguments': 1,
            'net_effect': 1
        },
    'key' : {
            'function': 'READ',
            'arguments': 0,
            'net_effect': 1
        },
    'space' : {
            'function': 'PUSHS " "\nWRITES',
            'arguments': 0,
            'net_effect': 0
        },
    'spaces' : {
            'function': 'spaces0:\nPUSHI 1\nSUB\nDUP 1\nPUSHI 32\nWRITECHR\nPUSHI 0\nSUP\nJZ endspaces0\nJUMP spaces0\nendspaces0:\nPOP 1',
            'arguments': 1,
            'net_effect': -1
        }
}

def count_arguments(function_name, expression):
    global function_arguments
    arguments = 0
    net_effect = 0
    decrement = ['pushi', 'pushf', 'pushg', 'char', 'dup', 'load']
    increment = ['add', 'sub', 'mul', 'div', 'mod', 'inf', 'sup', 'infeq', 'supeq', 'equal']
    store = ['storeg', 'jz']
   
    for word in expression.lower().split():
        if word in increment:
            arguments += 2
        elif word in decrement:
            arguments -= 1
        elif word in store:
            arguments += 1
        elif word in functions.keys():
            arguments += function_arguments[word]['arguments']
        elif word.lower() in reservedWords.keys():
            arguments += reservedWords[word]['arguments']

    function_arguments[function_name] = {
        'arguments': arguments,
        'net_effect' : net_effect
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
    count_arguments(p[2], p[3])
    p[0] = ""

def p_PARENCOMMENTS_OPERATION(p):
    "Operacao : PARENCOMMENTS"
    p[0] = ""

def p_LOOP_OPERATION(p):
    "Operacao : DO"
    global number_of_loops, loop_stack, stack_elements
    nol = number_of_loops
    number_of_loops += 1
    loop_stack.append(f'loop{nol}')
    if stack_elements < 3:
        se = 3
    else:
        se = stack_elements
    p[0] = f"WHILE{nol}:\nPUSHG {se - 1}\nPUSHG {se - 2}\nINF\nJZ ENDWHILE{nol}\nPUSHG {se - 3}\n"
    stack_elements += 1

def p_LOOPEND_OPERATION(p):
    "Operacao : LoopEnd "
    p[0] = p[1]

def p_LOOP_END_OPERATION(p):
    "LoopEnd : LOOP"
    global loop_stack, stack_elements
    loopN = loop_stack.pop()
    nol = loopN[4:]
    if stack_elements < 4:
        se = 4
    else:
        se = stack_elements
    p[0] = f"STOREG {se - 4}\nPUSHG {se-2}\nPUSHI 1\nADD\nSTOREG {se-2}\nJUMP WHILE{nol}\nENDWHILE{nol}:\nPOP 2\n"
    
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
        if stack_elements < 4:
            se = 4
        else:
            se = stack_elements
        p[0] = f"PUSHG {se - 2}\n"
        stack_elements += 1
    elif p[1] in functions:
        faa = function_arguments[p[1]]['arguments']
        fane = function_arguments[p[1]]['net_effect']
        stack_elements += faa
        result = ""
        result += functions[p[1]]
        stack_elements += fane
        p[0] = result
    elif p[1].lower() in reservedWords.keys():
        p[0] = f"{reservedWords[p[1].lower()]['function']}\n"
        stack_elements += reservedWords[p[1].lower()]['net_effect']

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
    stack_elements -= 1
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
    '''
    # Print das funções
    for key,function in functions.items():
        print(f"{key}:")
        fan = function_arguments[key]['arguments']
        if fan > 0:
            for i in range(fan):
                if fan > 0:
                    print(f"PUSHFP\nLOAD { i - (fan)}")
        print(f"{function}", end='')
    
        # RETURN
        print("RETURN\n")
    '''