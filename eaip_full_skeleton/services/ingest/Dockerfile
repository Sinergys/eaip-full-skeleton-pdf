FROM python:3.11-slim
WORKDIR /app

# Установка системных зависимостей для Tesseract OCR, pdf2image и Tabula (Java)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    poppler-utils \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8001","--proxy-headers"]
