"""
Název: 2. úloha do IPP 2022/2023
Login: xjetma02
Autor: Adam Jetmar
"""

import argparse
import sys
import xml.etree.ElementTree as ET

#Třída instrukce
class Instruction:
    #seznam návěští
    _labelFrame = {}
    #datový zásobník
    _dataFrame = []
    #List instrukcí
    _instrList = {}

    #definice rámců
    _framesDefinition = {
        "TF": False,
        "LF": False,
        "GF": True
    }

    #slovník pro ukládání
    _frames = {
        "GF": {},
        "LF": {},
        "TF": {}
    }
    

    #konstruktor třídy Instruction
    def __init__(self, initOpcode, order: int):
        self._opcode = initOpcode
        self._order = order
        self._instrList.update({order: initOpcode})

    #Getters
    #vrací název instrukce
    def getOpcode(self):
        return self._opcode

    #vrací hodnotu order pro danou instrukci
    def getOrder(self):
        return self._order

    #vrací seznam instrukcí
    def getInstrList(self):
        return self._instrList
    
    #vrátí rámec podle hodnoty v parametru index
    def getFrame(self, index):
        return self._frames[index]

    #vrátí hodnotu proměnné v rámci
    def getVarFromFrame(self, var):
        info = var.split("@")
        name = info[1]
        frame = info[0]

        #pokud je rámec nedefinovaný, vyhodí chybu 55
        if self.isFrameDefined(frame) == False or self.isFrameDefined(frame) is None:
            exit(55)
        result = self._frames[frame][name]
        return result

    #Setters
    #Aktualizuje opcode instrukce na novou hodnotu
    def setOpcode(self, opcodeVal):
        self._opcode = opcodeVal

    #Nastaví pořadí instrukce
    def setOrder(self, order):
        self._order = order

    """
    Funkce addToFrame vloží do rámce název proměnné a její hodnotu
    param. frame - název rámce
    param. name - název proměnné
    param. value - hodnota proměnné
    """
    def addToFrame(self, frame: str, name, value):

        if self._frames[frame].get(name) is None and self._opcode != "DEFVAR":
            exit(54)
        if self._frames[frame].get(name) is not None and self._opcode == "DEFVAR":
            exit(52)

        self._frames[frame].update({name: value})

    #přidá hodnou do datového zásobníku
    def addToDataFrame(self, value):
        self._dataFrame.append(value)

    #popne hodnotu z datového zásobníku
    def popDataFrame(self):
        item = self._dataFrame.pop()
        return item

    #přidá návěští do rámce návěští
    def addToLabelFrame(self, label, order):
        self._labelFrame.update({label: order})

    #vymaže hodnoty rámce
    def cleanFrame(self, index):
        self._frames[index].clear() 

    #definuje rámec a uloží do něj další rámec "anotherFrame"
    def updateFrame(self,frame, anotherFrame: dict):
        self._frames[frame].update(anotherFrame)

    #nastavý rámec na definovaný nebo nedefinovaný podle parametru "is_def"
    def defineFrame(self, frame, is_def: bool):
        self._framesDefinition.update({frame: is_def})

    #vrací boolean hodnotu podle hodnoty ve "_framesDefinition"
    def isFrameDefined(self, frame):
        return self._framesDefinition[frame]


class Argument:

    def __init__(self, num: int, typ, value):
        self._num = num
        self._typ = typ
        self._value = value

    #vrácí typ uložený v argumentě "typ"
    def getType(self):
        return self._typ

    #vrací hodnotu uloženou v argumentě "value"
    def getVal(self):
        return self._value

    #vrací pořadí argumentu v instrukci
    def getArgOrder(self):
        return self._num

#Instrukce pro práci s rámci, volání funkcí
class Move(Instruction):

    def __init__(self, arg1: Argument, arg2: Argument, order: int):
        super().__init__("MOVE", order)
        self._arg1: Argument = arg1
        self._arg2: Argument = arg2

    def execute(self):
        # print('Executing MOVE instruction')

        if self._arg2.getType() == "var" and self._arg1.getType() == "var":
            varVal = super().getVarFromFrame(self._arg2.getVal())
            info = self._arg1.getVal().split("@")
            super().addToFrame(info[0], info[1], varVal)

        elif self._arg1.getType() != "var" and self._arg2.getType() == "var":
            varVal = self._arg1.getVal()
            info = self._arg2.getVal().split("@")
            super().addToFrame(info[0], info[1], varVal)

        else:
            info = self._arg1.getVal().split("@")
            super().addToFrame(info[0], info[1], self._arg2.getVal())

