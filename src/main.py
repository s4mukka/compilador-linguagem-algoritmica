import sys
from antlr4 import *
from src.decorators import CustomErrorListener, CustomLexer

def main():
    # Define os arquivos de entrada e saída
    entrada = str(sys.argv[1])
    saida = str(sys.argv[2])

    input = FileStream(entrada, encoding='utf-8')
    output = open(saida, 'w')

    # Instancia o Lexer
    lexer = CustomLexer(input)

    # Adiciona erros customizados
    listener = CustomErrorListener(output)
    lexer.addErrorListener(listener)

    # Intera sobre os tokens
    while (token := lexer.nextToken()).type is not Token.EOF:
        symbolic_name = lexer.symbolicNames[token.type]
        ttype = symbolic_name
        if symbolic_name not in str(['IDENT','CADEIA','NUM_INT','NUM_REAL']):
            ttype = f"'{token.text}'"
        output.write(f"<'{token.text}',{ttype}>\n")

    output.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(error)
