import sys
import logging
from antlr4 import FileStream, CommonTokenStream
from src.decorators import CustomErrorListenerLexer, CustomErrorListenerParser, CustomErrorListenerVisitor,\
    CustomLexer, CustomParser, CustomVisitor

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
    listener_visitor = CustomErrorListenerVisitor(output)
    stream = CommonTokenStream(lexer)
    parser = CustomParser(stream, output)
    tree = parser.programa()
    visitor = CustomVisitor(listener_visitor)

    # Adiciona erros customizados
    lexer.addErrorListener(listener_lexer)
    parser.addErrorListener(listener_parser)

    visitor.handle(tree)

    output.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logging.error(error)
