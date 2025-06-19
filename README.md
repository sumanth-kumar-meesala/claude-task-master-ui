# Project Overview Agent

A sophisticated multi-agent AI system that transforms basic project ideas into comprehensive project overviews, complete with detailed file structures, technical specifications, and implementation roadmaps. Built with Google Gemini AI, FastAPI, and React.

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (Required for backend)
- **Node.js 18+** (Required for frontend)
- **Google Gemini API Key** (Required for AI functionality)

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env file and add your configuration:
# GEMINI_API_KEY=your_gemini_api_key_here
# DEBUG=True
# SECRET_KEY=your-secret-key
# TINYDB_PATH=../data
# CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Start the FastAPI development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
project-overview-agent/
├── backend/                           # FastAPI Backend Application
│   ├── app/
│   │   ├── api/v1/                   # API Routes (v1)
│   │   │   ├── router.py             # Main API router
│   │   │   ├── chat.py               # Chat/conversation endpoints
│   │   │   ├── enhanced_projects.py  # Enhanced project management
│   │   │   ├── file_management.py    # File operations
│   │   │   ├── project_files.py      # Project file handling
│   │   │   └── task_generation.py    # Task generation endpoints
│   │   ├── core/                     # Core Configuration
│   │   │   ├── config.py             # Application settings
│   │   │   └── exceptions.py         # Custom exceptions
│   │   ├── database/                 # Database Layer
│   │   │   ├── tinydb_handler.py     # TinyDB operations
│   │   │   └── schemas.py            # Database schemas
│   │   ├── models/                   # Data Models
│   │   │   ├── schemas.py            # Pydantic models
│   │   │   └── responses.py          # API response models
│   │   ├── services/                 # Business Logic
│   │   │   ├── project_overview_generator.py  # Project generation
│   │   │   └── task_master_service.py         # Task management
│   │   ├── utils/                    # Utility Functions
│   │   └── main.py                   # FastAPI application entry
│   ├── requirements.txt              # Python dependencies
│   ├── pyproject.toml               # Python project configuration
│   └── package.json                 # Node.js dependencies (for some tools)
├── frontend/                         # React + TypeScript Frontend
│   ├── src/
│   │   ├── components/              # React Components
│   │   │   ├── ui/                  # UI components
│   │   │   ├── projects/            # Project-related components
│   │   │   ├── chat/                # Chat interface components
│   │   │   ├── navigation/          # Navigation components
│   │   │   └── layouts/             # Layout components
│   │   ├── pages/                   # Page Components
│   │   │   ├── HomePage.tsx         # Landing page
│   │   │   ├── ProjectsPage.tsx     # Projects listing
│   │   │   ├── ProjectDetailPage.tsx # Project details
│   │   │   └── DashboardPage.tsx    # Main dashboard
│   │   ├── services/                # API Services
│   │   │   ├── api.ts               # Base API configuration
│   │   │   ├── projects.ts          # Project API calls
│   │   │   ├── health.ts            # Health check service
│   │   │   └── chat.ts              # Chat API calls
│   │   ├── types/                   # TypeScript Types
│   │   ├── utils/                   # Utility Functions
│   │   ├── hooks/                   # Custom React Hooks
│   │   ├── store/                   # State Management
│   │   └── router/                  # React Router Configuration
│   ├── package.json                 # Frontend dependencies
│   ├── vite.config.ts              # Vite configuration
│   ├── tailwind.config.js          # Tailwind CSS configuration
│   └── tsconfig.json               # TypeScript configuration
├── data/                            # TinyDB JSON Database Files
│   ├── projects.json                # Project data
│   ├── orchestration_sessions.json # Session data
│   ├── project_files.json          # Generated project files
│   ├── project_structure.json      # Project structures
│   ├── templates.json              # Project templates
│   ├── task_definitions.json       # Task definitions
│   └── generated_files.json        # Generated file metadata
└── README.md                       # Project documentation
```

## ✅ Implemented Features

### Backend (FastAPI)
- ✅ **FastAPI Application** with CORS and security middleware
- ✅ **TinyDB Database** with JSON-based storage and schema validation
- ✅ **Environment Configuration** using Pydantic Settings
- ✅ **Comprehensive API Endpoints**:
  - Health check and status endpoints
  - Project CRUD operations
  - File management and generation
  - Task generation and management
  - Chat/conversation interfaces
- ✅ **Error Handling** with custom exceptions and logging
- ✅ **Data Models** with Pydantic validation
- ✅ **Project Overview Generation** service
- ✅ **Task Master Integration** for automated task creation
- ✅ **File Structure Generation** and management

### Frontend (React + TypeScript)
- ✅ **Modern React 19** with TypeScript and Vite
- ✅ **Tailwind CSS + DaisyUI** for responsive design
- ✅ **React Router** for navigation and routing
- ✅ **State Management** with Zustand
- ✅ **API Integration** with Axios and React Query
- ✅ **Component Library**:
  - Project creation and management
  - File structure visualization
  - Chat interfaces
  - Dashboard and navigation
- ✅ **Form Handling** with React Hook Form and Zod validation
- ✅ **Toast Notifications** for user feedback
- ✅ **Responsive Design** with mobile-first approach

### Infrastructure & DevOps
- ✅ **Development Environment** with hot reload
- ✅ **Database Initialization** with automatic schema setup
- ✅ **CORS Configuration** for seamless frontend-backend communication
- ✅ **Code Quality Tools**:
  - ESLint and Prettier for frontend
  - Black and isort for backend
  - TypeScript strict mode
- ✅ **Build Configuration** for production deployment

## 🔄 Roadmap & Next Steps

### Phase 2: AI Agent Enhancement
- [ ] **CrewAI Integration** - Multi-agent orchestration framework
- [ ] **Advanced Gemini Features** - Function calling and structured outputs
- [ ] **Agent Collaboration** - Specialized agents for different project aspects
- [ ] **Prompt Engineering** - Optimized prompts for better outputs
- [ ] **Real-time Streaming** - Live updates during generation

### Phase 3: Advanced Features
- [ ] **Project Templates** - Pre-built templates for common project types
- [ ] **Export Capabilities** - Export to GitHub, ZIP files, or other formats
- [ ] **Version Control** - Track project evolution and changes
- [ ] **Collaboration Tools** - Multi-user project editing
- [ ] **Integration APIs** - Connect with external development tools

### Phase 4: Enterprise Features
- [ ] **User Authentication** - Secure user accounts and sessions
- [ ] **Team Management** - Organization and team-based access
- [ ] **Analytics Dashboard** - Project insights and usage metrics
- [ ] **API Rate Limiting** - Production-ready API management
- [ ] **Cloud Deployment** - Scalable cloud infrastructure

## 🛠 Technology Stack

### Backend Technologies
- **FastAPI** `0.104.1+` - High-performance async Python web framework
- **TinyDB** `4.8.0+` - Lightweight JSON-based document database
- **Google Gemini AI** `0.3.2+` - Advanced AI/LLM integration for content generation
- **Pydantic** `2.5.0+` - Data validation and settings management
- **Uvicorn** - ASGI server for production deployment
- **Python-dotenv** - Environment variable management
- **JSONSchema** - Database schema validation
- **PyYAML** - YAML configuration support

### Frontend Technologies
- **React** `19.1.0` - Modern UI framework with latest features
- **TypeScript** `5.8.3` - Static type checking and enhanced developer experience
- **Vite** `6.3.5` - Lightning-fast build tool and development server
- **Tailwind CSS** `4.1.10` - Utility-first CSS framework
- **DaisyUI** `5.0.43` - Beautiful component library for Tailwind
- **React Router** `7.6.2` - Client-side routing
- **React Query** `5.80.7` - Server state management and caching
- **Zustand** `5.0.5` - Lightweight state management
- **React Hook Form** `7.57.0` - Performant form handling
- **Zod** `3.25.64` - TypeScript-first schema validation
- **Axios** `1.9.0` - Promise-based HTTP client

### Development Tools
- **ESLint** - Code linting and quality enforcement
- **Prettier** - Code formatting
- **Black & isort** - Python code formatting
- **MyPy** - Python static type checking
- **Pytest** - Python testing framework

## 📊 Current Status

**Phase 1 Complete: Production-Ready Foundation ✅**

### Backend Status: ✅ Fully Operational
- **API Server**: Running on port 8000 with comprehensive endpoints
- **Database**: TinyDB with full CRUD operations and schema validation
- **AI Integration**: Google Gemini API ready for content generation
- **Health Monitoring**: Comprehensive health checks and error handling
- **CORS**: Properly configured for frontend communication
- **Documentation**: Auto-generated API docs available at `/docs`

### Frontend Status: ✅ Production Ready
- **Development Server**: Running on port 5173 with hot reload
- **UI Framework**: Complete component library with responsive design
- **State Management**: Integrated with backend APIs and local state
- **Routing**: Multi-page application with protected routes
- **Form Handling**: Robust form validation and submission
- **Error Handling**: User-friendly error messages and loading states

### Integration Status: ✅ Seamless Communication
- **API Communication**: Axios-based service layer with error handling
- **Real-time Updates**: React Query for efficient data fetching
- **Type Safety**: End-to-end TypeScript integration
- **Development Experience**: Hot reload, linting, and formatting configured

### Next Priorities
1. **Enhanced AI Features**: Advanced Gemini integration with function calling
2. **Multi-Agent System**: CrewAI implementation for specialized agents
3. **Advanced UI**: File tree visualization and real-time collaboration
4. **Production Deployment**: Docker containerization and cloud deployment

## 🔧 Development Commands

### Backend Commands
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run development server (alternative)
python app/main.py

# Install development dependencies
pip install -r requirements.txt

# Format code
black . && isort .

# Type checking
mypy app/

# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/
```

