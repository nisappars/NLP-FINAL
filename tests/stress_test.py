import os
import sys
import time
import shutil
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ada_semantic_analysis.core.lexer import AdaLexer
from ada_semantic_analysis.core.parser import AdaParser
from ada_semantic_analysis.core.skm import SystemKnowledgeModel
from ada_semantic_analysis.core.skm_builder import SKMBuilder
from ada_semantic_analysis.comparison.differ import SemanticDiffer

class AdaCodeGenerator:
    def __init__(self):
        self.systems = ["Engine", "Brake", "Fuel", "Navigation", "Climate", "Suspension", "Transmission", "Battery"]
        self.states = ["Idle", "Active", "Error", "Maintenance", "Startup", "Shutdown"]
        
    def generate_header(self, name):
        return [
            f"-- Industrial Embedded System Module: {name}",
            f"-- Generated for Stress Testing",
            f"with Ada.Text_IO;",
            f"use Ada.Text_IO;",
            ""
        ]

    def generate_specs(self):
        lines = []
        lines.append("    type System_State is (Idle, Active, Error, Maintenance, Startup, Shutdown);")
        lines.append("    type Sensor_Value is new Float range 0.0 .. 1000.0;")
        lines.append("    ")
        lines.append("    type Control_Record is record")
        lines.append("        State       : System_State := Idle;")
        lines.append("        Pressure    : Sensor_Value := 0.0;")
        lines.append("        Temperature : Sensor_Value := 25.0;")
        lines.append("        Is_Valid    : Boolean := False;")
        lines.append("        ErrorCode   : Integer := 0;")
        lines.append("    end record;")
        lines.append("    ")
        lines.append("    Current_Control : Control_Record;")
        lines.append("    Safety_Threshold : constant Sensor_Value := 850.0;")
        return lines

    def generate_subprogram(self, name, level=1):
        indent = "    " * level
        lines = []
        lines.append(f"{indent}procedure {name} (Input : in Integer) is")
        lines.append(f"{indent}    Local_Var : Integer := Input;")
        lines.append(f"{indent}begin")
        # Logic body
        lines.append(f"{indent}    if Local_Var > 100 then")
        lines.append(f"{indent}        Current_Control.State := Active;")
        lines.append(f"{indent}        Current_Control.Pressure := 500.0;")
        lines.append(f"{indent}    elsif Local_Var < 0 then")
        lines.append(f"{indent}        Current_Control.State := Error;")
        lines.append(f"{indent}        Current_Control.ErrorCode := -1;")
        lines.append(f"{indent}    else")
        lines.append(f"{indent}        Current_Control.State := Idle;")
        lines.append(f"{indent}    end if;")
        lines.append(f"{indent}end {name};")
        return lines

    def generate_state_machine(self, level=1):
        indent = "    " * level
        lines = []
        lines.append(f"{indent}    case Current_Control.State is")
        for state in self.states:
            lines.append(f"{indent}        when {state} =>")
            lines.append(f"{indent}            if Current_Control.Pressure > Safety_Threshold then")
            lines.append(f"{indent}                Current_Control.State := Error;")
            lines.append(f"{indent}                Current_Control.ErrorCode := 999;")
            lines.append(f"{indent}            else")
            lines.append(f"{indent}                Current_Control.Temperature := Current_Control.Temperature + 0.1;")
            lines.append(f"{indent}            end if;")
        lines.append(f"{indent}    end case;")
        return lines

    def generate_file(self, filename, line_target=500):
        base_name = os.path.splitext(os.path.basename(filename))[0]
        lines = self.generate_header(base_name)
        lines.append(f"procedure {base_name} is")
        lines.extend(self.generate_specs())
        
        # Add a subprogram
        lines.extend(self.generate_subprogram("Update_Diagnostics", level=1))
        
        lines.append("begin")
        lines.append("    -- Main Control Loop")
        lines.append("    loop")
        
        # Generate body content to reach target lines
        # We will repeat state machine logic and sensor updates
        
        count = 0 
        while len(lines) < line_target:
           lines.extend(self.generate_state_machine(level=2))
           lines.append("        Update_Diagnostics(count);")
           lines.append("        if count > 1000 then exit; end if;")
           lines.append("        count := count + 1;")
           
        lines.append("    end loop;")
        lines.append(f"end {base_name};")
        return lines

def modify_content_for_v2(lines, file_index):
    new_lines = lines[:]
    change_type = "None"
    
    # Deterministic injection based on index to ensure coverage of all types
    mode = file_index % 4
    
    # Mode 0: RENAME (Variable/Procedure Rename)
    # Simulate: "the variable name maybe changed"
    if mode == 0:
        # Rename 'Update_Diagnostics' to 'Monitor_Health'
        for i in range(len(new_lines)):
            if "procedure Update_Diagnostics" in new_lines[i] or "Update_Diagnostics(" in new_lines[i] or "end Update_Diagnostics" in new_lines[i]:
                new_lines[i] = new_lines[i].replace("Update_Diagnostics", "Monitor_Health")
        change_type = "Renamed"

    # Mode 1: NEW LOGIC (New Lines Added)
    # Simulate: "coder may added a new lines of code"
    elif mode == 1:
        # Insert a new check in the loop
        for i in range(len(new_lines)):
             if "loop" in new_lines[i]:
                 new_lines.insert(i+1, "        -- [NEW] Added Pre-Check Logic")
                 new_lines.insert(i+2, "        if Current_Control.Temperature > 900.0 then exit; end if;")
                 break
        change_type = "Logic Modified"

    # Mode 2: DEPENDENCY DELETION (Forgot to address past code/lines)
    # Simulate: "forget to address the past code lines... dont have a variable thats in the before"
    # We remove the call to Update_Diagnostics, breaking the data flow/dependency.
    elif mode == 2:
        for i in range(len(new_lines)):
            if "Update_Diagnostics(count);" in new_lines[i]:
                new_lines[i] = "-- Update_Diagnostics(count); -- DELETED CALL"
        change_type = "Dependency Change"

    # Mode 3: LOGIC INVERSION (The Low Level Issue from before)
    elif mode == 3:
        for i in range(len(new_lines)):
            if "Pressure > Safety_Threshold" in new_lines[i]:
                 new_lines[i] = new_lines[i].replace(">", "<")
                 break
        change_type = "Logic Modified"

    return new_lines, change_type

