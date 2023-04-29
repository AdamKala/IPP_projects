# IPP Projekt 2
# interpret pro IPPcode23
# Hlavni program
# Autor: Adam Kala
# Login: xkalaa00
# Datum: 18.4.2023

import re
import sys
import xml.etree.ElementTree as et
import argparse as ap
import os
from varClass import Var

########################### Zakladni globalni promenne a tridy
### Trida pro argumenty
class Argument:
    def __init__(self, name, type):
        self.name = name
        self.type = type

### Trida pro instrukce a inicializace listu pro instrukce
class Instruction:
    def __init__(self, name, number):
        self.name = name
        self.number = number

### List pro instrukce
instructions = list()
        
### Promenne pro zasobnik
stack = []
dStack = []

### Promene pro navesti 
labels = {}

### Ramce
globalFrame = {}
localFrame = []
temporaryFrame = None

### List pro poradi 
orders = list()

### Pomocne promenne pro celkovy beh programu
argDict = {}
orderHelp = -1
currIndex = 0

### Prevzeti trid ze souboru varClass.py
varClass = Var(globalFrame, localFrame, temporaryFrame)

########################### Funkce zpracovani zakladnich chyb
### Funkce pro vypis chybove hlasky a ukonceni prislusnym vystupovym kodem
def errorFunction(message, error_code):
    print(message, file=sys.stderr)
    exit(error_code)

### Zda jsou spravne zadane argumenty (jejich pocet)
def numberOfArgs(instruction, number):
    help = len(instruction) 
    if help != number:
        errorFunction("Spatne argumenty instrukce.", 32)

