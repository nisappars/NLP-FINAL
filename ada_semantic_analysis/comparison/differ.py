from typing import Dict, List, Tuple
from ..core.skm import SystemKnowledgeModel
from ..core.fingerprinting import FingerprintGenerator, BehavioralFingerprint

class Change:
    def __init__(self, file_name: str, line_range: str, classification: str, affected_files: str, risk: str, tests: str):
        self.file_name = file_name
        self.line_range = line_range
        self.classification = classification
        self.affected_files = affected_files # Multiline string "File:Line\nFile:Line"
        self.risk = risk
        self.tests = tests

class SemanticDiffer:
    def __init__(self, skm_old: SystemKnowledgeModel, skm_new: SystemKnowledgeModel):
        self.skm_old = skm_old
        self.skm_new = skm_new
        self.changes: List[Change] = []
    
    def diff(self) -> List[Change]:
        self.changes = []
        self._diff_procedures()
        return self.changes

    def _diff_procedures(self):
        old_procs = self.skm_old.procedures
        new_procs = self.skm_new.procedures
        
        old_names = set(old_procs.keys())
        new_names = set(new_procs.keys())
        
        added = new_names - old_names
        removed = old_names - new_names
        common = old_names & new_names
        
        # Helper to find callers (Impact Propagation)
        def get_affected(target_name, graph):
            affected_set = set()
            
            # 1. Check Full Name
            if graph.has_node(target_name):
                affected_set.update(graph.predecessors(target_name))
            
            # 2. Check Simple Name (Robustness for unqualified calls)
            simple = target_name.split('.')[-1]
            if graph.has_node(simple):
                affected_set.update(graph.predecessors(simple))
                
            if not affected_set:
                return "None Detected"
                
            callers = []
            for p in sorted(affected_set):
                 # Try to get edge lines from full name link if possible
                 edge_data = graph.get_edge_data(p, target_name)
                 lines = edge_data.get('lines', []) if edge_data else []
                 if not lines and simple != target_name:
                     edge_data = graph.get_edge_data(p, simple)
                     lines = edge_data.get('lines', []) if edge_data else []

                 if lines:
                     line_str = ", ".join(map(str, lines))
                     callers.append(f"{p}:{line_str}")
                 else:
                     proc = self.skm_new.procedures.get(p)
                     if not proc and self.skm_old: proc = self.skm_old.procedures.get(p)
                     line = proc.start_line if proc else "?"
                     callers.append(f"{p}:Start-{line}")

            return "\n".join(callers)

        # --- RENAME DETECTION ---
        # Heuristic: If A is removed and B is added, and they have high similarity, assume Rename.
        renamed_map = {} # Removed Name -> New Name
        processed_added = set()
        
        for r_name in list(removed):
            best_match = None
            
            p_old = old_procs[r_name]
            fp_old = BehavioralFingerprint(p_old).fingerprint
            
            for a_name in list(added):
                if a_name in processed_added: continue
                
                p_new = new_procs[a_name]
                fp_new = BehavioralFingerprint(p_new).fingerprint
                
                # Criteria 1: Exact structural hash match (Identity Rename)
                if fp_old == fp_new:
                    best_match = a_name
                    break
                
                # Criteria 2: Signature + Logic Match (Close enough)
                # Same inputs/outputs and slightly different internal complexity/calls?
                if fp_old['inputs'] == fp_new['inputs'] and fp_old['outputs'] == fp_new['outputs']:
                    # Weak signal, check complexity
                    if abs(fp_old['complexity'] - fp_new['complexity']) <= 1:
                        best_match = a_name
                        break
            
            if best_match:
                renamed_map[r_name] = best_match
                processed_added.add(best_match)
                added.remove(best_match)
                removed.remove(r_name)
                
                # Log Rename
                affected = get_affected(best_match, self.skm_new.call_graph)
                self.changes.append(Change(
                    file_name=best_match.split('.')[0] + ".adb",
                    line_range=f"{new_procs[best_match].start_line}-{new_procs[best_match].end_line}",
                    classification=f"Renamed Procedure ({r_name} -> {best_match})",
                    affected_files=affected,
                    risk="Low", 
                    tests=f"Unit: {best_match}; Regress: {r_name} Callers"
                ))

        # --- STANDARD ADD/REMOVE ---
        for name in added:
            proc = new_procs[name]
            affected = get_affected(name, self.skm_new.call_graph)
            
            self.changes.append(Change(
                file_name=name.split('.')[0] + ".adb", 
                line_range=f"{proc.start_line}-{proc.end_line}",
                classification="Code Inserted (New Procedure)",
                affected_files=affected,
                risk="Low",
                tests=f"Unit Test: {name}"
            ))
            
        for name in removed:
             # Can't get line range from new, assume deleted.
             self.changes.append(Change(
                file_name=name.split('.')[0] + ".adb",
                line_range="Deleted",
                classification="Variable/Code Removal",
                affected_files=get_affected(name, self.skm_old.call_graph), # Check who called it in old
                risk="High",
                tests="Regression: Check callers"
            ))
            
        # --- MODIFICATION ---
        for name in common:
            pf_old = BehavioralFingerprint(old_procs[name])
            pf_new = BehavioralFingerprint(new_procs[name])
            
            if pf_old.hash != pf_new.hash:
                details, risk = self._analyze_modification(pf_old.fingerprint, pf_new.fingerprint, name)
                
                # Impact Analysis
                affected = get_affected(name, self.skm_new.call_graph)
                
                # Test Recommendation
                tests = f"Verify {name}"
                if risk == "High":
                    tests += "; Full Regression"
                
                self.changes.append(Change(
                    file_name=name.split('.')[0] + ".adb",
                    line_range=f"{new_procs[name].start_line}-{new_procs[name].end_line}",
                    classification=f"Logic Modified: {details}",
                    affected_files=affected,
                    risk=risk,
                    tests=tests
                ))

    def _analyze_modification(self, old_fp: dict, new_fp: dict, name: str) -> Tuple[str, str]:
        reasons = []
        risk = "Low"
        triggered_rules = []
        
        # Manifest Rule: Conservative Safety Check
        is_safety_critical = "safety" in name.lower() or "handler" in name.lower()
        
        # Rule 1: Interface Change (High Risk)
        if old_fp["inputs"] != new_fp["inputs"]:
            reasons.append(f"Inputs changed: {old_fp['inputs']} -> {new_fp['inputs']}")
            risk = "High" 
            triggered_rules.append("RULE-1 (Interface Change)")
            
        if old_fp["outputs"] != new_fp["outputs"]:
            reasons.append(f"Outputs changed: {old_fp['outputs']} -> {new_fp['outputs']}")
            risk = "High"
            triggered_rules.append("RULE-1 (Interface Change)")

        # Rule 2: Side Effects (Medium/High)
        diff_writes = set(new_fp["writes"]) ^ set(old_fp["writes"])
        if diff_writes:
             reasons.append(f"Write side-effects changed: {diff_writes}")
             if risk == "Low": risk = "High" # Conservative: Global state change is risky
             triggered_rules.append("RULE-2 (Side Effect Change)")

        # Rule 3: Logic/Complexity (Medium)
        if old_fp["complexity"] != new_fp["complexity"]:
            reasons.append(f"Complexity changed: {old_fp['complexity']} -> {new_fp['complexity']}")
            if risk == "Low": risk = "Medium"
            triggered_rules.append("RULE-3 (Logic Modification)")

        # Rule 4: Dependency Change (Medium)
        added_calls = set(new_fp["calls"]) - set(old_fp["calls"])
        removed_calls = set(old_fp["calls"]) - set(new_fp["calls"])
        
        # Check for Safety Path Removal in removed_calls
        safety_removed = [c for c in removed_calls if "safety" in c.lower() or "handler" in c.lower()]
        if safety_removed:
            reasons.append(f"Safety Critical Calls Removed: {safety_removed}")
            risk = "High"
            triggered_rules.append("RULE-0 (Safety Path Removal)")
        
        if added_calls or removed_calls:
            reasons.append(f"Call graph changed (+{len(added_calls)}/-{len(removed_calls)})")
            if risk == "Low": risk = "Medium"
            triggered_rules.append("RULE-4 (Dependency Change)")

        if not reasons:
            reasons.append("Internal logic modified (structure change).")
            if risk == "Low": risk = "Medium"
            triggered_rules.append("RULE-3 (Logic Modification)")

        # Safety Logic Override
        # Rule Definition: "Safety Rule - Critical Logic Modification"
        # Configurable: Matches procedures with 'safety' or 'handler' in name.
        if is_safety_critical and risk != "High":
             risk = "High"
             triggered_rules.append("RULE-0 (Safety Critical Logic Modified)")

        return "; ".join(reasons) + f" [{', '.join(triggered_rules)}]", risk
