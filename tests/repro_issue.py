from ada_semantic_analysis.core.lexer import AdaLexer
from ada_semantic_analysis.core.parser import AdaParser

code = """
package HAL is
    procedure Read_Sensor(Id : Integer; Val : out Float_Type);
end HAL;
"""

try:
    lexer = AdaLexer(code)
    parser = AdaParser(lexer)
    unit = parser.parse_compilation_unit()
    print("Successfully parsed HAL package!")
    print(unit)
except Exception as e:
    print(f"FAILED: {e}")
