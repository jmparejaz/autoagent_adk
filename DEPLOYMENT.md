# Enterprise Agentic Platform

An AI Agent system built with Google Agent Development Kit (ADK) Python framework, featuring customizable branding, workflow orchestration, and a modern chat UI.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env and add your GOOGLE_API_KEY
nano .env

# 3. Build and run with Docker Compose
docker-compose up --build

# 4. Open http://localhost:8000
```

### Option 2: Local Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install and build frontend
cd frontend && npm install && npm run build && cd ..

# 4. Set environment variables
export GOOGLE_API_KEY="your-api-key"

# 5. Run the server
python run.py
```

## 🐳 Docker Commands

```bash
# Build the image
docker build -t agent-platform .

# Run with default settings
docker run -p 8000:8000 agent-platform

# Run with custom branding
docker run -p 8000:8000 \
  -e COMPANY_NAME="MyCompany" \
  -e PRIMARY_COLOR="#FF5500" \
  -e GOOGLE_API_KEY="your-key" \
  agent-platform

# Run with config file
docker run -p 8000:8000 \
  -v $(pwd)/my-config.yaml:/app/config.yaml \
  -e GOOGLE_API_KEY="your-key" \
  agent-platform
```

## ☁️ Cloud Deployment

### Google Cloud Run

```bash
# 1. Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/agent-platform

# 2. Deploy to Cloud Run
gcloud run deploy agent-platform \
  --image gcr.io/PROJECT_ID/agent-platform \
  --platform managed \
  --region us-central1 \
  --set-env-vars "GOOGLE_API_KEY=your-key,COMPANY_NAME=MyCompany"

# 3. Get the deployed URL
gcloud run services describe agent-platform --platform managed --region us-central1
```

### AWS ECS/Fargate

```bash
# 1. Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag agent-platform:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/agent-platform:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/agent-platform:latest

# 2. Create ECS task definition and service (via AWS Console or CLI)
```

### Azure Container Instances

```bash
# 1. Push to Azure Container Registry
az acr build --registry myregistry --image agent-platform .

# 2. Deploy to Container Instances
az container create \
  --resource-group myResourceGroup \
  --name agent-platform \
  --image myregistry.azurecr.io/agent-platform:latest \
  --dns-name-label my-agent-platform \
  --environment-variables GOOGLE_API_KEY=your-key
```

### DigitalOcean App Platform

```bash
# 1. Push to DigitalOcean Container Registry
doctl registry login
docker tag agent-platform:latest registry.digitalocean.com/myregistry/agent-platform:latest
docker push registry.digitalocean.com/myregistry/agent-platform:latest

# 2. Deploy via DigitalOcean App Platform dashboard or doctl
```

### Heroku Container Registry

```bash
# 1. Login to Heroku
heroku container:login

# 2. Push and release
heroku container:push web -a my-app-name
heroku container:release web -a my-app-name

# 3. Set environment variables
heroku config:set GOOGLE_API_KEY=your-key -a my-app-name
```

## 🎨 Customization

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COMPANY_NAME` | Company/project name | "Agent Platform" |
| `PROJECT_NAME` | Display name | "Enterprise Agentic Platform" |
| `PRIMARY_COLOR` | Primary brand color (hex) | #0066B3 |
| `SECONDARY_COLOR` | Secondary brand color (hex) | #1E3A8A |
| `ACCENT_COLOR` | Accent/highlight color (hex) | #0EA5E9 |
| `MASCOT_NAME` | Mascot character name | "Marina" |
| `GOOGLE_API_KEY` | Google Gemini API key | (required for LLM) |
| `MODEL_NAME` | Gemini model to use | gemini-2.0-flash |
| `SKILLS_DIR` | Skills directory path | .skills |
| `PORT` | Server port | 8000 |

### Custom Mascot

Replace the mascot SVG files in `frontend/public/mascot/`:
- `mascot-idle.svg` - Default state
- `mascot-thinking.svg` - Processing state
- `mascot-error.svg` - Error state

### Custom Logo

Replace `frontend/public/logo.svg` with your company logo.

## 📁 Project Structure

```
autoagent_adk/
├── backend/
│   ├── agents/          # ADK-style agents
│   ├── config/          # Configuration system
│   ├── workflows/       # Workflow definitions
│   ├── skills/          # Skill loader
│   └── main.py          # FastAPI app
├── frontend/
│   ├── src/components/  # React components
│   ├── src/styles/      # CSS styles
│   └── public/          # Static assets (logo, mascot)
├── .skills/             # Skill markdown files
├── config.yaml          # Default configuration
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose config
├── run.py               # CLI entry point
└── requirements.txt     # Python dependencies
```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve the web UI |
| GET | `/api/health` | Health check |
| GET | `/api/branding` | Get branding config |
| POST | `/api/chat` | Send message, get response |
| WS | `/ws/chat` | Real-time streaming chat |
| GET | `/api/workflows` | List available workflows |
| GET | `/api/skills` | List available skills |
| POST | `/api/skills/reload` | Hot-reload skills |

## 📝 Adding New Skills

Create a markdown file in `.skills/` directory:

```markdown
---
tool_name: my_custom_tool
description: Description of what this tool does
category: general
arguments:
  - name: input_param
    type: string
    description: Description of parameter
---

# Tool Implementation

This section contains the execution logic or API endpoint definition.
```

## 🛡️ Security Notes

- Never commit `.env` files with real API keys
- Use environment variables for secrets in production
- Consider adding authentication for production deployments
- Review CORS settings for your deployment environment

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Credits

- Built with [Google Agent Development Kit (ADK)](https://github.com/google/adk-python)
- Mascot "Marina" designed for the Marine Blue theme
