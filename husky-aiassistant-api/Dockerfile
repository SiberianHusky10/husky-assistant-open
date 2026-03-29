# FastAPI (husky-aiassistant-api)
FROM python:3.12-slim-bookworm

WORKDIR /app

# PyAudio 需要 portaudio；faster-whisper / edge-tts 常用 ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    ffmpeg \
    libsndfile1 \
    curl \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# 生产环境不要用 reload；密钥用 docker run -e 或 --env-file 注入，勿 COPY .env
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
