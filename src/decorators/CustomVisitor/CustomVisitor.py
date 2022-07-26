from src.lexer import LAVisitor, LAParser
from antlr4.error.ErrorListener import ErrorListener

class CustomVisitor(LAVisitor):

    def __init__(self, listener: ErrorListener = None):
        self.listener = listener
        self._indicadores = []

    def handle(self, tree):
        self.visit(tree)
        self.listener._file.write("Fim da compilacao\n")

    def visitTipo_basico_ident(self, ctx:LAParser.Tipo_basico_identContext):
        if ctx.IDENT():
            msg = f"tipo {ctx.IDENT()} nao declarado"
            self.listener.syntaxError(None, None, ctx.start.line, ctx.start.column, msg, None)
        return self.visitChildren(ctx)

    def visitVariavel(self, ctx:LAParser.VariavelContext):
        for identificador in ctx.identificador():
            if identificador.getText() not in self._indicadores:
                self._indicadores.append(identificador.getText())
            else:
                msg = f"identificador {identificador.getText()} ja declarado anteriormente"
                self.listener.syntaxError(None, None, identificador.start.line, identificador.start.column, msg, None)
        return self.visitChildren(ctx)

    def visitCmdLeia(self, ctx:LAParser.CmdLeiaContext):
        for identificador in ctx.identificador():
            if identificador.getText() not in self._indicadores:
                msg = f"identificador {identificador.getText()} nao declarado"
                self.listener.syntaxError(None, None, identificador.start.line, identificador.start.column, msg, None)

        return self.visitChildren(ctx)

    def visitParcela_unario(self, ctx:LAParser.Parcela_unarioContext):
        identificador = ctx.identificador()
        if identificador and identificador.getText() not in self._indicadores:
            msg = f"identificador {identificador.getText()} nao declarado"
            self.listener.syntaxError(None, None, identificador.start.line, identificador.start.column, msg, None)

        return self.visitChildren(ctx)

    def visitParcela_nao_unario(self, ctx:LAParser.Parcela_unarioContext):
        identificador = ctx.identificador()
        if identificador and identificador.getText() not in self._indicadores:
            msg = f"identificador {identificador.getText()} nao declarado"
            self.listener.syntaxError(None, None, identificador.start.line, identificador.start.column, msg, None)

        return self.visitChildren(ctx)

    def visitCmdAtribuicao(self, ctx:LAParser.CmdAtribuicaoContext):
        return self.visitChildren(ctx)