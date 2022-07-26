from src.lexer import LAVisitor, LAParser
from antlr4.error.ErrorListener import ErrorListener

class CustomVisitor(LAVisitor):

    def __init__(self, listener: ErrorListener = None):
        self.listener = listener
        self._indicadores = {}
        self._identificador_atribuido = None
        self._expressao_logica = False

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
                self._indicadores[identificador.getText()] = ctx.tipo().getText()
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
        if self._identificador_atribuido:
            tipo_esperado = self._indicadores[self._identificador_atribuido.getText()]
            atom = None
            if ctx.NUM_INT() and tipo_esperado not in ['inteiro','real']:
                atom = ctx.NUM_INT()
            if ctx.NUM_REAL() and tipo_esperado not in ['inteiro','real']:
                atom = ctx.NUM_REAL()
            if identificador and tipo_esperado not in [self._indicadores[identificador.getText()], 'logico']:
                if self._indicadores[identificador.getText()] in ['inteiro','real'] and tipo_esperado not in ['inteiro', 'real']:
                    atom = identificador
            if atom:
                msg = f"atribuicao nao compativel para {self._identificador_atribuido.getText()}"
                self.listener.syntaxError(None, None, self._identificador_atribuido.start.line, self._identificador_atribuido.start.column, msg, None)
        if identificador and identificador.getText() not in self._indicadores:
            msg = f"identificador {identificador.getText()} nao declarado"
            self.listener.syntaxError(None, None, identificador.start.line, identificador.start.column, msg, None)

        return self.visitChildren(ctx)

    def visitParcela_nao_unario(self, ctx:LAParser.Parcela_unarioContext):
        identificador = ctx.identificador()
        if self._identificador_atribuido:
            tipo_esperado = self._indicadores[self._identificador_atribuido.getText()]
            atom = None
            if ctx.CADEIA() and tipo_esperado != 'literal':
                atom = ctx.CADEIA()
            if identificador and tipo_esperado not in [self._indicadores[identificador.getText()], 'logico']:
                atom = identificador
            if atom:
                msg = f"atribuicao nao compativel para {self._identificador_atribuido.getText()}"
                self.listener.syntaxError(None, None, self._identificador_atribuido.start.line, self._identificador_atribuido.start.column, msg, None)
        if identificador and identificador.getText() not in self._indicadores:
            msg = f"identificador {identificador.getText()} nao declarado"
            self.listener.syntaxError(None, None, identificador.start.line, identificador.start.column, msg, None)

        return self.visitChildren(ctx)

    def visitCmdAtribuicao(self, ctx:LAParser.CmdAtribuicaoContext):
        self._identificador_atribuido = ctx.identificador()
        self.visitChildren(ctx.expressao())
        self._identificador_atribuido = None
        return self.visitChildren(ctx)

    def visitParcela_logica(self, ctx: LAParser.Parcela_logicaContext):
        if ctx.exp_relacional() is None and self._identificador_atribuido:
            msg = f"atribuicao nao compativel para {self._identificador_atribuido.getText()}"
            self.listener.syntaxError(None, None, self._identificador_atribuido.start.line, self._identificador_atribuido.start.column, msg, None)
        return self.visitChildren(ctx)
