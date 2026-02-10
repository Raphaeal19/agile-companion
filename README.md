# AI Agile Companion

Transform meeting transcripts into structured Agile documentation using Google Gemini AI.

**Live Demo:** https://agile-companion-ebon.vercel.app

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Local Development](#local-development)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Design Decisions](#design-decisions)
- [Production Considerations](#production-considerations)

---

## Overview

AI Agile Companion is an intelligent documentation generator designed for product teams. It analyzes meeting transcripts and automatically produces Agile artifacts including product backlog items, decision logs, risk registers, and release notes. The application uses Google Gemini AI to understand context, extract requirements, and format them according to Agile best practices.

**Problem Solved:** Teams spend significant time manually converting meeting discussions into structured documentation. This tool automates the process, ensuring consistency and saving hours of work per sprint.

---

## Features

### Product Backlog Generation
- Converts natural language requirements into properly formatted user stories
- Follows standard format: "As a [user type], I want [goal], so that [benefit]"
- Generates specific, testable acceptance criteria
- Categorizes by test type: Functional, UI/UX, Security, Performance, Regression

### Definition of Ready Checks
- Automatically evaluates if requirements are sprint-ready
- Identifies missing information and unclear boundaries
- Provides specific recommendations for refinement
- Prevents incomplete stories from entering sprints

### T-Shirt Sizing Complexity Estimation
- Estimates complexity using T-shirt sizes: XS, S, M, L, XL
- Follows Agile best practice: BA estimates complexity, developers assign story points
- Based on implied scope, dependencies, and technical considerations

### Decision Logging
- Extracts architectural and scope decisions from conversations
- Captures decision rationale and ownership
- Creates traceable decision history for future reference

### Risk Management
- Identifies technical risks, assumptions, and dependencies
- Assesses impact levels: High, Medium, Low
- Provides mitigation strategies for each identified risk

### Scope Sentinel - Scope Creep Detection
- Analyzes conversations for scope creep indicators
- Detects: feature creep, unclear requirements, timeline pressure, technical debt
- Provides severity levels and specific recommendations
- Shows quantitative metrics: features discussed, new items added, complexity increases

### Release Notes Generation
- Creates stakeholder-friendly feature descriptions
- Tailored for different audiences: Internal Users, External Customers, Admins, Developers
- Non-technical, value-focused language

---

## Technology Stack

### Backend
- **FastAPI** - High-performance async API framework
- **Python 3.11+** - Primary programming language
- **Pydantic** - Data validation and settings management
- **Google Generative AI (Gemini)** - Large language model integration
- **Python-dotenv** - Environment variable management

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and development server
- **Lucide React** - Icon library
- **CSS3** - Styling with custom properties

### Deployment
- **Railway** - Backend hosting
- **Vercel** - Frontend hosting
- **Git** - Version control
- **GitHub** - Code repository

---

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │────────>│   FastAPI    │────────>│   Gemini    │
│  Frontend   │  HTTPS  │   Backend    │   API   │     AI      │
│  (Vercel)   │<────────│  (Railway)   │<────────│   (Google)  │
└─────────────┘         └──────────────┘         └─────────────┘
```

### Request Flow

1. User pastes meeting transcript into React frontend
2. Frontend sends POST request to FastAPI backend
3. Backend constructs structured prompt for Gemini AI
4. Gemini analyzes transcript and generates JSON response
5. Backend validates response with Pydantic models
6. Frontend receives structured documentation and renders UI

### Key Design Patterns

**Model-View-Controller (MVC)**
- Models: Pydantic schemas define data structure
- Views: React components handle presentation
- Controller: FastAPI endpoints orchestrate business logic

**Separation of Concerns**
- Frontend handles only UI/UX
- Backend handles AI integration and validation
- Clear API contract between layers

**Type Safety**
- Pydantic models enforce type checking on backend
- Literal types ensure valid enum values
- Runtime validation prevents invalid data

---

## Getting Started

### Prerequisites

- **Python 3.11 or 3.12** (Python 3.14 not yet supported by dependencies)
- **Node.js 18+**
- **Git**
- **Google Gemini API Key** - Get one at https://aistudio.google.com/app/api-keys

### Quick Start

**1. Clone the repository**

```bash
git clone https://github.com/Raphaeal19/ai-agile-companion.git
cd ai-agile-companion
```

**2. Backend Setup**

```bash
cd backend

# Create virtual environment (use Python 3.11 or 3.12)
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
echo "GEMINI_API_KEY=your_api_key_here" > .env
echo "DEMO_MODE=true" >> .env
```

**3. Frontend Setup**

```bash
cd ../frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000" > .env.development
```

**4. Run the Application**

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**5. Access the Application**

Open http://localhost:5173 in your browser.

---

## Local Development

### Backend Development

**Running the server:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

The API will be available at http://localhost:8000


**Testing endpoints:**
```bash
# Health check
curl http://localhost:8000/health

# Generate documentation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "PM: We need a login feature. Dev: Should we support OAuth?",
    "model_choice": "gemini-2.5-flash"
  }'
```

### Frontend Development

**Running the dev server:**
```bash
cd frontend
npm run dev
```

The application will be available at http://localhost:5173 with hot module replacement.

**Building for production:**
```bash
npm run build
```

**Preview production build:**
```bash
npm run preview
```

---

## API Documentation

### Endpoints

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "gemini_configured": true,
  "available_models": ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"]
}
```

#### POST /api/generate

Generate Agile documentation from meeting transcript.

**Request:**
```json
{
  "transcript": "Meeting transcript text here...",
  "model_choice": "gemini-2.5-flash"
}
```

**Response:**
```json
{
  "meeting_summary": "Brief 2-3 sentence summary",
  "backlog_items": [
    {
      "id": "PBI-001",
      "title": "User Authentication",
      "user_story": "As a user, I want to log in securely, so that I can access my account",
      "priority": "Must Have",
      "complexity": "M",
      "definition_of_ready_status": "Ready for Sprint",
      "missing_info": "",
      "acceptance_criteria": [
        {
          "condition": "User can log in with email and password",
          "test_type": "Functional"
        }
      ]
    }
  ],
  "decision_log": [...],
  "risk_register": [...],
  "release_notes_draft": [...],
  "scope_sentinel": {
    "overall_risk": "Medium",
    "summary": "Assessment of scope health",
    "alerts": [...],
    "metrics": {
      "features_discussed": 5,
      "new_items_added": 2,
      "complexity_increases": 1,
      "unclear_requirements": 3
    }
  }
}
```

**Valid Values:**

- `model_choice`: "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"
- `priority`: "Must Have", "Should Have", "Could Have", "Won't Have"
- `complexity`: "XS", "S", "M", "L", "XL", "Needs Discussion"
- `definition_of_ready_status`: "Ready for Sprint", "Needs Refinement"
- `test_type`: "Functional", "UI/UX", "Security", "Performance", "Regression"

#### GET /api/stats

Get usage statistics (future endpoint).

**Response:**
```json
{
  "total_sessions": 0,
  "items_generated": 0,
  "avg_items_per_session": 0
}
```

---

## Project Structure

```
ai-agile-companion/
├── backend/
│   ├── main.py              # FastAPI application and endpoints
│   ├── models.py            # Pydantic data models
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables (not in git)
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── App.css          # Application styles
│   │   └── main.jsx         # React entry point
│   ├── public/
│   ├── index.html
│   ├── package.json         # Node dependencies
│   ├── vite.config.js       # Vite configuration
│   └── .gitignore
├── .gitignore
└── README.md
```

### Key Files Explained

**backend/main.py**
- FastAPI application initialization
- CORS middleware configuration
- API endpoints implementation
- Rate limiting logic for demo mode
- Gemini AI integration

**backend/models.py**
- Pydantic models for request/response validation
- Type definitions for all data structures
- Business logic constraints (Literal types for enums)

**frontend/src/App.jsx**
- Main React component
- State management for UI
- API integration logic
- Tab-based navigation
- Error handling

**frontend/src/App.css**
- Custom CSS properties for theming
- Responsive layout styles
- Component-specific styles
- Animation keyframes

---

## Configuration

### Backend Environment Variables

Create `backend/.env`:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
DEMO_MODE=true  # Enable rate limiting for public demo
```

### Frontend Environment Variables

**Development (.env.development):**
```bash
VITE_API_URL=http://localhost:8000
```

**Production (Vercel Environment Variables):**
```bash
VITE_API_URL=https://your-backend.up.railway.app
```

### Rate Limiting Configuration

In `backend/main.py`:

```python
DEMO_LIMIT = 5  # Requests per hour in demo mode
DEMO_WINDOW = 3600  # Time window in seconds
```

---

## Usage Examples

### Example 1: Basic Login Feature

**Input Transcript:**
```
PM: We need a user login feature.
Dev: Should we support OAuth?
PM: Yes, Google and GitHub. Also email/password.
Tech Lead: We need rate limiting for security.
```

**Generated Output:**
- User Story: "As a user, I want to log in to the application, so that I can securely access my account"
- Complexity: M
- Definition of Ready: Needs Refinement
- Missing Info: "Password policy, session duration, UI mockups"
- Acceptance Criteria: 3-5 testable conditions
- Decision Log: "Support OAuth (Google, GitHub) + email/password"
- Risk: "Security vulnerabilities in authentication" (High Impact)

### Example 2: Scope Creep Detection

**Input Transcript:**
```
PM: Let's add tagging to notes.
Dev: Simple tags?
PM: Yeah. Oh, and while we're at it, let's add folders too.
PM: And maybe categories.
Dev: That's getting complex...
```

**Scope Sentinel Output:**
- Overall Risk: High
- Alert: "Feature Creep detected - Original requirement (tagging) expanded to include folders and categories"
- Quote: "while we're at it, let's add folders too"
- Recommendation: "Break into separate stories and prioritize core tagging first"
- Metrics: features_discussed=3, new_items_added=2

---

## Design Decisions

### Why FastAPI?

**Chosen for:**
- Async support for handling multiple concurrent requests
- Automatic API documentation generation
- Fast performance (comparable to Node.js and Go)
- Type hints and Pydantic integration
- Easy deployment

**Alternative considered:** Flask (rejected due to lack of native async support)

### Why Pydantic for Validation?

**Chosen for:**
- Runtime type checking and validation
- Clear error messages for invalid data
- Automatic JSON schema generation
- Integration with FastAPI
- Type safety without additional libraries

**Benefit:** Prevents invalid data from Gemini AI from reaching the frontend

### Why React with Vite?

**Chosen for:**
- Fast development server with hot module replacement
- Modern build tooling
- Smaller bundle sizes than Create React App
- Better developer experience

**Alternative considered:** Next.js (rejected as unnecessary for this SPA)

### Why Separate Backend/Frontend?

**Reasoning:**
- **Scalability:** Can scale services independently
- **Flexibility:** Can swap frontend framework without touching backend
- **Clear separation:** API can be reused by mobile apps, CLI tools, etc.
- **Deployment:** Deploy to different platforms optimized for each layer

### T-Shirt Sizing vs Story Points

**Decision:** Use T-shirt sizing for complexity estimation.

**Reasoning:**
- Story points are assigned by development team, not BAs/PMs
- T-shirt sizing represents complexity, which BAs can estimate
- Follows Agile best practice: separate estimation concerns
- Less prone to misinterpretation ("5 points" means different things to different teams)

### Scope Sentinel Design

**Decision:** Analyze for scope creep in real-time during documentation generation.

**Reasoning:**
- Catches scope creep early before it impacts sprints
- Provides actionable recommendations
- Quantitative metrics help PMs make data-driven decisions
- Shows exact quotes for transparency

---


## License

MIT License - see LICENSE file for details

## Author

**Ayush Pathak**

---

**Built for Agile teams to streamline documentation and focus on delivery.**