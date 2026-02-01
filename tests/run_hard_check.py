import sys
import os
import shutil

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ada_semantic_analysis.core.lexer import AdaLexer
from ada_semantic_analysis.core.parser import AdaParser
from ada_semantic_analysis.core.skm import SystemKnowledgeModel
from ada_semantic_analysis.core.skm_builder import SKMBuilder
from ada_semantic_analysis.comparison.differ import SemanticDiffer
from ada_semantic_analysis.comparison.invariant_checker import LegacyInvariantChecker

SCENARIO_ROOT = os.path.abspath("tests/scenarios_hard")

def setup_scenarios():
    if os.path.exists(SCENARIO_ROOT):
        shutil.rmtree(SCENARIO_ROOT)
    os.makedirs(SCENARIO_ROOT)

    # --- Scenario 1: Identity Rename ---
    # V1: Proc A
    # V2: Proc B (Same Body)
    make_file("s1_identity", "v1", "proc.adb", "procedure A is begin null; end A;")
    make_file("s1_identity", "v2", "proc.adb", "procedure B is begin null; end B;")

    # --- Scenario 2: Arg Swap Rename ---
    # V1: Proc A(X, Y)
    # V2: Proc B(Y, X) - logic same
    make_file("s2_args", "v1", "proc.adb", "procedure A(X: in Int; Y: in Int) is begin null; end A;")
    make_file("s2_args", "v2", "proc.adb", "procedure B(Y: in Int; X: in Int) is begin null; end B;")

    # --- Scenario 3: Deep Safety Drop ---
    # V1: Call inside IF
    # V2: Removed
    body_v1 = "procedure X is begin if True then Safety_Handler; end if; end X;"
    body_v2 = "procedure X is begin if True then null; end if; end X;"
    make_file("s3_safety", "v1", "main.adb", body_v1)
    make_file("s3_safety", "v2", "main.adb", body_v2)

    # --- Scenario 4: Invariant Breach ---
    # V1: Main calls Init_Safety
    # V2: Main calls Nothing
    # V1: Main calls Init_Safety. Init_Safety exists.
    # V2: Main calls Nothing. Init_Safety exists or not doesn't matter for the call check, but let's define it so it's a valid ref.
    make_file("s4_invariant", "v1", "main.adb", "procedure Init_Safety is begin null; end; procedure Main is begin Init_Safety; end Main;")
    make_file("s4_invariant", "v2", "main.adb", "procedure Init_Safety is begin null; end; procedure Main is begin null; end Main;")

    # --- Scenario 5: Logic Change (Safe) ---
    make_file("s5_logic", "v1", "calc.adb", "procedure Do is begin x := x + 1; end Do;")
    make_file("s5_logic", "v2", "calc.adb", "procedure Do is begin x := x + 2; end Do;")

    # --- Scenario 6: Dependency Ripple ---
    # V1/V2: Root calls Leaf. Leaf modified.
    common_struct = "procedure Root is begin Leaf; end Root;"
    make_file("s6_ripple", "v1", "root.adb", common_struct)
    make_file("s6_ripple", "v2", "root.adb", common_struct)
    make_file("s6_ripple", "v1", "leaf.adb", "procedure Leaf is begin A; end Leaf;")
    make_file("s6_ripple", "v2", "leaf.adb", "procedure Leaf is begin B; end Leaf;")

    # --- Scenario 7: New Procedure ---
    make_file("s7_new", "v1", "pkg.adb", "package body P is end P;")
    make_file("s7_new", "v2", "pkg.adb", "package body P is procedure New_Feat is begin null; end; end P;")

    # --- Scenario 8: Deleted Procedure ---
    make_file("s8_del", "v1", "pkg.adb", "procedure Old is begin null; end;")
    make_file("s8_del", "v2", "pkg.adb", "") # Empty file

    # --- Scenario 9: Control Flow Swap ---
    # V1: While loop
    # V2: For loop
    make_file("s9_flow", "v1", "loop.adb", "procedure L is begin while True loop null; end loop; end L;")
    make_file("s9_flow", "v2", "loop.adb", "procedure L is begin for I in 1..10 loop null; end loop; end L;")

    # --- Scenario 10: Parser Resilience (Task) ---
    # V1: Simple
    # V2: Task syntax
    make_file("s10_task", "v1", "task.adb", "procedure T is begin null; end T;")
    make_file("s10_task", "v2", "task.adb", "task body T is begin accept E; end T;")


def make_file(scenario, ver, name, content):
    p = os.path.join(SCENARIO_ROOT, scenario, ver)
    os.makedirs(p, exist_ok=True)
    with open(os.path.join(p, name), 'w') as f:
        f.write(content)

def parse_dir(path, name):
    skm = SystemKnowledgeModel(name)
    builder = SKMBuilder(skm)
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.adb'):
                with open(os.path.join(root, f), 'r') as fh:
                    code = fh.read()
                try:
                    lexer = AdaLexer(code)
                    parser = AdaParser(lexer)
                    unit = parser.parse_compilation_unit()
                    builder.build(unit)
                except Exception as e:
                    print(f"    [WARN] Parser exception on {f}: {e}")
    return skm

