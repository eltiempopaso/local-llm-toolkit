local-llm-toolkit
Este repositorio contiene scripts y configuraciones para trabajar con modelos de lenguaje de inteligencia artificial en entornos locales. Está diseñado para facilitar la instalación, ejecución y gestión de modelos como llama.cpp o otros proyectos de IA en una máquina local o en contenedores Docker.

✅ Características principales
Scripts para instalar dependencias y configurar entornos.
Configuraciones para ejecutar modelos de lenguaje en CPU/GPU (ej: llama.cpp).
Guías para usar modelos locales con Docker o directamente en la terminal.
Ejemplos de cómo interactuar con modelos (ej: generar texto, ajustar parámetros, etc.).
🚀 Comenzando
1. Requisitos
Docker (opcional, pero recomendado).
Python 3.8 o superior.
Un modelo de lenguaje compatible (ej: ggml para llama.cpp).
2. Clonar el repositorio
Run
git clone https://github.com/tu-usuario/local-llm-toolkit.git
cd local-llm-toolkit
3. Ejecutar con Docker (si aplica)
Asegúrate de tener un archivo docker-compose.yml (ej: para llama.cpp):

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
Inicia el contenedor:
Run
docker compose up -d
Accede al servicio en http://localhost:8080.
4. Uso directo (sin Docker)
Ejecuta scripts en la carpeta scripts/ para configurar y correr modelos.
Ejemplo: ./scripts/run_llama.sh --model models/model.bin
📁 Estructura del repositorio

Apply
local-llm-toolkit/
├── README.md          # Este archivo
├── docker-compose.yml # Configuración para Docker (ej: llama.cpp)
├── models/            # Directorio para almacenar modelos (.bin, .ggml, etc.)
├── scripts/           # Scripts para ejecutar y gestionar modelos
│   ├── run_llama.sh
│   └── install_deps.sh
├── config/            # Archivos de configuración personalizados
└── docs/              # Documentación adicional (opcional)
🛠️ Consejos útiles
Modelos: Descarga modelos compatibles (ej: desde TheBloke) y colócalos en models/.
Rendimiento: Usa --threads para ajustar el número de hilos en scripts.
Logs: Revisa logs de Docker con docker logs -f llama.
Actualizaciones: Si modificas el código, reconstruye la imagen con docker compose build.
📚 Documentación adicional
Guía de llama.cpp
Docker Compose docs

♟️ Servidor MCP de ajedrez
El servidor de `chess-mcp/` expone herramientas para generar una imagen del tablero y gestionar posiciones FEN con `python-chess`: convertir PGN a FEN, aplicar jugadas SAN, validar posiciones, consultar jugadas legales, convertir SAN/UCI, revisar el estado de la partida, mostrar el tablero ASCII, resumir posiciones, contar material y listar capturas. Las tools `analyze_position`, `best_move` y `evaluate_position` usan Stockfish y devuelven evaluación desde la perspectiva de blancas y del turno actual; `analyze_position` también devuelve variantes principales en SAN y UCI.

El análisis está limitado por defecto a profundidad 12 y 2 segundos. Se puede ajustar la profundidad (1-30) y el tiempo máximo (0,1-10 segundos); en `analyze_position`, `multipv` controla el número de variantes (1-5). El análisis se detiene al alcanzar primero el límite de profundidad o de tiempo.

Si se pregunta por la evaluación, puntuación o ventaja según Stockfish, el servidor instruye al modelo para que use `stockfish_evaluation` (también está disponible `evaluate_position`). Para la mejor jugada, usa `best_move`; para varias líneas o variantes, `analyze_position`. Estas herramientas requieren un FEN o una secuencia de jugadas que identifique la posición.

Para construir, ejecutar y detener el servidor, usa los scripts `chess-mcp/build.sh`, `chess-mcp/run.sh` y `chess-mcp/stop.sh`. `run.sh` conecta el contenedor a la red Docker `searxng_default` para que Open WebUI pueda resolverlo por el nombre `chess-mcp:8000`; esa red debe existir previamente. Si el contenedor ya está en ejecución, el script lo conecta a la red si hace falta; si está detenido, lo reemplaza por uno creado desde la imagen actual. En una ejecución directa, instala `chess-mcp/requirements.txt` y ejecuta `python chess-mcp/server.py`.

🤝 Contribuciones
¡Cualquier mejora, script o corrección es bienvenida! Fork el repositorio y crea un PR.

📌 Licencia
Este proyecto está bajo la licencia MIT. Modifica según tus necesidades.