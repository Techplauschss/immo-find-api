FROM python:3.9-slim

# Install Chrome und notwendige Dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Setze Arbeitsverzeichnis
WORKDIR /app

# Kopiere Requirements und installiere sie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest der Anwendung
COPY . .

# Setze Umgebungsvariable für Chrome
ENV CHROME_PATH=/usr/bin/chromium

# Port freigeben
EXPOSE 8000

# Starte die Anwendung
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
