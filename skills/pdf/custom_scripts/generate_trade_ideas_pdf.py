#!/usr/bin/env python3
"""
Generate a professional dark-themed PDF report for trade ideas.
Usage: python generate_trade_ideas_pdf.py /path/to/trade_ideas.json
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image as PILImage


DARK_BG = HexColor('#121212')
DARK_CARD = HexColor('#16213e')
DARK_CARD_ALT = HexColor('#0f3460')
TEXT_PRIMARY = HexColor('#ffffff')
TEXT_SECONDARY = HexColor('#a0a0a0')
ACCENT_CYAN = HexColor('#00d9ff')
ACCENT_GREEN = HexColor('#00c853')
ACCENT_RED = HexColor('#ff1744')
ACCENT_ORANGE = HexColor('#ff9800')
ACCENT_YELLOW = HexColor('#ffeb3b')


class DarkPDFDocTemplate(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        SimpleDocTemplate.__init__(self, *args, **kwargs)


def draw_dark_background(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFillColor(DARK_BG)
    canvas_obj.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    canvas_obj.restoreState()


def create_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='DarkTitle',
        parent=styles['Title'],
        fontName='Times-Roman',
        fontSize=28,
        textColor=TEXT_PRIMARY,
        alignment=TA_LEFT,
        spaceAfter=6
    ))
    
    styles.add(ParagraphStyle(
        name='DarkSubtitle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        textColor=TEXT_SECONDARY,
        alignment=TA_LEFT,
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='DarkHeading1',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=18,
        textColor=ACCENT_CYAN,
        spaceBefore=12,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='DarkHeading2',
        parent=styles['Heading2'],
        fontName='Times-Bold',
        fontSize=14,
        textColor=ACCENT_CYAN,
        spaceBefore=10,
        spaceAfter=6
    ))
    
    styles.add(ParagraphStyle(
        name='DarkNormal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        textColor=TEXT_PRIMARY,
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='DarkBullet',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        textColor=TEXT_PRIMARY,
        leftIndent=20,
        bulletIndent=10,
        leading=14
    ))
    
    styles.add(ParagraphStyle(
        name='DarkSmall',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        textColor=TEXT_SECONDARY,
        leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='TradeName',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=16,
        textColor=TEXT_PRIMARY,
        spaceBefore=0,
        spaceAfter=4
    ))
    
    styles.add(ParagraphStyle(
        name='DirectionLong',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=14,
        textColor=ACCENT_GREEN,
        alignment=TA_LEFT,
        spaceBefore=4,
        spaceAfter=4
    ))
    
    styles.add(ParagraphStyle(
        name='DirectionShort',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=14,
        textColor=ACCENT_RED,
        alignment=TA_LEFT,
        spaceBefore=4,
        spaceAfter=4
    ))
    
    styles.add(ParagraphStyle(
        name='RiskWarning',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8,
        textColor=TEXT_SECONDARY,
        alignment=TA_CENTER,
        spaceBefore=20
    ))
    
    return styles


def format_timestamp(ts_str):
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M UTC')
    except:
        return ts_str


def create_header_section(data, styles):
    elements = []
    
    metadata = data.get('report_metadata', {})
    symbol = metadata.get('symbol', 'Unknown')
    generated_at = format_timestamp(metadata.get('generated_at', ''))
    analysis_type = metadata.get('analysis_type', 'Trade Ideas')
    
    elements.append(Paragraph(symbol, styles['DarkTitle']))
    elements.append(Paragraph(f"Generated: {generated_at}", styles['DarkSubtitle']))
    elements.append(Paragraph(analysis_type, styles['DarkSubtitle']))
    
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT_CYAN, spaceAfter=12))
    
    return elements


def create_trade_section(trade, styles, json_dir):
    elements = []
    
    trade_id = trade.get('trade_id', '')
    name = trade.get('name', 'Unknown Trade')
    direction = trade.get('direction', '').upper()
    risk_reward = trade.get('risk_reward_ratio', '')
    
    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT_CYAN, spaceBefore=12, spaceAfter=12))
    
    direction_style = 'DirectionLong' if direction == 'LONG' else 'DirectionShort'
    direction_text = f"{'▲' if direction == 'LONG' else '▼'} {direction}"
    
    header_data = [[
        Paragraph(f"Trade #{trade_id}: {name}", styles['TradeName']),
        Paragraph(direction_text, styles[direction_style])
    ]]
    header_table = Table(header_data, colWidths=[5*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(header_table)
    
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT_CYAN, spaceBefore=8, spaceAfter=8))
    
    entry_price = trade.get('entry_price', 'N/A')
    stop_loss = trade.get('stop_loss', 'N/A')
    target_1 = trade.get('target_1', {})
    target_2 = trade.get('target_2', {})
    
    tp_text = f"${target_1.get('price', 'N/A')}"
    if target_2.get('price'):
        tp_text += f" / ${target_2.get('price')}"
    
    trade_data = [
        ['Entry', f"${entry_price}"],
        ['TP', tp_text],
        ['SL', f"${stop_loss}"],
        ['Risk/Reward', str(risk_reward) if risk_reward else 'N/A'],
    ]
    
    trade_table = Table(trade_data, colWidths=[1.5*inch, 5.5*inch])
    trade_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (0, -1), ACCENT_CYAN),
        ('TEXTCOLOR', (1, 0), (1, -1), TEXT_PRIMARY),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(trade_table)
    
    notes = trade.get('notes')
    if notes:
        elements.append(Spacer(1, 8))
        elements.append(Paragraph("Reason", styles['DarkHeading2']))
        elements.append(Paragraph(notes, styles['DarkNormal']))
    
    charts = trade.get('charts', {})
    chart_5m_tpsl_path = charts.get('chart_5m_tpsl')
    chart_5m_vaval_path = charts.get('chart_5m_vaval')
    chart_1m_path = charts.get('chart_1m')
    
    max_chart_width = 6 * inch
    max_chart_height = 3.5 * inch
    
    images_added = []
    
    if chart_5m_tpsl_path:
        full_path = resolve_image_path(chart_5m_tpsl_path, json_dir)
        img_element = create_image_element(full_path, max_chart_width, max_chart_height, "5M TP/SL Chart")
        if img_element:
            images_added.append(img_element)
    
    if chart_5m_vaval_path:
        full_path = resolve_image_path(chart_5m_vaval_path, json_dir)
        img_element = create_image_element(full_path, max_chart_width, max_chart_height, "5M VAVAL Chart")
        if img_element:
            images_added.append(img_element)
    
    if chart_1m_path:
        full_path = resolve_image_path(chart_1m_path, json_dir)
        img_element = create_image_element(full_path, max_chart_width, max_chart_height, "1M Chart")
        if img_element:
            images_added.append(img_element)
    
    if images_added:
        elements.append(Spacer(1, 10))
        for img in images_added:
            elements.append(img)
            elements.append(Spacer(1, 8))
    
    return elements


def resolve_image_path(path_str, json_dir):
    if os.path.isabs(path_str):
        return path_str
    
    candidates = [
        path_str,
        os.path.join(json_dir, path_str),
        os.path.join(json_dir, os.path.basename(path_str)),
    ]
    
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    
    return path_str


def create_image_element(image_path, max_width, max_height, label=""):
    try:
        if not os.path.exists(image_path):
            print(f"Warning: Image not found: {image_path}")
            return None
        
        img = PILImage.open(image_path)
        img_width, img_height = img.size
        
        width_ratio = max_width / img_width
        height_ratio = max_height / img_height
        ratio = min(width_ratio, height_ratio, 1.0)
        
        display_width = img_width * ratio
        display_height = img_height * ratio
        
        return Image(image_path, width=display_width, height=display_height)
        
    except Exception as e:
        print(f"Warning: Could not load image {image_path}: {e}")
        return None


def create_risk_warning(data, styles):
    elements = []
    
    warning = data.get('risk_warning', '')
    
    if warning:
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=TEXT_SECONDARY, spaceAfter=10))
        elements.append(Paragraph(warning, styles['RiskWarning']))
    
    return elements


def generate_pdf(json_path):
    json_path = os.path.abspath(json_path)
    
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    json_dir = os.path.dirname(json_path)
    
    metadata = data.get('report_metadata', {})
    symbol = metadata.get('symbol', 'TRADE').replace('/', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"{symbol}_trade_ideas_{timestamp}.pdf"
    output_path = os.path.join(json_dir, output_filename)
    
    styles = create_styles()
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    story = []
    
    story.extend(create_header_section(data, styles))
    
    trade_ideas = data.get('trade_ideas', [])
    
    for i, trade in enumerate(trade_ideas):
        if i > 0:
            story.append(PageBreak())
        story.extend(create_trade_section(trade, styles, json_dir))
    
    story.extend(create_risk_warning(data, styles))
    
    doc.build(story, onFirstPage=draw_dark_background, onLaterPages=draw_dark_background)
    
    print(f"PDF generated successfully: {output_path}")
    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_trade_ideas_pdf.py <path_to_json_file>")
        print("Example: python generate_trade_ideas_pdf.py ./trade_ideas.json")
        sys.exit(1)
    
    json_path = sys.argv[1]
    generate_pdf(json_path)


if __name__ == "__main__":
    main()
