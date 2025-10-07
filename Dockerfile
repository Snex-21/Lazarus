FROM jrottenberg/ffmpeg:6.0-ubuntu2204

ENV DEBIAN_FRONTEND=noninteractive

FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-dev build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /BOT

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ['python3', 'run.py']