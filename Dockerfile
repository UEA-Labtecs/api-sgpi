FROM python:3.12-slim

# Instalações necessárias para o Playwright funcionar
RUN apt-get update && apt-get install -y wget curl unzip fonts-liberation \
    libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxrandr2 libgbm1 libgtk-3-0

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install

WORKDIR /app
COPY . .

EXPOSE 8009
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8009"]
