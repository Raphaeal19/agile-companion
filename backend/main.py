from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
from collections import defaultdict
from models import (
    TranscriptRequest, 
    DocumentationPackage, 
    HealthResponse
)

load_dotenv()

app = FastAPI(
    title="AI Agile Companion API",
    description="Generates Agile documentation from meeting transcripts",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://agile-companion-ebon.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting for demo mode
demo_usage = defaultdict(list)
DEMO_LIMIT = 5
DEMO_WINDOW = 3600

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# Configure API key ONCE at startup
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not set!")

def check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded demo rate limit"""
    if not DEMO_MODE:
        return True
    
    now = datetime.now()
    cutoff = now - timedelta(seconds=DEMO_WINDOW)
    
    demo_usage[client_ip] = [
        timestamp for timestamp in demo_usage[client_ip]
        if timestamp > cutoff
    ]
    
    if len(demo_usage[client_ip]) >= DEMO_LIMIT:
        return False
    
    demo_usage[client_ip].append(now)
    return True

@app.get("/")
def read_root():
    return {
        "message": "AI Agile Companion API",
        "demo_mode": DEMO_MODE,
        "endpoints": {
            "/health": "Health check",
            "/api/generate": "Generate documentation from transcript"
        }
    }

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        gemini_configured=bool(GEMINI_API_KEY),
        available_models=["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"]
    )

@app.post("/api/generate", response_model=DocumentationPackage)
async def generate_documentation(request: TranscriptRequest, req: Request):
    """
    Generate complete Agile documentation package from meeting transcript.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Service temporarily unavailable. API key not configured."
        )
    
    # Check rate limit
    client_ip = req.client.host
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail=f"Demo mode: Rate limit exceeded. You can make {DEMO_LIMIT} requests per hour."
        )
    
    if not request.transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty"
        )
    
    try:
        # Create model
        model = genai.GenerativeModel(request.model_choice)
        
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 8192,
        }
        
        prompt = f"""
You are a Senior Technical Product Manager with expertise in Agile/Scrum methodology.
Analyze the following meeting transcript and produce a formal Agile documentation package.

CRITICAL INSTRUCTIONS:
1. **Complexity:** Estimate T-Shirt size (XS, S, M, L, XL) based on implied complexity.
2. **Definition of Ready:** If vague, mark as "Needs Refinement" with missing info.
3. **Decisions:** Extract key architectural/scope decisions.
4. **Risks:** Identify technical risks and dependencies.
5. **Release Notes:** Write concise, non-technical summaries.
6. **SCOPE SENTINEL:** Flag scope creep indicators.

TRANSCRIPT:
{request.transcript}

Respond with ONLY valid JSON (no markdown):

{{
  "meeting_summary": "2-3 sentence summary",
  "backlog_items": [
    {{
      "id": "PBI-001",
      "title": "Short title",
      "user_story": "As a [user], I want [goal], so that [benefit]",
      "priority": "Must Have",
      "complexity": "M",
      "definition_of_ready_status": "Ready for Sprint",
      "missing_info": "",
      "acceptance_criteria": [
        {{"condition": "Testable condition", "test_type": "Functional"}}
      ]
    }}
  ],
  "decision_log": [
    {{"topic": "Topic", "decision_made": "Decision", "rationale": "Why", "owner": "Who"}}
  ],
  "risk_register": [
    {{"category": "Risk", "description": "Description", "impact": "High", "mitigation_strategy": "How to address"}}
  ],
  "release_notes_draft": [
    {{"feature_name": "Feature", "value_statement": "User benefit", "audience": "External Customers"}}
  ],
  "scope_sentinel": {{
    "overall_risk": "Medium",
    "summary": "Brief scope assessment (1-2 sentences)",
    "alerts": [
      {{
        "severity": "Medium",
        "category": "Feature Creep",
        "description": "Brief description",
        "quote": "Brief quote (max 20 words)",
        "recommendation": "Brief recommendation",
        "impacted_items": ["PBI-001"]
      }}
    ],
    "metrics": {{
      "features_discussed": 5,
      "new_items_added": 2,
      "complexity_increases": 1,
      "unclear_requirements": 3
    }}
  }}
}}

RULES:
- Keep quotes under 20 words
- Maximum 5 backlog items
- Maximum 3 acceptance criteria per item
- Maximum 3 scope alerts
- Be concise but complete

Valid values:
- priority: "Must Have", "Should Have", "Could Have", "Won't Have"
- complexity: "XS", "S", "M", "L", "XL", "Needs Discussion"
- definition_of_ready_status: "Ready for Sprint", "Needs Refinement"
- test_type: "Functional", "UI/UX", "Security", "Performance", "Regression"
- category (risk): "Risk", "Assumption", "Dependency"
- impact: "High", "Medium", "Low"
- audience: "Internal Users", "External Customers", "Admins", "Developers"
- severity: "Low", "Medium", "High", "Critical"
- category (scope): "Feature Creep", "Scope Expansion", "Timeline Pressure", "Unclear Requirements", "Technical Debt", "Resource Constraint"
- overall_risk: "Low", "Medium", "High", "Critical"
"""
        
        # Generate content
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()
        
        # Clean up response
        if response_text.startswith("```"):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])
        
        # Parse JSON
        data = json.loads(response_text)
        
        # Validate with Pydantic
        documentation = DocumentationPackage(**data)
        
        return documentation
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse response. Please try again."
        )
    except Exception as e:
        # Log the full error for debugging
        print(f"Error generating documentation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating documentation: {str(e)}"
        )

@app.get("/api/stats")
async def get_statistics():
    """
    Future endpoint for analytics/metrics
    """
    return {
        "total_sessions": 0,
        "items_generated": 0,
        "avg_items_per_session": 0
    }
