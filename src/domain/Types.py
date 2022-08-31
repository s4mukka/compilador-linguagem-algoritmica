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

    def get_format(self, type):
        if type in ['inteiro', 'logico']:
            return '%d'
        elif type == 'real':
            return '%f'
        elif type == 'literal':
            return '%s'

    def get_c_type(self, type):
        if type in ['inteiro', 'logico']:
            return 'int'
        elif type == 'real':
            return 'float'
        elif type == 'literal':
            return 'char *'
