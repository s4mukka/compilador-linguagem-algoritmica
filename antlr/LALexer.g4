lexer grammar LALexer;

KEYWORDS: 'algoritmo' | 'fim_algoritmo' | 'declare' | 'literal' | 'inteiro' |
          'leia' | 'escreva' | 'real' | 'logico' | 'enquanto' | 'fim_enquanto' |
          'se' | 'entao' | 'senao' | 'fim_se' | 'caso' |
          'seja' | 'fim_caso' | 'para' | 'ate' | 'faca' | 'fim_para' |
          'registro' | 'fim_registro' | 'tipo' | 'procedimento' | 'var' | 'fim_procedimento' |
          'funcao' | 'retorne' | 'fim_funcao' | 'constante' | 'falso' | 'verdadeiro';

LOGIC_OPERATORS: 'e' | 'ou' | 'nao';
ARITHMETIC_OPERATORS: '+' | '-' | '*' | '/' | '%';
RELATIONAL_OPERATORS: '>' | '>=' | '<' | '<=' | '<>' | '=';

NUM_INT: NUMBER+;
NUM_REAL: NUM_INT '.' NUM_INT;
IDENT: LETTER(LETTER|NUMBER)*('_')?((LETTER|NUMBER)*);
CADEIA: '"' ~('"'|'\r'|'\n')* '"';
COMENTARIO: '{' ~('}'|'{'|'\r'|'\n')* '}' -> skip;

WB: ([ \t\r\n]) -> skip;

ADDRESS: '&';
POINTER: '^';
COLON: ':';
RANGE: '..';
PARENTHESES: '(' | ')';
SQUARE_BRACKETS: '[' | ']';
SEP: ',';
METHOD: '.';
ATRIBUITION: '<-';

fragment
LETTER: ([a-zA-Z]);

fragment
NUMBER: ([0-9]);