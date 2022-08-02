# Compilador para a Linguagem Algorítmica
> Ministrada pelo professor `Daniel Lucrédio`

Esse repositório tem o intúito de implementar um compilador para a
`Linguagem Algorítmica` (desenvolvida pelo professor Jander, no âmbito do DC/UFSCar)
como estudo para a matéria `Contrução de Compiladores` na `Universidade Federal de São Carlos`.

### Alunos envolvidos
> - Samuel Henrique Ferreira Pereira - RA 769806
> - Kevin Vinicius Carvalho de Brito  - RA 769769

### O compilador consiste em 4 partes que serão divididos em 5 trabalhos para a matéria:
> - Analisador Léxico (Trabalho 1)
> - Analisador Sintático (Trabalho 2)
> - Analisador Semântico (Trabalho 3 e 4)
> - Gerador de código (Trabalho 5)

### Trabalhos feitos:
> - [x] Trabalho 1
> - [x] Trabalho 2
> - [X] Trabalho 3
> - [ ] Trabalho 4
> - [ ] Trabalho 5

### Rodando a aplicação
    # Clone este repositório
    $ git clone https://github.com/s4mukka/compilador-linguagem-algoritmica

    # Acesse a pasta do projeto
    $ cd compilador-linguagem-algoritmica

    # Instale o runtime para python
    $ pip install antlr4-python3-runtime

    # Para executar utilizando uma entrada customizada
    $ make

    # Para executar utilizando os casos de testes
    # O argumento T pode ser: t1|t2|t3|t4|t5|gabarito
    $ make test T=t1

### Tecnologias
As seguintes ferramentas foram usadas na construção do projeto:
> - [Python 3](https://www.python.org/)
> - [ANTLR](https://www.antlr.org/)
> - [GNU Make](https://www.gnu.org/software/make/)