########################### Funkce pro jednotlive instrukce
### Trida pro funkce
class Functions:
    def __init__(self, argDict):
        if len(argDict[orders[currIndex]]) > 0:
            self.type1 = argDict[orders[currIndex]][0].type
            self.symb1 = argDict[orders[currIndex]][0].name
        if len(argDict[orders[currIndex]]) > 1:
            self.type2 = argDict[orders[currIndex]][1].type
            self.symb2 = argDict[orders[currIndex]][1].name
        if len(argDict[orders[currIndex]]) > 2:
            self.type3 = argDict[orders[currIndex]][2].type
            self.symb3 = argDict[orders[currIndex]][2].name

    def MOVE(self):
        ### Vezmeme hodnote prejate z XML
        ### Pokud je to promenna, vezmeme pres getValue, jaka to je hodnota a jaky je jeji typ
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type2 == None:
            errorFunction("Type nemuze byt None.", 56)
        ### Ulozime pomoci setValue
        Var.setValue(self.symb1, self.type2, self.symb2, globalFrame, localFrame, temporaryFrame)

    def DEFVAR(self):
        ### Zjistime, jestli je to GF, TF nebo LF
        value = self.symb1
        value = value.strip()
        frame = value[:2]
        ### Zjistime, jak se ma promenna jmenovat
        name = value[3:]
        ### Ulozime podle prislusneho ramce
        if frame == "GF":
            if name in globalFrame:
                ### Pokud jiz existuje, ukonci se chybovym kodem 52
                errorFunction("Jmeno promenne jiz existuje.", 52)
            globalFrame[name] = {}
            globalFrame[name]["type"] = None
            globalFrame[name]["value"] = None
        elif frame == "LF":
            ### Pokud lokalni ramec neexistuje, ukonci se kodem 55
            if len(localFrame) == 0:
                errorFunction("Neexistuje.", 55)
            if name in localFrame[-1]:
                errorFunction("Jmeno promenne jiz existuje.", 52)
            localFrame[-1][name] = {}
            localFrame[-1][name]["type"] = None
            localFrame[-1][name]["value"] = None
        elif frame == "TF":
            ### Pokud docasny ramec neexistuje, ukonci se kodem 55
            if temporaryFrame == None:
                errorFunction("Neexistuje TF.", 55)
            if name in temporaryFrame:
                errorFunction("Jmeno promenne jiz existuje.", 52)
            temporaryFrame[name] = {}
            temporaryFrame[name]["type"] = None
            temporaryFrame[name]["value"] = None

    ## Aritmeticke, relacni, booleovske a konverzni instrukce
    def arithmetic(self):
        ### Vezmeme hodnoty argumentu z argDict (slovniku argumentu)
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type3 == "var":
            self.type3, self.symb3 = Var.getValue(self.symb3, globalFrame, localFrame, temporaryFrame)
        if self.type2 == None or self.type3 == None:
            errorFunction("Neidentifikovantelny.", 56)
        if self.type2 != "int" or self.type3 != "int":
            errorFunction("Musi byt int.", 53)
        if self.symb2 == None or self.symb3 == None:
            errorFunction("Nemuze byt None", 56)
        try:
            if instructions[currIndex].name == "ADD":
                result = int(self.symb2) + int(self.symb3)
            elif instructions[currIndex].name == "SUB":
                result = int(self.symb2) - int(self.symb3)
            elif instructions[currIndex].name == "MUL":
                result = int(self.symb2) * int(self.symb3)
            elif instructions[currIndex].name == "IDIV":
                if int(self.symb3) == 0:
                    errorFunction("Deleni 0 je zakazane.", 57)
                result = int(self.symb2) // int(self.symb3)
            Var.setValue(self.symb1, "int", result, globalFrame, localFrame, temporaryFrame)
        except ValueError:
            errorFunction("Spatna hodnota.", 32)
            
    def LTGT(self):
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type3 == "var":
            self.type3, self.symb3 = Var.getValue(self.symb3, globalFrame, localFrame, temporaryFrame)
        if self.type2 == None or self.type3 == None:
            errorFunction("Neidentifikovantelny.", 56)
        if not (self.type2 == self.type3):
            errorFunction("Musi byt stejny typ.", 53)
        if self.type2 == "nil" or self.type3 == "nil":
            errorFunction("Nesmi byt nil.", 53)
        if self.type2 == "int":          
            if instructions[currIndex].name == "LT":
                result = int(self.symb2) < int(self.symb3)
            elif instructions[currIndex].name == "GT":
                result = int(self.symb2) > int(self.symb3)
            if result == False:
                Var.setValue(self.symb1, "bool", "false", globalFrame, localFrame, temporaryFrame)
            if result == True:
                Var.setValue(self.symb1, "bool", "true", globalFrame, localFrame, temporaryFrame)
        elif self.type2 == "string":
            if instructions[currIndex].name == "LT":
                result = self.symb2 < self.symb3
            elif instructions[currIndex].name == "GT":
                result = self.symb2 > self.symb3
            if result == False:
                Var.setValue(self.symb1, "bool", "false", globalFrame, localFrame, temporaryFrame)
            if result == True:
                Var.setValue(self.symb1, "bool", "true", globalFrame, localFrame, temporaryFrame)
        else:
            if instructions[currIndex].name == "LT":
                result = self.symb2 < self.symb3
            elif instructions[currIndex].name == "GT":
                result = self.symb2 > self.symb3
            if result == False:
                Var.setValue(self.symb1, "bool", "false", globalFrame, localFrame, temporaryFrame)
            if result == True:
                Var.setValue(self.symb1, "bool", "true", globalFrame, localFrame, temporaryFrame)

    def EQ(self):
        result = None
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type3 == "var":
            self.type3, self.symb3 = Var.getValue(self.symb3, globalFrame, localFrame, temporaryFrame)
        if self.type2 == None or self.type3 == None:
            errorFunction("Neidentifikovantelny.", 56)
        if self.type2 == "nil" or self.type3 == "nil":
            if self.type2 == "nil" and self.type3 == "nil":
                Var.setValue(self.symb1, "bool", "true", globalFrame, localFrame, temporaryFrame)
            else:
                Var.setValue(self.symb1, "bool", "false", globalFrame, localFrame, temporaryFrame)
        else:
            if not (self.type2 == self.type3):
                errorFunction("Musi byt stejny typ nebo nil.", 53)
            if self.type2 == "int":          
                result = int(self.symb2) == int(self.symb3)
                if result == False:
                    Var.setValue(self.symb1, "bool", "false", globalFrame, localFrame, temporaryFrame)
                if result == True:
                    Var.setValue(self.symb1, "bool", "true", globalFrame, localFrame, temporaryFrame)
            elif self.type2 == "string":
                result = self.symb2 == self.symb3
                if result == False:
                    Var.setValue(self.symb1, "bool", "false", globalFrame, localFrame, temporaryFrame)
                if result == True:
                    Var.setValue(self.symb1, "bool", "true", globalFrame, localFrame, temporaryFrame)
            else:
                result = self.symb2 == self.symb3
                if result == False:
                    Var.setValue(self.symb1, "bool", "false", globalFrame, localFrame, temporaryFrame)
                if result == True:
                    Var.setValue(self.symb1, "bool", "true", globalFrame, localFrame, temporaryFrame)

    def AND(self):
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type3 == "var":
            self.type3, self.symb3 = Var.getValue(self.symb3, globalFrame, localFrame, temporaryFrame)
        if self.type2 == None or self.type3 == None:
            errorFunction("Neidentifikovantelny.", 56)
        if self.type2 != "bool" or self.type3 != "bool":
            errorFunction("Musi byt bool.", 53)
        if self.symb2 == "false":
            self.symb2 = False
        elif self.symb2 == "true":
            self.symb2 = True
        if self.symb3 == "false":
            self.symb3 = False
        elif self.symb3 == "true":
            self.symb3 = True
        try: 
            result = self.symb2 and self.symb3
            if result == False:
                result = "false"
            elif result == True:
                result = "true"
            Var.setValue(self.symb1, "bool", result, globalFrame, localFrame, temporaryFrame)
        except ValueError: 
            errorFunction("Chyba u AND.", 53)

    def OR(self):
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type3 == "var":
            self.type3, self.symb3 = Var.getValue(self.symb3, globalFrame, localFrame, temporaryFrame)
        if self.type2 == None or self.type3 == None:
            errorFunction("Neidentifikovantelny.", 56)
        if self.type2 != "bool" or self.type3 != "bool":
            errorFunction("Musi byt bool.", 53)
        if self.symb2 == "false":
            self.symb2 = False
        elif self.symb2 == "true":
            self.symb2 = True
        if self.symb3 == "false":
            self.symb3 = False
        elif self.symb3 == "true":
            self.symb3 = True
        try: 
            result = self.symb2 or self.symb3
            if result == False:
                result = "false"
            elif result == True:
                result = "true"
            Var.setValue(self.symb1, "bool", result, globalFrame, localFrame, temporaryFrame)
        except ValueError: 
            errorFunction("Chyba u OR.", 53)

    def NOT(self):
        self.symb = argDict[orders[currIndex]][0].name
        type1 = argDict[orders[currIndex]][1].type
        symb1 = argDict[orders[currIndex]][1].name
        if self.type2 == "var":
            self.type2, symb1 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type2 == None:
            errorFunction("Neidentifikovantelny.", 56)
        if self.type2 != "bool":
            errorFunction("Musi byt bool.", 53)
        if symb1 == "false":
            symb1 = False
        elif symb1 == "true":
            symb1 = True
        try: 
            result = not symb1
            if result == False:
                result = "false"
            elif result == True:
                result = "true"
            Var.setValue(self.symb1, "bool", result, globalFrame, localFrame, temporaryFrame)
        except ValueError: 
            errorFunction("Chyba u NOT.", 53)

    def INT2CHAR(self):
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        elif self.type2 != "int":
            errorFunction("Int2char pouze int.", 53)
        if self.type2 == None:
            errorFunction("Int2char pouze int.", 56)
        elif self.type2 != "int":
            errorFunction("Int2char pouze int.", 53)
        self.symb2 = int(self.symb2)
        try:
            trans = chr(self.symb2)
        except:
            errorFunction("Pouze platne ASCII.", 58)
        Var.setValue(self.symb1, "string", trans, globalFrame, localFrame, temporaryFrame)


    def STRI2INT(self):
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type3 == "var":
            self.type3, self.symb3 = Var.getValue(self.symb3, globalFrame, localFrame, temporaryFrame)
        elif self.type3 != "int":
            errorFunction("Int2char pouze int.", 53)
        if self.type3 == None or self.type2 == None:
            errorFunction("Int2char pouze int.", 56)
        elif self.type3 != "int" or self.type2 != "string":
            errorFunction("Int2char pouze int.", 53)
        lenght = len(self.symb2)
        index = int(self.symb3)
        if lenght < index or lenght == index or index < 0:
            errorFunction("Chybny index.", 58)
        ordered = ord(self.symb2[int(self.symb3)])
        type = None
        ordered, type = Var.getType(ordered)
        Var.setValue(self.symb1, type, ordered, globalFrame, localFrame, temporaryFrame)

    ## Vstupne-vystupni instrukce
    def READ(self, currIndex):     
        varValue = argDict[orders[currIndex]][0].name
        type = argDict[orders[currIndex]][1].type
        symb = argDict[orders[currIndex]][1].name
        read = ""

        ### Pokud se ve funkci read nenachazi type "type", ukonci se s chybou 32
        if type != "type":
            errorFunction("Chybny typ.", 32)
        if ParseFile.inputFile == sys.stdin:
            try:
                ### Precteme soubor
                read = input()
            except EOFError:
                ### Pokud se jedna o EOF, ulozi se hodnota do promenne nil@nil
                Var.setValue(varValue, "nil", "nil", globalFrame, localFrame, temporaryFrame)
        else:
            try:    
                ### Precteme jednotlive radky
                read = ParseFile.inputFile.readline()
            except EOFError:
                Var.setValue(varValue, "nil", "nil", globalFrame, localFrame, temporaryFrame)
        
        ### Pokud je prectena hodnota delky nula, ulozi se nil@nil
        if len(read) == 0:
            Var.setValue(varValue, "nil", "nil", globalFrame, localFrame, temporaryFrame)
        else:
            ### Pokud se jedna o konec radku, nebudeme tento symbol cist
            if read[-1] == "\n":
                read = read[:-1]

            ### Pokud se jedna i integer, ulozime jeho hodnotu, pokud to nepujde, ulozi se nil@nil
            if symb == "int":
                try:
                    Var.setValue(varValue, "int", int(read), globalFrame, localFrame, temporaryFrame)
                except:
                    Var.setValue(varValue, "nil", "nil", globalFrame, localFrame, temporaryFrame)
            ### Pokud se bude jednat o string, je prectena hodnota ulozena
            elif symb == "string":
                Var.setValue(varValue, "string", read, globalFrame, localFrame, temporaryFrame)
            ### Pokud se jedna o bool, cele prectene slovo se da na mala pismena a porovna s true nebo false
            ### Pokud bude delka retezce 5, ulozi se false, jinak nil@nil
            elif symb == "bool":
                if read.lower() == "true":
                    Var.setValue(varValue, "bool", "true", globalFrame, localFrame, temporaryFrame)
                elif read.lower() == "false":
                    Var.setValue(varValue, "bool", "false", globalFrame, localFrame, temporaryFrame)
                elif len(read) == 5:
                    Var.setValue(varValue, "bool", "false", globalFrame, localFrame, temporaryFrame)
                else:
                    Var.setValue(varValue, "nil", "nil", globalFrame, localFrame, temporaryFrame)


    def WRITE(self, currIndex):
        type1 = argDict[orders[currIndex]][0].type
        symb1 = argDict[orders[currIndex]][0].name
        if self.symb1 == None:
            print("")
        else:
            ### Pokud se jedna o promennou, ziska se jeji hodnota a podle prislusneho typu se vypise
            if self.type1 == "var":
                self.type1, self.symb1 = Var.getValue(self.symb1, globalFrame, localFrame, temporaryFrame)
                if self.type1 == None:
                    errorFunction("Neni definovano.", 56)
                if self.type1 == "int":
                    print(self.symb1, end="")
                elif self.type1 == "string":
                    print(self.symb1, end="")
                elif self.type1 == "bool":
                    if self.symb1 == "true":
                        print("true", end="")
                    elif self.symb1 == "false":
                        print("false", end="")
                elif self.type1 == "nil":
                    print("", end="")
                elif self.type1 == "string" and symb1 == "nil":
                    print("nil", end="")
                elif self.type1 == None and symb1 != None:
                    print(self.symb1, end="")

                if isinstance(self.symb1, list):
                    if self.symb1[0] != self.symb1[1]:
                        print(self.symb1[1], end="")
            else:
                ### Pokud to neni promenna, porovna se typ a prislusne vypise
                if self.type1 == "int":
                    print(self.symb1, end="")
                elif self.type1 == "string":
                    print(self.symb1, end="")
                elif self.type1 == "bool":
                    if self.symb1 == "true":
                        print("true", end="")
                    elif self.symb1 == "false":
                        print("false", end="")
                elif self.type1 == "nil":
                    print("", end="")
                elif self.type1 == "string" and self.symb1 == "nil":
                    print("nil", end="")
                elif self.type1 == None and self.symb1 != None:
                    print(self.symb1, end="")

                if isinstance(self.symb1, list):
                    if self.symb1[0] != self.symb1[1]:
                        print(self.symb1[1], end="")

    ## Prace s retezci
    def CONCAT(self, currIndex):
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type3 == "var":
            self.type3, self.symb3 = Var.getValue(self.symb3, globalFrame, localFrame, temporaryFrame)
        if self.type3 == None or self.type2 == None:
            errorFunction("Neexistuje.", 56)
        if self.type3 != "string" or self.type2 != "string":
            errorFunction("Musi byt string.", 53)
        Var.setValue(self.symb1, "string", self.symb2+self.symb3, globalFrame, localFrame, temporaryFrame)

    def STRLEN(self, currIndex):
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        elif self.type2 != "string":
            errorFunction("Strlen pouze string.", 53)
        if self.type2 == None:
            errorFunction("Strlen pouze string.", 56)
        elif self.type2 != "string":
            errorFunction("Strlen pouze string.", 53)
        Var.setValue(self.symb1, "int", len(self.symb2), globalFrame, localFrame, temporaryFrame)

    def GETCHAR(self, currIndex):
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type3 == "var":
            self.type3, self.symb3 = Var.getValue(self.symb3, globalFrame, localFrame, temporaryFrame)
        if self.type3 == None or self.symb2 == None:
            errorFunction("Chyba getchar.", 56)
        if self.type3 == None or self.symb3 == None:
            errorFunction("Chyba getchar.", 56)
        if self.type2 != "string":
            errorFunction("Chyba getchar.", 53)
        if self.type3 != "int":
            errorFunction("Chyba getchar.", 53)
        lenght = len(self.symb2)
        index = int(self.symb3)
        ### Pokud je zadana hodnota < 0, nebo prepisovany index neexistuje, ukonci se s 58
        if lenght < index or lenght == index or index < 0:
            errorFunction("Chyba getchar.", 58)
        self.symb3 = int(self.symb3)
        result = self.symb2[self.symb3]
        Var.setValue(self.symb1, "string", result, globalFrame, localFrame, temporaryFrame)
        

    def SETCHAR(self, currIndex):
        if self.type1 == "var":
            self.type1, symb0 = Var.getValue(self.symb1, globalFrame, localFrame, temporaryFrame)
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type3 == "var":
            self.type3, self.symb3 = Var.getValue(self.symb3, globalFrame, localFrame, temporaryFrame)
        if self.type2 == None or self.symb2 == None or self.type3 == None or self.symb3 == None or symb0 == None or self.type1 == None:
            errorFunction("Chyba setchar.", 56)
        if self.type2 != "int" or self.type1 == "int" or self.type1 == "bool" or self.type1 == "nil" or self.type3 != "string":
            errorFunction("Chyba setchar.", 53)
        lenght = len(symb0)
        index = int(self.symb2)
        if lenght < index or lenght == index or index < 0 or self.symb3 == "":
            errorFunction("Chyba setchar.", 58)
        result = list(symb0)
        
        self.symb2 = int(self.symb2)

        result[self.symb2] = self.symb3[0]
        result = "".join(result)
        Var.setValue(self.symb1, "string", result, globalFrame, localFrame, temporaryFrame)

    ## Prace s typy
    def TYPE(self, currIndex):
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type2 == None:
            Var.setValue(self.symb1, "nothing", "nothing", globalFrame, localFrame, temporaryFrame)
            return
        if self.type2 == "nil" and self.symb2 == "nil":
            Var.setValue(self.symb1, "string", "nil", globalFrame, localFrame, temporaryFrame)
        elif self.type2 == "int":
            Var.setValue(self.symb1, "int", self.type2, globalFrame, localFrame, temporaryFrame)
        else:
            Var.setValue(self.symb1, "string", self.type2, globalFrame, localFrame, temporaryFrame)
        return

    ## Ladici instrukce
    def EXITFNC(self):            
        if self.type1 == "var":
            self.type1, self.symb1 = Var.getValue(self.symb1, globalFrame, localFrame, temporaryFrame)
        if self.type1 == None or self.symb1 == None:
            errorFunction("Neni nadefinovane.", 56)
        if self.type1 != "int":
            errorFunction("Spatny datovy typ.", 53)
        self.symb1 = int(self.symb1)    
        if self.symb1 > 49 or self.symb1 < 0:
            errorFunction("Spatny navratovy typ.", 57)
        exit(self.symb1)

    ### Pokud existuje navesti, ulozi se jeho hodnota do currIndex
    def CALL(self, currIndex, stack, labels):
        stack.append(currIndex)
        if self.symb1 in labels:
            currIndex = labels[self.symb1]
        else:
            errorFunction("Chybne navesti.", 52)
        return currIndex

    def RETURN(self, currIndex, stack):
        if len(stack) == 0:
                errorFunction("Return chyba.", 56)
        currIndex = stack.pop()
        return currIndex, stack

    def PUSHS(self, dStack):
        if self.type1 == "var":
            self.type1, self.symb1 = Var.getValue(self.symb1, globalFrame, localFrame, temporaryFrame)
        if self.symb1 == None:
            errorFunction("Neni nadefinovano.", 56)
        dStack.append([self.type1, self.symb1])
        return dStack

    def POPS(self, dStack):
        if len(dStack) == 0:
            errorFunction("Nejde popnout prazdny stack.", 56)
        Var.setValue(self.symb1, "", dStack.pop(), globalFrame, localFrame, temporaryFrame)
        return dStack

    ### Vytvoreni prazdneho ramce
    def CREATEFRAME(self):
        temporaryFrame = {}
        return temporaryFrame

    ### Pokud lokalni ramec existuje, popne se do docasneho
    def POPFRAME(self, localFrame):
        help = len(localFrame)
        if help == 0:
            errorFunction("Ramec LF neexituje.", 55)
        temporaryFrame = localFrame.pop()
        return temporaryFrame, localFrame

    def PUSHFRAME(self, temporaryFrame):
        if temporaryFrame == None:
            errorFunction("Ramec TF neexituje.", 55)
        else:
            localFrame.append(temporaryFrame)
            temporaryFrame = None
        return temporaryFrame, localFrame

    def LABEL(self, labels, currIndex):
        labels[self.symb1] = currIndex
        return labels, currIndex

    ### Zjisti se zda navesti existuje a podle toho se vrati currIndex
    def JUMP(self, labels, currIndex):
        if self.symb1 in labels:
            currIndex = labels[self.symb1]
        else:
            errorFunction("Chybne navesti.", 52)
        return currIndex

    def JUMPIFEQN(self, labels, currIndex):
        if self.type2 == "var":
            self.type2, self.symb2 = Var.getValue(self.symb2, globalFrame, localFrame, temporaryFrame)
        if self.type3 == "var":
            self.type3, self.symb3 = Var.getValue(self.symb3, globalFrame, localFrame, temporaryFrame)
        if self.type2 == "int" and self.type3 == "int":
            self.symb2 = int(self.symb2)
            self.symb3 = int(self.symb3)
        if self.type2 == None or self.type3 == None:
            errorFunction("Neni nadefinovano.", 56)
        if self.type2 == self.type3:
            if self.symb1 not in labels:
                errorFunction("Navesti neexistuje.", 52)
            if instructions[currIndex].name == "JUMPIFEQ":
                if self.symb2 == self.symb3:
                    if self.symb1 not in labels:
                        errorFunction("Navesti neexistuje.", 52)
                    else:
                        currIndex = labels[self.symb1]
                return currIndex
            elif instructions[currIndex].name == "JUMPIFNEQ":
                if self.symb2 != self.symb3:
                    if self.symb1 not in labels:
                        errorFunction("Navesti neexistuje.", 52)
                    else:
                        currIndex = labels[self.symb1]
                return currIndex
        elif self.type2 == "nil" or self.type3 == "nil":
            if self.symb1 not in labels:
                errorFunction("Navesti neexistuje.", 52)
            if instructions[currIndex].name == "JUMPIFEQ":
                if self.symb2 == self.symb3:
                    if self.symb1 not in labels:
                        errorFunction("Navesti neexistuje.", 52)
                    else:
                        currIndex = labels[self.symb1]
                return currIndex
            elif instructions[currIndex].name == "JUMPIFNEQ":
                if self.symb2 != self.symb3:
                    if self.symb1 not in labels:
                        errorFunction("Navesti neexistuje.", 52)
                    else:
                        currIndex = labels[self.symb1]
                return currIndex
        else:
            errorFunction("Ruzne typy operandu.", 53)

    ### Funkce pro vypsani aktualni hodnoty na chybovy vystup
    def DPRINT(self):
        if self.type1 == "var":
            self.type1, self.symb1 = Var.getValue(self.symb1, globalFrame, localFrame, temporaryFrame)
        print(self.symb1, file=sys.stderr)

    ### Funkce na vypsani momentalni instrukce, jeji hodnoty a na jake jsme pozici
    def BREAK(self):
        type = argDict[orders[currIndex-1]][0].type
        symb = argDict[orders[currIndex-1]][0].name
        print("Momentalni typ instrukce:"+type+"\n", "Momentalni hodnota v instrukci:",symb,"\n", "Jsme na pozici:", currIndex, file=sys.stderr)

