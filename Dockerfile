FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Depêndencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright (se realmente precisar nos testes)
RUN playwright install-deps && playwright install

# Código
COPY . .

# Entrypoint que roda Alembic e depois Uvicorn
RUN chmod +x /app/entrypoint.sh
EXPOSE 8009
ENTRYPOINT ["/app/entrypoint.sh"]
