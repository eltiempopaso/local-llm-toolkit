
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    stockfish \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY server.py fen_tools.py .

ENV STOCKFISH_PATH=/usr/games/stockfish

EXPOSE 8000

CMD ["python", "server.py"]