class Createframe(Instruction):

    def __init__(self, order: int):
        super().__init__("CREATEFRAME", order)

    def execute(self):
        super().cleanFrame("TF")
        super().defineFrame("TF", True)
        super().defineFrame("LF", True)

class Pushframe(Instruction):

    def __init__(self, order: int):
        super().__init__("PUSHFRAME", order)

    def execute(self):
        if not super().isFrameDefined("LF") or not super().isFrameDefined("TF"):
            exit(55)
        frame = super().getFrame("TF")
        super().defineFrame("TF", False)
        super().updateFrame("LF", frame)

class Popframe(Instruction):

    def __init__(self, order: int):
        super().__init__("POPFRAME", order)

    def execute(self):
        if not super().isFrameDefined("LF"):
            exit(55)

        frame = super().getFrame("LF")
        super().defineFrame("TF", True)
        super().updateFrame("TF", frame)
        super().defineFrame("LF", False)

class Defvar(Instruction):

    def __init__(self, argument: Argument, order: int):
        super().__init__("DEFVAR", order)
        if argument.getType() == "var":
            self._arg: Argument = argument
        else:
            exit(53)

    def execute(self):
        # print("Executing DEFVAR instruction")
        info = self._arg.getVal().split("@")
        name: str = info[1]
        frame: str = info[0]
        value = ""

        if not super().isFrameDefined(frame):
            exit(55)

        super().addToFrame(frame, name, value)

#Instrukce pro práci s datovým zásobníkem
class Pushs(Instruction):
    def __init__(self, argument: Argument, initOrder: int):
        super().__init__("PUSHS", initOrder)
        self._arg: Argument = argument

    def execute(self):
        super().addToDataFrame(self._arg.getVal())

class Pops(Instruction):

    def __init__(self, argument: Argument, order: int):
        super().__init__("POPS", order)
        if argument.getType() == "var":
            self._arg: Argument = argument
        else:
            exit(53)

    def execute(self):
        value = super().popDataFrame()
        var = self._arg.getVal().split("@")
        super().addToFrame(var[0], var[1], value)

#Aritmetické, relační, booleovské a konverzní instrukce
class Operation(Instruction):

    def __init__(self, initOpcode, arg1: Argument, arg2: Argument, arg3: Argument, order: int):
        super().__init__(initOpcode, order)
        if arg1.getType() == "var":
            self._arg1: Argument = arg1
        else:
            exit(53)
        self._arg2 = arg2
        self._arg3 = arg3

    def execute(self):
        firstVal = self._arg2.getVal()
        secondVal = self._arg3.getVal()

        if self._arg2.getType() != "var" and self._arg2.getType() != "int":
            exit(53)
        if self._arg3.getType() != "var" and self._arg3.getType() != "int":
            exit(53)

        if self._arg2.getType() == "var":
            firstVal = super().getVarFromFrame(firstVal)

        if self._arg3.getType() == "var":
            secondVal = super().getVarFromFrame(secondVal)
        try:
            firstVal = int(firstVal)
            secondVal = int(secondVal)
        except ValueError:
            exit(32)

        result = 0
        if super().getOpcode() == "ADD":
            result = firstVal + secondVal
        elif super().getOpcode() == "SUB":
            result = firstVal - secondVal
        elif super().getOpcode() == "MUL":
            result = firstVal * secondVal
        elif super().getOpcode() == "IDIV":
            if secondVal == 0:
                exit(57)
            else:
                result = firstVal / secondVal
        result = int(result)
        result = str(result)
        info = self._arg1.getVal().split("@")
        super().addToFrame(info[0], info[1], result)

class BoolOperation(Instruction):

    def __init__(self, initOpcode, arg1: Argument, arg2: Argument, arg3: Argument, order: int):
        super().__init__(initOpcode, order)
        if arg1.getType() == "var":
            self._arg1: Argument = arg1
        else:
            exit(53)
        self._arg2 = arg2
        self._arg3 = arg3

    def execute(self):
        firstVal = self._arg2.getVal()
        secondVal = self._arg3.getVal()

        if self._arg2.getType() == "var":
            firstVal = super().getVarFromFrame(firstVal)

        if self._arg3.getType() == "var":
            secondVal = super().getVarFromFrame(secondVal)

        result = "false"

        if super().getOpcode() == "AND":
            if firstVal.lower() == "true" and secondVal.lower() == "true":
                result = "true"
            else:
                result = "false"

        if super().getOpcode() == "OR":
            if firstVal.lower() == "true" or secondVal.lower() == "true":
                result = "true"
            else:
                result = "false"

        if super().getOpcode() == "NOT":
            if firstVal.lower() == "false":
                result = "true"
            else:
                result = "false"

        info = self._arg1.getVal().split("@")
        super().addToFrame(info[0], info[1], result)