########################### Funkce pro zpracovani, zda existuje source/input soubor
class ParseFile:
    tree = None

    def __init__(self):
        self.argParser = ap.ArgumentParser(add_help=False)
        self.argParser.add_argument("--source", type=str, help="Source file path.")
        self.argParser.add_argument("--input", type=str, help="Input file path.")
        self.argParser.add_argument("--help", action="store_true")
        self.args = self.argParser.parse_args()

    ### Funkce pro zkontrolovani argumenty prikazoveho radku a pripadne otevreni souboru
    def run(self):
        if self.args.help:
            errorFunction("Použití skriptu: [python] interpret.py [--source=file | --input=file]", 0)
        if not self.args.source and not self.args.input and not self.args.help:
            self.errorFunction("Alespoň jeden z parametrů --source nebo --input musí být zadán.", 10)
        else:
            if self.args.source and not os.path.isfile(str(self.args.source)):
                self.errorFunction("Soubor nenalezen.", 11)
            if self.args.input and not os.path.isfile(str(self.args.input)):
                self.errorFunction("Soubor nenalezen.", 11)

        if not self.args.source:
            sourceFile = sys.stdin
        else:
            sourceFile = open(self.args.source, "r")

        if not self.args.input:
            ParseFile.inputFile = sys.stdin
        else:
            ParseFile.inputFile = open(self.args.input, "r")

        ## Inicializace "stromu"
        try:
            ParseFile.tree = et.parse(sourceFile)
        except:
            self.errorFunction("Chyba u XML souboru.", 31)

    def errorFunction(self, message, exitCode):
        print(message, file=sys.stderr)
        sys.exit(exitCode)

