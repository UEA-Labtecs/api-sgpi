FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Copia e instala dependências Python primeiro (inclui playwright)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Agora que o comando "playwright" existe, pode instalar deps e navegadores
RUN playwright install-deps
RUN playwright install

# Copia o restante do código da aplicação
COPY . .

EXPOSE 8009

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8009"]
