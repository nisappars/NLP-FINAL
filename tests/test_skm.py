import unittest
from ada_semantic_analysis.core.lexer import AdaLexer
from ada_semantic_analysis.core.parser import AdaParser
from ada_semantic_analysis.core.skm import SystemKnowledgeModel
from ada_semantic_analysis.core.skm_builder import SKMBuilder

class TestSKMBuilder(unittest.TestCase):
    def test_skm_extraction(self):
        code = """
        procedure Main is
           X : Integer := 10;
           procedure Helper(Val : in Integer) is
           begin
               X := Val;
           end Helper;
        begin
           if X > 5 then
               Helper(20);
           end if;
        end Main;
        """
        lexer = AdaLexer(code)
        parser = AdaParser(lexer)
        unit = parser.parse_compilation_unit()
        
        skm = SystemKnowledgeModel("TestSystem")
        builder = SKMBuilder(skm)
        builder.build(unit)
        
        # Verify Procedures
        self.assertIn("Global.Main", skm.procedures)
        self.assertIn("Main.Helper", skm.procedures)
        
        main = skm.procedures["Global.Main"]
        helper = skm.procedures["Main.Helper"]
        
        # Verify variables
        self.assertIn("Main.X", skm.variables)
        self.assertIn("Main.Helper.Val", skm.variables)
        
        # Verify calls (Basic name matching)
        self.assertIn("Helper", main.calls)
        
        # Verify writes
        self.assertIn("X", helper.written_vars)
        
        # Verify Complexity
        # Main has 1 IF -> complexity 2
        self.assertEqual(main.cyclomatic_complexity, 2)

if __name__ == '__main__':
    unittest.main()
