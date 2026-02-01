from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
import networkx as nx

@dataclass
class VariableInfo:
    name: str
    type_name: str
    scope: str # full path e.g. "Main.Procedure1"
    kind: str # "variable", "parameter", "constant"
    defined_at_line: int

@dataclass
class ProcedureInfo:
    name: str # full qualified name
    signature: str 
    start_line: int
    end_line: int
    inputs: List[str] # parameter names
    outputs: List[str] # out parameter names
    read_vars: Set[str] = field(default_factory=set) # full names of global/outer vars read
    written_vars: Set[str] = field(default_factory=set) # full names of global/outer vars written
    calls: Set[str] = field(default_factory=set) # names of procedures called
    call_locations: Dict[str, List[int]] = field(default_factory=dict) # K: Callee, V: List[Lines]
    cyclomatic_complexity: int = 1
    body_hash: str = ""

class SystemKnowledgeModel:
    def __init__(self, name: str):
        self.name = name
        self.variables: Dict[str, VariableInfo] = {} # Keyed by full qualified name
        self.procedures: Dict[str, ProcedureInfo] = {} # Keyed by full qualified name
        self.call_graph = nx.DiGraph()
        self.data_dependency_graph = nx.DiGraph()

    def add_variable(self, var: VariableInfo):
        self.variables[f"{var.scope}.{var.name}"] = var

    def add_procedure(self, proc: ProcedureInfo):
        if proc.name in self.procedures:
            # Merge existing
            existing = self.procedures[proc.name]
            existing.read_vars.update(proc.read_vars)
            existing.written_vars.update(proc.written_vars)
            existing.calls.update(proc.calls)
            
            # Merge Call Locations
            for callee, lines in proc.call_locations.items():
                if callee not in existing.call_locations:
                    existing.call_locations[callee] = []
                existing.call_locations[callee].extend(lines)

            # Complexity: max?
            existing.cyclomatic_complexity = max(existing.cyclomatic_complexity, proc.cyclomatic_complexity)
        else:
            self.procedures[proc.name] = proc
            self.call_graph.add_node(proc.name, type="procedure")

    def add_call(self, caller: str, callee: str, line: int = 0):
        if caller in self.procedures: # Callee might not be parsed yet
             proc = self.procedures[caller]
             proc.calls.add(callee)
             if callee not in proc.call_locations:
                 proc.call_locations[callee] = []
             proc.call_locations[callee].append(line)
             
             self.call_graph.add_edge(caller, callee, lines=proc.call_locations[callee])

    def finalize_dependencies(self):
        """Builds data dependency graph based on reads/writes."""
        # For every procedure, if it writes to V, and another reads V, edge?
        # Or simplistic: Node=Proc, Node=Var.
        for proc_name, proc in self.procedures.items():
            self.data_dependency_graph.add_node(proc_name, type="procedure")
            for var in proc.read_vars:
                self.data_dependency_graph.add_node(var, type="variable")
                self.data_dependency_graph.add_edge(var, proc_name, relationship="read")
            for var in proc.written_vars:
                self.data_dependency_graph.add_node(var, type="variable")
                self.data_dependency_graph.add_edge(proc_name, var, relationship="write")
