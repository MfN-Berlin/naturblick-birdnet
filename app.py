import io
import torch
import librosa
from urllib import request
from urllib import parse
import csv
import json
import numpy as np
import time
import logging

logger = logging.getLogger("gunicorn.error")

SR = 32000

# Create device and load model
device = torch.device("cpu")
model_version = "BirdNET+_V3.0-preview2_EUNA_1K_FP32"
model = torch.jit.load(f"{model_version}.pt", map_location=device)
model.eval()

# Load labels
labels = []
with open("BirdNET+_V3.0-preview2_EUNA_1K_Labels.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=";")
    next(reader) # Skip header
    for row in reader:
        labels.append(int(row[0].strip()))

# Warm up librosa, initial call can be _very_ slow
warmup_time = time.perf_counter()
librosa.load("amphibian_d52fd27a_06b4d9c428.mp3")
logger.info(f"Finished warm-up: {time.perf_counter() - warmup_time}")

def download_audio(url):
    return io.BytesIO(request.urlopen(url).read())

def decode_audio(encoded, start, end):
    return librosa.load(encoded, sr=SR, mono=True, offset=float(start) / 1000.0, duration = float(end - start) / 1000.0)[0]

def run_inference(audio):
    chunks = np.stack([audio], axis=0)
    with torch.inference_mode():
        x = torch.from_numpy(chunks).to(device)
        return model(x)[1][0].detach().cpu().numpy().astype(float)
        
def app(environ, start_response):
    status = '200 OK'
    params = dict(parse.parse_qsl(environ["QUERY_STRING"]))
    start = int(params["start"])
    end = int(params["end"])
    url = params["url"]
    download_time = time.perf_counter()
    encoded = download_audio(url)
    decode_time = time.perf_counter()
    decoded = decode_audio(encoded, start, end)
    model_time = time.perf_counter()
    result = run_inference(decoded)
    finish_time = time.perf_counter()
    logger.info(f"URL: {url} start: {start} end: {end} download: {decode_time - download_time:.3f}s decode: {model_time - decode_time:.3f}s model: {finish_time - model_time:.3f}s")
    results_with_labels = sorted(zip(labels, result), key = lambda r: r[1], reverse = True)
    data = json.dumps({"version": model_version, "results": [{"id": id, "score": e} for id, e in results_with_labels[:3]]}).encode("UTF-8")
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return iter([data])
