import unittest
from ada_semantic_analysis.core.lexer import AdaLexer
from ada_semantic_analysis.core.parser import AdaParser
from ada_semantic_analysis.core.ast_nodes import *

class TestAdaParser(unittest.TestCase):
    def test_simple_procedure(self):
        code = """
        procedure Hello is
           X : Integer := 10;
        begin
           X := X + 1;
        end Hello;
        """
        lexer = AdaLexer(code)
        parser = AdaParser(lexer)
        unit = parser.parse_compilation_unit()
        
        self.assertEqual(len(unit.files), 1)
        proc = unit.files[0]
        self.assertIsInstance(proc, SubprogramNode)
        self.assertEqual(proc.name, "Hello")
        self.assertEqual(len(proc.declarations), 1)
        self.assertEqual(len(proc.statements), 1)
        
    def test_if_statement(self):
        code = """
        procedure Check is
        begin
           if A > B then
              Do_Something;
           elsif A = B then
              Do_Other;
           else
              Do_Nothing;
           end if;
        end Check;
        """
        lexer = AdaLexer(code)
        parser = AdaParser(lexer)
        unit = parser.parse_compilation_unit()
        
        proc = unit.files[0]
        if_stmt = proc.statements[0]
        self.assertIsInstance(if_stmt, IfNode)
        self.assertTrue(">" in if_stmt.condition)
        self.assertEqual(len(if_stmt.elsif_parts), 1)
        self.assertIsNotNone(if_stmt.else_block)

    def test_package_spec(self):
        code = """
        package My_Types is
           type My_Int is range 1 .. 10;
           X : My_Int;
        end My_Types;
        """
        lexer = AdaLexer(code)
        parser = AdaParser(lexer)
        unit = parser.parse_compilation_unit()
        
        pkg = unit.files[0]
        self.assertIsInstance(pkg, PackageNode)
        self.assertEqual(pkg.name, "My_Types")
        self.assertFalse(pkg.is_body)
        self.assertEqual(len(pkg.declarations), 2)

if __name__ == '__main__':
    unittest.main()
