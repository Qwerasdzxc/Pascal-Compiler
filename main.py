from lexer import Lexer
from parser import Parser
from symbolizer import Symbolizer
from generator import Generator
from runner import Runner


def run():
    test_id = '01'  # Test folder number [01-11]
    path_root = 'Tests/'
    args = {'src': f'{path_root}{test_id}/src.pas', 'gen': f'{path_root}{test_id}/gen.c'}

    with open(args['src'], 'r') as source:
        text = source.read()
        lexer = Lexer(text)
        tokens = lexer.lex()
        parser = Parser(tokens)
        ast = parser.parse()
        symbolizer = Symbolizer(ast)
        symbolizer.symbolize()
        generator = Generator(ast)
        generator.generate(args['gen'])
        runner = Runner(ast)
        runner.run()


run()
