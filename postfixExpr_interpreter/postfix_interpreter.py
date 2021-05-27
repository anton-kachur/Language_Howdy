from lex_my_lang_03 import lex, tableToPrint
from lex_my_lang_03 import tableOfSymb, tableOfId, tableOfConst, tableOfLabel, sourceCode, tableOfWrite
import collections
from postfixExpr_translator_02 import postfixTranslator, postfixCode, FSuccess
from stack01 import Stack

stack = Stack()
n = 0
toView = False
instrNum = 0

def postfixInterpreter():
    FSuccess = postfixTranslator()
    if (True, 'Translator') == FSuccess:
        print('\nПостфіксний код: \n{0}'.format(postfixCode))
        return postfixProcessing()
    else:
        print('Interpreter: Translator завершив роботу аварійно')
        return False

lenCode = len(str(postfixCode))

def postfixProcessing():
    global stack, postfixCode, instrNum
    cyclesNumb = 0
    maxNumb = len(postfixCode)
    try:
        while instrNum < maxNumb and cyclesNumb < 1000:
            cyclesNumb += 1
            lex, tok = postfixCode[instrNum]
            if tok in ('int', 'real', 'ident', 'label'):
                stack.push((lex, tok))
                nextInstr = instrNum + 1
            elif tok in ('jump', 'jf', 'colon'):
                nextInstr = doJumps(tok)
            elif tok == 'Inp':
                doOut()
                nextInstr = instrNum + 1
            elif tok == 'Out':
                doIn()
                nextInstr = instrNum + 1
            else:
                doIt(lex, tok)
                nextInstr = instrNum + 1
            if toView: configToPrint(cyclesNumb, lex, tok, maxNumb)
            instrNum = nextInstr
        for Tbl in ('Id', 'Const', 'Label', 'Write'):
            tableToPrint(Tbl)
        print('Загальна кiлькiсть крокiв: {0}'.format(cyclesNumb))
        return True
    except SystemExit as e:
        # Повідомити про факт виявлення помилки
        print('RunTime: Аварійне завершення програми з кодом {0}'.format(e))
    return True


def doIn():
    (lex, tok) = stack.pop()
    print('Введіть змінну ' + lex + ': ')
    try:
        val = float(input())
    except:
        print('неправильний тип введених даних')
        exit(106)
    if (type(val) != float):
        failRunTime('неправильний тип введених даних', None)
    if (val.is_integer()):
        val = int(val)
        tableOfId[lex] = (tableOfId[lex][0], 'int', val)
    else:
        tableOfId[lex] = (tableOfId[lex][0], 'real', val)


def doOut():
    global n
    lex, tok = stack.pop()
    val = tableOfId[lex][2]
    tableOfWrite[n] = (lex, val)
    n += 1
    [last] = collections.deque(tableOfWrite, maxlen=1)
    print(tableOfWrite[last][0], "is", tableOfWrite[last][1])


def doJumps(tok):
    if tok == 'jump':
        next = processing_JUMP()
    elif tok == 'colon':
        next = processing_colon()
    elif tok == 'jf':
        next = processing_JF()
    return next


def processing_JUMP():
    global stack, postfixCode, instrNum
    (label, tok) = stack.pop()
    val = tableOfLabel[label]
    return val


def processing_colon():
    global stack, postfixCode, instrNum
    stack.pop()
    val = instrNum + 1
    return val


def processing_JF():
    global stack, postfixCode, instrNum
    (label, tok) = stack.pop()
    val = tableOfLabel[label]
    (boolVal, arg) = stack.pop()
    print(type(boolVal))
    if (boolVal == 'True'):
        val = instrNum + 1
    else:
        val += 1
    return val


