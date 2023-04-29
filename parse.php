<?php
ini_set('display_errors', 'stderr');

// Funkce pro odstraneni problematickych znaku v XML
function special_chars($line){
    if(strpos($line, '&') !== false){
    $line = str_replace("&", "&amp;", $line);
    }
    if(strpos($line, '<') !== false){
    $line = str_replace("<", "&lt;", $line);
    }
    if(strpos($line, '>') !== false){
    $line = str_replace(">", "&gt;", $line);
    }
    return $line;
}

// Funkce pro rozhodnuti o jaky typ se jedna
function decidetype($xx){
    if(preg_match("/^(int|string|bool)$/", $xx)){
        return "type";
    } else if(preg_match("/(int)@(.*)$/", $xx)){
        return "int";
    } else if(preg_match("/(bool)@(true|false)/", $xx)){
        return "bool";
    } else if(preg_match("/(\bnil\b)@(\bnil\b)/", $xx)){
        return "nil";
    } else if(preg_match("/(string)@(.*)/", $xx)){
        return "string";
    } else if(preg_match("/^(LF|GF|TF)@(.*)$/", $xx)){
        return "var";
    } else if(preg_match("/^[a-zA-Z?*!%&_\-$][a-zA-Z?*!%&_$\-0-9]*$/", $xx)){
        return "label";
    }
}

// Funkce pro vypis funkce
function instruction($arg,$skip,$number){
    echo("\t<instruction order=\"".$number."\" opcode=\"".strtoupper($skip[0])."\">\n");
    for($i = 1; $i <= $arg; $i++){
        if(preg_match("/(LF|GF|TF)@(.*)/", $skip[$i])){
            echo("\t\t<arg$i type=\"".decidetype($skip[$i])."\">$skip[$i]</arg$i>\n");
        } else if($skip[0] == "READ" && $i == 2){
                echo("\t\t<arg$i type=\"type\">$skip[$i]</arg$i>\n");
        } else {
            if(preg_match("/(int|string|bool|nil)@(.*)/", $skip[$i], $matches)){
            echo("\t\t<arg$i type=\"".decidetype($skip[$i])."\">$matches[2]</arg$i>\n");
            } else if(preg_match("/(label)/", $skip[$i], $matches)){
                echo("\t\t<arg$i type=\"label\">label</arg$i>\n");
            }
        }
    }
    echo("\t</instruction>\n");
}

// Funkce pro vypis souboru bez hlavicky
function noheader(){
    echo('<?xml version="1.0" encoding="UTF-8"?>');
    echo("\n");
    echo('<program language="IPPcode23"/>');
    echo("\n");
}

// Vypis souboru s hlavickou
function yesheader(){
    echo('<?xml version="1.0" encoding="UTF-8"?>');
    echo("\n");
    echo('<program language="IPPcode23">');
    echo("\n");
}

// Vypis konce programu
function callend(){
    echo("</program>");
}

// Odstraneni komentare a volani funkce pro odstraneni problematickych znaku
function mline(string $line){
    $line = special_chars($line);
    $line = trim($line);
    $note = strpos($line, "#");
    if($note === false){
        return $line;
    }
    return trim(substr($line, 0, $note));
}

// Spravnost typu
function checktype($type){
    if(preg_match("/^(int|string|bool)$/", $type)){
        return true;
    } else {
        return false;
    }
}

// Spravnost int, pro vsechny typy cisel
function checkint($int){
    if(preg_match("/^int@[+|-]?0[xX][0-9a-fA-F]+(?:_[0-9a-fA-F]+)*$/", $int)    //hexadecimalni cisla
    || preg_match("/^int@[+|-]?(0[oO][0-7]+|[0-7]+)$/", $int)                   //oktalova cisla
    || preg_match("/^int@[+|-]?\d+(?:_\d+)+/", $int)){                          //dekadicka cisla
        return true;
    } else {
        return false;
    }
}

// Spravnost bool
function checkbool($bool){
    if(preg_match("/^(bool)@(true|false)$/", $bool)){
        return true;
    } else {
        return false;
    }
}

// Spravnost nil
function checknil($nil){
    if(preg_match("/(\bnil\b)@(\bnil\b)/", $nil)){
        return true;
    } else {
        return false;
    }
}

// Spravnost stringu
function checkstring($string){
    if(preg_match("/(string)@([^\\\]|\\\[0-9][0-9][0-9])*$/", $string)){
        return true;
    } else {
        return false;
    }
}

// Spravnost var
function checkvar($var){
    if(preg_match("/(LF|GF|TF)@[a-zA-Z?*!%;&_$][a-zA-Z?*!%;&_$0-9]*$/", $var)){
        return true;
    } else {
        return false;
    }
}

// Volani vsech funkci, zda splnuji pozadavky, symbol muze byt i var
function checksymbol($symbol){
    if(checkint($symbol) || checkbool($symbol) || checknil($symbol) || checkstring($symbol) || checkvar($symbol)){
        return true;
    } else {
        return false;
    }
}

// Spravnost label
function checklabel($label){
    if(preg_match("/^[a-zA-Z?*!%&_\-$][a-zA-Z?*!%&_$\-0-9]*$/", $label)){
        return true;
    } else {
        return false;
    }
}

// Funkce pro zapisovani instrukci dle jejich poctu argumentu
function labelonly($skip, $number){
    if($skip[2] != ""){
        exit(23);
    }     
    if(checklabel($skip[1]) == true){       
        echo("\t<instruction order=\"".$number."\" opcode=\"".strtoupper($skip[0])."\">\n");
        echo("\t\t<arg1 type=\"label\">$skip[1]</arg1>\n");
        echo("\t</instruction>\n");
    } else {
        exit(23);
    }
}

