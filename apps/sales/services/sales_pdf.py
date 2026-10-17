from io import BytesIO
from decimal import Decimal
from html.parser import HTMLParser
from html import escape

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether,
    LongTable,
)
from apps.sales.models import Sale


def pdf_money(value, currency="MXN"):
    try:
        value = Decimal(value or 0)
    except Exception:
        value = Decimal("0")
    return f"${value:,.2f} {currency} "


class ReportLabHTMLParser(HTMLParser):
    ALLOWED_TAGS = {"b", "strong", "i", "em", "u", "br", "sup", "sub"}

    def __init__(self):
        super().__init__()
        self.output = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in self.ALLOWED_TAGS:
            if tag == "strong":
                tag = "b"
            elif tag == "em":
                tag = "i"
            self.output.append(f"<{tag}>")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self.ALLOWED_TAGS:
            if tag == "strong":
                tag = "b"
            elif tag == "em":
                tag = "i"
            if tag != "br":
                self.output.append(f"</{tag}>")

    def handle_data(self, data):
        self.output.append(escape(data, quote=False))


def clean_reportlab_html(value):
    if value is None:
        return ""
    value = str(value)
    parser = ReportLabHTMLParser()
    parser.feed(value)
    return "".join(parser.output)


def get_pdf_styles():
    styles = getSampleStyleSheet()

    # Paleta de colores clínica moderna (Azul ejecutivo corporativo / Gris pizarra / Acentos suaves)
    primary_color = colors.HexColor("#1A365D")   # Azul marino profundo y elegante
    secondary_color = colors.HexColor("#2B6CB0") # Azul corporativo brillante
    text_color = colors.HexColor("#2D3748")      # Gris oscuro muy legible

    styles.add(
        ParagraphStyle(
            name="ContractH1",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            spaceBefore=12,
            spaceAfter=6,
            textColor=primary_color,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ContractH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            spaceBefore=10,
            spaceAfter=4,
            textColor=secondary_color,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ContractH3",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            spaceBefore=8,
            spaceAfter=3,
            textColor=secondary_color,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ContractBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13.5,
            spaceAfter=5,
            textColor=text_color,
            wordWrap="LTR",
        )
    )

    styles.add(
        ParagraphStyle(
            name="ContractSmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#718096"),
        )
    )

    styles.add(
        ParagraphStyle(
            name="TableCell",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=text_color,
        )
    )

    styles.add(
        ParagraphStyle(
            name="TableHeader",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#FFFFFF"),
        )
    )

    styles.add(
        ParagraphStyle(
            name="SignatureText",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            alignment=TA_CENTER,
            textColor=text_color,
        )
    )

    return styles


def draw_pdf_header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4

    # Línea decorativa superior sutil
    canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, height - 12 * mm, width - 20 * mm, height - 12 * mm)

    # Pie de página moderno y limpio
    canvas.setFont("Helvetica", 7.5)
    
    # Izquierda: "Powered by " en gris y "PLUS ERP" en azul fuerte
    prefix_text = "Powered by "
    domain_text = "PLUS ERP"
    
    x_pos = 20 * mm
    y_pos = 10 * mm

    # Dibujar "Powered by "
    canvas.setFillColor(colors.HexColor("#A0AEC0"))
    canvas.drawString(x_pos, y_pos, prefix_text)
    
    # Calcular el ancho exacto del prefijo para concatenar el dominio justo al lado
    prefix_width = canvas.stringWidth(prefix_text, "Helvetica", 7.5)
    
    # Dibujar "PLUS ERP" en azul fuerte (puedes ajustar el HexColor a tu gusto, ej. #1A365D o #2B6CB0)
    canvas.setFillColor(colors.HexColor("#1A365D"))
    canvas.drawString(x_pos + prefix_width, y_pos, domain_text)

    # Derecha: Número de página (en color gris original)
    canvas.setFillColor(colors.HexColor("#A0AEC0"))
    canvas.drawRightString(
        width - 20 * mm,
        y_pos,
        f"Página {doc.page}",
    )

    canvas.restoreState()


def get_company_logo(company):
    if not company or not company.logo:
        return None
    try:
        file_obj = company.logo
        file_obj.open("rb")
        data = file_obj.read()
        file_obj.close()
        return BytesIO(data)
    except Exception:
        return None


