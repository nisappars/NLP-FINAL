import unittest
from ada_semantic_analysis.core.skm import SystemKnowledgeModel, ProcedureInfo, VariableInfo
from ada_semantic_analysis.comparison.differ import SemanticDiffer

class TestDiffer(unittest.TestCase):
    def test_detection(self):
        # SKM 1
        skm1 = SystemKnowledgeModel("V1")
        p1 = ProcedureInfo("Main", "procedure Main", 1, 10, [], [])
        p1.cyclomatic_complexity = 1
        skm1.add_procedure(p1)
        
        # SKM 2 (Modified Main, Added Helper)
        skm2 = SystemKnowledgeModel("V2")
        # Main modified: complexity increased, inputs changed
        p1_mod = ProcedureInfo("Main", "procedure Main", 1, 15, ["NewArg"], [])
        p1_mod.cyclomatic_complexity = 2
        skm2.add_procedure(p1_mod)
        
        # Helper added
        p2 = ProcedureInfo("Helper", "procedure Helper", 20, 30, [], [])
        skm2.add_procedure(p2)
        
        differ = SemanticDiffer(skm1, skm2)
        changes = differ.diff()
        
        self.assertEqual(len(changes), 2)
        
        added = [c for c in changes if c.kind == "ADDED"]
        self.assertEqual(len(added), 1)
        self.assertEqual(added[0].subject, "Helper")
        
        modified = [c for c in changes if c.kind == "MODIFIED"]
        self.assertEqual(len(modified), 1)
        self.assertEqual(modified[0].subject, "Main")
        self.assertIn("Inputs changed", modified[0].details)
        self.assertEqual(modified[0].risk, "High")

if __name__ == '__main__':
    unittest.main()
