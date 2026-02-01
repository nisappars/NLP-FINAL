import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ada_semantic_analysis.core.lexer import AdaLexer
from ada_semantic_analysis.core.parser import AdaParser
from ada_semantic_analysis.core.skm import SystemKnowledgeModel
from ada_semantic_analysis.core.skm_builder import SKMBuilder
from ada_semantic_analysis.comparison.differ import SemanticDiffer
from ada_semantic_analysis.comparison.invariant_checker import LegacyInvariantChecker

def parse_dir(path, name):
    skm = SystemKnowledgeModel(name)
    builder = SKMBuilder(skm)
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.adb'):
                with open(os.path.join(root, f), 'r') as fh:
                    code = fh.read()
                lexer = AdaLexer(code)
                parser = AdaParser(lexer)
                unit = parser.parse_compilation_unit()
                builder.build(unit)
    return skm

def main():
    v1_path = os.path.abspath("scenarios/test_v1")
    v2_path = os.path.abspath("scenarios/test_v2")

    print(f"Loading V1 from {v1_path}...")
    skm1 = parse_dir(v1_path, "V1")
    print(f"Loading V2 from {v2_path}...")
    skm2 = parse_dir(v2_path, "V2")

    print("Running Differ...")
    differ = SemanticDiffer(skm1, skm2)
    changes = differ.diff()

    print("Running Invariant Checker...")
    checker = LegacyInvariantChecker(skm1, skm2)
    invariants = checker.check()

    print("\n--- RESULTS ---")
    print(f"Changes Detected: {len(changes)}")
    for c in changes:
        print(f"  [{c.risk}] {c.classification} ({c.file_name})")

    print(f"\nInvariants Broken: {len(invariants)}")
    for inv in invariants:
        print(f"  [{inv.severity}] {inv.rule_id}: {inv.description}")

    # ASSERTIONS
    print("\n--- VERIFICATION ---")
    
    # 1. Rename Detection
    renames = [c for c in changes if "Renamed Procedure" in c.classification]
    # Check if correct rename pair is mentioned.
    if len(renames) == 1 and "To_Be_Renamed" in renames[0].classification and "Renamed_Logic" in renames[0].classification:
        print("PASS: Rename Detected correctly.")
    else:
        print(f"FAIL: Rename detection failed. Found: {[c.classification for c in renames]}")

    # 2. Safety Path Removal (Differ Risk)
    safety_changes = [c for c in changes if "RULE-0" in c.classification and c.risk == "High"]
    # The classification string contains "Logic Modified: ... [RULE-0 ...]"
    # Let's check specifically for Old_Logic
    old_logic_change = next((c for c in changes if "Old_Logic" in c.file_name or "Old_Logic" in c.classification or "Main.Old_Logic" in str(skm1.procedures.keys())), None)
    
    # Since filename is approximated from scope "Main.Old_Logic" -> "Main.adb" usually in real app, 
    # but here scope is "Main.Old_Logic", file is "Main.adb".
    # Wait, differ.py uses `name.split('.')[0] + ".adb"`. 
    # In my single file scenario, everything is in `Main`. 
    # Procedures are `Main.Old_Logic`, `Main.Safety_Check`.
    # So all changes will map to `Main.adb`.
    
    found_safety_rule = False
    for c in changes:
        if "RULE-0" in c.classification and "High" == c.risk:
            found_safety_rule = True
            print(f"PASS: Safety Rule triggered in changes: {c.classification}")
            break
    
    if not found_safety_rule:
        print("FAIL: Safety Rule (RULE-0) not triggered in Differ.")

    # 3. Invariant Checked
    # Expect INV-01 for Main.Old_Logic
    found_inv = False
    for inv in invariants:
        if inv.rule_id == "INV-01" and "Main.Old_Logic" in inv.description:
             found_inv = True
             print(f"PASS: Invariant Checker caught missed safety call: {inv.description}")
             break
    
    if not found_inv:
         print("FAIL: Invariant Checker missed the safety drop.")

if __name__ == "__main__":
    main()