########################### Zpracovani, zda je XML vstup spravny
class CheckXML:
    def checker(self, root):    
        ### Kontrola jestli je v miste instrukce napsane neco jineho nez "instruction"
        for instr in root:
            if instr.tag != "instruction":
                errorFunction("Chybny XML format.", 32)

        ### Kontrola jestli je opcode pouze ve formatu "opcode"
        for instr in root:
            if "opcode" not in instr.attrib:
                errorFunction("Chybny XML format.", 32)

        prevOrder = 0
        for instr in root.findall(".//instruction"):
            order = int(instr.attrib.get("order", 0))
            ### Pokud je dvakrat stejna hodnota argumentu, chyba
            if order <= prevOrder:
                errorFunction("Chybna instrukce.", 32)
            prevOrder = order

            arg1Exists = False
            arg2Exists = False
            arg3Exists = False

            ### Pokud jsou argumenty jine nez arg1 arg2 arg3 a jestli je jejich hodnota spravna
            for arg in instr:
                argType = arg.attrib.get("type")
                argName = arg.tag.strip()
                if argName == "arg1":
                    if arg1Exists == True:
                        errorFunction("Chybny argument.", 32)
                    arg1Exists = True
                    if argType not in ["int", "bool", "string", "var", "label", "nil", "float", "type"]:
                        errorFunction("Chybny argument.", 32)
                elif argName == "arg2":
                    arg2Exists = True
                    if arg1Exists == True and argType not in ["int", "bool", "string", "var", "label", "nil", "float", "type"]:
                        errorFunction("Chybny argument.", 32)
                elif argName == "arg3":
                    arg3Exists = True
                    if arg1Exists == True and arg2Exists == True and argType not in ["int", "bool", "string", "var", "label", "nil", "float", "type"]:
                        errorFunction("Chybny argument.", 32)
                else:
                    errorFunction("Chybny argument.", 32)

            ### Pokud napriklad existuje arg2 arg3 ale neexistuje arg1
            if arg2Exists and not arg1Exists:
                errorFunction("Chybny argument.", 32)
            if arg3Exists and not arg1Exists and not arg2Exists:
                errorFunction("Chybny argument.", 32)

