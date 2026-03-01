import fitz
import os

def generate_audit_pdf(input_md, output_pdf):
    if not os.path.exists(input_md):
        return

    with open(input_md, "r", encoding="utf-8") as f:
        content = f.read()

    doc = fitz.open()
    page = doc.new_page()
    margin = 50
    width = page.rect.width - 2 * margin
    y = margin
    
    # Nombres de fuentes estándar en PyMuPDF
    F_BOLD = "hebo"  # Helvetica-Bold
    F_REG = "helv"   # Helvetica
    
    font_size_title = 18
    font_size_header = 14
    font_size_body = 11
    
    lines = content.splitlines()
    
    for line in lines:
        if not line.strip():
            y += 10
            continue
            
        if y > page.rect.height - margin - 20:
            page = doc.new_page()
            y = margin

        if line.startswith("# "):
            text = line[2:].strip()
            page.insert_text((margin, y), text, fontsize=font_size_title, fontname=F_BOLD)
            y += font_size_title * 1.5
        elif line.startswith("## "):
            text = line[3:].strip()
            y += 10
            page.insert_text((margin, y), text, fontsize=font_size_header, fontname=F_BOLD)
            y += font_size_header * 1.5
        elif line.startswith("### "):
            text = line[4:].strip()
            page.insert_text((margin, y), text, fontsize=font_size_body + 1, fontname=F_BOLD)
            y += (font_size_body + 1) * 1.4
        elif line.startswith("* "):
            text = "• " + line[2:].strip()
            words = text.split()
            current_line = ""
            for word in words:
                if fitz.get_text_length(current_line + word + " ", fontsize=font_size_body) < width - 15:
                    current_line += word + " "
                else:
                    page.insert_text((margin + 15, y), current_line, fontsize=font_size_body, fontname=F_REG)
                    y += font_size_body * 1.2
                    current_line = word + " "
                    if y > page.rect.height - margin:
                        page = doc.new_page()
                        y = margin
            page.insert_text((margin + 15, y), current_line, fontsize=font_size_body, fontname=F_REG)
            y += font_size_body * 1.4
        elif line.strip() == "---":
            page.draw_line((margin, y), (page.rect.width - margin, y), color=(0.7, 0.7, 0.7), width=1)
            y += 15
        else:
            text = line.strip()
            words = text.split()
            current_line = ""
            for word in words:
                if fitz.get_text_length(current_line + word + " ", fontsize=font_size_body) < width:
                    current_line += word + " "
                else:
                    page.insert_text((margin, y), current_line, fontsize=font_size_body, fontname=F_REG)
                    y += font_size_body * 1.2
                    current_line = word + " "
                    if y > page.rect.height - margin:
                        page = doc.new_page()
                        y = margin
            page.insert_text((margin, y), current_line, fontsize=font_size_body, fontname=F_REG)
            y += font_size_body * 1.4

    doc.save(output_pdf)
    doc.close()

if __name__ == "__main__":
    generate_audit_pdf("AUDITORIA_UNCASE_V1.md", "AUDITORIA_UNCASE_V1.pdf")
