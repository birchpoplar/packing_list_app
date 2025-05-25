from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer, Frame, PageTemplate
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import sys

HEADER_IMAGE_PATH = "A_digital_graphic_design_image_serves_as_a_header_.png"

def parse_markdown_checklist(md_path):
    with open(md_path) as f:
        lines = [line.strip() for line in f.readlines()]

    sections = []
    current_section = ""
    current_items = []

    for line in lines:
        if line.startswith("## "):
            if current_section:
                sections.append((current_section, current_items))
            current_section = line[3:]
            current_items = []
        elif line.startswith("- [ ]"):
            current_items.append(line[6:].strip())
    if current_section:
        sections.append((current_section, current_items))

    return sections

def generate_pdf(md_path, pdf_path):
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    title = styles["Heading2"]

    sections = parse_markdown_checklist(md_path)

    items = []

    # Insert header image
    try:
        img = Image(HEADER_IMAGE_PATH, width=6.5*inch, height=2*inch)
        items.append(img)
        items.append(Spacer(1, 0.25*inch))
    except Exception as e:
        print("Could not load header image:", e)

    checkbox_symbol = "☐"  # Unicode empty checkbox

    for section, checklist in sections:
        items.append(Paragraph(f"<b>{section}</b>", title))
        items.append(Spacer(1, 0.1*inch))
        for item in checklist:
            items.append(Paragraph(f"{checkbox_symbol} {item}", normal))
        items.append(Spacer(1, 0.2*inch))

    # Two-column layout
    frame1 = Frame(doc.leftMargin, doc.bottomMargin, (doc.width / 2) - 6, doc.height, id='col1')
    frame2 = Frame(doc.leftMargin + (doc.width / 2) + 6, doc.bottomMargin, (doc.width / 2) - 6, doc.height, id='col2')
    doc.addPageTemplates([PageTemplate(id='TwoCol', frames=[frame1, frame2])])

    doc.build(items)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python export_pdf.py input.md output.pdf")
        sys.exit(1)
    generate_pdf(sys.argv[1], sys.argv[2])
