docker run -d \
  --name chess-mcp \
  --restart unless-stopped \
  -p 8000:8000 \
  chess-mcp