########################### Ziskani "rootu" a pripadne serazeni orderu
fileCheck = ParseFile()
fileCheck.run()

root = ParseFile.tree.getroot()
try:
    ### Serazeni poradi instrukci
    root[:] = sorted(root, key=lambda child:int(child.get("order")))
except:
    errorFunction("Chyba.", 32)

checkerXML = CheckXML()
checkerXML.checker(root)

########################### Prochazeni vsech instrukci, ulozeni jednotlivych argumentu a 
# volani funkce pro spravny pocet argumentu podle opcode
# Ukladani navestich
for instr in root:
    opcode = instr.get("opcode")
    opcode = opcode.upper()
    orders.append(instr.get("order"))
    args = []

    orderHelp += 1
    ### Ziskani vsech navesti
    if opcode == "LABEL":
        label = instr.find("arg1").text
        if label in labels:
            errorFunction("Label jiz existuje.", 52)
        labels[label] = orderHelp
    
    ### Prochazime serazene argumenty a ukladame jejich hodnoty
    for arg in sorted(instr.iter(), key=lambda x: int(x.tag[3:]) if x.tag.startswith("arg") else 0):
        if arg.tag.startswith("arg"):
            argType = arg.get("type")
            argValue = arg.text
            if argType == "string" and argValue == None:
                args.append(Argument("", argType))
            elif argType == "string":
                argValue = argValue.strip()
                ### Pokud je to string, nahradime jejich hodnoty dle zadani
                if "\\035" in argValue:
                    argValue = argValue.replace("\\035", "#")
                if "\\092" in argValue:
                    argValue = argValue.replace("\\092", "\\")
                if "\\010" in argValue:
                    argValue = argValue.replace("\\010", "\n")
                for string in re.findall(r"\\([0-9]{3})", argValue):
                    result = chr(int(string))
                    argValue = argValue.replace(f"\\{string}", result)
                ### Do args ukladame ziskany typ a hodnotu
                args.append(Argument(argValue, argType))
            else:
                args.append(Argument(argValue, argType))
    ### Ukladame argumenty do slovniku argumentu
    argDict[orders[-1]] = args
    ### Ukladame instrukce do slovniku instrukci
    instructions.append(Instruction(opcode.upper(), orders[-1]))

    ### Podle nazvu opcode kontrolujeme, zda byl zadan spravny pocet argumentu
    if opcode == "CREATEFRAME" or opcode == "PUSHFRAME" or opcode == "POPFRAME":
        numberOfArgs(instr, 0)
    elif opcode == "DEFVAR" or opcode == "CALL" or opcode == "POPS" or opcode == "PUSHS":
        numberOfArgs(instr, 1)
    elif opcode == "RETURN" or opcode == "BREAK":
        numberOfArgs(instr, 0)
    elif opcode == "ADD" or opcode == "SUB" or opcode == "MUL" or opcode == "IDIV":
        numberOfArgs(instr, 3)
    elif opcode == "LT" or opcode == "EQ" or opcode == "AND" or opcode == "OR":
        numberOfArgs(instr, 3)
    elif opcode == "NOT" or opcode == "INT2CHAR" or opcode == "READ" or opcode == "STRLEN" or opcode == "TYPE" or opcode == "MOVE":
        numberOfArgs(instr, 2)
    elif opcode == "STRI2INT" or opcode == "CONCAT" or opcode == "GETCHAR" or opcode == "SETCHAR":
        numberOfArgs(instr, 3)
    elif opcode == "WRITE" or opcode == "LABEL" or opcode == "JUMP" or opcode == "EXIT" or opcode == "DPRINT":
        numberOfArgs(instr, 1)
    elif opcode == "JUMPIFEQ" or opcode == "JUMPIFNEQ":
        numberOfArgs(instr, 3)

