# Quick Start Guide

## Running the Chainlit Web UI

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Azure

Create a `.env` file in the project root:

```bash
AZURE_AI_PROJECT_ENDPOINT=https://your-project-name.your-region.ai.azure.com
```

### 3. Authenticate with Azure

```bash
az login
```

### 4. Start the Chainlit Server

```bash
chainlit run chainlit_app.py
```

### 5. Open Your Browser

Navigate to: `http://localhost:8000`

That's it! You're ready to chat with your Azure AI Foundry agent through the web interface. 🎉

---

## Alternative: Command Line Interface

If you prefer the terminal:

```bash
python main.py
```

---

## Troubleshooting

**Port already in use?**
```bash
chainlit run chainlit_app.py --port 8080
```

**Need help?** Check `CHAINLIT_GUIDE.md` for detailed documentation.
