from .skm import SystemKnowledgeModel, ProcedureInfo
import hashlib
import json

class BehavioralFingerprint:
    def __init__(self, proc_info: ProcedureInfo):
        self.proc_info = proc_info
        self.fingerprint = self._generate()

    def _generate(self) -> dict:
        """
        Generates a deterministic dictionary representing the behavior.
        
        NOTE: This fingerprint represents structural behavior equivalence 
        (inputs, outputs, calls, control-flow), not functional correctness 
        or runtime equivalence.
        """
        return {
            "name": self.proc_info.name,
            "signature": self.proc_info.signature,
            "inputs": sorted(self.proc_info.inputs),
            "outputs": sorted(self.proc_info.outputs),
            "reads": sorted(list(self.proc_info.read_vars)),
            "writes": sorted(list(self.proc_info.written_vars)),
            "calls": sorted(list(self.proc_info.calls)),
            "complexity": self.proc_info.cyclomatic_complexity,
            "logic_hash": self.proc_info.body_hash
        }

    @property
    def hash(self) -> str:
        """Returns a SHA256 hash of the fingerprint."""
        data = json.dumps(self.fingerprint, sort_keys=True)
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

class FingerprintGenerator:
    def __init__(self, skm: SystemKnowledgeModel):
        self.skm = skm

    def generate_all(self) -> dict:
        """
        Returns a dictionary mapping procedure names to their behavioral hash.
        """
        results = {}
        for name, proc in self.skm.procedures.items():
            bf = BehavioralFingerprint(proc)
            results[name] = {
                "hash": bf.hash,
                "details": bf.fingerprint
            }
        return results
