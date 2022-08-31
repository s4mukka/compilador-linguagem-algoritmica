from typing import List
from src.domain import Types, Variable
from src.lexer import LAVisitor, LAParser
from antlr4.error.ErrorListener import ErrorListener
from antlr4.tree.Tree import TerminalNodeImpl

from src.utils import Scopes, SymbolTable

class CustomVisitor(LAVisitor):

    def __init__(self, listener: ErrorListener = None) -> None:
        self._listener: ErrorListener = listener
        self._scope = Scopes()
        self._types = Types()
        self._has_errors = False

    def handle(self, tree):
        self.visit(tree)
        if self._has_errors:
            self._listener._file.write("Fim da compilacao\n")

    def visitDecl_local_global(self, global_local_declaration: LAParser.Decl_local_globalContext):
        if global_local_declaration.declaracao_local():
            self.check_locale_declaration(self._scope, global_local_declaration.declaracao_local())
        else:
            var = self.check_global_declaration(global_local_declaration.declaracao_global())
            self._scope.see_scope().add(var)
        return None

    def visitCorpo(self, body: LAParser.CorpoContext):
        for declaracao in body.declaracao_local():
            self.check_locale_declaration(self._scope, declaracao)
        
        for cmd in body.cmd():
            self.cmd_validate(self._scope.see_scope(), cmd, True)

        return None
    
    def check_global_declaration(self, global_declaration: LAParser.Declaracao_globalContext):
        self._scope.copy_new_scope()
        correspondence = global_declaration.start.text
        var = Variable(global_declaration.IDENT().getText(), None)
        if correspondence == 'funcao':
            return_type = self.extended_type_validate(global_declaration.tipo_estendido())
            var.set_type('funcao')
            var.set_return_type(return_type)
            if global_declaration.parametros():
                params = self.params_validate(self._scope, global_declaration.parametros())
                var.set_params(params)
                self._scope.see_scope().add_all(params)
            for declaration in global_declaration.declaracao_local():
                self.check_locale_declaration(self._scope, declaration)
            for commands in global_declaration.cmd():
                self.cmd_validate(self._scope.see_scope(), commands)
        elif correspondence == 'procedimento':
            var.set_type('procedimento')
            if global_declaration.parametros():
                params = self.params_validate(self._scope, global_declaration.parametros())
                var.set_params(params)
                self._scope.see_scope().add_all(params)
            for declaration in global_declaration.declaracao_local():
                self.check_locale_declaration(self._scope, declaration)
            for commands in global_declaration.cmd():
                self.cmd_validate(self._scope.see_scope(), commands, True)
        self._scope.abandon_scope()
        return var

    def check_locale_declaration(self, scope: Scopes, declaration: LAParser.Declaracao_localContext):
        correspondence = declaration.start.text

        if correspondence == 'declare':
            self.variable_validate(scope, declaration.variavel())
        elif correspondence == 'tipo':
            type = self.check_type(declaration.tipo())
            if type == 'invalido':
                self._has_errors = True
                self._listener.syntaxError(
                    line = declaration.start.line,
                    msg=declaration.tipo().getText(),
                    e="undeclared_type"
                )
            else:
                name = declaration.IDENT().getText()
                self._types.add(name)
                var = Variable(name, type)
                if type == 'registro':
                    var.childrens = self.struct_validate(scope, declaration.tipo().registro())
                self._scope.see_scope().add(var)
        elif correspondence == 'constante':
            type = declaration.tipo_basico().getText()
            self._scope.see_scope().add(Variable(declaration.IDENT().getText(), type))

        return None

    def check_type(self, type: LAParser.TipoContext):
        if type.registro():
            return 'registro'
        return self.extended_type_validate(type.tipo_estendido())

    def variable_validate(self, scope: Scopes, variable: LAParser.VariavelContext):
        type = self.check_type(variable.tipo())
        list_vars = {}

        for identifier in variable.identificador():
            var = self.identifier_validate(scope.see_scope(), identifier)
            if var.type is None:
                var.set_type(type)
                if var.type == 'registro':
                    var.childrens = self.struct_validate(scope, variable.tipo().registro())
                scope.see_scope().add(var)
                
                list_vars[var.name] = var
            else:
                print(var)
                self._has_errors = True
                self._listener.syntaxError(
                    line = identifier.start.line,
                    msg=identifier.getText(),
                    e="alread_declared_identifier"
                )

        if type == 'invalido':
            self._has_errors = True
            self._listener.syntaxError(
                line = variable.start.line,
                msg=variable.tipo().getText(),
                e="undeclared_type"
            )
        
        return list_vars

    
    def extended_type_validate(self, extended_type: LAParser.Tipo_estendidoContext):
        return self.ident_type_validate(extended_type.tipo_basico_ident())

    def ident_type_validate(self, ident_type: LAParser.Tipo_basico_identContext):
        if ident_type.tipo_basico():
            return ident_type.tipo_basico().getText()

        if self._types.get_type(ident_type.IDENT().getText()): 
            return ident_type.IDENT().getText()
        
        return 'invalido'

    def identifier_validate(self, symbol_table: SymbolTable, identifier: LAParser.IdentificadorContext):
        name = identifier.IDENT(0).getText()

        if symbol_table.contain(name):
            var = symbol_table.get_var(name)
            if len(identifier.IDENT()) > 1:
                children = identifier.IDENT(1).getText()
                if var.type == 'registro':
                    return var.childrens[children]
                if children not in symbol_table.get_var(var.type).childrens:
                    return Variable(name, None)
                var = symbol_table.get_var(var.type).childrens[children]
            return var

        return Variable(name, None)
    
    def cmd_validate(self, symbol_table: SymbolTable, cmd: LAParser.CmdContext, procedure = False):
        if cmd.cmdLeia():
            for identifier in cmd.cmdLeia().identificador():
                var = self.identifier_validate(symbol_table, identifier)
                if var.type is None:
                    self._has_errors = True
                    self._listener.syntaxError(
                        line=identifier.start.line,
                        msg=identifier.getText(),
                        e="undeclared_identifier"
                    )
        elif cmd.cmdEscreva():
            for expression in cmd.cmdEscreva().expressao():
                self.expression_validate(symbol_table, expression)
        elif cmd.cmdAtribuicao():
            identifier = cmd.cmdAtribuicao().identificador()
            target = self.identifier_validate(symbol_table, identifier)
            tidentifier = identifier.getText()
            if '^' in cmd.getChild(0).getText():
                tidentifier = f"^{tidentifier}"
            if target.type is None:
                self._has_errors = True
                self._listener.syntaxError(
                    line=identifier.start.line,
                    msg=tidentifier,
                    e="undeclared_identifier"
                )
            elif self._types.validate(
                target.type,
                self.expression_validate(symbol_table, cmd.cmdAtribuicao().expressao())
            ) == 'invalido':
                self._has_errors = True
                self._listener.syntaxError(
                    line=identifier.start.line,
                    msg=tidentifier,
                    e="attribution_not_compatible"
                )
        elif cmd.cmdSe():
            self.expression_validate(symbol_table, cmd.cmdSe().expressao())
            for command in cmd.cmdSe().cmd():
                self.cmd_validate(symbol_table, command)
        elif cmd.cmdEnquanto():
            self.expression_validate(symbol_table, cmd.cmdEnquanto().expressao())
        elif cmd.cmdFaca():
            self.expression_validate(symbol_table, cmd.cmdFaca().expressao())
            for command in cmd.cmdFaca().cmd():
                self.cmd_validate(symbol_table, command)
        elif cmd.cmdRetorne():
            if procedure:
                self._has_errors = True
                self._listener.syntaxError(
                    line=cmd.start.line,
                    msg="",
                    e="return_not_allowed"
                )


    def expression_validate(self, symbol_table: SymbolTable, expression: LAParser.ExpressaoContext):
        type = self.logical_term_validate(symbol_table, expression.termo_logico(0))
        for i, logical_term in enumerate(expression.termo_logico()):
            if i > 0:
                type = self._types.validate(type, self.logical_term_validate(symbol_table, logical_term))
        # print('\t205', type)
        return type

    def logical_term_validate(self, symbol_table: SymbolTable, logical_term: LAParser.Termo_logicoContext):
        type = self.logical_factor_validate(symbol_table, logical_term.fator_logico(0))
        for i, logical_factor in enumerate(logical_term.fator_logico()):
            if i > 0:
                type = self._types.validate(type, self.logical_factor_validate(symbol_table, logical_factor))
        # print('\t213', type)
        return type

    def logical_factor_validate(self, symbol_table: SymbolTable, logical_factor: LAParser.Fator_logicoContext):
        type = self.logical_portion_validate(symbol_table, logical_factor.parcela_logica())
        if 'nao' in logical_factor.getChild(0).getText():
            # print('\t219', 'logico')
            return 'logico'
        # print('\t221', type)
        return type

    def logical_portion_validate(self, symbol_table: SymbolTable, logical_portion: LAParser.Parcela_logicaContext):
        if logical_portion.exp_relacional():
            type = self.relational_expression_validate(symbol_table, logical_portion.exp_relacional())
            # print('\t227', type)
            return type
        # print('\t229', 'logico')
        return 'logico'

    def relational_expression_validate(self, symbol_table: SymbolTable, relational_expression: LAParser.Exp_relacionalContext):
        type = self.arithmetic_expression_validate(symbol_table, relational_expression.exp_aritmetica(0))
        for i, arithmetic_expression in enumerate(relational_expression.exp_aritmetica()):
            if i > 0:
                type = self._types.validate(type, self.arithmetic_expression_validate(symbol_table, arithmetic_expression))
        # print('\t237', type)
        return type

    def arithmetic_expression_validate(self, symbol_table: SymbolTable, arithmetic_expression: LAParser.Exp_aritmeticaContext):
        type = self.term_validate(symbol_table, arithmetic_expression.termo(0))
        for i, term in enumerate(arithmetic_expression.termo()):
            if i > 0:
                type = self._types.validate(type, self.term_validate(symbol_table, term))
        # print('\t245', type)
        return type

    def term_validate(self, symbol_table: SymbolTable, term: LAParser.TermoContext):
        type = self.factor_validate(symbol_table, term.fator(0))
        for i, factor in enumerate(term.fator()):
            if i > 0:
                type = self._types.validate(type, self.factor_validate(symbol_table, factor))
        # print('\t253', type)
        return type

    def factor_validate(self, symbol_table: SymbolTable, factor: LAParser.FatorContext):
        type = self.portion_validate(symbol_table, factor.parcela(0))
        for i, portion in enumerate(factor.parcela()):
            if i > 0:
                type = self._types.validate(type, self.portion_validate(symbol_table, portion))
        # print('\t261', type)
        return type

    def portion_validate(self, symbol_table: SymbolTable, portion: LAParser.ParcelaContext):
        if portion.parcela_unario():
            type = self.unary_portion_validate(symbol_table, portion.parcela_unario())
            if portion.op_unario():
                if type not in ['inteiro', 'real']:
                    # print('\t269', type, None)
                    return None
            # print('\t271', type)
            return type
        return self.nonunary_portion_validate(symbol_table, portion.parcela_nao_unario())

    def unary_portion_validate(self, symbol_table: SymbolTable, unary_portion: LAParser.Parcela_unarioContext):
        if unary_portion.NUM_INT():
            return 'inteiro'
        if unary_portion.NUM_REAL():
            return 'real'
        if unary_portion.IDENT():
            return self.method_validate(symbol_table, unary_portion.IDENT(), unary_portion.expressao())
        if unary_portion.identificador():
            identifier = self.identifier_validate(symbol_table, unary_portion.identificador())
            if identifier.type is None:
                self._has_errors = True
                self._listener.syntaxError(
                    line=unary_portion.identificador().start.line,
                    msg=unary_portion.identificador().getText(),
                    e="undeclared_identifier"
                )
            return identifier.type

        type = self.expression_validate(symbol_table, unary_portion.expressao(0))
        for i, expression in enumerate(unary_portion.expressao()):
            if i > 0:
                type = self._types(type, self.expression_validate(symbol_table, expression))

        return type
        

    def nonunary_portion_validate(self, symbol_table: SymbolTable, nonunary_portion: LAParser.Parcela_nao_unarioContext):
        if nonunary_portion.CADEIA():
            # print('\t303', 'literal')
            return 'literal'
        if nonunary_portion.identificador():
            identifier = self.identifier_validate(symbol_table, nonunary_portion.identificador())
            if identifier.type is None:
                self._has_errors = True
                self._listener.syntaxError(
                    line=nonunary_portion.identificador().start.line,
                    msg=nonunary_portion.identificador().getText(),
                    e="undeclared_identifier"
                )
            # print('\t314', identifier.type)
            return identifier.type
    
    def struct_validate(self, scope: Scopes, struct: LAParser.RegistroContext):
        new_struct = Variable('', 'registro')
        scope.create_new_scope()

        for variable in struct.variavel():
            new_struct.childrens = new_struct.childrens | self.variable_validate(scope, variable)
        
        scope.abandon_scope()
        return new_struct.childrens

    def params_validate(self, scope: Scopes, params: LAParser.ParametrosContext):
        response = []

        for param in params.parametro():
            type = self.extended_type_validate(param.tipo_estendido())

            for identifier in param.identificador():
                response.append(Variable(identifier.getText(), type))

        return response

    def method_validate(self, symbol_table: SymbolTable, identifier: TerminalNodeImpl, expressions: List[LAParser.ExpressaoContext]):
        method = symbol_table.get_var(identifier.getText())
        response = method.return_type
        for expression in expressions:
            type = self.expression_validate(symbol_table, expression)
            response = self._types.equivalent(response, type)

        if response == 'invalido' or len(expressions) != len(method.params):
            self._has_errors = True
            self._listener.syntaxError(
                    line=identifier.getSymbol().line,
                    msg=identifier.getText(),
                    e="parameter_mismatch"
                )
        return response 