FROM python:3.13

WORKDIR /app

ADD https://zenodo.org/records/17631020/files/BirdNET+_V3.0-preview2_EUNA_1K_FP32.pt?download=1 /app/

ADD https://zenodo.org/records/17631020/files/BirdNET+_V3.0-preview2_EUNA_1K_Labels.csv?download=1 /app/

ADD https://naturblick.museumfuernaturkunde.berlin/media/audio_files/amphibian_d52fd27a_06b4d9c428.mp3 /app/

RUN apt update && apt install -y ffmpeg

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8080", "--preload", "app:app"]

EXPOSE 8080
