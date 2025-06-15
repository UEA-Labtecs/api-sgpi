FROM python:3.12

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y wget libnss3 libatk-bridge2.0-0 libatk1.0-0 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 libxshmfence1 libgtk-3-0 libxss1 libx11-xcb1
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN playwright install chromium

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
