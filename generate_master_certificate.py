import fitz
import os

def generate_master_certificate_pdf(input_md, output_pdf):
    if not os.path.exists(input_md):
        return

    with open(input_md, "r", encoding="utf-8") as f:
        content = f.read()

    doc = fitz.open()
    page = doc.new_page()
    
    COLOR_GOLD = (0.72, 0.53, 0.04)
    COLOR_DARK = (0.1, 0.1, 0.1)
    COLOR_GREY = (0.4, 0.4, 0.4)
    COLOR_BLUE = (0.0, 0.2, 0.4)

    page.draw_rect(page.rect + (20, 20, -20, -20), color=COLOR_BLUE, width=2)
    page.draw_rect(page.rect + (25, 25, -25, -25), color=COLOR_GOLD, width=1)

    margin = 60
    width = page.rect.width - 2 * margin
    y = margin + 20
    
    F_BOLD = "hebo"
    F_REG = "helv"
    
    lines = content.splitlines()
    
    for line in lines:
        if not line.strip():
            y += 8
            continue
            
        if y > page.rect.height - margin - 50:
            page = doc.new_page()
            page.draw_rect(page.rect + (20, 20, -20, -20), color=COLOR_BLUE, width=2)
            page.draw_rect(page.rect + (25, 25, -25, -25), color=COLOR_GOLD, width=1)
            y = margin

        if line.startswith("# "):
            text = line[2:].strip().replace("**", "")
            words = text.split()
            curr_title = ""
            for word in words:
                if fitz.get_text_length(curr_title + word + " ", fontsize=18, fontname=F_BOLD) < width:
                    curr_title += word + " "
                else:
                    page.insert_text((margin, y), curr_title, fontsize=18, fontname=F_BOLD, color=COLOR_BLUE)
                    y += 22
                    curr_title = word + " "
            page.insert_text((margin, y), curr_title, fontsize=18, fontname=F_BOLD, color=COLOR_BLUE)
            y += 30
        elif line.startswith("## "):
            text = line[3:].strip().replace("**", "")
            page.insert_text((margin, y), text, fontsize=11, fontname=F_BOLD, color=COLOR_GREY)
            y += 20
        elif line.startswith("### "):
            text = line[4:].strip().replace("**", "")
            y += 10
            rect = fitz.Rect(margin - 5, y - 12, page.rect.width - margin + 5, y + 5)
            page.draw_rect(rect, color=None, fill=(0.95, 0.95, 0.97))
            page.insert_text((margin, y), text, fontsize=12, fontname=F_BOLD, color=COLOR_DARK)
            y += 25
        elif line.startswith("#### "):
            text = line[5:].strip().replace("**", "")
            page.insert_text((margin, y), text, fontsize=10, fontname=F_BOLD, color=COLOR_BLUE)
            y += 18
        elif line.startswith("▪ "):
            bullet = "▪ "
            page.insert_text((margin, y), bullet, fontsize=9, fontname=F_BOLD, color=COLOR_GOLD)
            text = line[2:].strip().replace("**", "")
            words = text.split()
            current_line = ""
            for word in words:
                if fitz.get_text_length(current_line + word + " ", fontsize=9) < width - 20:
                    current_line += word + " "
                else:
                    page.insert_text((margin + 15, y), current_line, fontsize=9, fontname=F_REG)
                    y += 11
                    current_line = word + " "
                    if y > page.rect.height - margin:
                        page = doc.new_page()
                        y = margin
            page.insert_text((margin + 15, y), current_line, fontsize=9, fontname=F_REG)
            y += 14
        elif line.strip() == "---":
            page.draw_line((margin, y), (margin + 200, y), color=COLOR_GOLD, width=1)
            y += 20
        else:
            clean_line = line.strip().replace("**", "")
            words = clean_line.split()
            current_line = ""
            for word in words:
                if fitz.get_text_length(current_line + word + " ", fontsize=9) < width:
                    current_line += word + " "
                else:
                    page.insert_text((margin, y), current_line, fontsize=9, fontname=F_REG)
                    y += 11
                    current_line = word + " "
                    if y > page.rect.height - margin:
                        page = doc.new_page()
                        y = margin
            page.insert_text((margin, y), current_line, fontsize=9, fontname=F_REG)
            y += 14

    footer_y = page.rect.height - 70
    page.draw_line((margin, footer_y), (margin + 150, footer_y), color=COLOR_DARK, width=1)
    page.insert_text((margin, footer_y + 12), "Gonzalo Williams Hinojosa", fontsize=9, fontname=F_BOLD, color=COLOR_DARK)
    page.insert_text((margin, footer_y + 22), "Socio Representante", fontsize=8, fontname=F_REG, color=COLOR_GREY)
    
    page.insert_text((page.rect.width - margin - 100, footer_y + 12), "Sello de Validez V1.0", fontsize=8, fontname=F_REG, color=COLOR_GOLD)

    doc.save(output_pdf)
    doc.close()

if __name__ == "__main__":
    generate_master_certificate_pdf("CERTIFICACION_UNCASE_V1_MASTER.md", "CERTIFICACION_UNCASE_V1_MASTER.pdf")
