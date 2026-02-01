from .lexer import AdaLexer, token
from .ast_nodes import *
from typing import List, Optional

class PartialAnalysisError(Exception):
    """Raised when the parser encounters ambiguous or unsupported constructs."""
    pass

class AdaParser:
    """
    This module implements a Simplified Structural AST Builder intended for 
    semantic comparison and change impact analysis, not a full ADA compiler 
    or language-complete parser.
    """
    def __init__(self, lexer: AdaLexer):
        self.lexer = lexer
        self.tokens = self.lexer.tokenize()
        self.pos = 0
        self.current_token = self.tokens[0]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = token("EOF", "", -1, -1)

    def match(self, token_type: str) -> bool:
        if self.current_token.type == token_type:
            self.advance()
            return True
        return False

    def expect(self, token_type: str) -> token:
        if self.current_token.type == token_type:
            tok = self.current_token
            self.advance()
            return tok
        raise SyntaxError(f"Expected {token_type}, found {self.current_token.type} at line {self.current_token.line}")

    def peek(self) -> str:
        return self.current_token.type

    # --- Grammar Rules ---

    def parse_compilation_unit(self) -> CompilationUnitNode:
        units = []
        try:
            while self.peek() != "EOF":
                if self.peek() == "WITH" or self.peek() == "USE":
                    self.parse_context_clause()
                
                if self.peek() in ("PROCEDURE", "FUNCTION"):
                    units.append(self.parse_subprogram())
                elif self.peek() == "PACKAGE":
                    units.append(self.parse_package())
                else:
                    # Fail Semantic Safety: Do not guess.
                    # Flag manual review required for unsupported top-level items.
                    raise PartialAnalysisError(f"Unexpected top-level token: {self.current_token}")
        except PartialAnalysisError as e:
            # Re-raise to be caught by caller (App/Script)
            raise e
        except Exception as e:
            # Catch unexpected crashes and wrap them
            raise PartialAnalysisError(f"Parser Crash at line {self.current_token.line}: {e}")
            
        return CompilationUnitNode(files=units)

    def parse_context_clause(self):
        while self.peek() in ("WITH", "USE"):
            self.advance()
            # Consume until semicolon
            while self.peek() != "SEMI" and self.peek() != "EOF":
                self.advance()
            self.match("SEMI")

    def parse_package(self) -> PackageNode:
        self.expect("PACKAGE")
        is_body = False
        if self.match("BODY"):
            is_body = True
        
        name = self.parse_compound_name()
        self.expect("IS")
        
        declarations = self.parse_declarations()
        
        body_stmts = None
        if self.match("BEGIN"):
            body_stmts = self.parse_statements()
        
        self.expect("END")
        # Optional: match name again
        if self.peek() == "ID":
            self.advance() # consume name
            if self.peek() == "DOT": # Handle qualified names
                 self.advance()
                 self.match("ID")

        self.match("SEMI")
        
        return PackageNode(name=name, is_body=is_body, declarations=declarations, body=body_stmts)

    def parse_subprogram(self) -> SubprogramNode:
        kind = self.current_token.type.lower() # procedure or function
        self.advance()
        
        name = self.parse_compound_name()
        params = []
        if self.match("LPAREN"):
            params = self.parse_parameters()
            self.match("RPAREN")
            
        return_type = None
        if kind == "function":
            self.expect("RETURN")
            return_type = self.parse_type_name()
            
        decls = []
        stmts = []
        is_body = False
        
        if self.match("IS"):
            # It's a body or strict declaration?
            # Special case: "procedure X is new ..." (Generics - not supported yet but check)
            if self.match("NEW"):
                # Instantiation - Skip for now
                while self.peek() != "SEMI":
                    self.advance()
                self.match("SEMI")
                # Return empty node?
                return SubprogramNode(name=name, kind=kind, parameters=params, return_type=return_type, is_body=False)
            
            is_body = True
            decls = self.parse_declarations()
            self.expect("BEGIN")
            stmts = self.parse_statements()
            self.expect("END")
            # Optional name matching
            if self.peek() == "ID":
                self.parse_compound_name()
            self.match("SEMI")
            
        elif self.match("SEMI"):
            # It's a spec
            is_body = False
            
        else:
             # Error or Abstract?
             # procedure X is abstract;
             if self.match("ABSTRACT"):
                  is_body = False
                  self.match("SEMI")
             else:
                  # raise SyntaxError(f"Expected IS or SEMI, found {self.current_token}")
                  # robustness
                  self.match("SEMI")

        return SubprogramNode(name=name, kind=kind, parameters=params, return_type=return_type, declarations=decls, statements=stmts, is_body=is_body)

    def parse_compound_name(self) -> str:
        name = self.expect("ID").value
        while self.match("DOT"):
            name += "." + self.expect("ID").value
        return name

    def parse_parameters(self) -> List[ParameterNode]:
        params = []
        while True:
            names = []
            names.append(self.expect("ID").value)
            while self.match("COMMA"):
                names.append(self.expect("ID").value)
            
            self.expect("COLON")
            
            mode = "in"
            if self.match("IN"):
                if self.match("OUT"):
                    mode = "in out"
            elif self.match("OUT"):
                 mode = "out"
                 
            type_name = self.parse_type_name()
            
            # Default values (assignment)
            if self.match("ASSIGN"):
                # Simplified: consume until semi or comma or rparen
                # But actually parameters are separated by semi-colon if they have distinct types?
                # ADA Syntax: (A, B : Integer; C : Float)
                # My logic above assumes comma sep for same type.
                # Let's handle generic expressions? For now just consume one token
                self.advance() 

            for n in names:
                params.append(ParameterNode(name=n, mode=mode, type_name=type_name))
            
            if self.peek() == "SEMI":
                self.advance()
            else:
                break
        return params

    def parse_type_name(self) -> str:
        # Simple type name parsing (e.g. Integer, Standard.Integer)
        return self.parse_compound_name()

    def parse_declarations(self) -> List[ASTNode]:
        decls = []
        while self.peek() not in ("BEGIN", "END", "EOF"):
            if self.peek() == "TYPE":
                decls.append(self.parse_type_decl())
            elif self.peek() == "SUBTYPE":
                # Treat as type for now
                self.advance()
                self.advance() # name
                self.expect("IS")
                # consume until semi
                while self.peek() != "SEMI":
                    self.advance()
                self.match("SEMI")
            elif self.peek() in ("PROCEDURE", "FUNCTION"):
                 # Parse subprogram (spec or body)
                 decls.append(self.parse_subprogram())

            elif self.peek() == "ID":
                # Variable declaration? "X : Integer := 1;"
                # Or "X, Y : Float;"
                decls.append(self.parse_variable_decl())
            elif self.peek() == "FOR":
                # Representation clause? "for Type use ..."
                # Skip until semi
                while self.peek() != "SEMI":
                    self.advance()
                self.match("SEMI")
            elif self.peek() == "PRAGMA":
                 while self.peek() != "SEMI":
                     self.advance()
                 self.match("SEMI")
            elif self.peek() == "USE":
                  self.parse_context_clause()
            elif self.peek() == "PACKAGE":
                 # Nested package
                 decls.append(self.parse_package())
            elif self.peek() in ("TASK", "PROTECTED"):
                # Skip complex types for now
                while self.peek() != "IS" and self.peek() != "SEMI":
                    self.advance()
                if self.match("IS"):
                     while self.peek() != "END":
                         self.advance()
                     self.match("END")
                     self.advance() # ID
                     self.match("SEMI")
                else:
                    self.match("SEMI")
            else:
                 # Unknown declaration, consume until semi to recover
                # print(f"Skipping unknown declaration starting with {self.current_token}")
                self.advance()
                while self.peek() != "SEMI" and self.peek() != "EOF":
                    self.advance()
                self.match("SEMI")
                
        return decls

    def parse_variable_decl(self) -> VariableDeclNode:
        names = []
        names.append(self.expect("ID").value)
        while self.match("COMMA"):
            names.append(self.expect("ID").value)
        
        self.expect("COLON")
        
        # Handle CONSTANT
        if self.match("CONSTANT"):
            pass
            
        type_name = "Unknown"
        # Could be "array (...) of ..." or just ID
        if self.peek() == "ARRAY":
            # consume array type def
            while self.peek() != "ASSIGN" and self.peek() != "SEMI":
                self.advance()
            type_name = "ARRAY"
        elif self.peek() == "ACCESS":
            self.advance()
            # access type
            if self.peek() == "ALL" or self.peek() == "CONSTANT":
                self.advance()
            type_name = "ACCESS " + self.parse_type_name()
        else:
            type_name = self.parse_type_name()
            
        initial_val = None
        if self.match("ASSIGN"):
            # consume expression until semi
            # Simplified: just grab string
            initial_val = ""
            while self.peek() != "SEMI":
                initial_val += self.current_token.value + " "
                self.advance()
                
        self.match("SEMI")
        return VariableDeclNode(names=names, type_name=type_name, initial_value=initial_val)

    def parse_type_decl(self) -> TypeDeclNode:
        self.expect("TYPE")
        name = self.expect("ID").value
        self.expect("IS")
        
        # definition
        # record, array, range, enum...
        # consume until semi or end record
        
        type_def = ""
        if self.match("RECORD"):
            # consume components
            while self.peek() != "END":
                self.advance() # component
            self.expect("END")
            self.match("RECORD")
            type_def = "RECORD"
        else:
            while self.peek() != "SEMI":
                type_def += self.current_token.value + " "
                self.advance()
                
        self.match("SEMI")
        return TypeDeclNode(name=name, type_def=type_def)

    def parse_statements(self) -> List[ASTNode]:
        stmts = []
        while self.peek() not in ("END", "EOF", "ELSIF", "ELSE", "WHEN", "EXCEPTION"):
            if self.peek() == "IF":
                stmts.append(self.parse_if())
            elif self.peek() in ("LOOP", "WHILE", "FOR"):
                stmts.append(self.parse_loop())
            elif self.peek() == "RETURN":
                self.advance()
                expr = ""
                if self.peek() != "SEMI":
                    # consume expr
                    while self.peek() != "SEMI":
                        expr += self.current_token.value + " "
                        self.advance()
                self.match("SEMI")
                stmts.append(ReturnNode(expression=expr))
            elif self.peek() == "ID":
                # Assignment or Call
                # Lookahead
                save_pos = self.pos
                line = self.current_token.line # Capture line
                name = self.parse_compound_name()
                
                if self.peek() == "ASSIGN":
                    # Assignment
                    self.advance()
                    expr = ""
                    while self.peek() != "SEMI":
                         expr += self.current_token.value + " "
                         self.advance()
                    self.match("SEMI")
                    stmts.append(AssignmentNode(target=name, expression=expr, line=line))
                    
                elif self.peek() in ("SEMI", "LPAREN"):
                     # Procedure Call
                     args = []
                     if self.match("LPAREN"):
                         # consume args
                         while self.peek() != "RPAREN":
                             self.advance() 
                         self.match("RPAREN")
                     
                     self.match("SEMI")
                     stmts.append(CallNode(name=name, arguments=args, line=line))
                else:
                    # Could be label? <<Label>>
                    # For now recover
                    self.pos = save_pos
                    self.advance() # consume ID
                    # consume until semi
                    while self.peek() != "SEMI":
                        self.advance()
                    self.match("SEMI")
            elif self.peek() in ("EXIT", "NULL", "PRAGMA", "DELAY", "RAISE"):
                # Simple statements
                 while self.peek() != "SEMI":
                     self.advance()
                 self.match("SEMI")
                 
            elif self.peek() == "CASE":
                 stmts.append(self.parse_case())
            elif self.peek() == "DECLARE":
                # Block
                self.advance()
                self.parse_declarations()
                self.expect("BEGIN")
                self.parse_statements()
                self.expect("END")
                self.match("SEMI")
            else:
                 # Recover
                 # print(f"Skipping unknown statement starting with {self.current_token}")
                 self.advance()
                 while self.peek() != "SEMI" and self.peek() != "EOF":
                     self.advance()
                 self.match("SEMI")

        return stmts

    def parse_if(self) -> IfNode:
        self.expect("IF")
        cond = ""
        while self.peek() != "THEN":
            cond += self.current_token.value + " "
            self.advance()
        self.expect("THEN")
        
        then_block = self.parse_statements()
        elsif_parts = []
        else_block = None
        
        while self.match("ELSIF"):
             e_cond = ""
             while self.peek() != "THEN":
                 e_cond += self.current_token.value + " "
                 self.advance()
             self.expect("THEN")
             e_stmts = self.parse_statements()
             elsif_parts.append(ElsifNode(condition=e_cond, statements=e_stmts))
             
        if self.match("ELSE"):
            else_block = self.parse_statements()
            
        self.expect("END")
        self.match("IF")
        self.match("SEMI")
        
        return IfNode(condition=cond, then_block=then_block, elsif_parts=elsif_parts, else_block=else_block)

    def parse_loop(self) -> LoopNode:
        name = None
        # Check for loop name: Label: loop ...
        # (Parser logic for labels is tricky, simplified here)
        
        iteration = None
        if self.match("WHILE"):
            iteration = "WHILE "
            while self.peek() != "LOOP":
                iteration += self.current_token.value + " "
                self.advance()
        elif self.match("FOR"):
             iteration = "FOR "
             while self.peek() != "LOOP":
                 iteration += self.current_token.value + " "
                 self.advance()
                 
        self.expect("LOOP")
        stmts = self.parse_statements()
        self.expect("END")
        self.match("LOOP")
        if self.peek() == "ID":
            self.advance() # consume loop name
        self.match("SEMI")
        
        return LoopNode(name=name, iteration_scheme=iteration, statements=stmts)

    def parse_case(self) -> CaseNode:
        self.expect("CASE")
        # Consume expression until IS
        expression = ""
        while self.peek() != "IS":
             expression += self.current_token.value + " "
             self.advance()
        self.expect("IS")
        
        when_parts = []
        while self.peek() != "END":
            if self.match("WHEN"):
                choices = ""
                while self.peek() != "ARROW":
                    choices += self.current_token.value + " "
                    self.advance()
                self.match("ARROW")
                statements = self.parse_statements()
                when_parts.append(WhenNode(choices=choices, statements=statements))
            else:
                # Should not happen in valid ADA, check for END
                if self.peek() == "END":
                    break
                else:
                    # Skip to next WHEN or END to recover
                    self.advance()

        self.expect("END")
        self.match("CASE")
        self.match("SEMI")
        
        return CaseNode(expression=expression, when_parts=when_parts)
