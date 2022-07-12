from src.lexer import LALexer
from re import match
from antlr4 import Token

class CustomLexer(LALexer):
    def handle(self):
        """ Executa o analisador léxico """
        while (token := self.nextToken()).type is not Token.EOF:
            rule_name = self.ruleNames[token.type - 1]
            ttype = rule_name
            if rule_name not in str(['IDENT','CADEIA','NUM_INT','NUM_REAL']):
                ttype = f"'{token.text}'"
            self._output.write(f"<'{token.text}',{ttype}>\n")
