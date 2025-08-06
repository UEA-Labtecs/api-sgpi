FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Atualiza pip, setuptools, wheel e certifi para evitar problemas de SSL
RUN pip install --upgrade pip setuptools wheel certifi

# Copia apenas requirements.txt primeiro para usar cache de dependências
COPY requirements.txt .

# Usa trusted-hosts para contornar problemas com SSL
RUN pip install --no-cache-dir -r requirements.txt \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org

# Copia o restante do código
COPY . .

EXPOSE 8009

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8009"]
