from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, LongTable, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import List
from ..comparison.differ import Change
import os

class PDFReportGenerator:
    def __init__(self, filename: str, changes: List[Change], metrics: dict, invariant_violations: list = None, scope_data: list = None):
        self.filename = filename
        self.changes = changes
        self.metrics = metrics
        self.invariant_violations = invariant_violations or []
        # scope_data: List of tuples (filename, status, in_v1, in_v2)
        self.scope_data = scope_data or []

    def generate(self):
        doc = SimpleDocTemplate(self.filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = styles["Title"]
        elements.append(Paragraph("ADA Semantic Change Analysis Report", title_style))
        elements.append(Spacer(1, 12))
        
        # --- SCOPE INVENTORY (New) ---
        elements.append(Paragraph("Scope Inventory (Analyzed Files)", styles["Heading2"]))
        elements.append(Spacer(1, 6))
        
        if self.scope_data:
            inventory_data = [["File Name", "Status", "Before", "After"]]
            for fname, status, v1, v2 in self.scope_data:
                # Style status
                status_color = colors.black
                if status == "Modified": status_color = colors.orange
                elif status == "Added": status_color = colors.green
                elif status == "Deleted": status_color = colors.red
                elif status == "Renamed": status_color = colors.blue
                
                inventory_data.append([
                    Paragraph(fname, styles["Normal"]),
                    Paragraph(f"<font color='{status_color}'><b>{status}</b></font>", styles["Normal"]),
                    "Yes" if v1 else "-",
                    "Yes" if v2 else "-"
                ])
            
            scope_table = LongTable(inventory_data, colWidths=[200, 100, 80, 80], repeatRows=1)
            scope_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ]))
            elements.append(scope_table)
            elements.append(Spacer(1, 24))
        
        # Summary Metrics
        elements.append(Paragraph("Risk Assessment Summary", styles["Heading2"]))
        summary_text = f"""
        <b>Total Changes Detected:</b> {len(self.changes)}<br/>
        <b>Detailed Risk Breakout:</b><br/>
        High Risk: {self.metrics.get('high', 0)}<br/>
        Medium Risk: {self.metrics.get('medium', 0)}<br/>
        Low Risk: {self.metrics.get('low', 0)}<br/>"""
        
        if self.invariant_violations:
             summary_text += f"<br/><b>Invariant Violations:</b> <font color='red'>{len(self.invariant_violations)}</font>"
             
        elements.append(Paragraph(summary_text, styles["Normal"]))
        elements.append(Spacer(1, 24))

        # Change Table
        elements.append(Paragraph("Detailed Change Log", styles["Heading2"]))
        elements.append(Spacer(1, 12))
        
        # Columns: File Name, Lines, Classification, Affected Files, Risk, Tests
        data = [["File Name", "Lines", "Classification", "Affected Files", "Risk", "Tests Needed"]]
        
        for chg in self.changes:
            # Color code risk?
            risk_color = colors.black
            if chg.risk == "High": risk_color = colors.red
            elif chg.risk == "Medium": risk_color = colors.orange
            
            data.append([
                Paragraph(chg.file_name, styles["Normal"]),
                chg.line_range,
                Paragraph(chg.classification, styles["Normal"]),
                Paragraph(chg.affected_files.replace("\n", "<br/>"), styles["Normal"]),
                Paragraph(f"<font color='{risk_color}'><b>{chg.risk}</b></font>", styles["Normal"]),
                Paragraph(chg.tests, styles["Normal"])
            ])
            
        # Adjust col widths for better fit on Letter landscape or packed Portrait
        # Total ~540 pts available
        table = LongTable(data, colWidths=[80, 50, 120, 120, 50, 120], repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        
        # Invariant Violations
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("Invariant Violations (Legacy Check)", styles["Heading2"]))
        
        if self.invariant_violations:
            inv_data = [["Rule ID", "Description", "Location", "Severity"]]
            for inv in self.invariant_violations:
                inv_data.append([
                    inv.rule_id,
                    Paragraph(inv.description, styles["Normal"]),
                    inv.location,
                    Paragraph(f"<font color='red'><b>{inv.severity}</b></font>", styles["Normal"])
                ])
            
            inv_table = Table(inv_data, colWidths=[60, 250, 100, 60])
            inv_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(inv_table)
        else:
            elements.append(Paragraph("No explicit invariant violations detected in this pass.", styles["Normal"]))

        # Disclaimer
        elements.append(Spacer(1, 48))
        elements.append(Paragraph("System Limitation Disclaimer", styles["Heading2"]))
        disclaimer = """
        This analysis is based on static structural parsing of the ADA source code. 
        It guarantees complete structural impact coverage (call graphs, data dependencies) within the limits of the parser.
        <b>It does NOT guarantee the absence of runtime defects, functional logic errors, or compiler-level issues.</b>
        """
        elements.append(Paragraph(disclaimer, styles["Normal"]))

        doc.build(elements)
        print(f"Report generated at {os.path.abspath(self.filename)}")