class Int2Char(Instruction):

    def __init__(self, arg1: Argument, arg2: Argument, order: int):
        super().__init__("INT2CHAR", order)
        self._arg1: Argument = arg1
        self._arg2: Argument = arg2

    def execute(self):
        intVal = ""
        if self._arg2.getType() == "int":
            intVal = self._arg2.getVal()

        elif self._arg2.getType() == "var":
            var = self._arg2.getVal()
            intVal = super().getVarFromFrame(var)
        try:
            intVal = int(intVal)
        except ValueError:
            exit(58)

        if intVal < 0 or intVal > 127:
            exit(58)

        info = self._arg1.getVal().split("@")
        super().addToFrame(info[0], info[1], chr(intVal))

class Stri2Int(Instruction):

    def __init__(self, arg1: Argument, arg2: Argument, arg3: Argument, order: int):
        super().__init__("STRI2INT", order)

        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3

    def execute(self):
        firstVal = self._arg2.getVal()
        secondVal = self._arg3.getVal()

        if self._arg2.getType() == "var":
            firstVal = super().getVarFromFrame(firstVal)

        if self._arg3.getType() == "var":
            secondVal = super().getVarFromFrame(secondVal)
        index = 0
        try:
            index = int(secondVal)
        except ValueError:
            exit(53)

        if index >= len(firstVal):
            exit(58)

        orderChar = ord(firstVal[index])

        info = self._arg1.getVal().split("@")
        super().addToFrame(info[0], info[1], orderChar)

#Vstupně-výstupní instrukce
class Read(Instruction):

    def __init__(self, arg1: Argument, arg2: Argument, order: int):
        super().__init__("READ", order)
        self._arg1: Argument = arg1
        self._arg2: Argument = arg2

    def execute(self):
        global inputFile
        typ = self._arg2.getVal()
        info = self._arg1.getVal().split("@")
        inputVal = "nil"

        if typ == "string":
            inputVal = inputFile.readline()

        elif typ == "int":
            inputVal = inputFile.readline()
            try:
                int(inputVal)
            except ValueError:
                exit(53)

        elif typ == "bool":
            inputVal = inputFile.readline()
            if inputVal.lower() == "true":
                inputVal = "true"
            else:
                inputVal = "false"
        inputVal = inputVal.replace("\n", "")
        super().addToFrame(info[0], info[1], inputVal)

class Write(Instruction):

    def __init__(self, argument: Argument, order: int):
        super().__init__("WRITE", order)
        self._arg: Argument = argument

    def execute(self):
        # print('Executing WRITE instruction')
        typ = self._arg.getType()
        if typ == "string":
            string = self._arg.getVal()
            output = string.replace("\\032", " ")
            output = output.replace("\\010", "\n")
            output = output.replace("\\035", "#")
            output = output.replace("\\009", "\t")
            output = output.replace("\\092", "\\")
            print(output, end='')
        if typ == "var":
            value = super().getVarFromFrame(self._arg.getVal())
            output = value.replace("\\032", " ")
            output = output.replace("\\035", "#")
            output = output.replace("\\092", "\\")
            output = output.replace("\\010", "\n")
            output = output.replace("\\009", "\t")
            print(output, end='')
        if typ == "bool":
            write = self._arg.getVal()
            if write == "false":
                print("false", end='')
            elif write == "true":
                print("true", end='')
        if typ == "int":
            value = int(self._arg.getVal())
            print(value, end='')
        if typ == "nil":
            print("", end='')