def parse_dir(path, name):
    skm = SystemKnowledgeModel(name)
    builder = SKMBuilder(skm)
    file_count = 0
    start_time = time.time()
    
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.adb'):
                file_count += 1
                with open(os.path.join(root, f), 'r') as fh:
                    code = fh.read()
                try:
                    lexer = AdaLexer(code)
                    parser = AdaParser(lexer)
                    unit = parser.parse_compilation_unit()
                    builder.build(unit)
                except Exception as e:
                    print(f"Error parsing {f}: {e}")
                
    end_time = time.time()
    duration = end_time - start_time
    print(f"[{name}] Parsed {file_count} files in {duration:.4f} seconds.")
    return skm

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    v1_dir = os.path.join(root_dir, "stress_v1")
    v2_dir = os.path.join(root_dir, "stress_v2")
    
    # Clean up previous runs
    print("Cleaning up old test data...")
    if os.path.exists(v1_dir): shutil.rmtree(v1_dir)
    if os.path.exists(v2_dir): shutil.rmtree(v2_dir)
    
    os.makedirs(v1_dir)
    os.makedirs(v2_dir)
    
    files_to_generate = 100
    lines_per_file = 500
    
    print(f"Generating {files_to_generate} files with ~{lines_per_file} lines of Realistic Ada Code...")
    gen_start = time.time()
    
    generator = AdaCodeGenerator()
    ground_truth = {}
    
    for i in range(files_to_generate):
        fname = f"System_Module_{i:03d}.adb"
        
        # Generate base content
        lines_v1 = generator.generate_file(fname, lines_per_file)
        
        # Write V1
        with open(os.path.join(v1_dir, fname), 'w') as f:
            f.write("\n".join(lines_v1))
            
        # Create V2 content with Specific Semantic Changes
        lines_v2, type_label = modify_content_for_v2(lines_v1, i)
        ground_truth[fname] = type_label
        
        # Write V2
        with open(os.path.join(v2_dir, fname), 'w') as f:
            f.write("\n".join(lines_v2))
            
    print(f"Generation complete in {time.time() - gen_start:.4f} seconds.\n")
    
    # Run Analysis
    print("--- STARTING ANALYSIS ---")
    
    # Measure V1 parsing
    skm1 = parse_dir(v1_dir, "V1")
    
    # Measure V2 parsing
    skm2 = parse_dir(v2_dir, "V2")
    
    # Measure Diffing
    print("Running Differ...")
    diff_start = time.time()
    differ = SemanticDiffer(skm1, skm2)
    changes = differ.diff()
    diff_end = time.time()
    
    print(f"Differ finished in {diff_end - diff_start:.4f} seconds.")
    print(f"Total Changes Detected: {len(changes)}")
    
    # --- SEMANTIC VERIFICATION ---
    print("\n--- SEMANTIC AWARENESS VERIFICATION ---")
    
    # Group changes by file
    from collections import defaultdict
    file_changes = defaultdict(list)
    for c in changes:
        file_changes[c.file_name].append(c.classification)
        
    correct_files = 0
    total_files_checked = 0
    
    for fname, expected in ground_truth.items():
        if fname not in file_changes:
            print(f"MISSING: {fname} (Expected {expected})")
            continue
            
        detected_classes = file_changes[fname]
        total_files_checked += 1
        is_correct = False
        
        # Check if ANY of the detected classifications match expectations
        if expected == "Renamed":
            # Expect at least one Rename detection
            if any("Renamed" in c or "Interface" in c for c in detected_classes):
                is_correct = True
        elif expected == "Logic Modified":
            if any("Logic Modified" in c or "RULE-3" in c or "RULE-0" in c or "RULE-2" in c for c in detected_classes):
                is_correct = True
        elif expected == "Dependency Change":
            if any("Dependency Change" in c or "calls changed" in c or "Safety Path Removal" in c or "Variable/Code Removal" in c for c in detected_classes):
                 is_correct = True
        
        if is_correct:
            correct_files += 1
        else:
             print(f"MISCLASSIFICATION: {fname} | Expected: {expected} | Got: {detected_classes}")

    print(f"\nSemantic Accuracy: {correct_files}/{total_files_checked} ({(correct_files/total_files_checked)*100:.2f}%)")
    
    print("Test Complete. Files generated in stress_v1 and stress_v2 folders.")

if __name__ == "__main__":
    main()
