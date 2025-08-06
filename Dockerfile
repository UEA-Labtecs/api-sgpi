FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Instala dependências de sistema
RUN playwright install-deps

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala navegadores (Chromium, Firefox, WebKit)
RUN playwright install

COPY . .

EXPOSE 8009

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8009"]
