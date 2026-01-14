"""PDF export service using ReportLab."""
from decimal import Decimal
from io import BytesIO
from typing import BinaryIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_RIGHT, TA_LEFT

from ..models.invoice import Invoice

class PDFExportService:
    """Service for exporting invoices to PDF format."""
    
    def export_invoice(self, invoice: Invoice) -> bytes:
        """
        Export an invoice to PDF format.
        
        Args:
            invoice: The invoice to export
            
        Returns:
            PDF document as bytes
        """
        buffer = BytesIO()
        self._generate_pdf(invoice, buffer)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _generate_pdf(self, invoice: Invoice, buffer: BinaryIO) -> None:
        """
        Generate the PDF document.
        
        Args:
            invoice: The invoice to export
            buffer: Buffer to write PDF to
        """

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        elements = []

        styles = getSampleStyleSheet()

        elements.extend(self._create_header(invoice, styles))
        elements.append(Spacer(1, 0.3 * inch))

        elements.extend(self._create_client_section(invoice, styles))
        elements.append(Spacer(1, 0.3 * inch))

        elements.extend(self._create_line_items_table(invoice))
        elements.append(Spacer(1, 0.3 * inch))

        elements.extend(self._create_totals_section(invoice, styles))

        doc.build(elements)
    
    def _create_header(self, invoice: Invoice, styles) -> list:
        """Create the invoice header section."""
        elements = []

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
        )
        elements.append(Paragraph("INVOICE", title_style))

        normal_style = styles['Normal']
        elements.append(Paragraph(f"<b>Invoice Number:</b> {invoice.invoice_number}", normal_style))
        elements.append(Paragraph(f"<b>Invoice Date:</b> {invoice.invoice_date.strftime('%B %d, %Y')}", normal_style))
        elements.append(Paragraph(f"<b>Due Date:</b> {invoice.due_date.strftime('%B %d, %Y')}", normal_style))

        status_str = invoice.status.value if hasattr(invoice.status, 'value') else str(invoice.status)
        elements.append(Paragraph(f"<b>Status:</b> {status_str.upper()}", normal_style))
        
        return elements
    
    def _create_client_section(self, invoice: Invoice, styles) -> list:
        """Create the client information section."""
        elements = []
        
        if not invoice.client:
            return elements

        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
        )
        elements.append(Paragraph("Bill To:", heading_style))

        normal_style = styles['Normal']
        client = invoice.client
        elements.append(Paragraph(f"<b>{client.name}</b>", normal_style))
        elements.append(Paragraph(client.street, normal_style))
        elements.append(Paragraph(f"{client.city}, {client.state} {client.zip_code}", normal_style))
        elements.append(Paragraph(client.country, normal_style))
        elements.append(Paragraph(f"Email: {client.email}", normal_style))
        elements.append(Paragraph(f"Phone: {client.phone}", normal_style))
        
        return elements
    
    def _create_line_items_table(self, invoice: Invoice) -> list:
        """Create the line items table."""
        elements = []

        data = [
            ['Description', 'Quantity', 'Unit Rate', 'Amount']
        ]
        
        for item in invoice.line_items:
            amount = item.calculate_amount()
            data.append([
                item.description,
                f"{item.quantity:.2f}",
                f"${item.unit_rate:.2f}",
                f"${amount:.2f}"
            ])

        table = Table(data, colWidths=[3.5 * inch, 1 * inch, 1 * inch, 1 * inch])

        table.setStyle(TableStyle([

            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),

            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),

            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_totals_section(self, invoice: Invoice, styles) -> list:
        """Create the totals summary section."""
        elements = []

        subtotal = invoice.calculate_subtotal()
        tax = invoice.calculate_tax()
        total = invoice.calculate_total()

        totals_data = [
            ['Subtotal:', f"${subtotal:.2f}"],
            [f'Tax ({invoice.tax_rate}%):', f"${tax:.2f}"],
            ['Total:', f"${total:.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[1.5 * inch, 1 * inch], hAlign='RIGHT')
        
        totals_table.setStyle(TableStyle([

            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),

            ('TEXTCOLOR', (0, 0), (-1, 1), colors.HexColor('#4a5568')),

            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (-1, 2), 13),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#1a1a1a')),
            ('LINEABOVE', (0, 2), (-1, 2), 2, colors.HexColor('#4a5568')),
            ('TOPPADDING', (0, 2), (-1, 2), 10),
        ]))
        
        elements.append(totals_table)
        return elements