#Instrukce pro práci s řetězci
class Concat(Instruction):

    def __init__(self, arg1: Argument, arg2: Argument, arg3: Argument, order: int):
        super().__init__("CONCAT", order)
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3

    def execute(self):
        typ1 = self._arg2.getType()
        typ2 = self._arg3.getType()

        firstVal = self._arg2.getVal()
        secondVal = self._arg3.getVal()

        newString = ""

        if typ1 == "var" or typ2 == "var":
            if typ1 == "var":
                firstVal = super().getVarFromFrame(firstVal)
            if typ2 == "var":
                secondVal = super().getVarFromFrame(secondVal)
        elif typ1 == "int" or typ2 == "int":
            exit(53)

        try:
            newString = str(firstVal) + str(secondVal)
        except ValueError:
            exit(53)

        info = self._arg1.getVal().split("@")
        super().addToFrame(info[0], info[1], newString)

class Strlen(Instruction):

    def __init__(self, arg1: Argument, arg2: Argument, order: int):
        super().__init__("STRLEN", order)
        self._arg1: Argument = arg1
        self._arg2: Argument = arg2

    def execute(self):

        stringVal = ""
        if self._arg2.getType() == "var":
            stringVal = super().getVarFromFrame(self._arg2.getVal())
        else:
            stringVal = self._arg2.getVal()

        info = self._arg1.getVal().split("@")
        super().addToFrame(info[0], info[1], len(stringVal))

class Getchar(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument, arg3: Argument, order: int):
        super().__init__("GETCHAR", order)

        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3

    def execute(self):
        firstVal = self._arg2.getVal()
        secondVal = self._arg3.getVal()

        if self._arg2.getType() == "var":
            firstVal = super().getVarFromFrame(firstVal)

        if self._arg3.getType() == "var":
            secondVal = super().getVarFromFrame(secondVal)

        try:
            secondVal = int(secondVal)
        except ValueError:
            exit(53)

        if secondVal >= len(firstVal):
            exit(58)

        char = firstVal[secondVal]
        info = self._arg1.getVal().split("@")
        super().addToFrame(info[0], info[1], char)

class Setchar(Instruction):

    def __init__(self, arg1: Argument, arg2: Argument, arg3: Argument, order: int):
        super().__init__("SETCHAR", order)
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3

    def execute(self):

        string = super().getVarFromFrame(self._arg1.getVal())
        firstVal = self._arg2.getVal()
        secondVal = self._arg3.getVal()

        if self._arg2.getType() == "var":
            firstVal = super().getVarFromFrame(firstVal)

        if self._arg3.getType() == "var":
            secondVal = super().getVarFromFrame(secondVal)

        try:
            firstVal = int(firstVal)
        except ValueError:
            exit(53)

        if secondVal == "" or firstVal >= len(string):
            exit(58)

        char = secondVal[0]

        stringList = list(string)
        stringList[firstVal] = char

        newString = "".join(stringList)

        info = self._arg1.getVal().split("@")
        super().addToFrame(info[0], info[1], newString)

#Práce s typy
class Typ(Instruction):

    def __init__(self, arg1: Argument, arg2: Argument, order: int):
        super().__init__("TYPE", order)
        self._arg1: Argument = arg1
        self._arg2: Argument = arg2

    def execute(self):
        typ = self._arg2.getType()
        if typ == "var":
            value = super().getVarFromFrame(self._arg2.getVal())
            if value.lower() == "true" or value.lower() == "false":
                typ = "bool"
            elif value == "":
                typ = ""
            elif value == "nil":
                typ = "nil"
            else:
                typ = "string"

        info = self._arg1.getVal().split("@")
        super().addToFrame(info[0], info[1], typ)

#Instrukce pro řízení toku programu
class Label(Instruction):

    def __init__(self, argument: Argument, order: int):
        super().__init__("LABEL", order)
        self._arg: Argument = argument

    def execute(self):
        super().addToLabelFrame(self._arg.getVal(), super().getOpcode())

class Jumpifeq(Instruction):

    def __init__(self, arg1: Argument, arg2: Argument, arg3: Argument, order: int):
        super().__init__("JUMPIFEQ", order)
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3

    def execute(self):
        typ1 = self._arg2.getType()
        typ2 = self._arg3.getType()

        firstVal = self._arg2.getVal()
        secondVal = self._arg3.getVal()

        if typ1 == "var" or typ2 == "var":
            if typ1 == "var":
                firstVal = super().getVarFromFrame(firstVal)
            if typ2 == "var":
                secondVal = super().getVarFromFrame(secondVal)

            if firstVal == secondVal:
                return True
            else:
                return False

        elif typ1 == "nil" or typ2 == "nil":
            if firstVal == secondVal:
                return True
            else:
                return False
        elif typ1 == typ2:
            if firstVal == secondVal:
                return True
            else:
                return False
        else:
            exit(53)

