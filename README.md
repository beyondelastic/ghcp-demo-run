# Azure AI Foundry Chat Bot

A simple Python chat bot that connects to Azure AI Foundry using the Azure AI Projects SDK. This bot uses agents, threads, and messages for conversational AI capabilities.

## Features

- 🤖 Interactive chat bot powered by Azure AI Foundry
- 🌐 Modern web interface with Chainlit (optional)
- 💻 Command-line interface for terminal users
- 🔐 Secure authentication using Azure DefaultAzureCredential
- 💬 Conversation management with threads and messages
- 📜 Conversation history tracking
- 🔄 Conversation reset functionality
- 📝 Comprehensive logging and error handling

## Prerequisites

- Python 3.8 or higher
- Azure AI Foundry project setup
- Azure authentication configured (Azure CLI, Managed Identity, or Service Principal)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd ghcp-demo-run
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Configure your Azure AI Foundry endpoint in the `.env` file:
```bash
AZURE_AI_PROJECT_ENDPOINT=https://your-project-name.your-region.ai.azure.com
```

4. Ensure you're authenticated with Azure:
```bash
# Using Azure CLI
az login

# Or set up service principal environment variables
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret
export AZURE_TENANT_ID=your-tenant-id
```

## Usage

### Option 1: Web Interface (Chainlit UI)

Run the chat bot with a modern web interface:
```bash
chainlit run chainlit_app.py
```

Then open your browser to `http://localhost:8000` to access the chat interface.

### Option 2: Command Line Interface

Run the chat bot in the terminal:
```bash
python main.py
```

### Commands

**Web Interface:**
- Type any message to chat with the bot
- Refresh the page to start a new conversation
- The conversation history is maintained during your session

**Command Line Interface:**
- Type any message to chat with the bot
- Type `quit` to exit the application
- Type `reset` to start a new conversation
- Type `history` to view the conversation history

## Project Structure

```
ghcp-demo-run/
├── main.py              # Command-line chat bot application
├── chainlit_app.py      # Chainlit web interface
├── chainlit.md          # Welcome page for Chainlit UI
├── .chainlit            # Chainlit configuration
├── QUICKSTART.md        # Quick start guide
├── CHAINLIT_GUIDE.md    # Detailed Chainlit documentation
├── requirements.txt     # Python dependencies
├── .env                 # Azure configuration (not committed to git)
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## Key Components

### AzureAIFoundryBot Class

The main chat bot class that handles:
- Azure AI Foundry client initialization
- Agent and thread management
- Message sending and receiving
- Conversation history tracking

### Authentication

This project uses `DefaultAzureCredential` which supports multiple authentication methods:
- Managed Identity (recommended for Azure-hosted applications)
- Azure CLI authentication
- Service Principal with client secret
- Interactive browser authentication

### Error Handling

The application includes comprehensive error handling:
- Connection failures
- Authentication errors
- API request failures
- Rate limiting and retry logic

## Configuration

The bot uses the following environment variables:

- `AZURE_AI_PROJECT_ENDPOINT`: Your Azure AI Foundry project endpoint (required)

## Security Best Practices

- ✅ Uses managed identity and secure credential flows
- ✅ No hardcoded credentials
- ✅ Environment-based configuration
- ✅ Proper error handling and logging
- ✅ Connection string format for endpoint configuration

## Documentation

- **QUICKSTART.md** - Get started quickly with simple step-by-step instructions
- **CHAINLIT_GUIDE.md** - Comprehensive guide to the Chainlit UI implementation
- **README.md** (this file) - Overview and general information

## Troubleshooting

### Authentication Issues
- Ensure you're logged in with `az login`
- Check that your Azure account has access to the AI Foundry project
- Verify the project endpoint URL is correct

### Connection Issues
- Confirm your Azure AI Foundry project is active
- Check network connectivity to Azure services
- Verify the model deployment name if specified

### Runtime Errors
- Check the logs for detailed error messages
- Ensure all required packages are installed
- Verify Python version compatibility (3.8+)

## License

This project is licensed under the MIT License.