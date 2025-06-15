# ✅ Imagem base com Python
FROM python:3.12-slim

# ✅ Diretório de trabalho dentro do container
WORKDIR /app

# ✅ Instala dependências do sistema necessárias para Playwright e pandas/openpyxl
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libxss1 \
    libgbm1 \
    libpango-1.0-0 \
    libx11-xcb1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ✅ Copia os arquivos do projeto para o container
COPY . /app

# ✅ Atualiza pip
RUN pip install --upgrade pip

# ✅ Instala dependências Python
RUN pip install -r requirements.txt

# ✅ Instala navegador do Playwright (Chromium)
RUN playwright install --with-deps chromium

# ✅ Expõe a porta da API
EXPOSE 8000

# ✅ Comando para rodar a API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
