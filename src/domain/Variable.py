from typing import Dict

class Variable:
    def __init__(self, name = '', type = None):
        self.name = name
        self.type = type
        self.childrens: Dict[Variable] = {}
        self.return_type = None
        self.params: Dict[Variable] = {}

    def set_type(self, type):
        self.type = type

    def set_return_type(self, type):
        self.return_type = type

    def set_params(self, params):
        self.params = params

    def __str__(self):
        return f"Variable(name={self.name},type={self.type},childrens={self.childrens.keys()})"
