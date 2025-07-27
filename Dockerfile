FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    assimp-utils \
    libassimp-dev \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY kml_template.xml .

RUN mkdir -p /app/input /app/output
RUN chmod +x convert_obj_to_kmz.py

ENTRYPOINT ["python", "convert_obj_to_kmz.py"]