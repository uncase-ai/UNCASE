import fitz
import os

def generate_audit_report_pdf(input_md, output_pdf):
    if not os.path.exists(input_md):
        print(f"Error: {input_md} no encontrado.")
        return

    with open(input_md, "r", encoding="utf-8") as f:
        content = f.read()

    doc = fitz.open()
    page = doc.new_page()
    margin = 50
    width = page.rect.width - 2 * margin
    y = margin
    
    # Estilo de Colores
    COLOR_TITLE = (0.0, 0.2, 0.4)  # Azul Oscuro
    COLOR_TEXT = (0.1, 0.1, 0.1)
    COLOR_GREY = (0.4, 0.4, 0.4)
    COLOR_LINE = (0.8, 0.8, 0.8)

    F_BOLD = "hebo"
    F_REG = "helv"
    
    lines = content.splitlines()
    
    for line in lines:
        if not line.strip():
            y += 10
            continue
            
        if y > page.rect.height - margin - 30:
            page = doc.new_page()
            y = margin

        if line.startswith("# "):
            text = line[2:].strip().replace("**", "")
            page.insert_text((margin, y), text, fontsize=18, fontname=F_BOLD, color=COLOR_TITLE)
            y += 30
        elif line.startswith("## "):
            text = line[3:].strip().replace("**", "")
            y += 5
            page.insert_text((margin, y), text, fontsize=14, fontname=F_BOLD, color=COLOR_TITLE)
            y += 22
        elif line.startswith("### "):
            text = line[4:].strip().replace("**", "")
            page.insert_text((margin, y), text, fontsize=12, fontname=F_BOLD, color=COLOR_TEXT)
            y += 18
        elif line.startswith("* "):
            # Bullet point
            page.insert_text((margin + 10, y), "•", fontsize=11, fontname=F_BOLD, color=COLOR_TITLE)
            text = line[2:].strip().replace("**", "")
            words = text.split()
            current_line = ""
            for word in words:
                if fitz.get_text_length(current_line + word + " ", fontsize=10) < width - 25:
                    current_line += word + " "
                else:
                    page.insert_text((margin + 25, y), current_line, fontsize=10, fontname=F_REG, color=COLOR_TEXT)
                    y += 12
                    current_line = word + " "
                    if y > page.rect.height - margin:
                        page = doc.new_page()
                        y = margin
            page.insert_text((margin + 25, y), current_line, fontsize=10, fontname=F_REG, color=COLOR_TEXT)
            y += 15
        elif line.strip() == "---":
            page.draw_line((margin, y), (page.rect.width - margin, y), color=COLOR_LINE, width=1)
            y += 20
        else:
            # Texto normal o metadatos
            clean_line = line.strip().replace("**", "")
            words = clean_line.split()
            current_line = ""
            font_to_use = F_BOLD if line.startswith("**") else F_REG
            size_to_use = 10
            
            for word in words:
                if fitz.get_text_length(current_line + word + " ", fontsize=size_to_use) < width:
                    current_line += word + " "
                else:
                    page.insert_text((margin, y), current_line, fontsize=size_to_use, fontname=font_to_use, color=COLOR_TEXT)
                    y += 12
                    current_line = word + " "
                    if y > page.rect.height - margin:
                        page = doc.new_page()
                        y = margin
            page.insert_text((margin, y), current_line, fontsize=size_to_use, fontname=font_to_use, color=COLOR_TEXT)
            y += 14

    # Pie de página
    for i in range(len(doc)):
        p = doc[i]
        p.insert_text((p.rect.width / 2 - 20, p.rect.height - 30), f"Página {i+1}", fontsize=8, fontname=F_REG, color=COLOR_GREY)

    doc.save(output_pdf)
    doc.close()
    print(f"PDF generado exitosamente: {output_pdf}")

if __name__ == "__main__":
    generate_audit_report_pdf("AUDIT_REPORT_UNCASE.md", "AUDIT_REPORT_UNCASE.pdf")