class Exit(Instruction):

    def __init__(self, arg: Argument, order: int):
        super().__init__("EXIT", order)
        self._arg: Argument = arg

    def execute(self):
        exitVal = 0
        if self._arg.getType() == "var":
            exitVal = super().getVarFromFrame(self._arg.getVal())
        else:
            exitVal = self._arg.getVal()

        try:
            exitVal = int(exitVal)
        except ValueError:
            exit(57)

        if exitVal < 0 or exitVal > 49:
            exit(57)

        exit(exitVal)

#Ladicí instrukce
class Break(Instruction):

    def __init__(self, order: int):
        super().__init__("BREAK", order)

    def execute(self):

        print("Instrukce: ", super().getInstrList(), file=sys.stderr, end='')
        print("Aktuální pozice: ", super().getOrder(), file=sys.stderr, end='')
        print("Rámec GF: ", super().getFrame("GF"), file=sys.stderr, end='')
        print("Rámec LF: ", super().getFrame("LF"), file=sys.stderr, end='')
        print("Rámec TF: ", super().getFrame("TF"), file=sys.stderr, end='')

class Compare(Instruction):
    def __init__(self, initOpcode, arg1: Argument, arg2: Argument, arg3: Argument, order: int):
        super().__init__(initOpcode.upper(), order)
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3

    def execute(self):
        firstVal = self._arg2.getVal()
        secondVal = self._arg3.getVal()
        typ1 = self._arg2.getType()
        typ2 = self._arg3.getType()
        result = "false"

        if typ1 == "nil" or typ2 == "nil":
            if super().getOpcode() == "EQ":
                if typ1 == "var":
                    firstVal = super().getVarFromFrame(firstVal)
                if typ2 == "var":
                    secondVal = super().getVarFromFrame(secondVal)

                if firstVal == secondVal:
                    result = "true"
            else:
                exit(53)

        if (typ1 == "int" and typ2 == "int") or (typ1 == "string" and typ2 == "string"):

            if typ1 == "int" and typ2 == "int":
                try:
                    firstVal = int(firstVal)
                    secondVal = int(secondVal)
                except ValueError:
                    exit(53)

            if super().getOpcode() == "LT":
                if firstVal < secondVal:
                    result = "true"
            if super().getOpcode() == "GT":
                if firstVal > secondVal:
                    result = "true"
            if super().getOpcode() == "EQ":
                if firstVal == secondVal:
                    result = "true"

        elif typ1 == "bool" and typ2 == "bool":
            if super().getOpcode() == "LT":
                if firstVal.lower() == "false" and secondVal.lower() == "true":
                    result = "true"
            if super().getOpcode() == "GT":
                if firstVal.lower() == "true" and secondVal.lower() == "false":
                    result = "true"
            if super().getOpcode() == "EQ":
                if firstVal.lower() == secondVal.lower():
                    result = "true"

        elif typ1 == "var" or typ2 == "var":

            if typ1 == "var":
                firstVal = super().getVarFromFrame(firstVal)
            if typ2 == "var":
                secondVal = super().getVarFromFrame(secondVal)
            if typ1 == "var" and typ2 == "var":
                if super().getOpcode() == "LT":
                    if firstVal < secondVal:
                        result = "true"
                if super().getOpcode() == "GT":
                    if firstVal > secondVal:
                        result = "true"
                if super().getOpcode() == "EQ":
                    if firstVal == secondVal:
                        result = "true"

        else:
            exit(53)
            #TODO - ostatne pripady

        info = self._arg1.getVal().split("@")
        super().addToFrame(info[0], info[1], result)

