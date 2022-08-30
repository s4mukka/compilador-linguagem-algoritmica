from collections import deque
from typing import Deque

from .SymbolTable import SymbolTable

class Scopes:
    def __init__(self):
        self._scope_symbol_table: Deque[SymbolTable] = deque()
        self.create_new_scope()

    def create_new_scope(self):
        self._scope_symbol_table.appendleft(SymbolTable())

    def copy_new_scope(self):
        copy_table = self.see_scope().get_all()
        self.create_new_scope()
        self.see_scope().add_all(copy_table)

    def get_list_scopes(self):
        return self._scope_symbol_table

    def abandon_scope(self):
        poped = self._scope_symbol_table.popleft()

    def see_scope(self):
        return self._scope_symbol_table[0]