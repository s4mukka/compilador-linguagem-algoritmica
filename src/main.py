import sys
from antlr4 import *
from src.decorators import CustomErrorListener, CustomLexer
from src.lexer import LAParser

def main():
    # Define os arquivos de entrada e saída
    entrada = str(sys.argv[1])
    saida = str(sys.argv[2])

    input = FileStream(entrada, encoding='utf-8')
    output = open(saida, 'w')

    # Instancia o Lexer
    lexer = CustomLexer(input)
    listener = CustomErrorListener(output)
    stream = CommonTokenStream(lexer)
    parser = LAParser(stream)

    # Adiciona erros customizados
    lexer.addErrorListener(listener)
    parser.addErrorListener(listener)

    try:
        parser.programa()
    except Exception as error:
        print(error)

    output.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(error)
