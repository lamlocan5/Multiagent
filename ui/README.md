# Multiagent System UI

A modern React-based user interface for the Multiagent System.

## Features

- 🖥️ Clean, responsive interface
- 💬 Real-time chat with specialized agents
- 📊 Visual representation of agent selection process
- 📁 File upload for document processing, image analysis, and audio transcription
- 🔍 Knowledge base search and visualization
- 🌐 Vietnamese language support throughout the interface

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

1. Install dependencies:

```bash
npm install
```

2. Configure environment:

```bash
cp .env.example .env.local
```

Edit `.env.local` to set your API endpoint (default is `http://localhost:8000`).

### Development

Run the development server:

```bash
npm start
```

The app will be available at [http://localhost:3000](http://localhost:3000).

### Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `build/` directory.

## Architecture

The UI follows a modern React architecture:

- **React** for component-based UI
- **Material UI** for design system
- **React Query** for data fetching and caching
- **React Router** for navigation
- **Socket.io** for real-time communication

## Components

- `ChatInterface` - Main chat interface with agents
- `FileUploader` - Component for handling file uploads
- `AgentSelector` - Manual agent selection interface
- `KnowledgeExplorer` - Interface for exploring the knowledge base
- `SettingsPanel` - User preferences and API configuration
- `AudioRecorder` - Voice input component
- `VisualizationPanel` - Visualize agent reasoning process

## Integration with Backend

The UI communicates with the multiagent system backend through:

1. RESTful API calls for most operations
2. WebSocket connections for streaming responses
3. Server-sent events for notifications and updates

## Contributing

Please read our [Contributing Guide](../CONTRIBUTING.md) for details on the process for submitting pull requests.