########################### Prochazeni instrukci, skakani do prislusnych funkci pro instrukce
# Current Index bude sledovat, na jakem indexu se mame nachazet
# Pri kazdem vstupu do cyklu se nastavi argDict, aby pote prosla podminka ve tride
# Funkce jede, dokud nenarazi na posledni prvek, ktery je ulozen v orderHelp+1. Ten byl inkrementovat ve funkci pro navesti
while currIndex < orderHelp+1:
    funct = Functions(argDict)
    if currIndex < orderHelp+1:
        if instructions[currIndex].name == "MOVE":
            funct.MOVE()
        elif instructions[currIndex].name == "CREATEFRAME":
            temporaryFrame = funct.CREATEFRAME()
        elif instructions[currIndex].name == "PUSHFRAME":
            temporaryFrame, localFrame = funct.PUSHFRAME(temporaryFrame)
        elif instructions[currIndex].name == "POPFRAME":
            temporaryFrame, localFrame = funct.POPFRAME(localFrame)
        elif instructions[currIndex].name == "DEFVAR":
            funct.DEFVAR()
        elif instructions[currIndex].name == "CALL":
            currIndex = funct.CALL(currIndex, stack, labels)
        elif instructions[currIndex].name == "RETURN":
            currIndex, stack = funct.RETURN(currIndex, stack)
        elif instructions[currIndex].name == "PUSHS":
            dStack = funct.PUSHS(dStack)
        elif instructions[currIndex].name == "POPS":
            dStack = funct.POPS(dStack)
        elif instructions[currIndex].name == "ADD" or instructions[currIndex].name == "SUB" or instructions[currIndex].name == "MUL" or instructions[currIndex].name == "IDIV":
            funct.arithmetic()
        elif instructions[currIndex].name == "LT" or instructions[currIndex].name == "GT":
            funct.LTGT()
        elif instructions[currIndex].name == "EQ":
            funct.EQ()
        elif instructions[currIndex].name == "AND":    
            funct.AND()
        elif instructions[currIndex].name == "OR":
            funct.OR()
        elif instructions[currIndex].name == "NOT":
            funct.NOT()
        elif instructions[currIndex].name == "INT2CHAR":
            funct.INT2CHAR()
        elif instructions[currIndex].name == "STRI2INT":
            funct.STRI2INT()
        elif instructions[currIndex].name == "READ":
            funct.READ(currIndex)
        elif instructions[currIndex].name == "WRITE":
            funct.WRITE(currIndex)
        elif instructions[currIndex].name == "CONCAT":
            funct.CONCAT(currIndex)
        elif instructions[currIndex].name == "STRLEN":
            funct.STRLEN(currIndex)
        elif instructions[currIndex].name == "GETCHAR":
            funct.GETCHAR(currIndex)
        elif instructions[currIndex].name == "SETCHAR":
            funct.SETCHAR(currIndex)
        elif instructions[currIndex].name == "TYPE":
            funct.TYPE(currIndex)
        elif instructions[currIndex].name == "LABEL":
            labels, currIndex = funct.LABEL(labels, currIndex)
        elif instructions[currIndex].name == "JUMP":
            currIndex = funct.JUMP(labels, currIndex)
        elif instructions[currIndex].name == "JUMPIFEQ" or instructions[currIndex].name == "JUMPIFNEQ":
            currIndex = funct.JUMPIFEQN(labels, currIndex)
        elif instructions[currIndex].name == "EXIT":
            funct.EXITFNC()
        elif instructions[currIndex].name == "DPRINT":
            funct.DPRINT()
        elif instructions[currIndex].name == "BREAK":
            funct.BREAK()
        else:
            errorFunction("Chybovy opcode.", 32)
        currIndex += 1
    else:
        exit(0)