def build_sale_header(sale, styles):
    story = []
    company = sale.company
    branch = sale.branch

    logo_buffer = get_company_logo(company)
    company_name = (
        branch.name_branch
        if branch and branch.name_branch
        else company.company_name
    )
    responsible = (
        branch.name_of_the_person_in_charge
        if branch and branch.name_of_the_person_in_charge
        else company.name_of_the_person_in_charge
    )
    phone = branch.phone if branch and branch.phone else company.phone
    email = branch.email_branch if branch and branch.email_branch else company.support_email

    left = []
    if logo_buffer:
        logo = Image(
            logo_buffer,
            width=26 * mm,
            height=26 * mm,
            kind="proportional",
        )
        left.append(logo)

    clinic_text = f"""
    <b>{escape(company_name or "")}</b><br/>
    <font color="#718096">{escape(responsible or "")}<br/>
    {escape(phone or "")} | {escape(email or "")}</font>
    """
    left.append(Paragraph(clinic_text, styles["ContractSmall"]))

    right = Paragraph(
        f"""
        <font size="13" color="#1A365D"><b>ORDEN / CONTRATO</b></font><br/><br/>
        <b>Folio:</b> {escape(sale.reference or "")}<br/>
        <b>Emisión:</b> {sale.creationDate.strftime("%d/%m/%Y") if sale.creationDate else ""}<br/>
        <b>Estatus:</b> <font color="#2B6CB0"><b>{escape(sale.get_status_display() or "")}</b></font>
        """,
        styles["ContractSmall"],
    )

    header = Table(
        [[left, right]],
        colWidths=[115 * mm, 55 * mm],
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, 0),
                    0.8,
                    colors.HexColor("#1A365D"),
                ),
            ]
        )
    )

    story.append(header)
    story.append(Spacer(1, 5 * mm))
    return story


def build_customer_section(sale, styles):
    customer = sale.customer
    customer_name = customer.name if customer and customer.name else "Sin paciente asignado"
    customer_phone = customer.cellphone or customer.phone or "No registrado" if customer else "No registrado"
    customer_email = customer.email or "No registrado" if customer else "No registrado"

    # Tipografía limpia y formal para etiquetas
    customer_label_style = ParagraphStyle(
        name="CustomerLabelFormal",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#718096"), # Gris elegante neutral
    )
    
    # Tipografía sobria para los valores
    customer_value_style = ParagraphStyle(
        name="CustomerValueFormal",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
    )

    # Estructura de contenido limpia
    left_content = [
        Paragraph("PACIENTE", customer_label_style),
        Spacer(1, 1 * mm),
        Paragraph(f"<b>{escape(str(customer_name))}</b>", customer_value_style),
    ]

    right_content = [
        Paragraph("CONTACTO", customer_label_style),
        Spacer(1, 1 * mm),
        Paragraph(f"Tel: {escape(str(customer_phone))}<br/>Email: {escape(str(customer_email))}", customer_value_style),
    ]

    card_table = Table(
        [[left_content, right_content]],
        colWidths=[90 * mm, 80 * mm],
    )
    
    # Estilo formal: Fondo blanco, sin barras laterales, solo un borde sutil inferior
    card_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white), # Fondo estrictamente blanco
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                # Línea discreta y elegante en la parte inferior para delimitar la sección de datos
                ("LINEBELOW", (0, 0), (-1, -1), 0.75, colors.HexColor("#E2E8F0")),
            ]
        )
    )

    return [card_table, Spacer(1, 6 * mm)]