#Třída Factory vrátí vytvořenou instanci konkrétní instrukce podle zadaného opcode 
class Factory:

    @classmethod
    def resolve(cls, operation: str, elem):
        factoryOrder = elem.attrib["order"]
        argDef = Argument(1, "int", "-1")
        arg = argDef
        arg1 = argDef
        arg2 = argDef
        arg3 = argDef

        try:
            factoryOrder = int(factoryOrder)
        except ValueError:
            exit(32)

        tempOpcode = operation.upper();

        match tempOpcode:
            case "BREAK":
                if len(elem) > 0:
                    exit(32)

                return Break(factoryOrder)         
            case "CREATEFRAME":
                    if len(elem) > 0:
                        exit(32)
                    return Createframe(factoryOrder)
            case "PUSHFRAME":
                if len(elem) > 0:
                    exit(32)
                return Pushframe(factoryOrder)
            case "POPFRAME":
                if len(elem) > 0:
                    exit(32)
                return Popframe(factoryOrder)
            case "DEFVAR":
                if len(elem) > 1:
                    exit(32)
                try:
                    if elem[0].tag != "arg1":
                        exit(32)
                    arg = Argument(1, elem[0].attrib["type"], elem[0].text)
                except IndexError:
                    exit(32)

                return Defvar(arg, factoryOrder)
            case "PUSHS":
                if len(elem) > 1:
                    exit(32)
                try:
                    if elem[0].tag != "arg1":
                        exit(32)
                    arg = Argument(1, elem[0].attrib["type"], elem[0].text)
                except IndexError:
                    exit(32)
                return Pushs(arg, factoryOrder)
            case "POPS":
                if len(elem) > 1:
                    exit(32)
                try:
                    if elem[0].tag != "arg1":
                        exit(32)
                    arg = Argument(1, elem[0].attrib["type"], elem[0].text)
                except IndexError:
                    exit(32)
                return Pops(arg, factoryOrder)
            case "WRITE":
                if len(elem) > 1:
                    exit(32)
                try:
                    if elem[0].tag != "arg1":
                        exit(32)
                    arg = Argument(1, elem[0].attrib["type"], elem[0].text)
                except IndexError:
                    exit(32)
                return Write(arg, factoryOrder)
            case "DPRINT":
                if len(elem) > 1:
                    exit(32)
                try:
                    if elem[0].tag != "arg1":
                        exit(32)
                    arg = Argument(1, elem[0].attrib["type"], elem[0].text)
                except IndexError:
                    exit(32)
                return Write(arg, factoryOrder, sys.stderr)
            case "LABEL":
                if len(elem) > 1:
                    exit(32)
                try:
                    if elem[0].tag != "arg1":
                        exit(32)
                    arg = Argument(1, "label", elem[0].text)
                except IndexError:
                    exit(32)
                return Label(arg, factoryOrder)
            case "EXIT":
                if len(elem) > 1:
                    exit(32)
                arg = argDef
                try:
                    if elem[0].tag != "arg1":
                        exit(32)
                    arg = Argument(1, elem[0].attrib["type"], elem[0].text)
                except IndexError:
                    exit(32)
                return Exit(arg, factoryOrder)
            case "INT2CHAR":
                if len(elem) > 2:
                    exit(32)
                try:
                    if elem[0].tag != "arg1":
                        exit(32)
                    arg1 = Argument(1, elem[0].attrib["type"], elem[0].text)
                    arg2 = Argument(2, elem[1].attrib["type"], elem[1].text)
                except IndexError:
                    exit(32)
                return Int2Char(arg1, arg2, factoryOrder)
            case "MOVE":
                if len(elem) > 2:
                    exit(32)
                try:
                    if elem[0].tag != "arg1":
                        exit(32)
                    if elem[1].tag != "arg2":
                        exit(32)
                    arg1 = Argument(1, elem[0].attrib["type"], elem[0].text)
                    arg2 = Argument(2, elem[1].attrib["type"], elem[1].text)
                except IndexError:
                    exit(32)
                return Move(arg1, arg2, factoryOrder)
            case "READ":
                if len(elem) > 2:
                    exit(32)
                try:
                    arg1 = Argument(1, elem[0].attrib["type"], elem[0].text)
                    arg2 = Argument(2, elem[1].attrib["type"], elem[1].text)
                except IndexError:
                    exit(32)
                return Read(arg1, arg2, factoryOrder)
            case "TYPE":
                if len(elem) > 2:
                    exit(32)
                try:
                    arg1 = Argument(1, elem[0].attrib["type"], elem[0].text)
                    arg2 = Argument(2, elem[1].attrib["type"], elem[1].text)
                except IndexError:
                    exit(32)
                return Typ(arg1, arg2, factoryOrder)
            case "STRLEN":
                if len(elem) > 2:
                    exit(32)
                try:
                    arg1 = Argument(1, elem[0].attrib["type"], elem[0].text)
                    arg2 = Argument(2, elem[1].attrib["type"], elem[1].text)
                except IndexError:
                    exit(32)
                return Strlen(arg1, arg2, factoryOrder)
            case "ADD" | "SUB" | "MUL" | "IDIV":
                if len(elem) > 3:
                    exit(32)
                try:
                    arg1 = Argument(1, elem[0].attrib["type"], elem[0].text)
                    arg2 = Argument(2, elem[1].attrib["type"], elem[1].text)
                    arg3 = Argument(3, elem[2].attrib["type"], elem[2].text)
                except IndexError:
                    exit(32)
                return Operation(operation.upper(), arg1, arg2, arg3, factoryOrder)
            case "AND" | "OR" | "NOT":
                try:
                    arg1 = Argument(1, elem[0].attrib["type"], elem[0].text)
                    arg2 = Argument(2, elem[1].attrib["type"], elem[1].text)
                    if "NOT":
                        arg3 = arg2
                    else:
                        arg3 = Argument(3, elem[2].attrib["type"], elem[2].text)
                except IndexError:
                    exit(32)
                return BoolOperation(operation.upper(), arg1, arg2, arg3, factoryOrder)
            case "GETCHAR":
                if len(elem) > 3:
                    exit(32)
                try:
                    arg1 = Argument(1, elem[0].attrib["type"], elem[0].text)
                    arg2 = Argument(2, elem[1].attrib["type"], elem[1].text)
                    arg3 = Argument(3, elem[2].attrib["type"], elem[2].text)
                except IndexError:
                    exit(32)
                return Getchar(arg1, arg2, arg3, factoryOrder)
            case "JUMPIFEQ":
                try:
                    arg1 = Argument(1, elem[0].attrib["type"], elem[0].text)
                    arg2 = Argument(2, elem[1].attrib["type"], elem[1].text)
                    arg3 = Argument(3, elem[2].attrib["type"], elem[2].text)
                except IndexError:
                    exit(32)
                return Jumpifeq(arg1, arg2, arg3, factoryOrder)
            case "CONCAT":
                if len(elem) > 3:
                    exit(32)
                try:
                    arg1 = Argument(1, elem[0].attrib["type"], elem[0].text)
                    arg2 = Argument(2, elem[1].attrib["type"], elem[1].text)
                    arg3 = Argument(3, elem[2].attrib["type"], elem[2].text)
                except IndexError:
                    exit(32)
                return Concat(arg1, arg2, arg3, factoryOrder)
            case _:
                return None