def configToPrint(step, lex, tok, maxN):
    if step == 1:
        print('=' * 30 + '\nInterpreter run\n')
        tableToPrint('All')

    print('\nКрок інтерпретації: {0}'.format(step))
    if tok in ('int', 'real'):
        print('Лексема: {0} у таблиці констант: {1}'.format((lex, tok), lex + ':' + str(tableOfConst[lex])))
    elif tok in ('ident'):
        print('Лексема: {0} у таблиці ідентифікаторів: {1}'.format((lex, tok), lex + ':' + str(tableOfId[lex])))
    else:
        print('Лексема: {0}'.format((lex, tok)))
    print('postfixCode={0}'.format(postfixCode))
    stack.print()
    return True


def doIt(lex, tok):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    if (lex, tok) == ('=', 'assign_op'):
        # зняти з вершини стека запис (правий операнд = число)
        (lexL, tokL) = stack.pop()
        # зняти з вершини стека ідентифікатор (лівий операнд)
        (lexR, tokR) = stack.pop()

        # виконати операцію:
        # оновлюємо запис у таблиці ідентифікаторів
        # ідентифікатор/змінна  
        # (index не змінюється, 
        # тип - як у константи,  
        # значення - як у константи)
        tableOfId[lexR] = (tableOfId[lexR][0], tableOfConst[lexL][1], tableOfConst[lexL][2])
    elif tok in ('add_op', 'mult_op'):
        # зняти з вершини стека запис (правий операнд)
        (lexR, tokR) = stack.pop()
        # зняти з вершини стека запис (лівий операнд)
        (lexL, tokL) = stack.pop()

        processing_add_mult_op((lexL, tokL), lex, (lexR, tokR))
        # stack.push()
        pass
    elif tok in ('pow_op'):
        # зняти з вершини стека запис (правий операнд)
        (lexR, tokR) = stack.pop()
        # зняти з вершини стека запис (лівий операнд)
        (lexL, tokL) = stack.pop()

        processing_pow_op((lexL, tokL), lex, (lexR, tokR))
        pass

    elif tok == 'neg_val':
        (lexR, tokR) = stack.pop()
        valR = tableOfConst[lexR][2]
        getValue((0, '0', 'int'), lex, (valR, lexR, tokR))
    else:
        # зняти з вершини стека запис (правий операнд)
        (lexL, tokL) = stack.pop()

        # зняти з вершини стека запис (лівий операнд)
        (lexR, tokR) = stack.pop()
        processing_add_mult_op((lexL, tokL), lex, (lexR, tokR))
    return True


def processing_add_mult_op(ltL, lex, ltR):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    lexL, tokL = ltL
    lexR, tokR = ltR
    if tokL == 'ident':
        if tableOfId[lexL][1] == 'type_undef':
            failRunTime('неініціалізована змінна', (lexL, tableOfId[lexL], (lexL, tokL), lex, (lexR, tokR)))
        else:
            valL, tokL = (tableOfId[lexL][2], tableOfId[lexL][1])
    else:
        valL = tableOfConst[lexL][2]
    if tokR == 'ident':
        # print(('===========',tokL , tableOfId[lexL][1]))
        # tokL = tableOfId[lexL][1]
        if tableOfId[lexR][1] == 'type_undef':
            failRunTime('неініціалізована змінна', (lexR, tableOfId[lexR], (lexL, tokL), lex, (lexR, tokR)))
        else:
            valR, tokR = (tableOfId[lexR][2], tableOfId[lexR][1])
    else:
        valR = tableOfConst[lexR][2]
    getValue((valL, lexL, tokL), lex, (valR, lexR, tokR))


def processing_pow_op(ltL, lex, ltR):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    lexL, tokL = ltL
    lexR, tokR = ltR
    if tokL == 'ident':
        if tableOfId[lexL][1] == 'type_undef':
            failRunTime('неініціалізована змінна', (lexL, tableOfId[lexL], (lexL, tokL), lex, (lexR, tokR)))
        else:
            valL, tokL = (tableOfId[lexL][2], tableOfId[lexL][1])
    else:
        valL = tableOfConst[lexL][2]
    if tokR == 'ident':
        if tableOfId[lexR][1] == 'type_undef':
            failRunTime('неініціалізована змінна', (lexR, tableOfId[lexR], (lexL, tokL), lex, (lexR, tokR)))
        else:
            valR, tokR = (tableOfId[lexR][2], tableOfId[lexR][1])
    else:
        valR = tableOfConst[lexR][2]
    getValue((valL, lexL, tokL), lex, (valR, lexR, tokR))


