from src.domain import Variable, Types
from src.lexer import LAVisitor, LAParser
from src.decorators import CustomVisitor

class Generator(LAVisitor):
    def __init__(self, visitor: CustomVisitor):
        self._visitor = visitor
        self._types = Types()
    
    def handle(self, tree):
        self._visitor.handle(tree)
        if not self._visitor._has_errors:
            self.visit(tree)
    
    def visitPrograma(self, program: LAParser.ProgramaContext):
        self._visitor._listener._file.write("#include <stdio.h>\n")
        self._visitor._listener._file.write("#include <stdlib.h>\n")
        self._visitor._listener._file.write("\n\n")
        if program.declaracoes():
            self.visitDeclaracoes(program.declaracoes())
            self._visitor._listener._file.write("\n\n")
        self._visitor._listener._file.write("int main() {\n")
        self.visitCorpo(program.corpo())
        self._visitor._listener._file.write("\treturn 0;\n")
        self._visitor._listener._file.write("}\n")

    def visitDeclaracao_global(self, global_declaration: LAParser.Declaracao_globalContext):
        correspondence = global_declaration.start.text
        if correspondence == 'procedimento':
            procedure = self._visitor._scope.see_scope().get_var(global_declaration.IDENT().getText())
            self._visitor._listener._file.write(f"void {procedure.name} (")
            for i, param in enumerate(procedure.params):
                if i > 0:
                    self._visitor._listener._file.write(", ")
                self._visitor._listener._file.write(self.variable_generate(param))
            self._visitor._listener._file.write(") {\n")
            for declaration in global_declaration.declaracao_local():
                self.visitDeclaracao_local(declaration)
            self._visitor._scope.copy_new_scope()
            self._visitor._scope.see_scope().add_all(procedure.params)
            for command in global_declaration.cmd():
                self.visitCmd(command)
            self._visitor._scope.abandon_scope()
            self._visitor._listener._file.write("}\n\n")
        elif correspondence == 'funcao':
            function = self._visitor._scope.see_scope().get_var(global_declaration.IDENT().getText())
            self._visitor._listener._file.write(f"{self._types.get_c_type(function.return_type)} {function.name} (")
            for i, param in enumerate(function.params):
                if i > 0:
                    self._visitor._listener._file.write(", ")
                self._visitor._listener._file.write(self.variable_generate(param))
            self._visitor._listener._file.write(") {\n")
            for declaration in global_declaration.declaracao_local():
                self.visitDeclaracao_local(declaration)
            self._visitor._scope.copy_new_scope()
            self._visitor._scope.see_scope().add_all(function.params)
            for command in global_declaration.cmd():
                self.visitCmd(command)
            self._visitor._scope.abandon_scope()
            self._visitor._listener._file.write("}\n\n")
        return None

    def visitDeclaracao_local(self, declaration: LAParser.Declaracao_localContext):
        correspondence = declaration.start.text

        if correspondence == 'declare':
            self.visitVariavel(declaration.variavel())
        elif correspondence == 'constante':
            self._visitor._listener._file.write(f"#define {declaration.IDENT().getText()} ")
            self.visitValor_constante(declaration.valor_constante())
            self._visitor._listener._file.write(f"\n\n")
        elif correspondence == 'tipo':
            self._visitor._listener._file.write("\ttypedef struct {\n")
            type_name = declaration.IDENT().getText()
            var = self._visitor._scope.see_scope().get_var(type_name)
            if declaration.tipo().registro():
                for child in var.childrens:
                    self._visitor._listener._file.write(f"\t\t{self.variable_generate(var.childrens[child])}")
                    self._visitor._listener._file.write(";\n")
            self._visitor._listener._file.write("\t} " + f"{type_name};\n\n")

        return None

    def visitVariavel(self, variable: LAParser.VariavelContext):
        pointer = '^' in variable.tipo().getText()
        for identifier in variable.identificador():
            name = identifier.IDENT(0).getText()
            var = self._visitor._scope.see_scope().get_var(name)
            generated = self.variable_generate(var, pointer)
            self._visitor._listener._file.write(f"\t{generated}")
            if identifier.dimensao().exp_aritmetica():
                self.visitDimensao(identifier.dimensao())
            self._visitor._listener._file.write(";\n")
        self._visitor._listener._file.write(f"\n")
        return None
    
    def visitDimensao(self, dimension: LAParser.DimensaoContext):
        self._visitor._listener._file.write("[")
        for arithmetic_expression in dimension.exp_aritmetica():
            self.visitExp_aritmetica(arithmetic_expression)
        self._visitor._listener._file.write("]")

        return None

    def visitCmd(self, cmd: LAParser.CmdContext):
        if cmd.cmdLeia():
            var = self._visitor._scope.see_scope().get_var(cmd.cmdLeia().identificador(0).getText())
            self._visitor._listener._file.write(f"\tscanf(\"{var.format}\", &{var.name});\n\n")
        if cmd.cmdEscreva():
            for expression in cmd.cmdEscreva().expressao():
                type = self._visitor.expression_validate(self._visitor._scope.see_scope(), expression)
                self._visitor._listener._file.write(f"\tprintf(\"{self._types.get_format(type)}\", ")
                self.visitExpressao(expression)
                self._visitor._listener._file.write(f");\n")
            self._visitor._listener._file.write(f"\n")
        if cmd.cmdAtribuicao():
            self._visitor._listener._file.write("\t")
            if cmd.cmdAtribuicao().getChild(0).getText() == "^":
                self._visitor._listener._file.write("*")
            target = self._visitor.identifier_validate(self._visitor._scope.see_scope(), cmd.cmdAtribuicao().identificador())
            if target.type != 'literal':
                self.visitIdentificador(cmd.cmdAtribuicao().identificador())
                self._visitor._listener._file.write(f" = ")
                self.visitExpressao(cmd.cmdAtribuicao().expressao())
            else:
                self._visitor._listener._file.write(f"strcpy(")
                self.visitIdentificador(cmd.cmdAtribuicao().identificador())
                self._visitor._listener._file.write(f",")
                self.visitExpressao(cmd.cmdAtribuicao().expressao())
                self._visitor._listener._file.write(f")")
            self._visitor._listener._file.write(";\n\n")
        if cmd.cmdSe():
            self._visitor._listener._file.write(f"\tif (")
            self.visitExpressao(cmd.cmdSe().expressao())
            self._visitor._listener._file.write(") {\n")
            for command in cmd.cmdSe().cmd1:
                self._visitor._listener._file.write("\t")
                self.visitCmd(command)
            if cmd.cmdSe().cmd2:
                self._visitor._listener._file.write("\t} else {\n")
                for command in cmd.cmdSe().cmd2:
                    self._visitor._listener._file.write("\t")
                    self.visitCmd(command)
            self._visitor._listener._file.write("\t}\n")
        if cmd.cmdCaso():
            self._visitor._listener._file.write(f"\tswitch (")
            self.visitExp_aritmetica(cmd.cmdCaso().exp_aritmetica())
            self._visitor._listener._file.write(") {\n")
            for selection_item in cmd.cmdCaso().selecao().item_selecao():
                self.visitConstantes(selection_item.constantes())
                for command in selection_item.cmd():
                    self._visitor._listener._file.write("\t\t")
                    self.visitCmd(command)
                self._visitor._listener._file.write("\t\tbreak;\n")
            if cmd.cmdCaso().cmd():
                self._visitor._listener._file.write(f"\t\tdefault:\n")
                for command in cmd.cmdCaso().cmd():
                    self._visitor._listener._file.write(f"\t\t")
                    self.visitCmd(command)
            self._visitor._listener._file.write("\t}\n\n")
        if cmd.cmdPara():
            index = cmd.cmdPara().IDENT().getText()
            self._visitor._listener._file.write(f"\tfor({index} = ")
            self.visitExp_aritmetica(cmd.cmdPara().exp_aritmetica1)
            self._visitor._listener._file.write(f"; {index} <= ")
            self.visitExp_aritmetica(cmd.cmdPara().exp_aritmetica2)
            self._visitor._listener._file.write(f"; {index}++) " + " {\n")
            for command in cmd.cmdPara().cmd():
                self._visitor._listener._file.write(f"\t\t")
                self.visitCmd(command)
            self._visitor._listener._file.write("\t}\n\n")
        if cmd.cmdEnquanto():
            self._visitor._listener._file.write("\twhile(")
            self.visitExpressao(cmd.cmdEnquanto().expressao())
            self._visitor._listener._file.write(") {\n")
            for command in cmd.cmdEnquanto().cmd():
                self._visitor._listener._file.write(f"\t\t")
                self.visitCmd(command)
            self._visitor._listener._file.write("\t}\n\n")
        if cmd.cmdFaca():
            self._visitor._listener._file.write("\tdo {\n")
            for command in cmd.cmdFaca().cmd():
                self._visitor._listener._file.write(f"\t\t")
                self.visitCmd(command)
            self._visitor._listener._file.write("\t} while (")
            self.visitExpressao(cmd.cmdFaca().expressao())
            self._visitor._listener._file.write(");\n\n")
        if cmd.cmdChamada():
            self._visitor._listener._file.write(f"\t{cmd.cmdChamada().IDENT().getText()}(")
            for i, expression in enumerate(cmd.cmdChamada().expressao()):
                if i > 0:
                    self._visitor._listener._file.write(", ")
                self.visitExpressao(expression)
            self._visitor._listener._file.write(");\n")
        if cmd.cmdRetorne():
            self._visitor._listener._file.write("\treturn ")
            self.visitExpressao(cmd.cmdRetorne().expressao())
            self._visitor._listener._file.write(";\n")
        return None
    
    def visitExpressao(self, expression: LAParser.ExpressaoContext):
        self.visitTermo_logico(expression.termo_logico(0))
        for i, logical_term in enumerate(expression.termo_logico()):
            if i > 0:
                self._visitor._listener._file.write(f" || ")
                self.visitTermo_logico(logical_term)
        return None

    def visitTermo_logico(self, logical_term: LAParser.Termo_logicoContext):
        self.visitFator_logico(logical_term.fator_logico(0))
        for i, logical_factor in enumerate(logical_term.fator_logico()):
            if i > 0:
                self._visitor._listener._file.write(f" && ")
                self.visitFator_logico(logical_factor)
        return None

    def visitFator_logico(self, logical_factor: LAParser.Fator_logicoContext):
        if 'nao' in logical_factor.getChild(0).getText():
            self._visitor._listener._file.write(f"!")
        self.visitParcela_logica(logical_factor.parcela_logica())
        return None
    
    def visitParcela_logica(self, logical_portion: LAParser.Parcela_logicaContext):
        if logical_portion.exp_relacional():
            self.visitExp_relacional(logical_portion.exp_relacional())
            return None
        if logical_portion.getText() == 'verdadeiro':
            self._visitor._listener._file.write("1")
        else:
            self._visitor._listener._file.write("0")
        return None

    def visitExp_relacional(self, relational_expression: LAParser.Exp_relacionalContext):
        self.visitExp_aritmetica(relational_expression.exp_aritmetica(0))
        if relational_expression.op_relacional():
            self.visitOp_relacional(relational_expression.op_relacional())
            self.visitExp_aritmetica(relational_expression.exp_aritmetica(1))
        return None

    def visitOp_relacional(self, relational_operator: LAParser.Op_relacionalContext):
        operator = relational_operator.getText()
        if operator == '=':
            self._visitor._listener._file.write(" == ")
        elif operator == '<>':
            self._visitor._listener._file.write(" != ")
        else:
            self._visitor._listener._file.write(f" {operator} ")
        return None

    def visitExp_aritmetica(self, arithmetic_expression: LAParser.Exp_aritmeticaContext):
        self.visitTermo(arithmetic_expression.termo(0))
        for i, term in enumerate(arithmetic_expression.termo()):
            if i > 0:
                self._visitor._listener._file.write(f" {arithmetic_expression.op1(i - 1).getText()} ")
                self.visitTermo(term)
        return None
    
    def visitTermo(self, term: LAParser.TermoContext):
        self.visitFator(term.fator(0))
        for i, factor in enumerate(term.fator()):
            if i > 0:
                self._visitor._listener._file.write(f" {term.op2(i - 1).getText()} ")
                self.visitFator(factor)
        return None
    
    def visitFator(self, factor: LAParser.FatorContext):
        self.visitParcela(factor.parcela(0))
        for i, portion in enumerate(factor.parcela()):
            if i > 0:
                self._visitor._listener._file.write(f" {factor.op3(i - 1).getText()} ")
                self.visitParcela(portion)
        return None
    
    def visitParcela(self, portion: LAParser.ParcelaContext):
        if portion.parcela_unario():
            if portion.op_unario():
                self._visitor._listener._file.write(f" {portion.op_unario().getText()} ")
            self.visitParcela_unario(portion.parcela_unario())
        else:
            self.visitParcela_nao_unario(portion.parcela_nao_unario())
        return None
    
    def visitParcela_unario(self, unary_portion: LAParser.Parcela_unarioContext):
        if unary_portion.identificador():
            if (unary_portion.getChild(0).getText() == "^"):
                self._visitor._listener._file.write("*")
            self.visitIdentificador(unary_portion.identificador())
        elif unary_portion.IDENT():
            self._visitor._listener._file.write(f"{unary_portion.IDENT().getText()}(")
            self.visitExpressao(unary_portion.expressao(0))
            for i, expression in enumerate(unary_portion.expressao()):
                if i > 0:
                    self._visitor._listener._file.write(", ")
                    self.visitExpressao(expression)
            self._visitor._listener._file.write(")")
        elif unary_portion.NUM_INT():
            self._visitor._listener._file.write(unary_portion.NUM_INT().getText())
        elif unary_portion.NUM_REAL():
            self._visitor._listener._file.write(unary_portion.NUM_REAL().getText())
        else:
            self._visitor._listener._file.write("(")
            for expression in unary_portion.expressao():
                self.visitExpressao(expression)
            self._visitor._listener._file.write(")")
        return None
    
    def visitParcela_nao_unario(self, nonunary_portion: LAParser.Parcela_nao_unarioContext):
        if nonunary_portion.identificador():
            if nonunary_portion.getChild(0).getText() == "&":
                self._visitor._listener._file.write("&")
            self.visitIdentificador(nonunary_portion.identificador())
        else:
            self._visitor._listener._file.write(nonunary_portion.CADEIA().getText())
        return None
    
    def visitIdentificador(self, identifier: LAParser.IdentificadorContext):
        self._visitor._listener._file.write(identifier.getText())
        return None

    def visitConstantes(self, constants: LAParser.ConstantesContext):
        for range_number in  constants.numero_intervalo():
            start = int(range_number.NUM_INT(0).getText())
            if range_number.op_unario1:
                start = -start
            if range_number.op_unario2:
                end = -int(range_number.NUM_INT(1).getText())
            elif range_number.NUM_INT(1):
                end = int(range_number.NUM_INT(1).getText())
            else:
                end = start
            for i in range(start, end + 1):
                self._visitor._listener._file.write(f"\t\tcase {i}:\n")
        return None
    
    def visitValor_constante(self, constant_value: LAParser.Valor_constanteContext):
        if constant_value.CADEIA():
            self._visitor._listener._file.write(f"\"{constant_value.CADEIA().getText()}\"\n")
        elif constant_value.NUM_INT():
            self._visitor._listener._file.write(f"{constant_value.NUM_INT().getText()}\n")
        elif constant_value.NUM_REAL():
            self._visitor._listener._file.write(f"{constant_value.NUM_REAL().getText()}\n")
        elif constant_value.getChild(0).getText() == "verdadeiro":
            self._visitor._listener._file.write("1\n")
        else:
            self._visitor._listener._file.write("0\n")
        
        return None

    def variable_generate(self, variable: Variable, pointer = False):
        tpointer = "*" if pointer else ""
        if variable.type in ['inteiro', 'logico']:
            return f"int {tpointer}{variable.name}"
        elif variable.type == 'real':
            return f"float {tpointer}{variable.name}"
        elif variable.type == 'literal':
            return f"char {tpointer}{variable.name}[80]"
        elif variable.type == 'registro':
            text = "struct {\n"
            for child in variable.childrens:
                text+= "\t"
                text += self.variable_generate(variable.childrens[child])
                text+= ";\n"
            text += "} " + variable.name
            return text
        else:
            return f"{variable.type} {tpointer}{variable.name}"