if __name__ == '__main__':

    source = "stdin"
    inputFile = "stdin"
    tree = None

    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, help="Soubor pro načítání XML instrukcí")
    parser.add_argument("--input", type=str, help="Soubor pro vstupní data")

    #Ověření splnění podmínky, že byl zadán alespoň jeden argument
    if not (len(sys.argv) > 1):
        exit(10)
    args = parser.parse_args()

    #stdin
    if not args.source and not args.input:
        exit(10)
    if not args.source:
        try:
            tree = ET.parse(sys.stdin)
        except ET.ParseError:
            exit(31)
    else:
        try:
            tree = ET.parse(args.source)
        except FileNotFoundError:
            exit(31)
        except ET.ParseError:
            exit(31)

    if not args.input:
        inputFile = sys.stdin
    else:
        inputFile = open(args.input, "r")

    #Ověření správnosti proměnné tree
    if tree is None:
        exit(31)
    else:
        root = tree.getroot()

    i = 0
    labels = {} #Slovník pro jména návěští a pozice v kódě
    orders = [] #Seznam pozic
    calls = [] #Seznam pozic volání funkce CALL

    #Kontrola správnosti XML
    if root.tag != "program":
        exit(32)

    # Nalezení návěští a sběr pořadí instrukcí
    for elem in root:
        elem.set("executed", "False")
        opcode = ""
        order = 0
        try:
            order = elem.attrib["order"]
            opcode = elem.attrib["opcode"]
        except KeyError:
            exit(32)
        # Kontrola správnosti instrukcii v XML formate
        if elem.tag != "instruction":
            exit(32)
        try:
            order = int(order)
        except ValueError:
            exit(32)

        if order <= 0:
            exit(32)
        
        if opcode.upper() == "LABEL":
            exist = labels.get(elem[0].text)
            if exist is None:
                labels.update({elem[0].text: order})
            else:
                exit(52)

        orders.append(order)

    # Seřazení instrukcí podle pořadí
    orders = list(set(orders))
    orders.sort()


    if len(orders) != len(set(orders)):
        exit(32)

    lastOrder = orders[-1] #Poslední pořadí
    currOrder = orders[i] #Pořadí aktuální instrukce

    #Vykonání všech instrukcí
    # print("Before loop: currOrder =", currOrder)
    executedOrders = set()
    for i in range(len(orders)):
        currOrder = orders[i]
        

        element = None 

        # Nalezení aktuální instrukce
        for elem in root:
            if elem.attrib["order"] == str(currOrder):
                element = elem
                break

        opcode = element.attrib["opcode"]
        executed = element.attrib["executed"]

        opcodeUpper = opcode.upper()

        # print("Current instruction:", opcodeUpper)

        if executed == "True":
            # print("Skipping already executed instruction")
            executedOrders.add(currOrder)
            continue
        else:
            executedOrders.add(currOrder)

            match opcodeUpper:
                case "JUMP" | "CALL":
                    element.set("executed", "True")
                    label = labels.get(element[0].text)
                    if opcode.upper() == "CALL":
                        calls.append(order)

                    if label is None:
                        exit(52)
                    i = orders.index(label)

                case "JUMPIFEQ" | "JUMPIFNEQ":
                    element.set("executed", "True")
                    inst = Factory.resolve(opcode,  element)
                    jump = inst.execute()
                    if jump and opcode.upper() == "JUMPIFEQ":
                        label = labels.get(element[0].text)
                        if label is None:
                            exit(52)
                        i = orders.index(label)
                    elif not jump and opcode.upper() == "JUMPIFNEQ":
                        label = labels.get(element[0].text)
                        if label is None:
                            exit(52)
                        i = orders.index(label)
                case "RETURN":
                    element.set("executed", "True")
                    ret = calls.pop()
                    if i is None:
                        exit(56)
                    i = orders.index(ret)
                case "DEFVAR":
                    element.set("executed", "True")
                    # print("Executing DEFVAR instruction")
                    inst = Factory.resolve(opcode, element)
                    inst.execute()
                case "MOVE":
                    element.set("executed", "True")
                    # print("Executing MOVE instruction")
                    inst = Factory.resolve(opcode, element)
                    inst.execute()
                case ("WRITE" | "READ"):
                    element.set("executed", "True")
                    # print("Executing WRITE/READ instruction")
                    inst = Factory.resolve(opcode, element)
                    inst.execute()
                case "CREATEFRAME":
                    element.set("executed", "True")
                    # print("Executing CREATEFRAME instruction")
                    inst = Factory.resolve(opcode, element)
                    inst.execute()
                case "PUSHFRAME":
                    element.set("executed", "True")
                    # print("Executing PUSHFRAME instruction")
                    inst = Factory.resolve(opcode, element)
                    inst.execute()
                case "POPFRAME":
                    element.set("executed", "True")
                    # print("Executing POPFRAME instruction")
                    inst = Factory.resolve(opcode, element)
                    inst.execute()
                case "PUSHS":
                    element.set("executed", "True")
                    # print("Executing POPFRAME instruction")
                    inst = Factory.resolve(opcode, element)
                    inst.execute()
                case "POPS":
                    element.set("executed", "True")
                    # print("Executing POPFRAME instruction")
                    inst = Factory.resolve(opcode, element)
                    inst.execute()
                case "ADD" | "SUB" | "MUL" | "IDIV" | "LT" | "GT" | "EQ" | "AND" | "OR" | "NOT" | "INT2CHAR" | "STRI2INT":
                    element.set("executed", "True")
                    # print("Executing ADD (or other of the same kind) instruction")
                    inst = Factory.resolve(opcode, element)
                    inst.execute()
                case "CONCAT" | "STRLEN" | "GETCHAR" | "SETCHAR":
                    element.set("executed", "True")
                    # print("Executing CONCAT (etc) instruction")
                    inst = Factory.resolve(opcode, element)
                    inst.execute()
                case "TYPE":
                    element.set("executed", "True")
                    # print("Executing TYPE instruction")
                    inst = Factory.resolve(opcode, element)
                    inst.execute()
                case _:
                    inst = Factory.resolve(opcode, element)
                    if inst is None:
                        exit(32)
                    inst.execute()
                    element.set("executed", "True")
            
        i += 1
        if i >= len(orders):
            break
        else:
            currOrder = orders[i]

    # print("After loop: currOrder =", currOrder)