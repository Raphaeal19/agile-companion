from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@app.get("/")
def read_root():
    return {
        "message": "AI Agile Companion API",
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
async def generate_documentation(request: TranscriptRequest):
    """
    Generate complete Agile documentation package from meeting transcript.
    
    Returns:
    - Product Backlog Items (with DoR checks)
    - Decision Log
    - Risk Register
    - Release Notes Draft
    """
    print(request)
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY not configured"
        )
    
    if not request.transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty"
        )
    
    try:
        model = genai.GenerativeModel(request.model_choice)
        
        # Enhanced prompt with explicit JSON structure

        prompt = f"""
        You are a Senior Technical Product Manager with expertise in Agile/Scrum methodology.
        Analyze the following meeting transcript and produce a formal Agile documentation package.

        CRITICAL INSTRUCTIONS:
        1. **Complexity (Not Points):** Do not assign Story Points. Instead, estimate T-Shirt size (XS, S, M, L, XL) based on implied complexity.
        2. **Definition of Ready:** If a requirement is vague or lacks detail, mark it as "Needs Refinement" and specify what information is missing.
        3. **Decisions:** Extract specific architectural, scope, or process decisions made during the meeting.
        4. **Risks & Assumptions:** Identify technical risks, dependencies, and assumptions that could impact delivery.
        5. **Release Notes:** Write value-focused, non-technical summaries suitable for stakeholders.
        6. **SCOPE SENTINEL:** Analyze for scope creep indicators including:
          - New features mentioned beyond original intent
          - Requirements that grew in complexity during discussion
          - Unclear boundaries that could expand later
          - Timeline pressure combined with feature additions
          - "Just one more thing" patterns
          - Technical debt being added

        TRANSCRIPT:
        {request.transcript}

        You MUST respond with ONLY valid JSON in this EXACT structure (no markdown, no explanations):

        {{
          "meeting_summary": "Brief 2-3 sentence summary of what was discussed",
          "backlog_items": [
            {{
              "id": "PBI-001",
              "title": "Short descriptive title",
              "user_story": "As a [user type], I want [goal], so that [benefit]",
              "priority": "Must Have",
              "complexity": "M",
              "definition_of_ready_status": "Ready for Sprint",
              "missing_info": "",
              "acceptance_criteria": [
                {{
                  "condition": "Specific testable condition",
                  "test_type": "Functional"
                }}
              ]
            }}
          ],
          "decision_log": [
            {{
              "topic": "Decision topic",
              "decision_made": "What was decided",
              "rationale": "Why this decision was made",
              "owner": "Person responsible"
            }}
          ],
          "risk_register": [
            {{  
              "category": "Risk",
              "description": "What could go wrong",
              "impact": "High",
              "mitigation_strategy": "How to address it"
            }}
          ],
          "release_notes_draft": [
            {{
              "feature_name": "Feature name",
              "value_statement": "Non-technical benefit to users",
              "audience": "External Customers"
            }}
          ],
          "scope_sentinel": {{
            "overall_risk": "Medium",
            "summary": "Brief assessment of scope health and creep indicators",
            "alerts": [
              {{
                "severity": "Medium",
                "category": "Feature Creep",
                "description": "What scope creep was detected",
                "quote": "Exact quote from transcript showing the issue",
                "recommendation": "How to address this",
                "impacted_items": ["PBI-001", "PBI-002"]
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

        Valid values:
        - priority: "Must Have", "Should Have", "Could Have", "Won't Have"
        - complexity: "XS", "S", "M", "L", "XL", "Needs Discussion"
        - definition_of_ready_status: "Ready for Sprint", "Needs Refinement"
        - test_type: "Functional", "UI/UX", "Security", "Performance", "Regression"
        - category (risk): "Risk", "Assumption", "Dependency"
        - impact: "High", "Medium", "Low"
        - audience: "Internal Users", "External Customers", "Admins", "Developers"
        - severity (scope): "Low", "Medium", "High", "Critical"
        - category (scope): "Feature Creep", "Scope Expansion", "Timeline Pressure", "Unclear Requirements", "Technical Debt", "Resource Constraint"
        - overall_risk: "Low", "Medium", "High", "Critical"

        RESPOND WITH ONLY THE JSON OBJECT, NO OTHER TEXT.
        """
        
        # Generate content
        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": 8192}
        )
        response_text = response.text.strip()
        
        # Clean up response (remove markdown code blocks if present)
        if response_text.startswith("```"):
            # Remove ```json or ``` markers
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])  # Remove first and last line
        
        # Parse JSON
        data = json.loads(response_text)
        
        # Validate with Pydantic
        documentation = DocumentationPackage(**data)
        
        return documentation
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse Gemini response as JSON. Response: {response_text[:200]}..."
        )
    except Exception as e:
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