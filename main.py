import tkinter as tk
from ada_semantic_analysis.gui.app import AdaAnalysisApp

def main():
    root = tk.Tk()
    app = AdaAnalysisApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
