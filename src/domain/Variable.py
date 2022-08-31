from typing import Dict, List

class Variable:
    def __init__(self, name = '', type = None):
        self.name = name
        self.type = type
        self.childrens: Dict[Variable] = {}
        self.return_type = None
        self.params: List[Variable] = {}

    def set_type(self, type):
        self.type = type

    def set_return_type(self, type):
        self.return_type = type

    def set_params(self, params):
        self.params = params

    @property
    def format(self):
        if self.type in ['inteiro', 'logico']:
            return '%d'
        elif self.type == 'real':
            return '%f'
        elif self.type == 'literal':
            return '%s'

    def __str__(self):
        text = f"Variable(name={self.name},type={self.type}"
        if self.childrens:
            text += f",childrens={self.childrens.keys()}"
        if self.params:
            text += f",params={self.params}"
        return f"{text})"
