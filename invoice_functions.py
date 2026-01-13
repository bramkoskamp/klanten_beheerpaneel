import datetime
import io
import os
import time
import textwrap

from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def generate_pdf(doc_type, customer_name, customer_address, customer_country, items, sender_info):
    """ doc_type: "invoice" of "quote" """
    load_dotenv()
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin_left = 40  # Optional logo placement
    logo_path = os.path.join(os.path.dirname(__file__), "static", "logo", "logo.png")
    logo_drawn = False
    logo_width_max, logo_height_max = 140, 70
    logo_y_top = height - 40
    draw_w = draw_h = 0
    
    if os.path.exists(logo_path):
        try:
            logo_reader = ImageReader(logo_path)
            img_w, img_h = logo_reader.getSize()
            scale = min(logo_width_max / img_w, logo_height_max / img_h)
            draw_w, draw_h = img_w * scale, img_h * scale
            pdf.drawImage(logo_reader, margin_left, logo_y_top - draw_h, width=draw_w, height=draw_h, mask="auto")
            logo_drawn = True
        except Exception:
            pass
    
    logo_height_used = draw_h if logo_drawn else 0
    header_y = (logo_y_top - logo_height_used) - 20 if logo_drawn else height - 60
    header_x = margin_left

    # --- Generate unique invoice number ---
    invoice_number = f"{int(time.time())}"
    # --- Header ---
    pdf.setFont("Helvetica-Bold", 16)
    title = "Factuur" if doc_type == "invoice" else "Offerte"
    pdf.drawString(header_x, header_y, title)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(header_x, header_y - 20, sender_info.get('name', 'Naam'))
    pdf.drawString(header_x, header_y - 32, sender_info.get('address', 'Adres'))
    pdf.drawString(header_x, header_y - 44, sender_info.get('country', 'Land'))
    pdf.drawString(header_x, header_y - 56, f"Factuur nummer: {invoice_number}")

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(width - 180, header_y, "Klantgegevens:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(width - 180, header_y - 20, customer_name)
    pdf.drawString(width - 180, header_y - 32, customer_address)
    pdf.drawString(width - 180, header_y - 44, customer_country)

    # --- Datum en vervaldatum ---
    today_str = datetime.datetime.now().strftime('%d-%m-%Y')
    pdf.drawString(width - 180, header_y - 70, f"{'Factuurdatum' if doc_type == 'invoice' else 'Offertedatum'}: {today_str}")

    if doc_type == "invoice":
        pdf.drawString(width - 180, header_y - 82, "Vervaldatum: 12-12-2025")
    else:
        pdf.drawString(width - 180, header_y - 82, "Geldig t/m: 30-12-2025")

    # Load owner data from environment
    owner_name = os.getenv('OWNER_NAME', 'Naam')
    owner_address = os.getenv('OWNER_ADDRESS', 'Adres')
    owner_city = os.getenv('OWNER_CITY', 'Stad')
    owner_iban = os.getenv('OWNER_IBAN', 'IBAN')
    owner_vat = os.getenv('OWNER_VAT_NUMBER', 'VAT')
    owner_phone = os.getenv('OWNER_PHONE', 'Telefoon')
    owner_email = os.getenv('OWNER_EMAIL', 'E-mail')
    owner_kvk = os.getenv('OWNER_KVK_NUMBER', 'KVK')

    # --- Table header ---
    table_top = header_y - 120
    pdf.setFont("Helvetica-Bold", 10)
    headers = ["Titel", "Aantal", "Bedrag", "BTW", "Totaal excl. BTW"]
    col_widths = [220, 70, 80, 50, 100]
    x = margin_left

    for i, h in enumerate(headers):
        pdf.drawString(x, table_top, h)
        x += col_widths[i]
    
    pdf.setLineWidth(1)
    pdf.line(margin_left, table_top - 5, width - margin_left, table_top - 5)

    # --- Table items ---
    pdf.setFont("Helvetica", 10)
    y_row = table_top - 25

    for item in items:
        x = margin_left
        amount = item['amount']
        price = item['price']
        tax_rate = float(item.get('tax', 0))
        total_ex = amount * price
        row = [
            item['title'],
            str(amount),
            f"€ {price:.2f}",
            f"{tax_rate:.0f}%",
            f"€ {total_ex:.2f}"
        ]

        for i, cell in enumerate(row):
            pdf.drawString(x, y_row, cell)
            x += col_widths[i]
        y_row -= 18

    # --- Description block under table ---
    description_text = " ".join([item.get('description', '') for item in items if item.get('description')]) or "Geen omschrijving opgegeven"
    desc_lines = textwrap.wrap(description_text, width=90)
    desc_height = max(40, 16 + len(desc_lines) * 12)
    desc_top = y_row - 10


    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(margin_left, desc_top - 14, "Omschrijving van de dienst")
    pdf.setFont("Helvetica", 10)
    text_y = desc_top - 28
    for line in desc_lines:
        pdf.drawString(margin_left, text_y, line)
        text_y -= 12

    # --- Subtotal, VAT, total ---
    summary_base = desc_top - desc_height -50
    subtotal = sum(item['amount'] * item['price'] for item in items)
    vat = sum(item['amount'] * item['price'] * (float(item.get('tax', 0)) / 100) for item in items)
    total = subtotal + vat
    pdf.setFont("Helvetica", 10)

    pdf.drawString(margin_left, summary_base, "Subtotaal")
    pdf.drawString(margin_left + 250, summary_base, f"€ {subtotal:.2f}")

    vat_rates = sorted({float(item.get('tax', 0)) for item in items})
    vat_label = f"BTW {vat_rates[0]:.0f}%" if len(vat_rates) == 1 else "BTW"
    pdf.drawString(margin_left, summary_base - 20, vat_label)
    pdf.drawString(margin_left + 250, summary_base - 20, f"€ {vat:.2f}")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin_left, summary_base - 40, "Totaal te betalen")
    pdf.drawString(margin_left + 250, summary_base - 40, f"€ {total:.2f}")

    # --- Payment note (only for invoice) ---
    if doc_type == "invoice":
        pdf.setFont("Helvetica", 9)
        pdf.drawString(margin_left, summary_base - 90, "We verzoeken u vriendelijk het bovenstaande bedrag voor de genoemde vervaldatum te voldoen.")

        # --- Footer ---
        pdf.setFont("Helvetica", 9)
        center_x = width / 2
        pdf.drawCentredString(center_x, 62, f"{owner_name} | {owner_address} | {owner_city}")
        pdf.drawCentredString(center_x, 50, f"IBAN: {owner_iban} | BTW: {owner_vat}")
        pdf.drawCentredString(center_x, 38, f"Mobiel: {owner_phone} | E-mail: {owner_email} | KVK: {owner_kvk}")
        pdf.drawCentredString(center_x, 26, "Automatisch gegenereerd door software van Bram Koskamp")

    pdf.save()
    buffer.seek(0)
    return buffer