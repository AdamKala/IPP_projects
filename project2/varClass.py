# IPP Projekt 2
# Interpret pro IPPcode23
# Trida pro promenne
# Autor: Adam Kala
# Login: xkalaa00
# Datum: 18.4.2023

import re

########################### Trida pro praci s promennou
class Var:
    def __init__(self, globalFrame, localFrame, temporaryFrame):
        self.globalFrame = globalFrame
        self.localFrame = localFrame
        self.temporaryFrame = temporaryFrame

    ### Staticka metoda pro ziskani typu promenne
    @staticmethod
    def getType(varGet):
        typeGet = None
        if isinstance(varGet, int):
            typeGet = "int"
        elif re.match(r"^[+-]?\d+(\.\d+)?$", varGet):
            typeGet = "int"
        elif re.match(r"^(true|false)$", varGet):
            typeGet = "bool"
        elif re.match(r"^(nil)$", varGet):
            typeGet = "nil"
        elif re.match(r"^[+-]?(?:0[xX][0-9a-fA-F]+\.[0-9a-fA-F]*|\d+\.\d*)(?:[eE][+-]?\d+)?$", varGet):
            typeGet = "float"
        elif re.match(r"^((\\[0-9]{3})|[^#\s\\])*$", varGet):
            typeGet = "string"
            varGet = re.sub(r"\\[0-9]{3}", "", varGet)
        return varGet, typeGet

    ### Staticka metoda pro ziskani hodnoty a typu ze slovniku
    @staticmethod
    def getValue(varGet, globalFrame, localFrame, temporaryFrame):
        varGet = varGet.strip()
        frame = varGet[:2]
        name = varGet[3:]
        valueGet = None

        if frame == "GF":
            if name not in globalFrame:
                exit(54)
            typeGet = globalFrame[name]["type"]
            if typeGet == "":
                typeGet, valueGet = globalFrame[name]["value"]
            else:
                valueGet = globalFrame[name]["value"]
            return typeGet, valueGet
        elif frame == "LF":
            if len(localFrame) == 0:
                exit(55)
            if name not in localFrame[-1]:
                exit(54)
            valueGet = localFrame[-1][name]["value"]
            typeGet = localFrame[-1][name]["type"]
            return typeGet, valueGet
        elif frame == "TF":
            if temporaryFrame == None:
                exit(55)
            if name not in temporaryFrame:
                exit(54)
            valueGet = temporaryFrame[name]["value"]
            typeGet = temporaryFrame[name]["type"]
            return typeGet, valueGet
        else:
            exit(52)

    ### Staticka trida pro zapsani hodnoty a typu do promenne
    @staticmethod
    def setValue(varSet, typeSet, symbSet, globalFrame, localFrame, temporaryFrame):
        varSet = varSet.strip()
        frameSet = varSet[:2] #jestli GF, TF atd.
        nameSet = varSet[3:] # napr. GF@name
        
        if frameSet == "GF":
            if nameSet not in globalFrame:
                exit(54)
            globalFrame[nameSet]["type"] = typeSet    # int
            globalFrame[nameSet]["value"] = symbSet   # 2s
        elif frameSet == "LF":
            if len(localFrame) ==  0:
                exit(55)
            if nameSet not in localFrame[-1]:
                exit(54)
            localFrame[-1][nameSet]["type"] = typeSet
            localFrame[-1][nameSet]["value"] = symbSet
        elif frameSet == "TF":
            if temporaryFrame == None:
                exit(55)
            if nameSet not in temporaryFrame:
                exit(54)
            temporaryFrame[nameSet]["type"] = typeSet
            temporaryFrame[nameSet]["value"] = symbSet
        else:
            exit(52)
