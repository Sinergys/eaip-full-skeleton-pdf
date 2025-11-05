# PDF Generation with Cyrillic Support

## Overview

The reports service generates PDF documents with full support for Cyrillic characters (Russian, Ukrainian, etc.) using the DejaVuSans TTF font.

## Architecture

### Font Registration

Fonts are registered when the Python module loads:

```python
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

font_path = os.path.join(os.path.dirname(__file__), 'assets', 'fonts', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
```

### Font Family Setup

For bold text support, a font family is registered:

```python
pdfmetrics.registerFontFamily(
    'DejaVuSans',
    normal='DejaVuSans',
    bold='DejaVuSans-Bold'  # Falls back to regular if not available
)
```

## Usage

### API Endpoint

```http
POST /reports/passport?format=pdf
Accept: application/pdf
Content-Type: application/json

{
  "auditId": "demo-1",
  "summary": {
    "efficiency": 92,
    "savings_usd": 2400
  }
}
```

### Response

Returns a PDF file with:
- Valid PDF headers (`%PDF-1.x`)
- Cyrillic text rendered correctly
- Formatted tables and sections
- Bold text support

## Troubleshooting

### Cyrillic Not Displaying

1. Check font file exists:
   ```bash
   docker compose exec reports ls -la /app/assets/fonts/
   ```

2. Check font registration in logs:
   ```bash
   docker compose logs reports | grep -i font
   ```

3. Verify font is registered:
   ```bash
   docker compose exec reports python -c "from reportlab.pdfbase import pdfmetrics; print('DejaVuSans' in pdfmetrics.getRegisteredFontNames())"
   ```

### Connection Refused

The demo script includes automatic port readiness check. If issues persist:

1. Verify service is running:
   ```bash
   docker compose ps reports
   ```

2. Check service logs:
   ```bash
   docker compose logs reports
   ```

3. Test port manually:
   ```powershell
   Test-NetConnection -ComputerName 127.0.0.1 -Port 8005
   ```

## Technical Details

### Supported Characters

- Cyrillic (Russian, Ukrainian, Belarusian, etc.)
- Latin characters
- Numbers and symbols
- Special characters (Unicode)

### Font Files

- `DejaVuSans.ttf` - Regular font (required)
- `DejaVuSans-Bold.ttf` - Bold font (optional, falls back to regular)

### Dependencies

- `reportlab==4.2.5` - PDF generation library
- TTF font support via `reportlab.pdfbase.ttfonts`

## References

- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [DejaVu Fonts](https://dejavu-fonts.github.io/)

