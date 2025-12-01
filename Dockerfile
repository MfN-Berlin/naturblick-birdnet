FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ADD https://zenodo.org/records/17631020/files/BirdNET+_V3.0-preview2_EUNA_1K_FP32.pt?download=1 /app/

ADD https://zenodo.org/records/17631020/files/BirdNET+_V3.0-preview2_EUNA_1K_Labels.csv?download=1 /app/

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "--preload", "app:app"]

EXPOSE 8080
