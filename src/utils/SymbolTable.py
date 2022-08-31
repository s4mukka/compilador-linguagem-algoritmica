from typing import Dict, List
from src.domain import Variable

class SymbolTable:
    def __init__(self):
        self._table: Dict[Variable] = {}

    def get_type(self, name: str):
        return self._table[name].type
    
    def get_var(self, name: str) -> Variable:
        return self._table[name]
    
    def get_all(self) -> List[Variable]:
        return list(self._table.values())
    
    def add(self, var: Variable):
        self._table[var.name] = var
    
    def add_all(self, vars: List[Variable]):
        for var in vars:
            self._table[var.name] = var

    def contain(self, name: str):
        return name in self._table