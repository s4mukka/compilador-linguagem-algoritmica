from cmath import exp
from src.lexer import LAVisitor, LAParser
from antlr4.error.ErrorListener import ErrorListener

class CustomVisitor(LAVisitor):

    def __init__(self, listener: ErrorListener = None):
        self.listener = listener
        self._indicadores = {}
        self._tipos = {}
        self._identificador_atribuido = None
        self._expressao_logica = False
        self._funcoes = {}
        self._funcao = None
        self._escopo = None
        self._constantes = {}
        self._tipo_esperado = None

    def handle(self, tree):
        self.visit(tree)
        self.listener._file.write("Fim da compilacao\n")

    def getIndicador(self, indicador):
        
        splited = indicador.getText().split('.')
        tindicador = splited[0]
        if indicador.dimensao():
            tindicador = tindicador.replace(indicador.dimensao().getText(), '')
        if tindicador in self._indicadores:
            if len(splited) == 2:
                if 'type' in self._indicadores[tindicador]:
                    if self._indicadores[tindicador]['type'] not in self._tipos:
                        
                        return None
                    if splited[1] not in self._tipos[self._indicadores[tindicador]['type']]:
                        
                        return None
                    if self._tipos[self._indicadores[tindicador]['type']][splited[1]]['pointer']:
                        
                        return '^' + tindicador + '.' + splited[1]
                    
                    return tindicador + '.' + splited[1]

                if splited[1] not in self._indicadores[tindicador]:
                    
                    return None
                if self._indicadores[tindicador][splited[1]]['pointer']:
                    
                    return '^' + tindicador + '.' + splited[1]
                
                return tindicador + '.' + splited[1]

            if self._indicadores[tindicador]['pointer']:
                
                return '^' + tindicador

            if indicador.dimensao():
                
                return tindicador + indicador.dimensao().getText()
            
            return tindicador
        if tindicador in self._tipos:
            
            return tindicador
        
        return None
    
    def getType(self, indicador):
        
        splited = indicador.getText().split('.')
        tindicador = splited[0]
        
        if indicador.dimensao():
            tindicador = tindicador.replace(indicador.dimensao().getText(), '')
        if len(splited) == 2:
            if 'type' in self._indicadores[tindicador] and self._indicadores[tindicador]['type'] in self._tipos:
                
                return self._tipos[self._indicadores[tindicador]['type']][splited[1]]['type']
            
            return self._indicadores[tindicador][splited[1]]['type']
        
        return self._indicadores[tindicador]['type']

    def visitTipo_basico_ident(self, ctx:LAParser.Tipo_basico_identContext):
        
        if ctx.IDENT() and ctx.IDENT().getText() not in self._tipos:
            msg = f"tipo {ctx.IDENT().getText()} nao declarado"
            self.listener.syntaxError(None, None, ctx.start.line, ctx.start.column, msg, None)
        
        return self.visitChildren(ctx)

    def visitVariavel(self, ctx:LAParser.VariavelContext, registro = False):
        indicadores = {}
        

        for identificador in ctx.identificador():
            if identificador.getText() not in self._indicadores and identificador.getText() not in self._tipos:
                ttipo = ttipo = ctx.tipo().getText()
                if ctx.tipo().registro():
                    self.visitRegistro(ctx.tipo().registro(), identificador.getText())
                indicador = {
                    "type": ttipo.replace('^',''),
                    "pointer": '^' in ttipo,
                    "size": None
                }

                tindicador = identificador.getText()
                if identificador.dimensao():
                    indicador["size"] = identificador.dimensao().getText().replace('[','').replace(']','')
                    tindicador = tindicador.replace(identificador.dimensao().getText(), '')



                if registro:
                    indicadores[tindicador] = indicador
                elif not ctx.tipo().registro():
                    self._indicadores[tindicador] = indicador
            else:
                msg = f"identificador {self.getIndicador(identificador)} ja declarado anteriormente"
                self.listener.syntaxError(None, None, identificador.start.line, identificador.start.column, msg, None)

        
        if registro:
            return indicadores

        return self.visitChildren(ctx)
    
    def visitCorpo(self, ctx: LAParser.CorpoContext):
        self._indicadores = self._constantes
        self._escopo = 'corpo'
        self.visitChildren(ctx)
        self._escopo = None

    def visitDeclaracao_local(self, ctx: LAParser.Declaracao_localContext):
        if ctx.tipo_basico():
            indicador = {
                    "type": ctx.tipo_basico().getText().replace('^',''),
                    "pointer": '^' in ctx.tipo_basico().getText(),
                    "size": None
                }
            self._constantes[ctx.IDENT().getText()] = indicador
            
        if ctx.tipo() and ctx.tipo().registro():
            return self.visitRegistro(ctx.tipo().registro(), ctx.IDENT().getText(), True)
        return self.visitChildren(ctx)

    def visitDeclaracao_global(self, ctx: LAParser.Declaracao_globalContext):
        ttype = "void"
        if ctx.tipo_estendido():
            ttype = ctx.tipo_estendido().getText()
        self._funcoes[ctx.IDENT().getText()] = {
            'parameters': self.visitParametros(ctx.parametros()),
            'returns': ttype
        }

        indicador = {
            "type": "function",
            "pointer": None,
            "size": None
        }

        self._constantes[ctx.IDENT().getText()] = indicador

        self._escopo = ctx.IDENT().getText()
        self._indicadores = self._funcoes[ctx.IDENT().getText()]['parameters']
        self.visitChildren(ctx)
        self._escopo = None
        self._indicadores = {}
        

    def visitCmdRetorne(self, ctx: LAParser.CmdRetorneContext):
        if self._escopo:
            if self._escopo == 'corpo' or self._funcoes[self._escopo]['returns'] == 'void':
                msg = f"comando retorne nao permitido nesse escopo"
                self.listener.syntaxError(None, None, ctx.start.line, ctx.start.column, msg, None)
        return self.visitChildren(ctx)

    def visitParametros(self, ctx: LAParser.ParametrosContext):
        parametros = {}
        
        for parametro in ctx.parametro():
            for identificador in parametro.identificador():
                param = {
                    identificador.getText(): {
                        'type': parametro.tipo_estendido().getText().replace('^',''),
                        'pointer': '^' in parametro.tipo_estendido().getText()
                    }
                }
                parametros = dict(parametros, **param)
        
        return parametros

    def visitRegistro(self, ctx: LAParser.RegistroContext, identificador = None, tipo = False):
        
        if tipo:
            self._tipos[identificador] = {}
            for variavel in ctx.variavel():
                indicador = self.visitVariavel(variavel, True)
                self._tipos[identificador] = dict(self._tipos[identificador], **indicador)
        else:
            for variavel in ctx.variavel():
                indicador = self.visitVariavel(variavel, True)
                self._indicadores[identificador] = indicador
        

    def visitCmdLeia(self, ctx:LAParser.CmdLeiaContext):
        
        for identificador in ctx.identificador():
            if not self.getIndicador(identificador):
                msg = f"identificador {identificador.getText()} nao declarado"
                self.listener.syntaxError(None, None, identificador.start.line, identificador.start.column, msg, None)
        

        return self.visitChildren(ctx)

    def visitDimensao(self, ctx: LAParser.DimensaoContext):
        pass

    def visitParcela_unario(self, ctx:LAParser.Parcela_unarioContext):
        identificador = ctx.identificador()

        if self._identificador_atribuido or self._tipo_esperado:
            if self._identificador_atribuido:
                tipo_esperado = self.getType(self._identificador_atribuido)
            if self._tipo_esperado:
                tipo_esperado = self._tipo_esperado
            atom = None
            if ctx.NUM_INT() and tipo_esperado not in ['inteiro','real']:
                atom = ctx.NUM_INT()
            if ctx.NUM_REAL() and tipo_esperado not in ['inteiro','real']:
                atom = ctx.NUM_REAL()
            if identificador and tipo_esperado not in [self.getType(identificador), 'logico']:
                if self.getType(identificador) in ['inteiro','real'] and tipo_esperado not in ['inteiro', 'real']:
                    atom = identificador
                elif self._funcao:
                    atom = identificador
            if atom:
                if self._identificador_atribuido:
                    msg = f"atribuicao nao compativel para {self.getIndicador(self._identificador_atribuido)}"
                    self.listener.syntaxError(None, None, self._identificador_atribuido.start.line, self._identificador_atribuido.start.column, msg, None)
                if self._tipo_esperado:
                    msg = f"incompatibilidade de parametros na chamada de {self._funcao}"
                    self.listener.syntaxError(None, None, atom.start.line, atom.start.column, msg, None)

        if identificador and not self.getIndicador(identificador):
            msg = f"identificador {identificador.getText()} nao declarado"
            self.listener.syntaxError(None, None, identificador.start.line, identificador.start.column, msg, None)

        if ctx.IDENT():
            identificador = ctx.IDENT()
            if len(self._funcoes[ctx.IDENT().getText()]['parameters']) != len(ctx.expressao()):
                msg = f"incompatibilidade de parametros na chamada de {identificador.getText()}"
                self.listener.syntaxError(None, None, ctx.start.line, ctx.start.column, msg, None)
            for i, expressao in enumerate(ctx.expressao()):
                self._funcao = ctx.IDENT().getText()
                self._tipo_esperado = self._funcoes[ctx.IDENT().getText()]['parameters'][list(self._funcoes[ctx.IDENT().getText()]['parameters'])[i]]['type']
                self.visitExpressao(expressao)
                self._funcao = None
                self._tipo_esperado = None
        
        

        return self.visitChildren(ctx)

    def visitParcela_nao_unario(self, ctx:LAParser.Parcela_unarioContext):
        identificador = ctx.identificador()
        
        if self._identificador_atribuido or self._tipo_esperado:
            if self._identificador_atribuido:
                tipo_esperado = self.getType(self._identificador_atribuido)
            elif self._tipo_esperado:
                tipo_esperado = self._tipo_esperado
            atom = None
            if ctx.CADEIA() and tipo_esperado != 'literal':
                atom = ctx.CADEIA()
            if identificador and tipo_esperado not in [self.getType(identificador), 'logico']:
                atom = identificador
            if atom:
                msg = f"atribuicao nao compativel para {self.getIndicador(self._identificador_atribuido)}"
                self.listener.syntaxError(
                    None,
                    None,
                    self._identificador_atribuido.start.line,
                    self._identificador_atribuido.start.column,
                    msg,
                    None
                )

        if identificador and not self.getIndicador(identificador):
            msg = f"identificador {identificador.getText()} nao declarado"
            self.listener.syntaxError(None, None, identificador.start.line, identificador.start.column, msg, None)

        

        return self.visitChildren(ctx)

    def visitCmdAtribuicao(self, ctx:LAParser.CmdAtribuicaoContext):
        self._identificador_atribuido = ctx.identificador()
        if self.getIndicador(self._identificador_atribuido):
            self.visitChildren(ctx.expressao())
        else:
            msg = f"identificador {self._identificador_atribuido.getText()} nao declarado"
            self.listener.syntaxError(None, None, self._identificador_atribuido.start.line, self._identificador_atribuido.start.column, msg, None)
        self._identificador_atribuido = None
        return self.visitChildren(ctx)

    def visitParcela_logica(self, ctx: LAParser.Parcela_logicaContext):
        if ctx.exp_relacional() is None and self._identificador_atribuido:
            msg = f"atribuicao nao compativel para {self.getIndicador(self._identificador_atribuido)}"
            self.listener.syntaxError(
                None,
                None,
                self._identificador_atribuido.start.line,
                self._identificador_atribuido.start.column,
                msg,
                None
            )

        return self.visitChildren(ctx)
