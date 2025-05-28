FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg aria2

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt yt-dlp

COPY . .

CMD ["python3", "bot.py"]
