from fpdf import FPDF
import re
from typing import List


class PDF(FPDF):
    def header(self):
        # Custom header could be added here if needed
        pass


def _split_lines(md_text: str) -> List[str]:
    return md_text.splitlines()


def render_markdown_to_pdf(md_text: str, output_path: str) -> str:
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", size=12)

    lines = _split_lines(md_text)
    for line in lines:
        if not line.strip():
            pdf.ln(5)
            continue
        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 18)
            pdf.multi_cell(0, 10, line[2:].strip(), align="C")
            pdf.ln(2)
            pdf.set_font("Helvetica", size=12)
        elif line.startswith("## "):
            pdf.set_font("Helvetica", "B", 14)
            pdf.multi_cell(0, 8, line[3:].strip())
            pdf.ln(1)
            pdf.set_font("Helvetica", size=12)
        elif re.match(r"^\d+\. ", line):
            pdf.set_font("Helvetica", size=12)
            pdf.multi_cell(0, 7, line)
        else:
            pdf.multi_cell(0, 7, line)
    pdf.output(output_path)
    return output_path