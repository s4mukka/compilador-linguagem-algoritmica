import sys
from antlr4 import FileStream, CommonTokenStream
from src.decorators import CustomErrorListenerLexer, CustomErrorListenerParser,\
    CustomLexer, CustomParser

def main():
    # Define os arquivos de entrada e saída
    entrada = str(sys.argv[1])
    saida = str(sys.argv[2])

    input = FileStream(entrada, encoding='utf-8')
    output = open(saida, 'w')

    # Instancia as classes
    lexer = CustomLexer(input, output)
    listener_lexer = CustomErrorListenerLexer(output)
    listener_parser = CustomErrorListenerParser(output)
    stream = CommonTokenStream(lexer)
    parser = CustomParser(stream, output)

    # Adiciona erros customizados
    lexer.addErrorListener(listener_lexer)
    parser.addErrorListener(listener_parser)

    try:
        parser.handle()
    except Exception as error:
        print(error)

    output.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(error)
