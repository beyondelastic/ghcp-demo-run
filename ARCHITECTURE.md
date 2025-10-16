# Chainlit UI Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Web Browser                         │
│                    http://localhost:8000                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ HTTP/WebSocket
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      Chainlit Server                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              chainlit_app.py                         │  │
│  │                                                      │  │
│  │  @cl.on_chat_start   @cl.on_message   @cl.on_end   │  │
│  │       │                   │                │        │  │
│  └───────┼───────────────────┼────────────────┼────────┘  │
│          │                   │                │           │
│  ┌───────▼───────────────────▼────────────────▼────────┐  │
│  │          User Session Management                    │  │
│  │  (Each user gets isolated bot instance)            │  │
│  └───────────────────────┬─────────────────────────────┘  │
└──────────────────────────┼────────────────────────────────┘
                           │
                           │
┌──────────────────────────▼────────────────────────────────┐
│              AzureAIFoundryBot Class                      │
│                                                           │
│  ┌────────────────────┐  ┌────────────────────┐         │
│  │  Agent Management  │  │  Thread Management │         │
│  └──────────┬─────────┘  └──────────┬─────────┘         │
└─────────────┼────────────────────────┼───────────────────┘
              │                        │
              │                        │
              │    Azure SDK           │
              │                        │
┌─────────────▼────────────────────────▼───────────────────┐
│              Azure AI Foundry Service                    │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Agent   │  │  Thread  │  │   GPT-4  │             │
│  │ Instance │  │  Store   │  │   Model  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└──────────────────────────────────────────────────────────┘
```

## Message Flow

```
1. User sends message
   │
   ├─> Chainlit receives message
   │
   ├─> Routed to @cl.on_message handler
   │
   ├─> Retrieve bot instance from user session
   │
   ├─> bot.send_message(user_message)
   │   │
   │   ├─> Create message in Azure thread
   │   │
   │   ├─> Run agent on thread
   │   │
   │   ├─> Wait for completion (with backoff)
   │   │
   │   └─> Retrieve assistant response
   │
   ├─> Return response to Chainlit
   │
   └─> Display response in chat UI
```

## Session Lifecycle

```
New User Connection
   │
   ├─> @cl.on_chat_start triggered
   │
   ├─> Create AzureAIFoundryBot instance
   │   │
   │   ├─> Initialize Azure client
   │   │
   │   ├─> Create agent
   │   │
   │   └─> Create thread
   │
   ├─> Store bot in cl.user_session
   │
   └─> Send welcome message

User Active Session
   │
   ├─> Messages processed
   │
   ├─> Conversation maintained in thread
   │
   └─> Session active (timeout: 3600s)

User Disconnects / Timeout
   │
   ├─> @cl.on_chat_end triggered
   │
   ├─> Cleanup resources
   │
   └─> Session terminated
```

## Component Interaction

```
┌──────────────┐
│   Browser    │ User interacts with web interface
└───────┬──────┘
        │
        │ WebSocket
        ▼
┌──────────────┐
│   Chainlit   │ Manages UI, sessions, routing
└───────┬──────┘
        │
        │ Function calls
        ▼
┌──────────────┐
│  Bot Class   │ Business logic, Azure integration
└───────┬──────┘
        │
        │ SDK calls
        ▼
┌──────────────┐
│  Azure API   │ AI model processing
└──────────────┘
```

## File Organization

```
chainlit_app.py
├── AzureAIFoundryBot (Class)
│   ├── __init__()
│   ├── _initialize_agent_and_thread()
│   ├── send_message()
│   └── reset_conversation()
│
└── Chainlit Handlers
    ├── @cl.on_chat_start
    │   └── Initialize bot for new user
    │
    ├── @cl.on_message
    │   └── Process user messages
    │
    ├── @cl.action_callback("reset")
    │   └── Handle reset actions
    │
    └── @cl.on_chat_end
        └── Cleanup on disconnect
```

## Configuration Flow

```
.env
├── AZURE_AI_PROJECT_ENDPOINT
└── (Other Azure credentials via DefaultAzureCredential)
        │
        ├─> Loaded by load_dotenv()
        │
        └─> Used by AzureAIFoundryBot.__init__()

.chainlit
├── [UI]
│   ├── name
│   ├── description
│   └── theme
│
├── [features]
│   ├── file_upload
│   └── latex
│
└── [project]
    ├── session_timeout
    └── cache

chainlit.md
└── Welcome page content (Markdown)
```

## Data Flow

```
User Input → Chainlit → Bot → Azure → GPT-4 → Response
                ↓                               ↓
         Session Store                    Message Thread
              ↓                                 ↓
         Persistent                        Persistent
      (during session)                 (in Azure service)
```

## Error Handling

```
Try
├── Initialize bot
│   ├── Success → Welcome message
│   └── Failure → Error message
│
└── Process message
    ├── Success → Display response
    └── Failure → Error message

Errors Caught:
├── Authentication failures
├── Network issues
├── API errors
└── Runtime exceptions
```

## Deployment Options

```
Local Development
└── chainlit run chainlit_app.py

Production Server
├── chainlit run chainlit_app.py --host 0.0.0.0 --port 80
└── Or use WSGI server (Gunicorn, uWSGI)

Cloud Deployment
├── Azure App Service
├── AWS Elastic Beanstalk
├── Docker Container
└── Kubernetes Pod
```
