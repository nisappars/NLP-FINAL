from typing import List, Dict, Set
from ..core.skm import SystemKnowledgeModel, ProcedureInfo

class InvariantViolation:
    def __init__(self, rule_id: str, description: str, severity: str, location: str):
        self.rule_id = rule_id
        self.description = description
        self.severity = severity
        self.location = location

class LegacyInvariantChecker:
    def __init__(self, skm_old: SystemKnowledgeModel, skm_new: SystemKnowledgeModel):
        self.skm_old = skm_old
        self.skm_new = skm_new
        self.violations: List[InvariantViolation] = []

    def check(self) -> List[InvariantViolation]:
        self.violations = []
        self._check_safety_handler_calls()
        self._check_protected_writes()
        return self.violations

    def _check_safety_handler_calls(self):
        """
        Invariant 1: Critical Call Preservation.
        If a procedure in Old called a known Safety/Handler procedure,
        it must still call a Safety/Handler procedure in New (unless the caller itself is gone).
        """
        # Heuristic: Identify "Safety/Handler" procedures by name in Old
        safety_targets_old = {
            name for name in self.skm_old.procedures 
            if "safety" in name.lower() or "handler" in name.lower() or "critical" in name.lower()
        }

        if not safety_targets_old:
            return

        for caller_name, old_proc in self.skm_old.procedures.items():
            # If this caller no longer exists, that's a different problem (Removal) - handled by Differ
            if caller_name not in self.skm_new.procedures:
                continue
            
            new_proc = self.skm_new.procedures[caller_name]
            
            # Check if it *used to* call a safety target
            # Note: proc.calls contains unqualified names (e.g. "Safety_Check"), 
            # while safety_targets_old contains fully qualified names (e.g. "Main.Safety_Check").
            called_safety_old = set()
            for call in old_proc.calls:
                # Naive matching: check if call matches the suffix of any safety target
                for target in safety_targets_old:
                    if target.endswith(f".{call}") or target == call:
                        called_safety_old.add(call) # Store the name as it appears in 'calls'
            
            if called_safety_old:
                # It did call safety stuff. Does it still?
                # We need to find "Safety/Handler" procedures in New
                safety_targets_new = {
                    name for name in self.skm_new.procedures 
                    if "safety" in name.lower() or "handler" in name.lower() or "critical" in name.lower()
                }
                
                called_safety_new = set()
                for call in new_proc.calls:
                    for target in safety_targets_new:
                        if target.endswith(f".{call}") or target == call:
                            called_safety_new.add(call)
                
                if not called_safety_new:
                    self.violations.append(InvariantViolation(
                        rule_id="INV-01",
                        description=f"Procedure '{caller_name}' stopped calling required Safety/Handler procedures. Previously called: {', '.join(called_safety_old)}",
                        severity="High",
                        location=caller_name
                    ))

    def _check_protected_writes(self):
        """
        Invariant 2: Protected Write Access.
        Writes to global variables that were previously "Protected" (or just critical globals) 
        should arguably remain consistent or guarded.
        
        Simplified Check: If a variable was written by X, Y, Z in Old, 
        and in New it is written by A (where A is not in X,Y,Z), flagging it as potential invariant risk 
        if A is not a 'trusted' scope.
        """
        # For this prototype, let's just flag if a "Critical" variable has a NEW writer
        # that didn't exist before.
        
        for var_name, var_info in self.skm_old.variables.items():
            if "critical" in var_name.lower() or "state" in var_name.lower():
                # Find writers in Old
                writers_old = set()
                for p_name, p_val in self.skm_old.procedures.items():
                    if var_name in p_val.written_vars:
                        writers_old.add(p_name)
                
                # If variable still exists in New
                if var_name in self.skm_new.variables:
                     # Find writers in New
                    writers_new = set()
                    for p_name, p_val in self.skm_new.procedures.items():
                        if var_name in p_val.written_vars:
                            writers_new.add(p_name)
                    
                    new_writers = writers_new - writers_old
                    # If there's a new writer that isn't just a rename (hard to tell), flag it
                    if new_writers:
                         self.violations.append(InvariantViolation(
                            rule_id="INV-02",
                            description=f"Critical variable '{var_name}' has new writer(s): {', '.join(new_writers)}",
                            severity="Medium",
                            location=var_name
                        ))