def getValue(vtL, lex, vtR):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    valL, lexL, tokL = vtL
    valR, lexR, tokR = vtR
    if lex == '+':
        value = valL + valR
    elif lex == '-':
        value = valL - valR
    elif lex == '*' and tokL == tokR == 'int':
        value = int(valL * valR)
        tokL = 'int'
    elif lex == '*' and tokL == tokR == 'real':
        value = float('{:.3f}'.format(valL * valR))
        tokL = 'real'
    elif lex == '*' and tokL != tokR:
        value = float('{:.3f}'.format(valL * valR))
        tokL = 'real'
    elif lex == '^':
        value = pow(valL, valR)
        tokL = 'real'
    elif lex == '/' and (valR == 0):
        failRunTime('ділення на нуль', ((lexL, tokL), lex, (lexR, tokR)))
    elif lex == '/' and (tokL == 'real' or tokR == 'real'):
        value = float('{:.3f}'.format(valL / valR))
    elif lex == '/' and tokL == 'int' and tokR == "int":
        value = float('{:.3f}'.format(valL / valR))
        tokL = 'real'
    elif lex == 'NEG':
        value = - valR
        tokL = tokR
    elif lex == '^E':
        value = valR * pow(10, valL)
        tokL = 'real'
    elif lex == '>':
        if (valL < valR):
            value = True
        else:
            value = False
        tokL = 'bool'
    elif lex == '<':
        if (valL > valR):
            value = True
        else:
            value = False
        tokL = 'bool'
    elif lex == '>=':
        if (valL <= valR):
            value = True
        else:
            value = False
        tokL = 'bool'
    elif lex == '<=':
        if (valL >= valR):
            value = True
        else:
            value = False
        tokL = 'bool'
    elif lex == 'is':
        if (valL == valR):
            value = True
        else:
            value = False
        tokL = 'bool'
    elif lex == '!=':
        if (valL != valR):
            value = True
        else:
            value = False
        tokL = 'bool'
    elif lex == 'and':
        if (valL == valR == True):
            value = True
        else:
            value = False
        tokL = 'bool'
    elif lex == 'or':
        if (valL == valR == True):
            value = False
        else:
            value = True
        tokL = 'bool'
    else:
        pass
    stack.push((str(value), tokL))
    toTableOfConst(value, tokL)


def toTableOfConst(val, tok):
    lexeme = str(val)
    indx1 = tableOfConst.get(lexeme)
    if indx1 is None:
        indx = len(tableOfConst) + 1
        tableOfConst[lexeme] = (indx, tok, val)


def failRunTime(str, tuple):
    if str == 'невідповідність типів':
        ((lexL, tokL), lex, (lexR, tokR)) = tuple
        print('RunTime ERROR: \n\t Типи операндів відрізняються у {0} {1} {2}'.format((lexL, tokL), lex, (lexR, tokR)))
        exit(1)
    elif str == 'неініціалізована змінна':
        (lx, rec, (lexL, tokL), lex, (lexR, tokR)) = tuple
        print('RunTime ERROR: \n\t Значення змінної {0}:{1} не визначене. Зустрылось у {2} {3} {4}'.format(lx, rec,
                                                                                                           (lexL, tokL),
                                                                                                           lex, (
                                                                                                               lexR,
                                                                                                               tokR)))
        exit(2)
    elif str == 'ділення на нуль':
        ((lexL, tokL), lex, (lexR, tokR)) = tuple
        print('RunTime ERROR: \n\t Ділення на нуль у {0} {1} {2}. '.format((lexL, tokL), lex, (lexR, tokR)))
        exit(3)

print("<*************************************************************************************************>")
print("     <====================================HOWDY====================================>")
print("     <==============================The world improves=============================>")
print("<*************************************************************************************************>")
postfixInterpreter()