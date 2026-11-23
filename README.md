local-llm-toolkit
This repository contains scripts and configurations for working with AI language models locally. It is designed to simplify installing, running, and managing models such as llama.cpp and other AI projects on a local machine or in Docker containers.

✅ Key features
Scripts for installing dependencies and configuring environments.
Configurations for running language models on CPU/GPU (e.g., llama.cpp).
Guides for using local models with Docker or directly from the terminal.
Examples of interacting with models (e.g., generating text, tuning parameters, etc.).
🚀 Getting started
1. Requirements
Docker (optional, but recommended).
Python 3.8 or later.
A compatible language model (e.g., GGML for llama.cpp).
2. Clone the repository
Run
git clone https://github.com/your-user/local-llm-toolkit.git
cd local-llm-toolkit
3. Run with Docker (if applicable)
Make sure you have a docker-compose.yml file (e.g., for llama.cpp):

Apply
version: '3'
services:
  llama:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./models:/models
    environment:
      - MODEL_PATH=/models/model.bin
Start the container:
Run
docker compose up -d
Access the service at http://localhost:8080.
4. Run directly (without Docker)
Run scripts in the scripts/ directory to configure and start models.
Example: ./scripts/run_llama.sh --model models/model.bin
📁 Repository structure

Apply
local-llm-toolkit/
├── README.md          # This file
├── docker-compose.yml # Docker configuration (e.g., llama.cpp)
├── models/            # Directory for storing models (.bin, .ggml, etc.)
├── scripts/           # Scripts for running and managing models
│   ├── run_llama.sh
│   └── install_deps.sh
├── config/            # Custom configuration files
└── docs/              # Additional documentation (optional)
🛠️ Tips
Models: Download compatible models (e.g., from TheBloke) and place them in models/.
Performance: Use --threads to adjust the number of threads in scripts.
Logs: View Docker logs with docker logs -f llama.
Updates: If you modify the code, rebuild the image with docker compose build.
📚 Additional documentation
llama.cpp guide
Docker Compose documentation

♟️ Chess MCP server
The `chess-mcp/` server exposes seven tools: `list_skills`, `get_skill`, `render_board_image`, `pgn_to_position`, `play_moves`, `inspect_position`, and `stockfish_analyze`. `list_skills` returns the available skill names and descriptions; `get_skill` loads a skill's Markdown instructions. `inspect_position` combines validity, game status, material, and optionally legal moves and an ASCII board. `play_moves` applies a sequence in SAN or UCI and returns both notations. `stockfish_analyze` offers `evaluation`, `best_move`, and `variations` modes, with scores from White's and the side-to-move perspectives.

The server provides the `analyze_position` skill at `chess-mcp/skills/analyze_position.md`. For position analysis, evaluation, or move recommendations, the model should call the `get_skill` tool with `name="analyze_position"` and follow the returned workflow before using the chess tools. The server instructions describe the available skill and when to load it; the Markdown is bundled in the Docker image.

Analysis defaults to depth 12 and 2 seconds. You can adjust the depth (1-30) and time limit (0.1-10 seconds); `multipv` controls the number of variations (1-5). Analysis stops when either the depth or time limit is reached.

For questions about Stockfish evaluations, scores, advantages, best moves, or analysis, use `stockfish_analyze` with the appropriate mode. Position tools require a FEN or a sequence of moves that identifies the position.

To build, run, and stop the server, use `chess-mcp/build.sh`, `chess-mcp/run.sh`, and `chess-mcp/stop.sh`. `run.sh` connects the container to the Docker network `searxng_default`, allowing Open WebUI to resolve it as `chess-mcp:8000`; the network must already exist. If the container is running, the script connects it to the network if needed; if it is stopped, the script replaces it with a container created from the current image. For direct execution, install `chess-mcp/requirements.txt` and run `python chess-mcp/server.py`.

🤝 Contributions
Improvements, scripts, and fixes are welcome! Fork the repository and create a PR.

📌 License
This project is licensed under the MIT License. Modify it to suit your needs.