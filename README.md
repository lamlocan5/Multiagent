# Multiagent System

A sophisticated platform that coordinates specialized AI agents to solve complex tasks with enhanced capabilities for Vietnamese language processing.

## Overview

This multiagent system provides a flexible framework for developing, deploying, and orchestrating multiple specialized AI agents. By decomposing complex problems into domains handled by specialized agents, we achieve better results than using a single general-purpose agent.

### Key Features

- 🤖 **Multiple specialized agents** with different capabilities
- 🧠 **Intelligent task routing** to determine the best agent for each task
- 🔄 **Cross-agent coordination** for complex workflows
- 🌐 **Multi-modal processing** for text, audio, and vision
- 🇻🇳 **Vietnamese language optimization** for all components
- 🔍 **Advanced RAG** with hybrid vector/keyword search
- 🌐 **Web search and scraping** for real-time data access

### System Capabilities

- **Retrieval-Augmented Generation**: Combines semantic search with keyword-based retrieval
- **Advanced reasoning**: Chain-of-thought, Agent Chain, and Mixture of Experts paradigms
- **Vision processing**: OCR optimized for Vietnamese, visual question answering
- **Audio processing**: Speech-to-text and text-to-speech with Vietnamese voice support
- **Web integration**: Search, content extraction, and automated crawling
- **Data validation**: Schema-based validation with custom rules

## Architecture

The system is built with a modular architecture:
```bash
multiagent-system/
├── src/ # Source code
│ ├── agents/ # Agent implementations
│ ├── api/ # REST API endpoints
│ ├── audio/ # Audio processing components
│ ├── config/ # Configuration management
│ ├── core/ # Core shared components
│ ├── rag/ # Retrieval components
│ ├── utils/ # Utility functions
│ ├── vision/ # Vision processing components
│ └── web/ # Web search and scraping
├── logs/ # Log files
└── data/ # Vector databases and data files
```
See [architecture.md](docs/architecture.md) for detailed system design.

## Setup

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (for containerized deployment)
- API keys for external services (OpenAI, ElevenLabs, etc.)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/multiagent-system.git
cd multiagent-system
```

2. Set up environment variables:

```bash
cp .env.example .env
```

3. Install dependencies:

```bash
pip install -e .
```

### Running the System

#### Using Python directly:
```bash
python -m src.main
```

#### Using Docker:

```bash
docker-compose up -d
```


The API will be available at http://localhost:8000. API documentation is at http://localhost:8000/docs.

## Development

### Adding a New Agent

1. Create a new class in `src/agents/` that extends `BaseAgent`
2. Implement the required methods:
   - `process()` - Process a task
   - `get_suitability_score()` - Determine agent suitability
3. Register your agent with the coordinator

Example:

```python
from src.agents.base import BaseAgent
class CustomAgent(BaseAgent):
def init(self, llm):
super().init(
llm=llm,
name="Custom Agent",
description="Handles specific domain tasks"
)
async def process(self, task):
# Implementation here
return {"result": "Task completed"}
async def get_suitability_score(self, task):
return 0.8 if "relevant_keyword" in task["query"].lower() else 0.2
```


### Project Structure

- `src/agents/` - Agent implementations
- `src/api/` - API routes and middleware
- `src/audio/` - Audio processing components
- `src/config/` - Configuration management
- `src/core/` - Core models and exceptions
- `src/rag/` - Retrieval components
- `src/utils/` - Utility functions
- `src/vision/` - Vision processing components
- `src/web/` - Web search and scraping

## API Reference

The system exposes several API endpoints:

- `/api/agents` - Agent management and task execution
- `/api/rag` - Retrieval and knowledge base operations
- `/api/vision` - Image and OCR processing
- `/api/audio` - Speech-to-text and text-to-speech

For detailed API documentation, see the Swagger UI at `/docs` when running the server.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
