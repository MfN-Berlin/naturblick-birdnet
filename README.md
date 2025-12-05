# naturblick-birdnet
This is a simple HTTP wrapper around BirdNET to allow it to be run inside a docker as an HTTP server.

## Run locally
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
gunicorn --preload app:app
``` 

## Usage

`GET /?url=<soundfile URL>&start=<start in milliseconds>&end=<end in milliseconds>`
