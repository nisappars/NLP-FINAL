import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ada_semantic_analysis.core.lexer import AdaLexer
from ada_semantic_analysis.core.parser import AdaParser
from ada_semantic_analysis.core.skm import SystemKnowledgeModel
from ada_semantic_analysis.core.skm_builder import SKMBuilder
import hashlib

code_v1 = """
procedure Test is
    Safety_Threshold : constant Float := 850.0;
begin
    null;
end Test;
"""

code_v2 = """
procedure Test is
    Safety_Threshold : constant Float := 900.0;
begin
    null;
end Test;
"""

def get_hash(code, name):
    skm = SystemKnowledgeModel(name)
    builder = SKMBuilder(skm)
    lexer = AdaLexer(code)
    parser = AdaParser(lexer)
    unit = parser.parse_compilation_unit()
    builder.build(unit)
    
    proc = skm.procedures.get("Test")
    if proc:
        print(f"[{name}] Hash: {proc.body_hash}")
        # print(f"[{name}] Vars: {skm.variables.keys()}")
        return proc.body_hash
    return None

h1 = get_hash(code_v1, "V1")
h2 = get_hash(code_v2, "V2")

if h1 == h2:
    print("FAIL: Hash Collision! Change not detected.")
else:
    print("PASS: Hash changed.")