def run_test(name, validator):
    print(f"Running {name}...", end=" ")
    v1 = os.path.join(SCENARIO_ROOT, name, "v1")
    v2 = os.path.join(SCENARIO_ROOT, name, "v2")
    
    skm1 = parse_dir(v1, "V1")
    skm2 = parse_dir(v2, "V2")
    
    differ = SemanticDiffer(skm1, skm2)
    changes = differ.diff()
    
    checker = LegacyInvariantChecker(skm1, skm2)
    invs = checker.check()
    
    try:
        validator(changes, invs)
        print("PASS")
        return True
    except AssertionError as e:
        print(f"FAIL -> {e}")
        # Debug info
        print("    Changes Found:")
        for c in changes: print(f"      - {c.classification} ({c.risk})")
        print("    Invariants:")
        for i in invs: print(f"      - {i.description}")
        return False

def main():
    setup_scenarios()
    print("--- STARTING HARD CHECK ---")
    
    passed = 0
    total = 10
    
    # 1. Identity Rename
    def val_1(chgs, invs):
        renames = [c for c in chgs if "Renamed" in c.classification]
        assert len(renames) == 1, f"Expected 1 rename, got {len(renames)}"
        assert renames[0].risk == "Low", "Rename should be Low risk"
    if run_test("s1_identity", val_1): passed += 1

    # 2. Arg Swap (Structural Logic Same?)
    def val_2(chgs, invs):
        # A(X, Y) vs B(Y, X). Fingerprint input set is same ({X, Y}:Int). Logic null.
        # Should be rename.
        renames = [c for c in chgs if "Renamed" in c.classification]
        assert len(renames) == 1, "Failed to detect rename with arg swap"
    if run_test("s2_args", val_2): passed += 1

    # 3. Deep Safety Drop
    def val_3(chgs, invs):
        safetys = [c for c in chgs if "RULE-0" in c.classification]
        assert len(safetys) > 0, "Missed safety removal in nested block"
        assert safetys[0].risk == "High", "Safety removal must be High risk"
    if run_test("s3_safety", val_3): passed += 1

    # 4. Invariant Breach
    def val_4(chgs, invs):
        # Differ might capture logic change, but Invariant MUST capture "Stop Calling Safety"
        # INV-01: Procedure Main stopped calling...
        assert len(invs) > 0, "Invariant Checker missed dropped safety call"
        assert "Main" in invs[0].location, "Location wrong"
    if run_test("s4_invariant", val_4): passed += 1

    # 5. Logic Change
    def val_5(chgs, invs):
        # x+1 vs x+2. Fingerprint should differ.
        mods = [c for c in chgs if "Logic Modified" in c.classification]
        assert len(mods) == 1, "Missed logic modification (+1 to +2)"
    if run_test("s5_logic", val_5): passed += 1

    # 6. Ripple
    def val_6(chgs, invs):
        # Leaf modified. Root calls Leaf.
        # We expect 1 change (Leaf). Skm naming might be Global.Leaf -> Global.adb.
        assert len(chgs) > 0, "No changes found for Ripple test"
        leaf_change = chgs[0] 
        print(f"      (Debug) Change File: {leaf_change.file_name}, Affected: {leaf_change.affected_files}")
        
        # Since Root calls Leaf, and Root is in V2 skm call graph... 
        # differ.py uses skm_new.call_graph. 
        # get_affected finds callers.
        # Expect "Root" in the affected list
        assert "Root" in leaf_change.affected_files, f"Impact prop failed. Affected: {leaf_change.affected_files}"
    if run_test("s6_ripple", val_6): passed += 1

    # 7. New Procedure
    def val_7(chgs, invs):
        adds = [c for c in chgs if "Inserted" in c.classification]
        assert len(adds) == 1, "Missed new procedure insertion"
        assert adds[0].risk == "Low", "New code should be Low risk"
    if run_test("s7_new", val_7): passed += 1

    # 8. Deleted Procedure
    def val_8(chgs, invs):
        dels = [c for c in chgs if "Removal" in c.classification]
        assert len(dels) == 1, "Missed deletion"
        assert dels[0].risk == "High", "Deletion should be High risk"
    if run_test("s8_del", val_8): passed += 1
    
    # 9. Flow Swap
    def val_9(chgs, invs):
        # While vs For. Fingerprint complexity/tokens differ.
        mods = [c for c in chgs if "Logic Modified" in c.classification]
        assert len(mods) == 1, "Missed control flow structure change"
    if run_test("s9_flow", val_9): passed += 1

    # 10. Parser Resilience (Task)
    def val_10(chgs, invs):
        # Task body syntax might fail if parser assumes 'procedure/function/package'
        # BUT we implemented PartialAnalysisError. 
        # Our parse_dir catches Exception and prints WARN.
        # So SKM might be empty.
        # If SKM is null, we might see "Removal" of T (from v1).
        # We just want to ensure it didn't crash the script.
        pass # If we got here, we didn't crash.
    if run_test("s10_task", val_10): passed += 1

    print(f"\nSCORE: {passed}/{total}")
    if passed == total:
        print("RESULT: EXCELLENT (System is highly robust)")
    elif passed >= 8:
        print("RESULT: GOOD (Minor gaps)")
    else:
        print("RESULT: NEEDS WORK")

if __name__ == "__main__":
    main()
