import re
from typing import NamedTuple, Iterator, List

class token(NamedTuple):
    type: str
    value: str
    line: int
    column: int

class AdaLexer:
    """
    A deterministic regex-based tokenizer for ADA.
    
    NOTE: This lexer performs pattern matching for tokenization only.
    It does not validate ADA grammar or semantics.
    """
    
    # Define token patterns
    # Order matters: Specific keywords first, then general identifiers
    KEYWORDS = {
        'procedure', 'function', 'package', 'body', 'is', 'begin', 'end',
        'if', 'then', 'elsif', 'else', 'loop', 'while', 'for', 'in', 'out',
        'return', 'type', 'record', 'array', 'of', 'constant', 'all', 'reverse',
        'null', 'others', 'case', 'when', 'exit', 'goto', 'raise', 'exception',
        'terminate', 'select', 'accept', 'entry', 'protected', 'task', 'with', 'use', 'new'
    }

    TOKEN_SPEC = [
        ('COMMENT',   r'--.*'),           # Single line comment
        ('STRING',    r'"([^"]|"")*"'),   # String literal
        ('NUMBER',    r'\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?'), # Integer or Float
        ('ASSIGN',    r':='),             # Assignment
        ('NEQ',       r'/='),             # Not equal
        ('GTE',       r'>='),             # Greater than or equal
        ('LTE',       r'<='),             # Less than or equal
        ('BOX',       r'<>'),             # Box
        ('ARROW',     r'=>'),             # Arrow
        ('DOT_DOT',   r'\.\.'),           # Range
        ('TICK',      r"'"),              # Attribute tick
        ('LPAREN',    r'\('),
        ('RPAREN',    r'\)'),
        ('SEMI',      r';'),
        ('COLON',     r':'),
        ('COMMA',     r','),
        ('DOT',       r'\.'),
        ('PLUS',      r'\+'),
        ('MINUS',     r'-'),
        ('STAR',      r'\*'),
        ('SLASH',     r'/'),
        ('EQ',        r'='),
        ('GT',        r'>'),
        ('LT',        r'<'),
        ('PIPE',      r'\|'),
        ('ID',        r'[A-Za-z][A-Za-z0-9_]*'), # Identifiers
        ('NEWLINE',   r'\n'),             # Line endings
        ('SKIP',      r'[ \t\r]+'),       # Skip over spaces and tabs
        ('MISMATCH',  r'.'),              # Any other character
    ]

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tokens = []
        self.current_token_idx = 0

    def tokenize(self) -> List[token]:
        """
        Tokenizes the input source code.
        """
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.TOKEN_SPEC)
        get_token = re.compile(tok_regex).match
        line_num = 1
        line_start = 0
        mo = get_token(self.source_code)
        
        self.tokens = []
        
        while mo is not None:
            kind = mo.lastgroup
            value = mo.group(kind)
            
            if kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
            elif kind == 'SKIP':
                pass
            elif kind == 'COMMENT':
                pass
            elif kind == 'MISMATCH':
                # For now, just print or ignore, but strictly we should error
                # print(f"Unexpected character: {value!r} on line {line_num}")
                pass
            else:
                if kind == 'ID' and value.lower() in self.KEYWORDS:
                    kind = value.upper() # Use the keyword as the token type
                
                column = mo.start() - line_start
                self.tokens.append(token(kind, value, line_num, column))
                
            mo = get_token(self.source_code, mo.end())
            
        # Add EOF token
        self.tokens.append(token("EOF", "", line_num, 0))
        return self.tokens

if __name__ == "__main__":
    # Simple test
    code = """
    procedure Hello is
       X : Integer := 10;
    begin
       if X > 5 then
          X := X + 1;
       end if;
    end Hello;
    """
    lexer = AdaLexer(code)
    for tok in lexer.tokenize():
        print(tok)
