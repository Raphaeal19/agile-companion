from pydantic import BaseModel, Field
from typing import List, Literal

class AcceptanceCriteria(BaseModel):
    condition: str = Field(..., description="The condition that must be met.")
    test_type: Literal["Functional", "UI/UX", "Security", "Performance", "Regression"]

class BacklogItem(BaseModel):
    id: str = Field(..., description="ID like PBI-001")
    title: str = Field(..., description="Short title of the item")
    user_story: str = Field(..., description="As a X, I want Y, so that Z")
    priority: Literal["Must Have", "Should Have", "Could Have", "Won't Have"]
    complexity: Literal["XS", "S", "M", "L", "XL", "Needs Discussion"] = Field(
        ..., description="Estimated T-shirt size complexity."
    )
    definition_of_ready_status: Literal["Ready for Sprint", "Needs Refinement"] = Field(
        ..., description="Is this story clear enough to start work?"
    )
    missing_info: str = Field(
        ..., description="If not ready, list what is missing. If ready, return an empty string."
    )
    acceptance_criteria: List[AcceptanceCriteria]

class DecisionNote(BaseModel):
    topic: str
    decision_made: str
    rationale: str
    owner: str = Field(..., description="Who made or owns this decision?")

class RiskAssumption(BaseModel):
    category: Literal["Risk", "Assumption", "Dependency"]
    description: str
    impact: Literal["High", "Medium", "Low"]
    mitigation_strategy: str

class ReleaseNoteEntry(BaseModel):
    feature_name: str
    value_statement: str = Field(
        ..., description="Non-technical explanation of value for end-users."
    )
    audience: Literal["Internal Users", "External Customers", "Admins", "Developers"]

class ScopeAlert(BaseModel):
    severity: Literal["Low", "Medium", "High", "Critical"]
    category: Literal[
        "Feature Creep",
        "Scope Expansion", 
        "Timeline Pressure",
        "Unclear Requirements",
        "Technical Debt",
        "Resource Constraint"
    ]
    description: str
    quote: str = Field(..., description="Exact quote from transcript showing the issue")
    recommendation: str
    impacted_items: List[str] = Field(
        ..., description="List of PBI IDs that might be affected"
    )

class ScopeSentinel(BaseModel):
    overall_risk: Literal["Low", "Medium", "High", "Critical"]
    summary: str = Field(..., description="Brief assessment of scope health")
    alerts: List[ScopeAlert]
    metrics: dict = Field(
        ..., 
        description="Quantitative metrics like feature_count, new_items_mentioned, etc."
    )


class DocumentationPackage(BaseModel):
    meeting_summary: str
    backlog_items: List[BacklogItem]
    decision_log: List[DecisionNote]
    risk_register: List[RiskAssumption]
    release_notes_draft: List[ReleaseNoteEntry]
    scope_sentinel: ScopeSentinel 

# Request/Response models for API
class TranscriptRequest(BaseModel):
    transcript: str
    model_choice: Literal["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"]

class HealthResponse(BaseModel):
    status: str
    gemini_configured: bool
    available_models: List[str]


