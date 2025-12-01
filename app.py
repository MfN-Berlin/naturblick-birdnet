import io
import torch
import librosa
from urllib import request
from urllib import parse
import csv
import json
import numpy as np

SR = 32000

device = torch.device("cpu")
model = torch.jit.load("BirdNET+_V3.0-preview2_EUNA_1K_FP32.pt", map_location=device)
model.eval()
labels = []
with open("BirdNET+_V3.0-preview2_EUNA_1K_Labels.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=";")
    next(reader) # Skip header
    for row in reader:
        labels.append(int(row[0].strip()))

def run_inference(url, start, end):
    y, _ = librosa.load(io.BytesIO(request.urlopen(url).read()), sr=SR, mono=True, offset=float(start) / 1000.0, duration = float(end - start) / 1000.0)
    chunks = np.stack([y], axis=0)
    with torch.inference_mode():
        x = torch.from_numpy(chunks).to(device)
        return model(x)[1][0].detach().cpu().numpy().astype(float)
        
def app(environ, start_response):
    status = '200 OK'
    params = dict(parse.parse_qsl(environ["QUERY_STRING"]))
    start = int(params["start"])
    end = int(params["end"])
    url = params["url"]
    result = run_inference(url, start, end)
    results_with_labels = sorted(zip(labels, result), key = lambda r: r[1], reverse = True)
    data = json.dumps([{"id": id, "score": e} for id, e in results_with_labels[:3]]).encode("UTF-8")
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return iter([data])