function noargs($skip, $number){
    if($skip[1] != ""){
        exit(23);
    }            
    instruction(0, $skip, $number);
}

function onearg($skip, $number){
    if($skip[2] != ""){
        exit(23);
    }            
    if(checkvar($skip[1]) == false){
        exit(23);
    }   
    instruction(1, $skip, $number);
}

function onearg1($skip, $number){
    if($skip[2] != ""){
        exit(23);
    }            
    if((checksymbol($skip[1]) == false) || checklabel($skip[1]) == true){
        exit(23);
    }   
    instruction(1, $skip, $number);
}

function twoargs($skip, $number){
    if($skip[3] != ""){
        exit(23); 
    }            
    if((checkvar($skip[1]) == false) || 
    ((checksymbol($skip[2])) == false)){
        exit(23);
    }    
    instruction(2, $skip, $number);
}

function twoargs1($skip, $number){
    if($skip[3] != ""){
        exit(23);
    }            
    if((checkvar($skip[1]) == false) || (checktype($skip[2]) == false)){
        exit(23);
    }   
    instruction(2, $skip, $number);
}

function threeargs1($skip, $number){
    if($skip[4] != ""){
        exit(23);
    }            

    if((checkvar($skip[1]) == false) || 
    (checksymbol($skip[2]) == false) || 
    (checksymbol($skip[3]) == false)){
        exit(23);
    }    
    instruction(3, $skip, $number);
}

function threeargs2($skip, $number){
    if($skip[4] != ""){
        exit(23);
    }            
    if((checklabel($skip[1]) == false) || 
    (checksymbol($skip[2]) == false) || 
    (checksymbol($skip[3]) == false)){
        exit(23);
    }     
    instruction(3, $skip, $number);
}

// Vypsani help
if($argc > 1 && $argv[1] == "--help"){
    echo("Pouziti skriptu: parse.php [nastaveni] <file\n");
    exit(0);
}

$number = 0;
$header = false;

// While cyklus pro vsechny radky v souboru
while($line = fgets(STDIN)){
    $line = mline($line);               // Volani funkce pro oddeleni poznamky a problematickych znaku
    $skip = preg_split('/\s+/', $line); // Rozdeli slova podle mezery/mezer

    // If pro spravne fungovani, kdyz je prvni radek poznamka
    if($line == NULL){
        continue;
    }

    // Dvojita hlavicka
    if($header == true && $line == ".IPPcode23"){
        exit(22);
    }

    // Neni hlavicka
    if($header == false && $skip[0][0] == ""){
        noheader();
        exit(0);
    }   
     
    // Overeni, zda je spravne zapsany prvni radek (hlavicka)
    if($header == false && preg_match("/(.[i|I][p|P][p|P][c|C][o|O][d|D][e|E]23)$/", $skip[0])){
        $header = true;
        yesheader();
        continue;
    } else if($header == false && ((preg_match("/(.[i|I][p|P][p|P][c|C][o|O][d|D][e|E]23)$/", $skip[0]) == false) || $skip[0] != "#")){
        exit(21);
    }

    // Switch dle ramce
    switch(strtoupper($skip[0])){
        case 'MOVE': //dodelat
            $number++;
            twoargs($skip, $number);
            break;
        case 'CREATEFRAME':
            $number++;
            noargs($skip, $number);
            break;
        case 'PUSHFRAME':
            $number++;
            noargs($skip, $number);
            break;
        case 'POPFRAME':
            $number++;
            noargs($skip, $number);
            break;
        case 'DEFVAR':
            $number++;
            onearg($skip, $number);
            break;
        case 'CALL':
            $number++;
            labelonly($skip, $number);
            break;
        case 'RETURN':
            $number++;
            noargs($skip, $number);
            break;
        case 'PUSHS':
            $number++;
            onearg1($skip, $number);
            break;
        case 'POPS':
            $number++;
            onearg($skip, $number);
            break;
        case 'ADD':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'SUB':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'MUL':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'IDIV':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'LT':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'GT':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'EQ':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'AND':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'OR':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'NOT':
            $number++;
            twoargs($skip, $number);
            break;
        case 'INT2CHAR':
            $number++;
            twoargs($skip, $number);
            break;
        case 'STRI2INT':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'READ':
            $number++;
            twoargs1($skip, $number);
            break;
        case 'WRITE':
            $number++;
            onearg1($skip, $number);
            break;
        case 'CONCAT':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'STRLEN':
            $number++;
            twoargs($skip, $number);
            break;
        case 'GETCHAR':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'SETCHAR':
            $number++;
            threeargs1($skip, $number);
            break;
        case 'TYPE':
            $number++;
            twoargs($skip, $number);
            break;
        case 'LABEL':
            $number++;
            labelonly($skip, $number);
            break;
        case 'JUMP':
            $number++;
            labelonly($skip, $number);
            break;
        case 'JUMPIFEQ':
            $number++;
            threeargs2($skip, $number);
            break;
        case 'JUMPIFNEQ':
            $number++;
            threeargs2($skip, $number);
            break;
        case 'EXIT':
            $number++;
            onearg1($skip, $number);
            break;
        case 'DPRINT':
            $number++;
            onearg1($skip, $number);
            break;
        case 'BREAK':
            $number++;
            noargs($skip, $number);
            break;
        default: 
            exit(22);
    }
}
// Zavolani funkce pro vypsani konce
callend();
exit(0);
?>