def build_sale_items(sale, styles):
    currency = sale.currency or "MXN"
    header = [
        Paragraph("CONCEPTO / TRATAMIENTO", styles["TableHeader"]),
        Paragraph("CANT.", styles["TableHeader"]),
        Paragraph("P. UNITARIO", styles["TableHeader"]),
        Paragraph("DESC.", styles["TableHeader"]),
        Paragraph("IMPUESTO", styles["TableHeader"]),
        Paragraph("TOTAL", styles["TableHeader"]),
    ]

    rows = [header]
    for item in sale.items.all():
        discount = item.discount or Decimal("0")
        rows.append([
            Paragraph(escape(item.name or ""), styles["TableCell"]),
            Paragraph(str(item.quantity), styles["TableCell"]),
            Paragraph(pdf_money(item.unit_price, currency), styles["TableCell"]),
            Paragraph(pdf_money(discount, currency), styles["TableCell"]),
            Paragraph(pdf_money(item.tax_amount, currency), styles["TableCell"]),
            Paragraph(f"<b>{pdf_money(item.total, currency)}</b>", styles["TableCell"]),
        ])

    table = LongTable(
        rows,
        repeatRows=1,
        colWidths=[55 * mm, 14 * mm, 26 * mm, 20 * mm, 25 * mm, 30 * mm],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
                ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#1A365D")),
                ("LINEBELOW", (0, 1), (-1, -1), 0.4, colors.HexColor("#EDF2F7")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    return [table, Spacer(1, 5 * mm)]


def build_totals(sale, styles):
    currency = sale.currency or "MXN"
    data = [
        ["", Paragraph("Subtotal", styles["TableCell"]), Paragraph(pdf_money(sale.subtotal, currency), styles["TableCell"])],
        ["", Paragraph("Descuento", styles["TableCell"]), Paragraph(pdf_money(sale.discount_total, currency), styles["TableCell"])],
        ["", Paragraph("Impuestos", styles["TableCell"]), Paragraph(pdf_money(sale.tax_total, currency), styles["TableCell"])],
        ["", Paragraph("<b>TOTAL</b>", styles["TableCell"]), Paragraph(f"<b>{pdf_money(sale.total, currency)}</b>", styles["TableCell"])],
        ["", Paragraph("Pagado", styles["TableCell"]), Paragraph(pdf_money(sale.amount_paid, currency), styles["TableCell"])],
        ["", Paragraph("<b>SALDO PENDIENTE</b>", styles["TableCell"]), Paragraph(f"<b>{pdf_money(sale.balance, currency)}</b>", styles["TableCell"])],
    ]

    table = Table(data, colWidths=[90 * mm, 40 * mm, 40 * mm])
    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
                ("LINEABOVE", (1, 3), (-1, 3), 0.8, colors.HexColor("#1A365D")),
                ("LINEABOVE", (1, 5), (-1, 5), 0.8, colors.HexColor("#1A365D")),
            ]
        )
    )
    return table


def build_payment_history(sale, styles):
    payments = list(sale.payments.all())
    if not payments:
        return []

    currency = sale.currency or "MXN"
    rows = [[
        Paragraph("FECHA", styles["TableHeader"]),
        Paragraph("RECIBIDO", styles["TableHeader"]),
        Paragraph("CAMBIO", styles["TableHeader"]),
        Paragraph("ACUMULADO", styles["TableHeader"]),
        Paragraph("SALDO", styles["TableHeader"]),
    ]]

    for payment in payments:
        rows.append([
            Paragraph(payment.date.strftime("%d/%m/%Y %H:%M") if payment.date else "", styles["TableCell"]),
            Paragraph(pdf_money(payment.cash_received, currency), styles["TableCell"]),
            Paragraph(pdf_money(payment.change_given, currency), styles["TableCell"]),
            Paragraph(pdf_money(payment.new_amount_paid, currency), styles["TableCell"]),
            Paragraph(pdf_money(payment.new_balance, currency), styles["TableCell"]),
        ])

    table = LongTable(
        rows,
        repeatRows=1,
        colWidths=[32 * mm, 32 * mm, 30 * mm, 38 * mm, 38 * mm],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
            ]
        )
    )

    return [
        Spacer(1, 4 * mm),
        Paragraph("Historial de Transacciones / Pagos", styles["ContractH3"]),
        table,
    ]


def render_contract_content(sale, styles):
    story = []
    contract_sale_data = getattr(sale, "contractSale", None)
    contract_obj = getattr(sale, "contract", None)

    if not contract_sale_data and not contract_obj:
        return story

    story.append(PageBreak())
    story.append(Paragraph("TÉRMINOS Y CONDICIONES DEL TRATAMIENTO", styles["ContractH1"]))
    story.append(Spacer(1, 2 * mm))

    # 1. Renderizar contenido desde sale.contractSale (dict con bloques o texto)
    if isinstance(contract_sale_data, dict):
        blocks = contract_sale_data.get("blocks", [])
        if isinstance(blocks, list) and blocks:
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                flowables = render_contract_block(block, styles)
                if flowables:
                    story.extend(flowables)
        else:
            # Si el diccionario tiene otro formato o texto directo
            for key, val in contract_sale_data.items():
                if isinstance(val, str) and val.strip():
                    story.append(Paragraph(clean_reportlab_html(val), styles["ContractBody"]))
    elif isinstance(contract_sale_data, str) and contract_sale_data.strip():
        for paragraph in contract_sale_data.split("\n"):
            if paragraph.strip():
                story.append(Paragraph(clean_reportlab_html(paragraph), styles["ContractBody"]))
    elif contract_obj and getattr(contract_obj, "contract_text", None):
        # Fallback al texto encriptado del modelo Contract si contractSale no estuviera presente
        raw_text = str(contract_obj.contract_text or "")
        for paragraph in raw_text.split("\n"):
            if paragraph.strip():
                story.append(Paragraph(clean_reportlab_html(paragraph), styles["ContractBody"]))

    # 2. Renderizar sección de firmas usando el modelo Contract asociado a la venta
    if contract_obj:
        story.extend(render_contract_signatures(sale, contract_obj, styles))

    return story


