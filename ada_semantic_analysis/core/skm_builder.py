from .ast_nodes import *
from .skm import SystemKnowledgeModel, VariableInfo, ProcedureInfo

class SKMBuilder:
    def __init__(self, skm: SystemKnowledgeModel):
        self.skm = skm
        self.current_scope = [] # stack of scope names
        self.current_proc: Optional[ProcedureInfo] = None

    def build(self, unit: CompilationUnitNode):
        for file_node in unit.files:
            self.visit(file_node)

    def visit(self, node: ASTNode):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        # Default: visit all children that are ASTNodes or lists of ASTNodes
        for field, value in node.__dict__.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ASTNode):
                        self.visit(item)
            elif isinstance(value, ASTNode):
                self.visit(value)

    def get_scope_name(self):
        return ".".join(self.current_scope) if self.current_scope else ""

    def visit_PackageNode(self, node: PackageNode):
        self.current_scope.append(node.name)
        for decl in node.declarations:
            self.visit(decl)
        if node.body:
            for stmt in node.body:
                self.visit(stmt)
        self.current_scope.pop()

    def visit_SubprogramNode(self, node: SubprogramNode):
        scope = self.get_scope_name()
        full_name = f"{scope}.{node.name}" if scope else node.name
        
        # Create ProcedureInfo
        # Compute Structural Body Hash
        # (Naive serialization of statements for logic comparison)
        # INCLUDE DECLARATIONS IN HASH
        body_str = str([str(d) for d in node.declarations]) + str([str(s) for s in node.statements]) 
        import hashlib
        body_hash = hashlib.md5(body_str.encode()).hexdigest()

        proc_info = ProcedureInfo(
            name=full_name,
            signature=f"{node.kind} {node.name}",
            start_line=0, # AST doesn't have line nums yet everywhere, placeholder
            end_line=0,
            inputs=[p.name for p in node.parameters if "in" in p.mode],
            outputs=[p.name for p in node.parameters if "out" in p.mode],
            body_hash=body_hash
        )
        self.skm.add_procedure(proc_info)
        
        parent_proc = self.current_proc
        self.current_proc = proc_info
        self.current_scope.append(node.name)

        # Process params as variables
        for param in node.parameters:
            var_info = VariableInfo(
                name=param.name,
                type_name=param.type_name,
                scope=full_name,
                kind="parameter",
                defined_at_line=0
            )
            self.skm.add_variable(var_info)

        # Declarations
        for decl in node.declarations:
            self.visit(decl)

        # Body statements
        for stmt in node.statements:
            self.visit(stmt)

        self.current_scope.pop()
        self.current_proc = parent_proc

    def visit_VariableDeclNode(self, node: VariableDeclNode):
        scope = self.get_scope_name()
        for name in node.names:
            var_info = VariableInfo(
                name=name,
                type_name=node.type_name,
                scope=scope,
                kind="variable",
                defined_at_line=0
            )
            self.skm.add_variable(var_info)

    def visit_AssignmentNode(self, node: AssignmentNode):
        if self.current_proc:
            # Simple heuristic: identifying variable writes
            # Need to resolve scope? For now just store the name
            # Ideally we resolve "X" to "Global.Package.X"
            self.current_proc.written_vars.add(node.target)
            
            # Reads in expression?
            # Basic analysis: finding tokens in expression that match var names
            # self.find_reads_in_expr(node.expression)
            pass

    def visit_CallNode(self, node: CallNode):
        if not self.current_proc:
            return

        caller = self.current_proc.name
        # Simple name resolution: Check aliases, check current package
        callee = node.name
        
        # Try to resolve based on USE clauses? 
        # For now, just store as is.
        self.skm.add_call(caller, callee, line=node.line)
    
    def visit_IfNode(self, node: IfNode):
        if self.current_proc:
            self.current_proc.cyclomatic_complexity += 1
            # Check condition for reads
            
        self.generic_visit(node) # visit blocks

    def visit_LoopNode(self, node: LoopNode):
        if self.current_proc:
            self.current_proc.cyclomatic_complexity += 1
        self.generic_visit(node)
