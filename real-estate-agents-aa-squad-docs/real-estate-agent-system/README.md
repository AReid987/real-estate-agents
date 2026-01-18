# Real Estate Agent Marketing System

A comprehensive AI-powered marketing automation system for real estate agents, built with AG2 (Autogen) multi-agent architecture, Langflow workflows, and modern web technologies.

## 🏗️ Architecture Overview

This system uses a multi-agent architecture to automate real estate marketing tasks:

- **AG2 Multi-Agent Core**: Orchestrates specialized agents for different tasks
- **Langflow**: Visual workflow engine for content optimization
- **API Gateway**: FastAPI-based REST API with authentication
- **Frontend Dashboard**: Next.js React application for agent interaction
- **Database**: PostgreSQL with vector search capabilities
- **Deployment**: Docker Compose with Dagger CI/CD

## 🤖 Agent Responsibilities

### Core Agents
- **Listing Agent**: Scrapes property listings from various sources
- **Content Agent**: Generates marketing content using AI
- **Social Media Agent**: Manages posting to Facebook, Instagram, LinkedIn
- **User Proxy Agent**: Handles human-in-the-loop approval workflows
- **Notification Agent**: Sends notifications via email, SMS, and push

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd real-estate-agent-system

# Copy environment variables
cp .env.example .env

# Edit .env file with your API keys
nano .env
```

### 2. Required API Keys

Add these to your `.env` file:

```bash
# AI Services
OPENAI_API_KEY=your_openai_api_key
PORTKEY_API_KEY=your_portkey_api_key  # Optional: for LLM cost optimization
PORTKEY_VIRTUAL_KEY=your_portkey_virtual_key

# Social Media APIs
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret

# Security
JWT_SECRET=generate_a_strong_random_string_here
NEXTAUTH_SECRET=generate_another_strong_random_string
```

### 3. Start the System

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Access the Applications

- **Frontend Dashboard**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **AG2 Core**: http://localhost:8001
- **Langflow**: http://localhost:7860
- **Grafana Monitoring**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

## 📊 System Components

### AG2 Multi-Agent Core (Port 8001)
- Orchestrates all AI agents
- Handles content generation and approval workflows
- Manages listing scraping and processing

### API Gateway (Port 8000)
- RESTful API for frontend communication
- JWT-based authentication
- Request routing to AG2 core

### Frontend Dashboard (Port 3000)
- Agent interface for content review and approval
- Listing management and social media account setup
- Real-time notifications and system monitoring

### Langflow (Port 7860)
- Visual workflow designer
- Content optimization pipelines
- AI model orchestration

## 🔧 Development

### Running Individual Services

```bash
# AG2 Core only
cd agents
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# API Gateway only
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend only
cd frontend
npm install
npm run dev
```

### Database Management

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d real_estate_agents

# View logs
docker-compose logs postgres
docker-compose logs ag2-core
docker-compose logs api-gateway
```

## 🎯 Key Features

### MVP Features
- ✅ Property listing scraping from holidaybuilders.com
- ✅ AI-powered content generation (social media posts, flyers)
- ✅ Human-in-the-loop approval workflows
- ✅ Multi-platform social media posting
- ✅ Real-time notifications and monitoring

### Post-MVP Features
- 📋 Lead generation and nurturing
- 📋 Advanced analytics and reporting
- 📋 CRM integration
- 📋 Email marketing campaigns
- 📋 Advanced social media engagement

## 🔒 Security

- JWT-based authentication
- Encrypted social media tokens
- Environment-based configuration
- CORS protection
- Input validation and sanitization

## 📈 Monitoring

The system includes comprehensive monitoring:

- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Structured Logging**: Centralized logging with structlog
- **Health Checks**: Service availability monitoring

## 🛠️ Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yml
2. **Database connection**: Ensure PostgreSQL is running
3. **API key errors**: Verify all required keys in .env
4. **Memory issues**: Increase Docker memory allocation

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f ag2-core
docker-compose logs -f api-gateway
docker-compose logs -f frontend
```

## 📚 API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Open an issue with detailed information

## 🔄 System Flow

1. **Listing Agent** scrapes new properties
2. **Content Agent** generates marketing content
3. **User Proxy Agent** requests human approval
4. **Social Media Agent** posts approved content
5. **Notification Agent** keeps agents informed

This creates a fully automated marketing pipeline with human oversight.