def render_contract_block(block, styles):
    block_type = block.get("type", "p")
    content = block.get("content", "")
    block_styles = block.get("styles") or {}
    color = block_styles.get("color", "#2D3748")
    align = block_styles.get("align", "left")

    alignment_map = {"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT}
    alignment = alignment_map.get(align, TA_LEFT)

    if block_type == "h1":
        style = ParagraphStyle("DynH1", parent=styles["ContractH1"], textColor=color, alignment=alignment)
        return [Paragraph(clean_reportlab_html(content), style), Spacer(1, 2 * mm)]
    if block_type == "h2":
        style = ParagraphStyle("DynH2", parent=styles["ContractH2"], textColor=color, alignment=alignment)
        return [Paragraph(clean_reportlab_html(content), style)]
    if block_type == "h3":
        style = ParagraphStyle("DynH3", parent=styles["ContractH3"], textColor=color, alignment=alignment)
        return [Paragraph(clean_reportlab_html(content), style)]
    if block_type == "p":
        style = ParagraphStyle("DynP", parent=styles["ContractBody"], textColor=color, alignment=alignment)
        return [Paragraph(clean_reportlab_html(content), style)]
    if block_type == "table":
        table_data = block.get("tableData")
        if not isinstance(table_data, list) or not table_data:
            return []
        rows = []
        for r_idx, row in enumerate(table_data):
            if not isinstance(row, list):
                continue
            curr = []
            for cell in row:
                c_text = clean_reportlab_html(cell or "")
                st = styles["TableHeader"] if r_idx == 0 else styles["TableCell"]
                curr.append(Paragraph(c_text, st))
            rows.append(curr)
        col_w = (170 * mm) / max(len(r) for r in rows)
        t = LongTable(rows, repeatRows=1, colWidths=[col_w] * max(len(r) for r in rows))
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        return [t, Spacer(1, 3 * mm)]
    if block_type in ["li", "ul"]:
        return [Paragraph("• " + clean_reportlab_html(content), styles["ContractBody"])]

    return [Paragraph(clean_reportlab_html(content), styles["ContractBody"])]


from reportlab.graphics.shapes import Drawing, Path, Rect

def draw_signature_from_json(signature_json, width=70 * mm, height=22 * mm):
    """
    Convierte una estructura JSON de coordenadas de firma (ej. trazos con x, y)
    en un objeto Flowable de ReportLab (Drawing) que dibuja la firma de forma vectorial.
    """
    d = Drawing(width, height)
    
    # Fondo opcional simulando el recuadro de un canvas limpio
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#FAFAFA"), strokeColor=colors.HexColor("#CBD5E0"), strokeWidth=0.5, rx=3, ry=3))

    if not signature_json or not isinstance(signature_json, list):
        return d

    # 1. Encontrar los límites (bounding box) de las coordenadas para escalar la firma al tamaño del recuadro
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')

    has_points = False
    for stroke in signature_json:
        if isinstance(stroke, list):
            for pt in stroke:
                if isinstance(pt, dict) and 'x' in pt and 'y' in pt:
                    x, y = float(pt['x']), float(pt['y'])
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
                    has_points = True

    if not has_points or min_x == max_x or min_y == max_y:
        return d

    src_w = max_x - min_x
    src_h = max_y - min_y

    # Márgenes internos dentro del dibujo para que la firma no pegue con los bordes
    padding = 6
    target_w = width - (padding * 2)
    target_h = height - (padding * 2)

    scale_x = target_w / src_w
    scale_y = target_h / src_h
    scale = min(scale_x, scale_y) # Mantener proporción (aspect ratio)

    # 2. Dibujar los trazos vectoriales
    for stroke in signature_json:
        if not isinstance(stroke, list) or len(stroke) < 2:
            continue
        
        path = Path(strokeWidth=1.2, strokeColor=colors.HexColor("#1A365D"), strokeLineCap=1, strokeLineJoin=1)
        started = False

        for pt in stroke:
            if not isinstance(pt, dict) or 'x' not in pt or 'y' not in pt:
                continue
            x = float(pt['x'])
            y = float(pt['y'])

            # Normalizar, escalar e invertir el eje Y para ReportLab
            nx = padding + (x - min_x) * scale
            ny = height - (padding + (y - min_y) * scale)

            if not started:
                path.moveTo(nx, ny)
                started = True
            else:
                path.lineTo(nx, ny)

        if started:
            d.add(path)

    return d


def render_contract_signatures(sales, contract_obj, styles):
    company_name_val = str(sales.user.name or "Especialista / Personal Autorizado")
    patient_name_val = str(
        getattr(contract_obj, "patient_name", None) 
        or (sales.customer.name if sales and sales.customer else None) 
        or "Paciente / Responsable"
    )    
    company_date = contract_obj.company_signed_at.strftime("%d/%m/%Y %H:%M") if contract_obj.company_signed_at else ""
    patient_date = contract_obj.patient_signed_at.strftime("%d/%m/%Y %H:%M") if contract_obj.patient_signed_at else ""

    patient_signature_json = getattr(contract_obj, "patiente_signature_json", None)
    company_signature_json = getattr(contract_obj, "company_signature_json", None)
    is_signed = getattr(contract_obj, "is_signed", False)

    # --- Bloque Firma Doctor / Empresa ---
    doctor_sig_content = []
    if company_signature_json:
        doctor_sig_content.append(draw_signature_from_json(company_signature_json))
    else:
        doctor_sig_content.append(Paragraph("<br/><br/>________________________________________", styles["SignatureText"]))
        if is_signed:
            doctor_sig_content.append(Paragraph("<font color='#2B6CB0'><b>[ FIRMA REGISTRADA ]</b></font>", styles["SignatureText"]))

    doctor_sig_content.extend([
        Spacer(1, 2 * mm),
        Paragraph("<b>Por parte de la Clínica</b>", styles["SignatureText"]),
        Paragraph(f"<b>{escape(company_name_val)}</b>", styles["SignatureText"]),
        Paragraph(f"<font size='7' color='#718096'>Fecha: {company_date}</font>", styles["SignatureText"])
    ])

    # --- Bloque Firma Paciente ---
    patient_sig_content = []
    if patient_signature_json:
        patient_sig_content.append(draw_signature_from_json(patient_signature_json))
    else:
        patient_sig_content.append(Paragraph("<br/><br/>________________________________________", styles["SignatureText"]))
        if is_signed:
            patient_sig_content.append(Paragraph("<font color='#2B6CB0'><b>[ FIRMA REGISTRADA ]</b></font>", styles["SignatureText"]))

    patient_sig_content.extend([
        Spacer(1, 2 * mm),
        Paragraph("<b>De Conformidad del Paciente</b>", styles["SignatureText"]),
        Paragraph(f"<b>{escape(patient_name_val)}</b>", styles["SignatureText"]),
        Paragraph(f"<font size='7' color='#718096'>Fecha: {patient_date}</font>", styles["SignatureText"])
    ])

    sig_table = Table(
        [[doctor_sig_content, patient_sig_content]],
        colWidths=[85 * mm, 85 * mm],
    )
    sig_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    return [
        Spacer(1, 8 * mm),
        KeepTogether([
            Paragraph("<b>Autorización y Conformidad del Tratamiento</b>", styles["ContractH3"]),
            Spacer(1, 4 * mm),
            sig_table
        ])
    ]

def download_sale_pdf(request, sale_id):
    sale = get_object_or_404(
        Sale.objects
        .select_related(
            "company",
            "branch",
            "customer",
            "user",
            "created_by",
            "contract",  # Relación OneToOne con el modelo Contract
        )
        .prefetch_related(
            "items",
            "payments",
        )
        .filter(
            company=request.user.company
        ),
        id=sale_id,
    )

    buffer = BytesIO()
    styles = get_pdf_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"Orden y Contrato {sale.reference}",
        author="Denty.cloud",
    )

    story = []

    story.extend(build_sale_header(sale, styles))
    story.extend(build_customer_section(sale, styles))
    story.extend(build_sale_items(sale, styles))
    
    story.append(
        KeepTogether([
            build_totals(sale, styles)
        ])
    )

    story.extend(build_payment_history(sale, styles))

    # Renderizamos el contenido del contrato usando sale.contractSale y las firmas del modelo Contract
    if getattr(sale, "contractSale", None) or getattr(sale, "contract", None):
        story.extend(render_contract_content(sale, styles))

    doc.build(
        story,
        onFirstPage=draw_pdf_header_footer,
        onLaterPages=draw_pdf_header_footer,
    )

    buffer.seek(0)
    filename = f"{sale.reference or 'venta'}_contrato_medico.pdf"

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response