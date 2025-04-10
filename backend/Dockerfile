FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt update && \
    apt install -y ffmpeg libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

RUN apt update

COPY . .

EXPOSE 4444

CMD ["python", "-u", "server.py"]
