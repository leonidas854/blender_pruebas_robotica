#!/usr/bin/env python3
"""
Manual Técnico Completo de Modelado y Configuración en Blender
Autor: Thiago Sossa
Proyecto: Personaje "Viajero entre Épocas"
Genera: Documento Word (.docx) y convierte a PDF (.pdf)
"""

import os
import sys
import subprocess
from pathlib import Path

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

ROOT = Path("/home/leonidas/deveploment/blender_pruebas_robotica")
DOCS_DIR = ROOT / "docs"
ENTREGA_DIR = ROOT / "entrega"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
ENTREGA_DIR.mkdir(parents=True, exist_ok=True)

OUT_DOCX = DOCS_DIR / "Manual_Tecnico_Blender_Viajero_Thiago_Sossa.docx"
OUT_PDF = DOCS_DIR / "Manual_Tecnico_Blender_Viajero_Thiago_Sossa.pdf"

# Paleta cromática editorial
HEX_PRIMARY = "162B4D"     # Azul Marino Profundo
HEX_ACCENT = "C29B38"      # Dorado Ocre Noble
HEX_STEEL = "2C3E50"       # Gris Pizarra
HEX_LIGHT_BG = "F8FAFC"    # Fondo gris tenue para filas
HEX_CALLOUT_BG = "EFF6FF"  # Fondo azul suave para avisos
HEX_BORDER = "CBD5E1"      # Borde tenue

COLOR_PRIMARY = RGBColor(0x16, 0x2B, 0x4D)
COLOR_ACCENT = RGBColor(0xC2, 0x9B, 0x38)
COLOR_STEEL = RGBColor(0x2C, 0x3E, 0x50)
COLOR_DARK = RGBColor(0x1E, 0x29, 0x3B)
COLOR_MUTED = RGBColor(0x64, 0x74, 0x8B)

fig_counter = 1

def set_cell_background(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tc_pr.append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'  <w:top w:w="{top}" w:type="dxa"/>'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'  <w:left w:w="{left}" w:type="dxa"/>'
        f'  <w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)

def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders_xml = f'<w:tcBorders {nsdecls("w")}>'
    for side, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        if val:
            borders_xml += f'<{side} w:val="{val.get("val","single")}" w:sz="{val.get("sz","4")}" w:space="0" w:color="{val.get("color","auto")}"/>'
        else:
            borders_xml += f'<{side} w:val="none"/>'
    borders_xml += '</w:tcBorders>'
    tc_pr.append(parse_xml(borders_xml))

def add_header_footer(doc):
    section = doc.sections[0]
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.4)
    section.right_margin = Cm(2.4)

    header = section.header
    header_p = header.paragraphs[0]
    header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = header_p.add_run("MANUAL DE CONFIGURACIÓN 3D EN BLENDER — VIAJERO ENTRE ÉPOCAS")
    hrun.font.name = "Arial"
    hrun.font.size = Pt(8.5)
    hrun.font.color.rgb = COLOR_MUTED

    footer = section.footer
    footer_p = footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    frun1 = footer_p.add_run("Autor: Thiago Sossa  |  Blender 3.6 LTS & Cycles Engine")
    frun1.font.name = "Arial"
    frun1.font.size = Pt(8.5)
    frun1.font.color.rgb = COLOR_MUTED

def add_title(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(22)
    run.font.bold = True
    run.font.color.rgb = COLOR_PRIMARY
    return p

def add_subtitle(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(16)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(12)
    run.font.bold = False
    run.font.color.rgb = COLOR_ACCENT
    return p

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(15)
    run.font.bold = True
    run.font.color.rgb = COLOR_PRIMARY
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(13)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = COLOR_STEEL
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(10.5)
    run.font.bold = True
    run.font.color.rgb = COLOR_PRIMARY
    return p

def add_body_p(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        brun = p.add_run(bold_prefix)
        brun.font.name = "Arial"
        brun.font.size = Pt(9.5)
        brun.font.bold = True
        brun.font.color.rgb = COLOR_PRIMARY
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(9.5)
    run.font.color.rgb = COLOR_DARK
    return p

def add_bullet_p(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        brun = p.add_run(bold_prefix)
        brun.font.name = "Arial"
        brun.font.size = Pt(9.5)
        brun.font.bold = True
        brun.font.color.rgb = COLOR_PRIMARY
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(9.5)
    run.font.color.rgb = COLOR_DARK
    return p

def add_callout(doc, title, text, bg_color=HEX_CALLOUT_BG, border_color=HEX_ACCENT):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.8)
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=130, bottom=130, left=190, right=170)
    set_cell_borders(cell, left={"val": "single", "sz": "24", "color": border_color})
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    trun = p.add_run(title)
    trun.font.name = "Arial"
    trun.font.size = Pt(10)
    trun.font.bold = True
    trun.font.color.rgb = COLOR_PRIMARY
    
    p2 = cell.add_paragraph()
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after = Pt(0)
    p2.paragraph_format.line_spacing = 1.15
    run = p2.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(9)
    run.font.color.rgb = COLOR_DARK

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(3)
    sp.paragraph_format.space_after = Pt(3)

def add_figure(doc, img_rel_path, caption_text, width=Inches(4.1)):
    global fig_counter
    img_path = ROOT / img_rel_path
    if not img_path.exists():
        print(f"ALERTA: Imagen no encontrada: {img_path}")
        return None

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    run.add_picture(str(img_path), width=width)

    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_before = Pt(2)
    cp.paragraph_format.space_after = Pt(9)
    cp.paragraph_format.keep_with_next = True
    crun_bold = cp.add_run(f"Figura {fig_counter}: ")
    crun_bold.font.name = "Arial"
    crun_bold.font.size = Pt(9)
    crun_bold.font.bold = True
    crun_bold.font.color.rgb = COLOR_PRIMARY
    
    crun = cp.add_run(caption_text)
    crun.font.name = "Arial"
    crun.font.size = Pt(8.5)
    crun.font.italic = True
    crun.font.color.rgb = COLOR_MUTED

    fig_counter += 1
    return p

def add_styled_table(doc, headers, rows, col_widths=None):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    for c_idx, h in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        if col_widths and c_idx < len(col_widths):
            cell.width = col_widths[c_idx]
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=130, bottom=130, left=130, right=130)
        set_cell_borders(cell,
                         top={"val": "single", "sz": "6", "color": HEX_PRIMARY},
                         bottom={"val": "single", "sz": "12", "color": HEX_ACCENT})
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(h)
        run.font.name = "Arial"
        run.font.size = Pt(9)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r_idx, row_data in enumerate(rows):
        bg = HEX_LIGHT_BG if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = tbl.cell(r_idx + 1, c_idx)
            if col_widths and c_idx < len(col_widths):
                cell.width = col_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=90, bottom=90, left=130, right=130)
            set_cell_borders(cell,
                             bottom={"val": "single", "sz": "4", "color": HEX_BORDER})
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.1
            run = p.add_run(str(val))
            run.font.name = "Arial"
            run.font.size = Pt(8.5)
            run.font.color.rgb = COLOR_DARK

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(3)
    sp.paragraph_format.space_after = Pt(5)

print("Iniciando compilación del documento técnico...")
