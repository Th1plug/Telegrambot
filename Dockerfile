# Gebruik officiële Python 3.11 image
FROM python:3.11

# Zet werkdirectory
WORKDIR /app

# Kopieer alle bestanden naar de container
COPY . .

# Installeer afhankelijkheden
RUN pip install -r requirements.txt

# Start de bot
CMD ["python", "main.py"]
