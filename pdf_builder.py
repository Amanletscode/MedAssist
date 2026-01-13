"""
PDF generation module for creating medical claim summaries.
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
from typing import Dict, List
import datetime


class PDFError(Exception):
    """Raised when PDF generation fails."""
    pass


def build_claim_pdf(
    output_path: str,
    patient: Dict[str, str],
    diagnoses: List[str],
    procedures: List[str]
) -> str:
    """
    Generate a claim PDF with patient info, diagnoses, and procedures.
    
    Args:
        output_path: Where to save the PDF
        patient: Dict with keys: name, dob, insurance, policy
        diagnoses: List of ICD-10 codes/descriptions
        procedures: List of CPT-4 codes/descriptions
        
    Returns:
        Path to the generated PDF
        
    Raises:
        PDFError: If PDF generation fails
    """
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height - 50, "MedAssist AI - Claim Summary")
        
        # Generated date
        c.setFont("Helvetica", 9)
        c.drawString(50, height - 70, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Patient info section
        y = height - 100
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Patient Information")
        c.setFont("Helvetica", 11)
        y -= 25
        c.drawString(60, y, f"Name: {patient.get('name', 'N/A')}")
        y -= 18
        c.drawString(60, y, f"DOB: {patient.get('dob', 'N/A')}")
        y -= 18
        c.drawString(60, y, f"Insurance: {patient.get('insurance', 'N/A')}")
        y -= 18
        c.drawString(60, y, f"Policy #: {patient.get('policy', 'N/A')}")
        
        # Diagnoses section
        y -= 35
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Diagnoses (ICD-10) - {len(diagnoses)} code(s)")
        c.setFont("Helvetica", 11)
        y -= 20
        
        for d in diagnoses:
            if y < 100:  # Start new page if needed
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 11)
            c.drawString(60, y, f"• {d}")
            y -= 18
        
        if not diagnoses:
            c.drawString(60, y, "No diagnoses specified")
            y -= 18
        
        # Procedures section
        y -= 25
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Procedures (CPT-4) - {len(procedures)} code(s)")
        c.setFont("Helvetica", 11)
        y -= 20
        
        for p in procedures:
            if y < 100:  # Start new page if needed
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 11)
            c.drawString(60, y, f"• {p}")
            y -= 18
        
        if not procedures:
            c.drawString(60, y, "No procedures specified")
        
        c.showPage()
        c.save()
        
        return str(output_path)
        
    except Exception as e:
        raise PDFError(f"Failed to generate PDF: {e}")
