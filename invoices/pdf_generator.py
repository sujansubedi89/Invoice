"""
PDF GENERATOR - ReportLab Module
ReportLab draws PDFs like a canvas: you place elements at X,Y coordinates.
This recreates the exact invoice layout from the image.
"""
import os
from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer ,Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# Brand colors matching the invoice image
BRAND_RED   = colors.HexColor('#C0395A')
LIGHT_GRAY  = colors.HexColor('#F5F0EE')
MID_GRAY    = colors.HexColor('#CCCCCC')
DARK_TEXT   = colors.HexColor('#2C2C2C')
TABLE_HEADER_BG = colors.HexColor('#D9D3D0')


def generate_invoice_pdf(invoice):
    """
    Build a PDF in memory and return it as a BytesIO buffer.
    We use ReportLab's Platypus (high-level layout engine) with Tables.
    """
    buffer = BytesIO()

    # A4 page, 20mm margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()
    story  = []  # List of "flowable" elements that get stacked top-to-bottom

    # ── HEADER: Company Logo + Name ──────────────────────────────────────────
    header_style = ParagraphStyle(
        'CompanyName',
        fontSize=16,
        textColor=DARK_TEXT,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        letterSpacing=3,
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        fontSize=9,
        textColor=colors.HexColor('#888888'),
        alignment=TA_CENTER,
        fontName='Helvetica',
        letterSpacing=2,
        spaceAfter=8
    )

    # Company logo letter "J" in brand red
    logo_style = ParagraphStyle(
        'Logo', fontSize=28, textColor=BRAND_RED,
        alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=2
    )
    logo_path=os.path.join(settings.BASE_DIR,'static','jyaba_logo.jpg')
    if not os.path.exists(logo_path):
     logo_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'jyaba_logo.jpg')

    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=120,height=50)
        logo_img.hAlign = 'CENTER'
        story.append(logo_img)
    else:   
        styles=getSampleStyleSheet()
        story.append(Paragraph("Jyaba Tech", styles['heading1']))
    # story.append(Paragraph("J", logo_style))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("JYABA TECH PVT LTD", header_style))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("Data Engineering Provider", subtitle_style))
    story.append(Spacer(1, 8*mm))

    # ── INVOICE META: Issued To + Invoice Number/Date ────────────────────────
    bold_label = ParagraphStyle('BoldLabel', fontSize=9, fontName='Helvetica-Bold', textColor=DARK_TEXT)
    normal_val = ParagraphStyle('NormalVal', fontSize=9, fontName='Helvetica', textColor=DARK_TEXT)
    right_bold = ParagraphStyle('RightBold', fontSize=9, fontName='Helvetica-Bold', textColor=DARK_TEXT, alignment=TA_RIGHT)
    right_val  = ParagraphStyle('RightVal',  fontSize=9, fontName='Helvetica', textColor=DARK_TEXT, alignment=TA_RIGHT)

    meta_data = [
        [
            Paragraph("ISSUED TO:", bold_label),
            Paragraph("", normal_val),
            Paragraph("INVOICE NO:", right_bold),
            Paragraph(f"<b>{invoice.invoice_number}</b>", right_val),
        ],
        [
            Paragraph(invoice.vendor_client, normal_val),
            Paragraph("", normal_val),
            Paragraph("DATE:", right_bold),
            Paragraph(invoice.invoice_date.strftime("%d.%m.%Y"), right_val),
        ],
    ]
    if invoice.vendor_address:
        meta_data.append([
            Paragraph(invoice.vendor_address.replace('\n', '<br/>'), normal_val),
            '', '', ''
        ])
    if invoice.due_date:
        meta_data.append([
            '', '',
            Paragraph("DUE DATE:", right_bold),
            Paragraph(invoice.due_date.strftime("%d.%m.%Y"), right_val),
        ])

    meta_table = Table(meta_data, colWidths=[60*mm, 30*mm, 40*mm, 40*mm])
    meta_table.setStyle(TableStyle([
        ('ALIGN',     (0,0), (-1,-1), 'LEFT'),
        ('VALIGN',    (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6*mm))

    # ── SERVICE TITLE ─────────────────────────────────────────────────────────
    service_label_style = ParagraphStyle(
        'ServiceLabel', fontSize=9, fontName='Helvetica-Bold',
        textColor=DARK_TEXT, spaceAfter=1
    )
    service_val_style = ParagraphStyle(
        'ServiceVal', fontSize=9, fontName='Helvetica',
        textColor=DARK_TEXT, spaceAfter=5
    )
    story.append(Paragraph("SERVICE TITLE:", service_label_style))
    story.append(Paragraph(invoice.service_title, service_val_style))
    story.append(Spacer(1, 3*mm))

    # ── LINE ITEMS TABLE ──────────────────────────────────────────────────────
    currency = invoice.currency

    col_header_style = ParagraphStyle(
        'ColHeader', fontSize=8, fontName='Helvetica-Bold',
        textColor=DARK_TEXT, alignment=TA_CENTER
    )
    cell_style = ParagraphStyle(
        'Cell', fontSize=9, fontName='Helvetica',
        textColor=DARK_TEXT, alignment=TA_LEFT
    )
    cell_right = ParagraphStyle(
        'CellRight', fontSize=9, fontName='Helvetica',
        textColor=DARK_TEXT, alignment=TA_RIGHT
    )
    cell_center = ParagraphStyle(
        'CellCenter', fontSize=9, fontName='Helvetica',
        textColor=DARK_TEXT, alignment=TA_CENTER
    )

    # Table header row
    table_data = [[
        Paragraph("DESCRIPTION", col_header_style),
        Paragraph("UNITS", col_header_style),
        Paragraph("PER UNIT NET PRICE", col_header_style),
        Paragraph("COST", col_header_style),
        Paragraph("TOTAL", col_header_style),
    ]]

    # Data rows for each line item
    for item in invoice.line_items.all():
        table_data.append([
            Paragraph(item.description, cell_style),
            Paragraph(str(item.units), cell_center),
            Paragraph(f"{currency} {item.unit_price:.2f}", cell_right),
            Paragraph(f"{currency} {item.unit_price:.2f}", cell_right),
            Paragraph(f"{currency} {item.total:.2f}", cell_right),
        ])

    # Subtotal, Tax, Total rows
    subtotal    = invoice.get_subtotal()
    tax_amount  = invoice.get_tax_amount()
    grand_total = invoice.get_grand_total()

    summary_bold = ParagraphStyle('SumBold', fontSize=9, fontName='Helvetica-Bold', textColor=DARK_TEXT)
    total_bold   = ParagraphStyle('TotalBold', fontSize=10, fontName='Helvetica-Bold', textColor=DARK_TEXT, alignment=TA_RIGHT)
    total_val    = ParagraphStyle('TotalVal', fontSize=10, fontName='Helvetica-Bold', textColor=DARK_TEXT, alignment=TA_RIGHT)

    table_data.append([
        Paragraph("SUBTOTAL", summary_bold), '', '', '',
        Paragraph(f"{subtotal:.2f}", cell_right)
    ])
    table_data.append([
        '', '', '', Paragraph("Tax", cell_right),
        Paragraph(f"{tax_amount:.2f}", cell_right)
    ])
    table_data.append([
        '', '', '', Paragraph("TOTAL", total_bold),
        Paragraph(f"{currency} {grand_total:.2f}", total_val)
    ])

    # Column widths: Description gets the most space
    col_widths = [65*mm, 20*mm, 35*mm, 30*mm, 20*mm]

    items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(TableStyle([
        # Header row: gray background
        ('BACKGROUND',   (0,0), (-1,0), TABLE_HEADER_BG),
        ('TEXTCOLOR',    (0,0), (-1,0), DARK_TEXT),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,0), 8),
        ('ALIGN',        (0,0), (-1,0), 'CENTER'),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-3), [colors.white, LIGHT_GRAY]),
        # Subtotal row
        ('BACKGROUND',   (0,-3), (-1,-3), colors.white),
        # Total row: gray background to match image
        ('BACKGROUND',   (0,-1), (-1,-1), TABLE_HEADER_BG),
        # Grid lines
        ('LINEBELOW',    (0,0), (-1,0), 0.5, MID_GRAY),
        ('LINEBELOW',    (0,-4), (-1,-4), 0.5, MID_GRAY),
        ('LINEBELOW',    (0,-1), (-1,-1), 0.5, MID_GRAY),
        # Padding
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('LEFTPADDING',  (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        # Span SUBTOTAL across first 4 cols
        ('SPAN',         (0,-3), (3,-3)),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 8*mm))

    # ── PAYMENT DETAILS ───────────────────────────────────────────────────────
    payment_bold = ParagraphStyle('PayBold', fontSize=9, fontName='Helvetica-Bold', textColor=DARK_TEXT, spaceAfter=2)
    payment_val  = ParagraphStyle('PayVal',  fontSize=9, fontName='Helvetica-Oblique', textColor=DARK_TEXT)

    story.append(Paragraph("PAYMENT DETAILS", payment_bold))

    story.append(Paragraph(
    "PayPal Email: <b>techjyaba@gmail.com</b>",
    payment_val
))

    story.append(Spacer(1, 10*mm))

    # ── TERMS & CONDITIONS ─────────────────────────────────────────────────────
    terms_title = ParagraphStyle('TermsTitle', fontSize=9, fontName='Helvetica', textColor=DARK_TEXT, spaceAfter=3)
    terms_item  = ParagraphStyle('TermsItem',  fontSize=8, fontName='Helvetica-Oblique', textColor=colors.HexColor('#666666'), leftIndent=10)

    story.append(Paragraph("Terms & Conditions", terms_title))
    story.append(Paragraph("• The above mentioned pricings does not include any taxes", terms_item))
    story.append(Paragraph("• The cost is payable for the initial service delivery", terms_item))

    if invoice.notes:
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph(invoice.notes, terms_item))

    story.append(Spacer(1, 10*mm))

    # ── THANK YOU ─────────────────────────────────────────────────────────────
    thank_style = ParagraphStyle(
        'ThankYou', fontSize=10, fontName='Helvetica-Bold',
        textColor=DARK_TEXT, alignment=TA_CENTER
    )
    story.append(Paragraph("THANK YOU", thank_style))

    # Build the PDF and write to buffer
    doc.build(story)
    buffer.seek(0)  # Rewind buffer to the beginning before returning
    return buffer
