# Chainlit UI Guide

This guide provides detailed information about the Chainlit web interface for the Azure AI Foundry Chat Bot.

## What is Chainlit?

Chainlit is a Python framework for building conversational AI applications with a modern web interface. It provides:
- Real-time chat UI
- Session management
- Easy integration with AI models
- Customizable themes and configurations

## Getting Started

### Installation

The Chainlit dependency is included in `requirements.txt`. Install it along with other dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application

Start the Chainlit server:

```bash
chainlit run chainlit_app.py
```

The application will be available at `http://localhost:8000`

### Custom Port

To run on a different port:

```bash
chainlit run chainlit_app.py --port 8080
```

### Production Deployment

For production deployment with auto-reload disabled:

```bash
chainlit run chainlit_app.py --host 0.0.0.0 --port 80
```

## Features

### User Sessions

Each user gets their own isolated chat session with a dedicated:
- Azure AI Foundry bot instance
- Conversation thread
- Message history

### Session Management

- **New Session**: Automatically created when a user connects
- **Session Timeout**: Sessions expire after 1 hour of inactivity (configurable in `.chainlit`)
- **Session Cleanup**: Resources are cleaned up when sessions end

### Error Handling

The application includes comprehensive error handling:
- Azure authentication errors
- API connection failures
- Message processing errors
- Graceful degradation with user-friendly error messages

## Customization

### Configuration File

The `.chainlit` file contains all configuration options:

```toml
[UI]
name = "Azure AI Foundry Chat Bot"
description = "Chat with your Azure AI Foundry agent"
```

### Welcome Page

Edit `chainlit.md` to customize the welcome page shown to users.

### Styling

You can customize the UI theme in `.chainlit`:

```toml
[UI.theme.light.primary]
main = "#F80061"
```

## Architecture

### Components

1. **AzureAIFoundryBot Class**: Core bot logic (reused from main.py)
   - Azure AI client initialization
   - Agent and thread management
   - Message processing

2. **Chainlit Decorators**:
   - `@cl.on_chat_start`: Initialize bot when user connects
   - `@cl.on_message`: Handle incoming messages
   - `@cl.on_chat_end`: Cleanup when session ends

3. **Session Storage**: User-specific bot instances stored in Chainlit sessions

### Flow

1. User opens browser → `@cl.on_chat_start` triggered
2. Bot instance created and stored in session
3. User sends message → `@cl.on_message` triggered
4. Message processed by Azure AI agent
5. Response displayed in chat interface
6. Session ends → `@cl.on_chat_end` triggered

## Troubleshooting

### Port Already in Use

If port 8000 is in use:
```bash
chainlit run chainlit_app.py --port 8001
```

### Azure Authentication Issues

Ensure you're authenticated:
```bash
az login
```

Check your `.env` file has the correct endpoint:
```
AZURE_AI_PROJECT_ENDPOINT=https://your-project.region.ai.azure.com
```

### Module Not Found Error

Install all dependencies:
```bash
pip install -r requirements.txt
```

### Session Lost

If sessions disconnect frequently, increase the timeout in `.chainlit`:
```toml
session_timeout = 7200  # 2 hours
```

## Development Tips

### Hot Reload

Chainlit supports hot reload during development. Changes to `chainlit_app.py` will automatically reload the application.

### Debugging

Enable debug mode:
```bash
chainlit run chainlit_app.py --debug
```

### Logs

Check logs for detailed information:
- Application logs: Console output
- Chainlit logs: `.chainlit/` directory

## Security Considerations

- Environment variables are not exposed to the client
- Each user has an isolated session
- Azure credentials use secure DefaultAzureCredential flow
- No hardcoded secrets in the code

## Comparison with CLI

| Feature | CLI (main.py) | Web UI (chainlit_app.py) |
|---------|---------------|--------------------------|
| Interface | Terminal | Web Browser |
| Multiple Users | No | Yes (concurrent) |
| History Command | Yes | Automatic |
| Reset Command | Manual | Refresh page |
| Accessibility | Limited | Better (GUI) |
| Deployment | Local only | Can be hosted |

## Next Steps

- Customize the UI theme in `.chainlit`
- Add file upload capabilities
- Implement conversation persistence
- Deploy to a cloud platform (Azure, AWS, etc.)
- Add authentication and authorization
- Integrate with additional Azure services

## Resources

- [Chainlit Documentation](https://docs.chainlit.io/)
- [Azure AI Projects SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)
- [Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-studio/)
