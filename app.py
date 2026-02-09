import streamlit as st
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Literal
import json

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Agile Documentation Generator", page_icon="📑", layout="wide")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    model_choice = st.selectbox("Model", ["gemini-1.5-pro", "gemini-2.5-flash"]) 
    st.caption("Pro recommended for accurate 'Definition of Ready' checks.")

# --- 2. DATA MODELS (Scrum-Compliant) ---

class AcceptanceCriteria(BaseModel):
    condition: str = Field(..., description="The condition that must be met.")
    test_type: Literal["Functional", "UI/UX", "Security", "Performance", "Regression"]

class BacklogItem(BaseModel):
    id: str = Field(..., description="ID like PBI-001")
    title: str = Field(..., description="Short title of the item")
    user_story: str = Field(..., description="As a X, I want Y, so that Z")
    priority: Literal["Must Have", "Should Have", "Could Have", "Won't Have"]
    
    # CHANGE: Switched from Story Points (Int) to Complexity (T-Shirt Size)
    # This aligns with the feedback: BAs estimate size/complexity, Devs assign points.
    complexity: Literal["XS", "S", "M", "L", "XL", "Needs Discussion"] = Field(..., description="Estimated T-shirt size complexity.")
    
    definition_of_ready_status: Literal["Ready for Sprint", "Needs Refinement"] = Field(..., description="Is this story clear enough to start work?")
    missing_info: str = Field(..., description="If not ready, list what is missing. If ready, return an empty string.")
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
    value_statement: str = Field(..., description="Non-technical explanation of value for end-users.")
    audience: Literal["Internal Users", "External Customers", "Admins", "Developers"]

class DocumentationPackage(BaseModel):
    meeting_summary: str
    backlog_items: List[BacklogItem]
    decision_log: List[DecisionNote]
    risk_register: List[RiskAssumption]
    release_notes_draft: List[ReleaseNoteEntry]

# --- 3. APP LOGIC ---
st.title("📑 AI Agile Documenter")
st.markdown("Generates **Backlog Items (T-Shirt Sized), Decision Logs, and Release Notes**.")

transcript = st.text_area("Paste Meeting Transcript", height=300)

if st.button("Generate Documentation Package", type="primary"):
    if not api_key:
        st.error("🔑 Please enter your Gemini API Key in the sidebar.")
    elif not transcript:
        st.warning("⚠️ Please enter a transcript to analyze.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name=model_choice,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": DocumentationPackage
                }
            )

            with st.spinner("Drafting formal documentation..."):
                prompt = f"""
                You are a Senior Technical Product Manager.
                Analyze the transcript and produce a formal Agile documentation package.
                
                CRITICAL INSTRUCTIONS:
                1. **Complexity (Not Points):** Do not assign Story Points. Instead, estimate T-Shirt size (S, M, L) based on implied complexity.
                2. **Definition of Ready:** If a requirement is vague (e.g. "needs a tag") but lacks detail (e.g. "where does the tag go?"), mark it as "Needs Refinement".
                3. **Decisions:** Extract specific architectural or scope decisions (e.g. "Killing the Export feature").
                
                TRANSCRIPT:
                {transcript}
                """
                response = model.generate_content(prompt)
                data = json.loads(response.text)
                docs = DocumentationPackage(**data)

            st.success("Documentation Generated Successfully!")
            
            # --- DISPLAY ---
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 Product Backlog", 
                "⚡ Decisions & Risks", 
                "📢 Release Notes", 
                "💾 JSON Data"
            ])

            # TAB 1: BACKLOG
            with tab1:
                st.subheader("Updated Product Backlog")
                
                # Simple stats
                ready_count = sum(1 for item in docs.backlog_items if item.definition_of_ready_status == "Ready for Sprint")
                st.caption(f"Ready: {ready_count} / {len(docs.backlog_items)} Items")

                for item in docs.backlog_items:
                    # Status Icons
                    status_icon = "✅" if item.definition_of_ready_status == "Ready for Sprint" else "⚠️"
                    
                    # Complexity Badge Color
                    complexity_color = "red" if item.complexity in ["L", "XL"] else "green" if item.complexity in ["XS", "S"] else "orange"
                    
                    # Expander Header
                    header = f"{status_icon} [{item.priority}] {item.title} — :{complexity_color}[Size: {item.complexity}]"
                    
                    with st.expander(header):
                        st.markdown(f"**User Story:** {item.user_story}")
                        
                        # Show Missing Info prominently if it exists
                        if item.missing_info and item.missing_info.strip():
                            st.error(f"**Needs Refinement:** {item.missing_info}")
                        
                        st.markdown("**Acceptance Criteria:**")
                        for ac in item.acceptance_criteria:
                            st.markdown(f"- `{ac.test_type}` {ac.condition}")

            # TAB 2: GOVERNANCE
            with tab2:
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("📝 Decision Log")
                    if not docs.decision_log:
                        st.info("No major decisions recorded.")
                    for d in docs.decision_log:
                        st.success(f"**{d.topic}**\n\nDecision: {d.decision_made}\n\n*Rationale: {d.rationale}*")
                
                with c2:
                    st.subheader("🛡️ Risk Register")
                    if not docs.risk_register:
                        st.info("No high-level risks recorded.")
                    for r in docs.risk_register:
                        st.warning(f"**{r.category}: {r.description}**\n\nMitigation: {r.mitigation_strategy}")

            # TAB 3: STAKEHOLDERS
            with tab3:
                st.subheader("📢 Draft Release Notes")
                txt_output = "## Release Highlights\n\n"
                for note in docs.release_notes_draft:
                    entry = f"**{note.feature_name}** ({note.audience})\n{note.value_statement}\n\n"
                    st.markdown(entry)
                    txt_output += entry
                st.download_button("Download .txt", txt_output, "release_notes.txt")

            # TAB 4: RAW DATA
            with tab4:
                st.json(data)

        except Exception as e:
            st.error(f"Error parsing response: {e}")