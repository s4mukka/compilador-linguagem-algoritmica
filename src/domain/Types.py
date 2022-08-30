class Types:
    def __init__(self):
        self._natives = ['inteiro', 'real', 'literal', 'logico']
        self._created = []

    def get_type(self, type):
        if type in self._natives or type in self._created:
            return type
        return None

    def validate(self, a, b):
        if a == 'literal' and b == 'literal':
            return 'literal'
        if a == 'real' and b in ['inteiro', 'real']:
            return 'real'
        if a == 'logico' and b in ['logico', 'inteiro', 'real']:
            return 'logico'
        if a == 'inteiro' and b in ['inteiro', 'real']:
            return 'inteiro'
        if a == b:
            return a
        print("*****************", a, b, "**************")
        return 'invalido'

    def equivalent(self, a, b):
        if a == b:
            return a
        return 'invalido'
    
    def add(self, type):
        self._created.append(type)