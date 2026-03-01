import fitz
import os
import re

def generate_objective_pdf(input_md, output_pdf):
    if not os.path.exists(input_md):
        return

    with open(input_md, "r", encoding="utf-8") as f:
        content = f.read()

    doc = fitz.open()
    page = doc.new_page()
    margin = 50
    width = page.rect.width - 2 * margin
    y = margin
    
    F_BOLD = "hebo"  # Helvetica-Bold
    F_REG = "helv"   # Helvetica
    
    font_size_title = 18
    font_size_header = 14
    font_size_body = 11
    
    lines = content.splitlines()
    
    def write_rich_text(page, text, pos, font_reg, font_bold, size, max_w):
        """Dibuja texto procesando negritas con **."""
        x, curr_y = pos
        # Separar por partes de negrita
        parts = re.split(r"(\*\*.*?\*\*)", text)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                clean_text = part[2:-2]
                f = font_bold
            else:
                clean_text = part
                f = font_reg
            
            # Dibujar la parte (sin wrap aquí por simplicidad del split asumiendo que ya viene pre-formateado o es corto)
            # Para un wrap real con negritas mezcladas, se requiere un motor de layout más complejo.
            # Aquí lo haremos simple por palabra si es necesario.
            page.insert_text((x, curr_y), clean_text, fontsize=size, fontname=f)
            x += fitz.get_text_length(clean_text, fontsize=size, fontname=f)
        return curr_y

    for line in lines:
        if not line.strip():
            y += 10
            continue
            
        if y > page.rect.height - margin - 30:
            page = doc.new_page()
            y = margin

        if line.startswith("# "):
            text = line[2:].strip().replace("**", "")
            page.insert_text((margin, y), text, fontsize=font_size_title, fontname=F_BOLD)
            y += font_size_title * 1.8
        elif line.startswith("## "):
            text = line[3:].strip().replace("**", "")
            y += 10
            page.insert_text((margin, y), text, fontsize=font_size_header, fontname=F_BOLD)
            y += font_size_header * 1.6
        elif line.startswith("### "):
            text = line[4:].strip()
            # Procesar negritas inline si existen
            write_rich_text(page, text, (margin, y), F_REG, F_BOLD, font_size_body + 1, width)
            y += (font_size_body + 1) * 1.5
        elif line.startswith("* "):
            # Bullet point con soporte de negrita básico
            page.insert_text((margin, y), "• ", fontsize=font_size_body, fontname=F_REG)
            text = line[2:].strip()
            
            # Word wrap manual con soporte de negritas es complejo, así que limpiaremos 
            # las negritas para el wrap pero mantendremos la lógica de seguridad solicitada.
            # Para cumplir al 100% el "no sugarcoat" y "no asteriscos", los eliminamos 
            # o los procesamos. Aquí los eliminamos para asegurar que no se escapen.
            clean_line = text.replace("**", "")
            words = clean_line.split()
            current_line = ""
            for word in words:
                if fitz.get_text_length(current_line + word + " ", fontsize=font_size_body) < width - 20:
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
        elif line.startswith("|"): # Tabla simple
            text = line.replace("|", "  ").replace("**", "").strip()
            page.insert_text((margin, y), text, fontsize=font_size_body - 1, fontname=F_REG)
            y += font_size_body * 1.2
        else:
            # Párrafo normal, eliminando asteriscos para evitar que se escapen
            clean_line = line.strip().replace("**", "")
            words = clean_line.split()
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
    generate_objective_pdf("AUDITORIA_TECNICA_OBJETIVA_V1.md", "AUDITORIA_TECNICA_OBJETIVA_V1.pdf")
