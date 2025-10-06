FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \ && apt-get install -y --no-install-recommends ffmpeg \ && apt-get clean \ && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./

RUN python -m pip install --upgrade pip \ && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ['python', '-u', 'run.py']