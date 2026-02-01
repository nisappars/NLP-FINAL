import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import json
from ..core.lexer import AdaLexer
from ..core.parser import AdaParser
from ..core.skm import SystemKnowledgeModel
from ..core.skm_builder import SKMBuilder
from ..comparison.differ import SemanticDiffer
from ..comparison.invariant_checker import LegacyInvariantChecker
from ..reporting.pdf_generator import PDFReportGenerator

class AdaAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ada TF-IDF Change + Impact Analyzer (Categorical + PDF)") # Matching image title
        self.root.geometry("1100x800")
        
        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variables
        self.input_mode = tk.StringVar(value="Folders")
        self.path_old = tk.StringVar()
        self.path_new = tk.StringVar()
        self.changed_file_filter = tk.StringVar()
        self.status = tk.StringVar(value="Ready")
        
        self.changes = []
        self.invariant_violations = []
        self.metrics = {}
        self.scope_data = []
        
        self._build_ui()
        
    def _build_ui(self):
        main_pad = 5
        
        # --- Top Control Bar ---
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=main_pad, pady=main_pad)
        
        ttk.Label(self.top_frame, text="Input Mode:").pack(side=tk.LEFT)
        ttk.Radiobutton(self.top_frame, text="Folders", variable=self.input_mode, value="Folders", command=self._toggle_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.top_frame, text="Paste", variable=self.input_mode, value="Paste", command=self._toggle_mode).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.top_frame, text="Context lines:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Spinbox(self.top_frame, from_=0, to=10, width=3).pack(side=tk.LEFT)
        
        ttk.Checkbutton(self.top_frame, text="Mask strings").pack(side=tk.LEFT, padx=10)
        
        # --- Folder Mode Frame ---
        self.frame_folders = ttk.LabelFrame(self.root, text="Folder Mode")
        # Managed by toggle_mode
        
        # Old Folder
        f1 = ttk.Frame(self.frame_folders)
        f1.pack(fill=tk.X, pady=2)
        ttk.Label(f1, text="Old folder:", width=15, anchor="w").pack(side=tk.LEFT)
        ttk.Entry(f1, textvariable=self.path_old).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(f1, text="Browse...", command=lambda: self._browse(self.path_old)).pack(side=tk.LEFT)
        
        # New Folder
        f2 = ttk.Frame(self.frame_folders)
        f2.pack(fill=tk.X, pady=2)
        ttk.Label(f2, text="New folder:", width=15, anchor="w").pack(side=tk.LEFT)
        ttk.Entry(f2, textvariable=self.path_new).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(f2, text="Browse...", command=lambda: self._browse(self.path_new)).pack(side=tk.LEFT)
        
        # Changed File Filter
        f3 = ttk.Frame(self.frame_folders)
        f3.pack(fill=tk.X, pady=2)
        ttk.Label(f3, text="Changed file (relative path):", width=25, anchor="w").pack(side=tk.LEFT)
        ttk.Entry(f3, textvariable=self.changed_file_filter).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(f3, text="Ex: src/calc_engine.adb", foreground="gray").pack(side=tk.LEFT, padx=5)

        # --- Paste Mode Frame (Visual only for now) ---
        self.frame_paste = ttk.LabelFrame(self.root, text="Paste Mode")
        # Managed by toggle_mode
        
        pf = ttk.Frame(self.frame_paste)
        pf.pack(fill=tk.BOTH, expand=True)
        
        p1 = ttk.Frame(pf)
        p1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        ttk.Label(p1, text="Old content:").pack(anchor="w")
        self.txt_paste_old = tk.Text(p1, height=10)
        self.txt_paste_old.pack(fill=tk.BOTH, expand=True)
        
        p2 = ttk.Frame(pf)
        p2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        ttk.Label(p2, text="New content:").pack(anchor="w")
        self.txt_paste_new = tk.Text(p2, height=10)
        self.txt_paste_new.pack(fill=tk.BOTH, expand=True)

        # --- Buttons ---
        self.btn_frame = ttk.Frame(self.root)
        self.btn_frame.pack(fill=tk.X, padx=main_pad, pady=10)
        
        ttk.Button(self.btn_frame, text="Analyze File (Categorize)", command=self._start_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.btn_frame, text="Impact on Other Files (Categorize)", command=self._start_analysis).pack(side=tk.LEFT, padx=5)
        self.btn_pdf = ttk.Button(self.btn_frame, text="Export PDF...", command=self._generate_report, state=tk.DISABLED)
        self.btn_pdf.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.btn_frame, text="Save JSON...", command=self._save_json, state=tk.NORMAL).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.btn_frame, text="Clear Output", command=self._clear_output).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.btn_frame, textvariable=self.status, foreground="blue").pack(side=tk.RIGHT, padx=10)

        # --- Output Area ---
        # Impacted Files (Ranked) | Report Output
        out_frame = ttk.Frame(self.root)
        out_frame.pack(fill=tk.BOTH, expand=True, padx=main_pad, pady=main_pad)
        
        # Left: Impacted
        left_out = ttk.LabelFrame(out_frame, text="Impacted Files (ranked)")
        left_out.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.lst_impact = tk.Listbox(left_out, width=40)
        self.lst_impact.pack(fill=tk.BOTH, expand=True)
        
        # Right: Report Output (Treeview for structured data)
        right_out = ttk.LabelFrame(out_frame, text="Report Output")
        right_out.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        cols = ("File", "Lines", "Classification", "Risk")
        self.tree = ttk.Treeview(right_out, columns=cols, show='headings')
        self.tree.heading("File", text="File")
        self.tree.heading("Lines", text="Lines")
        self.tree.heading("Classification", text="Classification")
        self.tree.heading("Risk", text="Risk")
        self.tree.column("File", width=150)
        self.tree.column("Lines", width=80)
        self.tree.column("Classification", width=300)
        self.tree.column("Risk", width=80)
        
        sb = ttk.Scrollbar(right_out, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._toggle_mode()

    def _toggle_mode(self):
        mode = self.input_mode.get()
        if mode == "Folders":
            self.frame_folders.pack(fill=tk.X, padx=5, pady=5, before=self.btn_frame)
            self.frame_paste.pack_forget()
        else:
            self.frame_folders.pack_forget()
            self.frame_paste.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, before=self.btn_frame)

    def _browse(self, var):
        d = filedialog.askdirectory()
        if d:
            var.set(d)

    def _clear_output(self):
        self.lst_impact.delete(0, tk.END)
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.status.set("Ready")

    def _start_analysis(self):
        p1 = self.path_old.get()
        p2 = self.path_new.get()
        
        if self.input_mode.get() == "Folders":
            if not p1 or not p2:
                messagebox.showerror("Error", "Please select both directories.")
                return
        else:
             messagebox.showinfo("Info", "Paste mode logic not fully implemented. Please use Folders.")
             return
            
        self.status.set("Analyzing...")
        self._clear_output()
        threading.Thread(target=self._run_analysis_logic, args=(p1, p2), daemon=True).start()

    def _run_analysis_logic(self, p1, p2):
        try:
            skm1 = self._process_directory(p1, "Baseline")
            skm2 = self._process_directory(p2, "Modified")
            
            differ = SemanticDiffer(skm1, skm2)
            self.changes = differ.diff()
            
            # Invariant Checking
            checker = LegacyInvariantChecker(skm1, skm2)
            self.invariant_violations = checker.check()
            
            # Compute metrics
            high = sum(1 for c in self.changes if c.risk == "High")
            med = sum(1 for c in self.changes if c.risk == "Medium")
            low = sum(1 for c in self.changes if c.risk == "Low")
            self.metrics = {"high": high, "medium": med, "low": low}
            
            # --- Scope Inventory Calculation ---
            v1_files = {p.split('.')[0] + ".adb" for p in skm1.procedures}
            v2_files = {p.split('.')[0] + ".adb" for p in skm2.procedures}
            all_files = sorted(v1_files.union(v2_files))
            
            self.scope_data = [] 
            changed_files = {c.file_name for c in self.changes}
            
            for f in all_files:
                in_v1 = f in v1_files
                in_v2 = f in v2_files
                status = "Unchanged"
                
                if f in changed_files:
                    # Determine specific status from changes
                    file_changes = [c for c in self.changes if c.file_name == f]
                    # Priority: Deleted > Added > Modified
                    if any("Removal" in c.classification for c in file_changes): status = "Deleted"
                    elif any("Inserted" in c.classification for c in file_changes): status = "Added"
                    else: status = "Modified"
                elif in_v1 and not in_v2: status = "Deleted"
                elif not in_v1 and in_v2: status = "Added"
                
                self.scope_data.append((f, status, in_v1, in_v2))
            
            self.root.after(0, self._analysis_complete)
        except Exception as e:
            # We catch generic exceptions to prevent crash, but in dev we might want to see stack
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: self._analysis_failed(str(e)))
            
    def _process_directory(self, path, name) -> SystemKnowledgeModel:
        skm = SystemKnowledgeModel(name)
        builder = SKMBuilder(skm)
        
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.lower().endswith(('.adb', '.ads', '.ada')):
                    full_path = os.path.join(root, f)
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as fh:
                            code = fh.read()
                        
                        lexer = AdaLexer(code)
                        parser = AdaParser(lexer)
                        unit = parser.parse_compilation_unit()
                        builder.build(unit)
                    except Exception as e:
                        print(f"Error parsing {f}: {e}")
        return skm

    def _analysis_complete(self):
        self.status.set(f"Analysis Complete. {len(self.changes)} changes, {len(self.invariant_violations)} compliance violations.")
        self.btn_pdf.config(state=tk.NORMAL)
        
        # Populate Tree
        for c in self.changes:
             self.tree.insert("", "end", values=(c.file_name, c.line_range, c.classification, c.risk))
        
        # Populate Invariants
        for inv in self.invariant_violations:
             self.tree.insert("", "end", values=(
                 inv.location, 
                 "N/A", 
                 f"INVARIANT: {inv.description}", 
                 inv.severity
             ), tags=('violation',))
        
        self.tree.tag_configure('violation', foreground='red')
            
        # Populate Impacted Files (Simulated Ranking based on Risk) (could use affected_files list)
        impacted = set()
        for c in self.changes:
            if c.affected_files and "None" not in c.affected_files:
                 for line in c.affected_files.split('\n'):
                     impacted.add(line)
        
        for f in sorted(list(impacted)):
            self.lst_impact.insert(tk.END, f)

    def _analysis_failed(self, error_msg):
        self.status.set("Error")
        messagebox.showerror("Analysis Error", error_msg)

    def _generate_report(self):
        f = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Documents", "*.pdf")])
        if f:
            try:
                gen = PDFReportGenerator(f, self.changes, self.metrics, self.invariant_violations, self.scope_data)
                gen.generate()
                messagebox.showinfo("Success", f"Report saved to {f}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate report: {e}")

    def _save_json(self):
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if f:
            data = []
            for c in self.changes:
                # impacted_files is currently a string "File:Line\nFile:Line"
                # Parse it into a structured list
                impact_list = []
                if c.affected_files and "None" not in c.affected_files:
                    for line in c.affected_files.split('\n'):
                        parts = line.split(':')
                        if len(parts) >= 2:
                            impact_list.append({"file": parts[0], "line_info": parts[1]})
                        else:
                            impact_list.append({"file": line, "line_info": "?"})

                data.append({
                    "file": c.file_name,
                    "lines": c.line_range,
                    "type": c.classification,
                    "risk": c.risk,
                    "impacted_files": impact_list, # Structured list
                    "impact_summary": c.affected_files, # Keep raw string for ref
                    "tests": c.tests
                })
            for inv in self.invariant_violations:
                data.append({
                    "file": inv.location,
                    "lines": "N/A",
                    "type": f"Invariant Violation ({inv.rule_id}) - {inv.description}",
                    "risk": inv.severity,
                    "impact": "System Safety",
                    "tests": "Compliance Review"
                })
            with open(f, 'w') as fh:
                json.dump(data, fh, indent=4)
            messagebox.showinfo("Success", "JSON Saved")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdaAnalysisApp(root)
    root.mainloop()