### Frontend Commands
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format

# Check formatting
npm run format:check

# Type checking
npm run type-check
```

### Full Stack Development
```bash
# Start both backend and frontend (requires two terminals)

# Terminal 1 - Backend
cd backend && python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev
```

## 📝 Environment Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory with the following configuration:

```env
# Application Settings
DEBUG=True
APP_VERSION=0.1.0
SECRET_KEY=your-super-secret-key-here

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
TINYDB_PATH=../data

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Logging Configuration
LOG_LEVEL=INFO
```

### Getting Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `.env` file

### Frontend Environment Variables (Optional)

Create a `.env` file in the `frontend/` directory if needed:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1

# Development Configuration
VITE_DEV_MODE=true
```

### Environment File Security

⚠️ **Important**: Never commit `.env` files to version control. They are already included in `.gitignore`.

## 🚀 Production Deployment

### Backend Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment variables
export DEBUG=False
export GEMINI_API_KEY=your_production_key

# Run with production ASGI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Serve static files (example with serve)
npx serve -s dist -l 3000
```

## 🧪 Testing

### Backend Testing
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py
```

### Frontend Testing
```bash
cd frontend

# Run unit tests (when implemented)
npm test

# Run e2e tests (when implemented)
npm run test:e2e
```

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check if Python 3.11+ is installed: `python --version`
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is available: `lsof -i :8000`
- Verify environment variables are set correctly

**Frontend won't start:**
- Check if Node.js 18+ is installed: `node --version`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check if port 5173 is available
- Verify backend is running and accessible

**API connection issues:**
- Check CORS configuration in backend `.env`
- Verify backend health endpoint: `curl http://localhost:8000/health`
- Check browser console for network errors

## 🤝 Contributing

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch**: `git checkout -b feature/amazing-feature`
4. **Make your changes** following the coding standards
5. **Run tests** to ensure everything works
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to your branch**: `git push origin feature/amazing-feature`
8. **Submit a pull request** with a clear description

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful language model capabilities
- **FastAPI** for the excellent Python web framework
- **React Team** for the amazing frontend framework
- **Tailwind CSS** for the utility-first CSS framework
- **Open Source Community** for the incredible tools and libraries
