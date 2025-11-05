from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os

# Register TTF fonts for Cyrillic support
base_dir = os.path.dirname(__file__)
font_path = os.path.join(base_dir, 'assets', 'fonts', 'DejaVuSans.ttf')
font_bold_path = os.path.join(base_dir, 'assets', 'fonts', 'DejaVuSans-Bold.ttf')

# Check if fonts exist and register them
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
    print(f"✓ Registered DejaVuSans from {font_path}")
else:
    print(f"⚠ Warning: Font file not found at {font_path}")

# Register bold font if available
if os.path.exists(font_bold_path):
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_bold_path))
    print(f"✓ Registered DejaVuSans-Bold from {font_bold_path}")
else:
    # Fallback: use regular font for bold if bold not available
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_path))
        print(f"⚠ Warning: Bold font not found, using regular font for bold text")

# Register font family for bold text support in Paragraph
if os.path.exists(font_path):
    pdfmetrics.registerFontFamily(
        'DejaVuSans',
        normal='DejaVuSans',
        bold='DejaVuSans-Bold'
    )

app = FastAPI(title="EAIP reports", version="0.1.0")

@app.get("/health")
def health():
    return {"service":"reports","status":"ok"}

class PassportReq(BaseModel):
    auditId: str
    summary: dict | None = None

def generate_pdf_content(req: PassportReq) -> bytes:
    """Генерирует PDF файл с энергетическим паспортом"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Create Unicode-enabled styles with DejaVuSans
    unicode_font_name = 'DejaVuSans'
    unicode_font_bold = 'DejaVuSans-Bold'
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=unicode_font_name,
        fontSize=18,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading2_style = ParagraphStyle(
        'UnicodeHeading2',
        parent=styles['Heading2'],
        fontName=unicode_font_name,
        fontSize=14,
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'UnicodeNormal',
        parent=styles['Normal'],
        fontName=unicode_font_name,
        fontSize=12
    )
    
    # Заголовок
    story.append(Paragraph("Энергетический паспорт", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Основная информация
    story.append(Paragraph(f"<b>Audit ID:</b> {req.auditId}", normal_style))
    story.append(Paragraph(f"<b>Версия:</b> v2.1", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Соответствие стандартам
    story.append(Paragraph("<b>Соответствие стандартам:</b>", heading2_style))
    compliance_list = ["Decree 690 (19.10.2024)", "ISO 50001:2018", "O'z DSt 1987:2010"]
    for comp in compliance_list:
        story.append(Paragraph(f"• {comp}", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Разделы
    story.append(Paragraph("<b>Разделы документа:</b>", heading2_style))
    sections = ["General", "Baseline", "Consumption", "Findings", "Measures", "KPIs"]
    for section in sections:
        story.append(Paragraph(f"• {section}", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Сводка
    if req.summary:
        story.append(Paragraph("<b>Сводка:</b>", heading2_style))
        summary_data = [
            ['Параметр', 'Значение'],
        ]
        if 'efficiency' in req.summary:
            summary_data.append(['Эффективность (%)', str(req.summary['efficiency'])])
        if 'savings_usd' in req.summary:
            summary_data.append(['Экономия (USD)', f"${req.summary['savings_usd']:,}"])
        
        if len(summary_data) > 1:
            table = Table(summary_data, colWidths=[8*cm, 6*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), unicode_font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

@app.post("/reports/passport")
async def generate_passport(req: PassportReq, request: Request):
    try:
        if not req.auditId or not req.auditId.strip():
            raise HTTPException(status_code=400, detail="auditId is required and cannot be empty")
        
        # Проверяем заголовок Accept или параметр format
        accept_header = request.headers.get("Accept", "")
        format_param = request.query_params.get("format", "")
        
        # Если запрашивается PDF
        if "application/pdf" in accept_header or format_param.lower() == "pdf":
            try:
                pdf_content = generate_pdf_content(req)
                if not pdf_content or len(pdf_content) == 0:
                    raise HTTPException(status_code=500, detail="PDF generation produced empty content")
                
                return Response(
                    content=pdf_content,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename=passport_{req.auditId}.pdf"
                    }
                )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
        
        # Иначе возвращаем JSON
        return {
            "auditId": req.auditId,
            "version": "v2.1",
            "compliance": ["Decree 690 (19.10.2024)", "ISO 50001:2018", "O'z DSt 1987:2010"],
            "sections": ["General", "Baseline", "Consumption", "Findings", "Measures", "KPIs"],
            "summary": req.summary or {}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
