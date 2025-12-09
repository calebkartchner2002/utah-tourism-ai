# Utah Tourism AI

An AI-powered Utah tourism recommendation system that demonstrates Docker's AI capabilities, including **Docker Model Runner** for local LLM hosting and **MCP Gateway** for tool integration.

![Docker AI](https://img.shields.io/badge/Docker-AI-blue) ![Llama 3.2](https://img.shields.io/badge/LLM-Llama%203.2-green) ![MCP](https://img.shields.io/badge/Protocol-MCP-orange)

## Features

- **Local LLM** - Runs Llama 3.2 via Docker Model Runner (no API keys needed)
- **MCP Integration** - Connects to external tools via Docker MCP Gateway for real-time weather and web search
- **Utah Expertise** - Comprehensive knowledge of Utah's Mighty Five national parks
- **Modern UI** - Responsive web interface with Tailwind CSS
- **PostgreSQL Database** - Stores recommendation history
- **Single Compose File** - Everything orchestrated with Docker Compose

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         Docker Compose                           │
│  ┌──────────────┐  ┌───────────┐  ┌──────────────┐  ┌────────┐  │
│  │ Utah Tourism │  │    MCP    │  │ Docker Model │  │ Postgres│  │
│  │     App      │──│  Gateway  │  │   Runner     │  │   DB   │  │
│  │  (FastAPI)   │  │           │  │ (Llama 3.2)  │  │        │  │
│  └──────┬───────┘  └─────┬─────┘  └──────┬───────┘  └────┬───┘  │
│         │                │                │               │      │
│         └────────────────┴────────────────┴───────────────┘      │
└──────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- **Docker Desktop 4.40+** with Docker Model Runner enabled
- **Docker Compose v2.38+** (for `models` top-level element support)
- At least **8GB RAM** (16GB recommended for better model performance)
- GPU recommended but not required (Apple Silicon, NVIDIA)

### Enable Docker Model Runner

1. Open Docker Desktop
2. Go to **Settings** → **Features in development**
3. Enable **Docker Model Runner**
4. Apply & Restart

## Quick Start

### 1. Clone or Download

```bash
git clone <repository-url>
cd utah-tourism-ai
```

### 2. Start the Application

```bash
docker compose up
```

The first run will:
- Pull the Llama 3.2 model (~2-4GB depending on quantization)
- Build the application container
- Start the MCP Gateway

### 3. Access the Application

Open [http://localhost:8080](http://localhost:8080) in your browser.

## Usage

1. **Enter your interests** - Hiking, photography, skiing, etc.
2. **Set your parameters** - Duration, season, activity level
3. **Generate recommendations** - AI creates personalized itineraries with real-time weather and search data
4. **View history** - Browse past recommendations at `/history`

## Project Structure

```
utah-tourism-ai/
├── compose.yaml              # Docker Compose configuration
├── Dockerfile                # Application container definition
├── pyproject.toml            # Python dependencies
├── src/
│   ├── main.py              # FastAPI application with endpoints
│   ├── llm_client.py        # Docker Model Runner client
│   ├── mcp_client.py        # MCP Gateway client (weather, search)
│   ├── utah_data.py         # Utah destination data
│   └── database.py          # PostgreSQL database models
└── templates/
    ├── index.html           # Main page
    ├── recommendation.html  # Results page
    └── history.html         # Recommendation history
```

## Configuration

### Docker Compose (compose.yaml)

The compose file defines four main services:

```yaml
services:
  utah-tourism-app:     # FastAPI web application
  mcp-gateway:          # MCP Gateway for tools (weather, search)
  db:                   # PostgreSQL database

models:
  llm:                  # Local LLM via Docker Model Runner
    model: ai/llama3.2
```

### Available Models

You can change the model in `compose.yaml`:

| Model | Size | RAM Required | Best For |
|-------|------|--------------|----------|
| `ai/smollm2` | ~270MB | 2GB | Testing, fast responses |
| `ai/llama3.2` | ~2GB | 4GB | Balanced performance |
| `ai/llama3.3` | ~4GB | 8GB | Better quality |
| `ai/gemma3` | ~3GB | 6GB | Good reasoning |

### MCP Servers

The MCP Gateway connects to:
- **duckduckgo** - Web search for travel recommendations
- **openweather** - Real-time weather data for Utah cities

Additional servers available at [Docker Hub MCP](https://hub.docker.com/search?q=mcp)

## Development

### Run Locally Without Docker

```bash
# Install dependencies
pip install uv
uv pip install -e .

# Set environment variables
export LLM_API_URL="http://localhost:12434/engines/llama.cpp/v1"
export LLM_MODEL_NAME="ai/llama3.2"
export MCP_GATEWAY_ENDPOINT="http://localhost:8811/sse"

# Run the model separately
docker model run ai/llama3.2

# Start the app
uvicorn src.main:app --reload --port 8080
```

### Run with Docker Offload

For GPU-accelerated cloud execution:

```bash
# Start Docker Offload
docker offload start

# Run the application
docker compose up
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/health` | GET | Health check |
| `/recommend` | POST | Generate recommendation (HTML) |
| `/api/recommend` | POST | Generate recommendation (JSON) |
| `/api/destinations` | GET | List all destinations |
| `/history` | GET | View recommendation history |
| `/api/recommendations` | GET | Get recommendations as JSON |
| `/api/recommendations/{id}` | GET | Get specific recommendation |
| `/api/tools` | GET | List available MCP tools |

### Example API Usage

```bash
curl -X POST http://localhost:8080/api/recommend \
  -F "interests=hiking and photography" \
  -F "duration=1 week" \
  -F "season=fall" \
  -F "activity_level=moderate"
```

## Troubleshooting

### Model Won't Load

```bash
# Check if Docker Model Runner is enabled
docker model ls

# Manually pull the model
docker model pull ai/llama3.2
```

### MCP Gateway Connection Failed

The application will work without MCP Gateway (search features disabled). Check:

```bash
# Verify gateway is running
docker compose logs mcp-gateway
```

### Slow Responses

- Use a smaller model like `ai/smollm2` for faster responses
- Reduce `context_size` in compose.yaml
- Enable GPU acceleration if available

### Database Connection Issues

Check that PostgreSQL is running:
```bash
docker compose logs db
```

## License

MIT License - feel free to use this as a template for your own projects!

## Acknowledgments

- [Docker Model Runner](https://docs.docker.com/ai/model-runner/) - Local LLM hosting
- [Docker MCP Gateway](https://docs.docker.com/ai/mcp-gateway/) - Tool integration
- [Meta Llama](https://llama.meta.com/) - Open-source LLM
- [Visit Utah](https://www.visitutah.com/) - Destination information

---

Built with ❤️ using Docker AI features
