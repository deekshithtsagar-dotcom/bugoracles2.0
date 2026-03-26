"""
AI Release Testing System - Streamlit Web Interface
====================================================
A clean web UI for the AI-Agent Driven Context-Aware Release Testing System.

Run with: streamlit run app.py
"""

import streamlit as st
import sys
import os
import re
import io
import textwrap
from dotenv import load_dotenv
import pandas as pd
import altair as alt
from config import Config

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env from project root explicitly.
# override=True prevents stale shell variables from shadowing updated .env keys.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

CREW_SETUP_IMPORT_ERROR = None
try:
    from crew_setup import ReleaseTestingCrew
except Exception as exc:
    ReleaseTestingCrew = None
    CREW_SETUP_IMPORT_ERROR = exc


STRUCTURED_STORY_PROMPT = """
You are a senior product analyst and QA strategist.

Convert raw product requirement text into a clean structured user story.

Output format (strict):
As a [specific user/persona], I want [feature/action], so that [business/user benefit].

Acceptance Criteria:
- [criterion 1]
- [criterion 2]
- [criterion 3]
- [criterion 4]
- [criterion 5]
- [criterion 6 optional]
- [criterion 7 optional]
- [criterion 8 optional]

Rules:
- Always include "As a", "I want", and "so that" in one sentence.
- Acceptance Criteria must have 5 to 8 bullets.
- Include validation rules, edge cases, and normal flow.
- Keep concise and production-ready.
- Return only the final structured story text.
"""

STRUCTURED_BUG_HISTORY_PROMPT = """
You are a senior QA analyst.

Convert raw, unstructured bug notes into structured historical bug entries.

Output format (strict):
Recent Bug History (Last 6 months):

BUG-YYYY-001: [Short bug summary]
- Severity: [Critical/High/Medium/Low]
- Module: [Most relevant module]
- Root Cause: [Likely technical root cause]

BUG-YYYY-002: ...

Rules:
- Generate 3 to 6 bug entries.
- Keep concise and realistic.
- Use diverse but relevant modules and causes.
- Include auth/payment/state/API patterns where appropriate.
- Return only the formatted bug history.
"""


# Page configuration
st.set_page_config(
    page_title="BUGORACLE",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top right, #1e293b 0%, #0f172a 45%, #020617 100%);
        color: #e2e8f0;
    }
    .stApp p, .stApp label, .stApp span, .stApp div, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        color: #dbe4ef;
    }
    .hero {
        background: linear-gradient(135deg, #3b82f6 0%, #64748b 40%, #475569 100%);
        border-radius: 16px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1rem;
        color: #FFFFFF;
        border: 1px solid rgba(148, 163, 184, 0.35);
        box-shadow: 0 16px 40px rgba(2, 6, 23, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 0.35rem;
    }
    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.95;
        margin-bottom: 0;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0.2rem 0 0.6rem 0;
        color: #cbd5e1;
    }
    .panel {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.75));
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 12px 28px rgba(2, 6, 23, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.12);
    }
    .stat-chip {
        display: inline-block;
        font-size: 0.85rem;
        font-weight: 600;
        background: linear-gradient(135deg, rgba(226, 232, 240, 0.25), rgba(148, 163, 184, 0.18));
        color: #f8fafc;
        border-radius: 999px;
        padding: 0.3rem 0.7rem;
        margin-right: 0.45rem;
        border: 1px solid rgba(226, 232, 240, 0.28);
    }
    .stTextArea textarea, .stTextInput input {
        font-family: 'Consolas', 'Monaco', monospace;
        border-radius: 12px !important;
        border: 1px solid rgba(148, 163, 184, 0.55) !important;
        background: rgba(15, 23, 42, 0.88) !important;
        color: #f8fafc !important;
        caret-color: #f8fafc !important;
    }
    .stTextArea textarea::placeholder, .stTextInput input::placeholder {
        color: #94a3b8 !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #60a5fa 0%, #64748b 100%) !important;
        color: #f8fafc !important;
        border-radius: 12px;
        font-weight: 700;
        border: 0;
        padding-top: 0.65rem;
        padding-bottom: 0.65rem;
        box-shadow: 0 10px 24px rgba(2, 6, 23, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.25);
    }
    [data-testid="stSidebar"] * {
        color: #dbe4ef !important;
    }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #e2e8f0 !important;
    }
    [data-baseweb="tab-list"] {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }
    button[data-baseweb="tab"] {
        color: #cbd5e1 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #f8fafc !important;
        background: rgba(96, 165, 250, 0.2) !important;
        border-radius: 8px;
    }
    .stMarkdown a {
        color: #93c5fd !important;
    }
    .status-badge {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        font-weight: 700;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.28);
        margin-bottom: 0.4rem;
    }
    .prediction-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.86), rgba(15, 23, 42, 0.82));
        border: 1px solid rgba(96, 165, 250, 0.28);
        border-radius: 12px;
        padding: 0.8rem 0.95rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 8px 18px rgba(2, 6, 23, 0.35);
    }
    .prediction-title {
        font-weight: 700;
        color: #bfdbfe;
        margin-bottom: 0.35rem;
    }
    .prediction-kv {
        color: #e2e8f0;
        margin: 0.15rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Sample data
SAMPLE_USER_STORY = """As a registered user of the e-commerce platform,
I want to be able to add products to my shopping cart
So that I can purchase multiple items in a single transaction.

Acceptance Criteria:
- User must be logged in to add items to cart
- Product page should display "Add to Cart" button
- Clicking the button adds the product with selected quantity
- Cart icon should update to show total items count
- User should see a confirmation message after adding item
- Cart should persist across browser sessions
- User can add the same product multiple times
- Maximum quantity per product is 99 units
- Out-of-stock items cannot be added to cart
- Cart should display product image, name, price, and quantity"""

SAMPLE_BUG_HISTORY = """Recent Bug History (Last 6 months):

BUG-2024-001: Cart count not updating after adding items
- Severity: High
- Module: Shopping Cart
- Root Cause: State management issue in frontend

BUG-2024-015: Session cart data lost on browser refresh
- Severity: Critical
- Module: Shopping Cart, Session Management
- Root Cause: LocalStorage not syncing with backend

BUG-2024-023: Race condition when adding same item rapidly
- Severity: Medium
- Module: Shopping Cart API
- Root Cause: No debouncing on add-to-cart API calls

BUG-2024-045: Price calculation error with quantity > 50
- Severity: High
- Module: Cart Calculations
- Root Cause: Integer overflow in legacy calculation code

BUG-2024-067: Add to cart fails silently for out-of-stock items
- Severity: Medium
- Module: Inventory Integration
- Root Cause: Missing error handling for inventory check

BUG-2024-089: Guest users could add items without login redirect
- Severity: High
- Module: Authentication, Shopping Cart
- Root Cause: Missing auth middleware on cart endpoints"""


def check_api_key():
    """Check if Groq API key is configured."""
    api_key = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
    if not api_key or api_key == "your-groq-api-key-here":
        return False
    return True


def run_analysis(user_story: str, bug_history: str):
    """Run the AI analysis crew."""
    if ReleaseTestingCrew is None:
        raise RuntimeError(
            "CrewAI runtime is unavailable in this environment. "
            "Use Python 3.11 or 3.12, reinstall dependencies, then rerun the app."
        ) from CREW_SETUP_IMPORT_ERROR

    crew = ReleaseTestingCrew(user_story, bug_history)
    return crew.run()


def _ensure_acceptance_criteria(story_text: str, raw_input: str) -> str:
    """Normalize generated story to always include valid acceptance criteria."""
    text = (story_text or "").strip()
    if not text:
        text = f"As a user, I want {raw_input.strip()}, so that I can complete the intended workflow reliably."

    if "as a" not in text.lower() or "i want" not in text.lower() or "so that" not in text.lower():
        text = f"As a user, I want {raw_input.strip()}, so that I can complete the intended workflow reliably.\n\n" + text

    if "Acceptance Criteria:" not in text:
        text += "\n\nAcceptance Criteria:\n"

    lines = text.splitlines()
    bullet_lines = [line for line in lines if re.match(r"^\s*[-*]\s+", line)]

    fallback_bullets = [
        "- System validates all required fields before processing.",
        "- Successful flow shows clear confirmation to the user.",
        "- Invalid input shows actionable error messages.",
        "- Session/state remains consistent after refresh and retry.",
        "- Edge cases (empty, duplicate, max-limit values) are handled gracefully.",
        "- Failures from dependent APIs are handled with safe fallback behavior.",
    ]

    if len(bullet_lines) < 5:
        base_without_bullets = [line for line in lines if not re.match(r"^\s*[-*]\s+", line)]
        text = "\n".join(base_without_bullets).strip()
        if "Acceptance Criteria:" not in text:
            text += "\n\nAcceptance Criteria:"
        text += "\n" + "\n".join(fallback_bullets)
        return text

    if len(bullet_lines) > 8:
        kept = 0
        compact_lines = []
        for line in lines:
            if re.match(r"^\s*[-*]\s+", line):
                kept += 1
                if kept <= 8:
                    compact_lines.append(line)
            else:
                compact_lines.append(line)
        return "\n".join(compact_lines)

    return text


def generate_structured_user_story(raw_input: str) -> str:
    """Generate structured user story + acceptance criteria from natural language input.

    Uses LLM-based interpretation with deterministic fallback normalization.
    """
    raw = (raw_input or "").strip()
    if not raw:
        return ""

    try:
        from litellm import completion

        response = completion(
            model=Config.MODEL_NAME,
            api_key=os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'"),
            temperature=0.2,
            messages=[
                {"role": "system", "content": STRUCTURED_STORY_PROMPT},
                {"role": "user", "content": f"Raw requirement:\n{raw}"},
            ],
        )
        generated = response["choices"][0]["message"]["content"]
        return _ensure_acceptance_criteria(generated, raw)
    except Exception:
        fallback = (
            f"As a user, I want {raw}, so that I can complete the intended workflow reliably.\n\n"
            "Acceptance Criteria:\n"
            "- System validates required input fields before processing.\n"
            "- Success flow completes and shows confirmation to the user.\n"
            "- Invalid or partial input returns clear validation errors.\n"
            "- Duplicate and boundary-value scenarios are handled safely.\n"
            "- API or dependency failures are handled without data loss.\n"
            "- User can recover and retry the flow without inconsistent state."
        )
        return _ensure_acceptance_criteria(fallback, raw)


def _ensure_structured_bug_history(bug_text: str, raw_input: str) -> str:
    """Normalize generated bug history into consistent structured entries."""
    text = (bug_text or "").strip()
    if not text:
        text = "Recent Bug History (Last 6 months):"

    if "Recent Bug History" not in text:
        text = "Recent Bug History (Last 6 months):\n\n" + text

    entries = re.findall(r"BUG-\d{4}-\d{3}:", text)
    if len(entries) >= 3:
        return text

    raw_summary = raw_input.strip() if raw_input.strip() else "User-reported instability in feature flows"
    fallback = (
        "Recent Bug History (Last 6 months):\n\n"
        f"BUG-2026-001: {raw_summary}\n"
        "- Severity: High\n"
        "- Module: Core Workflow\n"
        "- Root Cause: Incomplete validation and state synchronization\n\n"
        "BUG-2026-002: Payment confirmation mismatch under retry\n"
        "- Severity: Critical\n"
        "- Module: Payment & Notifications\n"
        "- Root Cause: Race condition between transaction callback and UI refresh\n\n"
        "BUG-2026-003: Session expired users could trigger stale actions\n"
        "- Severity: Medium\n"
        "- Module: Authentication / Session\n"
        "- Root Cause: Missing server-side session guard on async endpoints"
    )
    return fallback


def generate_structured_bug_history(raw_input: str) -> str:
    """Generate structured bug history from simple natural language notes."""
    raw = (raw_input or "").strip()
    if not raw:
        return ""

    try:
        from litellm import completion

        response = completion(
            model=Config.MODEL_NAME,
            api_key=os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'"),
            temperature=0.2,
            messages=[
                {"role": "system", "content": STRUCTURED_BUG_HISTORY_PROMPT},
                {"role": "user", "content": f"Raw bug notes:\n{raw}"},
            ],
        )
        generated = response["choices"][0]["message"]["content"]
        return _ensure_structured_bug_history(generated, raw)
    except Exception:
        fallback = (
            "Recent Bug History (Last 6 months):\n\n"
            "BUG-2026-001: Checkout retries caused duplicate charge warnings\n"
            "- Severity: High\n"
            "- Module: Payment Gateway Integration\n"
            "- Root Cause: Missing idempotency token enforcement\n\n"
            "BUG-2026-002: Logged-out users intermittently accessed protected actions\n"
            "- Severity: Critical\n"
            "- Module: Authentication\n"
            "- Root Cause: Session guard skipped on one API route\n\n"
            "BUG-2026-003: Cart count desynced after rapid item updates\n"
            "- Severity: Medium\n"
            "- Module: Cart State Management\n"
            "- Root Cause: Concurrent state update collision"
        )
        return _ensure_structured_bug_history(fallback, raw)


def generate_pdf_report_bytes(user_story: str, bug_history: str, results: dict) -> bytes | None:
    """Generate a user-friendly PDF report as bytes for download.

    Returns None if PDF dependency is unavailable.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception:
        return None

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    left_margin = 40
    top_margin = 40
    bottom_margin = 40
    line_height = 13
    y_pos = height - top_margin

    def ensure_space(lines_needed: int = 1):
        nonlocal y_pos
        if y_pos - (lines_needed * line_height) < bottom_margin:
            pdf.showPage()
            y_pos = height - top_margin

    def write_heading(text: str):
        nonlocal y_pos
        ensure_space(2)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(left_margin, y_pos, text)
        y_pos -= line_height + 4

    def write_body(text: str):
        nonlocal y_pos
        pdf.setFont("Helvetica", 10)
        for raw_line in (text or "").splitlines():
            wrapped = textwrap.wrap(raw_line, width=110) or [""]
            ensure_space(len(wrapped) + 1)
            for line in wrapped:
                safe_line = line.replace("•", "-")
                pdf.drawString(left_margin, y_pos, safe_line)
                y_pos -= line_height
        y_pos -= 4

    decision = results.get("release_decision", {})
    confidence = results.get("confidence", {})

    write_heading("AI Release Testing Report")
    write_body("Generated by AI-Agent Driven Context-Aware Release Testing System")

    write_heading("User Story")
    write_body(user_story)

    write_heading("Bug History")
    write_body(bug_history)

    write_heading("Release Decision")
    write_body(f"Decision: {decision.get('decision', 'N/A')}")
    for reason in decision.get("reason_bullets", []):
        write_body(f"- {reason}")

    write_heading("AI Confidence")
    write_body(f"Score: {confidence.get('score', 'N/A')}% ({confidence.get('category', 'N/A')})")
    for factor in confidence.get("factors", []):
        write_body(f"- {factor}")

    write_heading("Risk Analysis")
    write_body(results.get("risk_analysis", "N/A"))

    write_heading("Predicted Failures & Root Causes")
    write_body(results.get("root_cause_predictions", "N/A"))

    write_heading("Generated Test Cases")
    write_body(results.get("test_cases", "N/A"))

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def parse_root_cause_predictions(predictions_text: str):
    """Parse RCA markdown/text output into structured issue dictionaries."""
    if not predictions_text:
        return []

    blocks = re.split(r"(?=Predicted Issue\s*\d+:)", predictions_text, flags=re.IGNORECASE)
    parsed = []

    for block in blocks:
        chunk = block.strip()
        if not chunk:
            continue
        if not re.search(r"Predicted Issue\s*\d+", chunk, flags=re.IGNORECASE):
            continue

        title_match = re.search(r"(Predicted Issue\s*\d+:)", chunk, flags=re.IGNORECASE)
        module_match = re.search(r"-\s*Module:\s*(.+)", chunk, flags=re.IGNORECASE)
        cause_match = re.search(r"-\s*Possible Root Cause:\s*(.+)", chunk, flags=re.IGNORECASE)
        impact_match = re.search(r"-\s*Impact:\s*(.+)", chunk, flags=re.IGNORECASE)

        parsed.append(
            {
                "title": title_match.group(1).strip() if title_match else "Predicted Issue",
                "module": module_match.group(1).strip() if module_match else "Not specified",
                "root_cause": cause_match.group(1).strip() if cause_match else "Not specified",
                "impact": impact_match.group(1).strip() if impact_match else "Not specified",
            }
        )

    return parsed


def display_results(results: dict):
    """Display the analysis results in a formatted way."""

    risk_level = results.get("risk_level", "LOW")
    risk_numeric_score = int(results.get("risk_numeric_score", 25))
    decision = results.get("release_decision", {})
    confidence = results.get("confidence", {})
    priority_summary = results.get("test_priority_summary", {})
    risk_distribution = results.get("risk_distribution", {"LOW": 60, "MEDIUM": 30, "HIGH": 10})

    decision_text = decision.get("decision", "NEEDS MORE TESTING")
    decision_color = decision.get("color", "#f59e0b")
    confidence_score = confidence.get("score", 0)
    confidence_category = confidence.get("category", "Low Confidence")
    confidence_color = "#10b981" if confidence_score > 80 else "#f59e0b" if confidence_score >= 50 else "#ef4444"
    risk_color = "#ef4444" if risk_level == "HIGH" else "#f59e0b" if risk_level == "MEDIUM" else "#10b981"

    st.markdown('<p class="section-title">🚦 Release Intelligence</p>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(
            f'<span class="status-badge" style="background:{decision_color};">{decision_text}</span>',
            unsafe_allow_html=True,
        )
        reason_bullets = decision.get("reason_bullets", [])
        for reason in reason_bullets:
            st.markdown(f"- {reason}")

    with col_b:
        st.markdown(
            f'<span class="status-badge" style="background:{confidence_color};">AI Confidence Score: {confidence_score}% ({confidence_category})</span>',
            unsafe_allow_html=True,
        )
        for factor in confidence.get("factors", []):
            st.markdown(f"- {factor}")

    with col_c:
        st.markdown(
            f'<span class="status-badge" style="background:{risk_color};">Risk Level: {risk_level}</span>',
            unsafe_allow_html=True,
        )
        st.progress(min(max(risk_numeric_score, 0), 100), text=f"Risk Score: {risk_numeric_score}/100")

    show_pie = st.checkbox("Show risk distribution chart", value=True, key="show_risk_distribution")
    if show_pie:
        chart_data = pd.DataFrame(
            {
                "Risk Level": list(risk_distribution.keys()),
                "Weight": list(risk_distribution.values()),
            }
        )
        chart = (
            alt.Chart(chart_data)
            .mark_arc(innerRadius=45)
            .encode(
                theta=alt.Theta(field="Weight", type="quantitative"),
                color=alt.Color(
                    field="Risk Level",
                    type="nominal",
                    scale=alt.Scale(
                        domain=["LOW", "MEDIUM", "HIGH"],
                        range=["#10b981", "#f59e0b", "#ef4444"],
                    ),
                ),
                tooltip=["Risk Level", "Weight"],
            )
            .properties(height=260)
        )
        st.altair_chart(chart, use_container_width=True)

    st.markdown('<p class="section-title">🧩 Predicted Failures & Root Causes</p>', unsafe_allow_html=True)
    prediction_items = parse_root_cause_predictions(results.get("root_cause_predictions", ""))
    if prediction_items:
        for item in prediction_items:
            st.markdown(
                f"""
                <div class="prediction-card">
                    <div class="prediction-title">⚠️ {item['title']}</div>
                    <div class="prediction-kv"><b>Module:</b> {item['module']}</div>
                    <div class="prediction-kv"><b>Possible Root Cause:</b> {item['root_cause']}</div>
                    <div class="prediction-kv"><b>Impact:</b> {item['impact']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(results.get("root_cause_predictions", "No root cause predictions generated."))

    st.markdown('<p class="section-title">📊 Analysis Results</p>', unsafe_allow_html=True)
    req_tab, risk_tab, test_tab, rca_tab, priority_tab = st.tabs([
        "📋 Requirements",
        "⚠️ Risk",
        "🧪 Test Cases",
        "🧩 RCA",
        "🎯 Prioritization",
    ])

    with req_tab:
        st.markdown(results.get("requirements", "No requirements analysis generated."))

    with risk_tab:
        st.markdown(results.get("risk_analysis", "No risk analysis generated."))

    with test_tab:
        st.markdown(results.get("test_cases", "No test cases generated."))

    with rca_tab:
        prediction_items = parse_root_cause_predictions(results.get("root_cause_predictions", ""))
        if prediction_items:
            for item in prediction_items:
                st.markdown(
                    f"""
                    <div class="prediction-card">
                        <div class="prediction-title">⚠️ {item['title']}</div>
                        <div class="prediction-kv"><b>Module:</b> {item['module']}</div>
                        <div class="prediction-kv"><b>Possible Root Cause:</b> {item['root_cause']}</div>
                        <div class="prediction-kv"><b>Impact:</b> {item['impact']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(results.get("root_cause_predictions", "No root cause predictions generated."))

    with priority_tab:
        distribution = priority_summary.get("distribution", {"HIGH": 0, "MEDIUM": 0, "LOW": 0})
        st.markdown(f"- Total Test Cases: {priority_summary.get('total_test_cases', 0)}")
        st.markdown(f"- HIGH Priority: {distribution.get('HIGH', 0)}")
        st.markdown(f"- MEDIUM Priority: {distribution.get('MEDIUM', 0)}")
        st.markdown(f"- LOW Priority: {distribution.get('LOW', 0)}")


def main():
    """Main application entry point."""

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">🧪 BUGORACLE</div>
            <p class="hero-subtitle">AI-agent powered, context-aware requirements, risk analysis, and test generation</p>
            <div style="margin-top:0.8rem;">
                <span class="stat-chip">3 AI Agents</span>
                <span class="stat-chip">Structured Output</span>
                <span class="stat-chip">Markdown Report Export</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Analysis Stages", "3")
    with m2:
        st.metric("Input Sources", "2", help="User Story + Bug History")
    with m3:
        st.metric("Output Type", "Report")
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This system uses **3 AI Agents** to:
        
        1. **Requirement Agent** - Extracts requirements, edge cases, and test scenarios
        
        2. **Risk Agent** - Analyzes risks based on bug history
        
        3. **Test Case Agent** - Generates comprehensive test cases
        
        ---
        
        **Powered by:**
        - CrewAI
        - Groq LLM (Llama 3.3)
        """)

        st.markdown("---")
        st.markdown("**Workflow**")
        st.markdown("1. Provide user story")
        st.markdown("2. Add bug history")
        st.markdown("3. Run analysis")
        st.markdown("4. Review tabs + download report")
        
        st.header("⚙️ Settings")
        use_sample = st.checkbox("Load sample data", value=True)
        
        # API Key status
        st.header("🔑 API Status")
        if check_api_key():
            st.success("Groq API Key: Configured ✓")
        else:
            st.error("Groq API Key: Not found!")
            st.info("Add GROQ_API_KEY to your .env file")

        st.markdown("**Set API Key (session only)**")
        manual_api_key = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            key="manual_groq_api_key"
        )
        if st.button("Use this key", use_container_width=True):
            if manual_api_key.strip():
                os.environ["GROQ_API_KEY"] = manual_api_key.strip()
                st.success("API key applied for this session.")
            else:
                st.warning("Please paste a valid Groq API key.")
    
    # Main content area
    st.markdown('<p class="section-title">🧾 Inputs</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("📝 User Story")
        simple_input_mode = st.checkbox("Use Simple Input Mode", value=False, key="simple_input_mode")

        generated_story = st.session_state.get("generated_user_story", "")

        if simple_input_mode:
            raw_default = "I want users to pay using UPI and card and see confirmation" if use_sample else ""
            raw_input = st.text_area(
                "Describe your feature in simple words:",
                value=raw_default,
                placeholder="Example: I want users to pay using UPI and card and see confirmation",
                height=130,
                key="raw_feature_input"
            )

            if st.button("✨ Generate Structured User Story", use_container_width=True):
                if not raw_input.strip():
                    st.warning("Please describe the feature first.")
                else:
                    with st.spinner("Generating structured story..."):
                        st.session_state["generated_user_story"] = generate_structured_user_story(raw_input)
                    generated_story = st.session_state.get("generated_user_story", "")

            if generated_story:
                st.text_area(
                    "Generated Structured User Story (used for analysis):",
                    value=generated_story,
                    height=220,
                    key="generated_user_story_preview"
                )

            user_story = generated_story
        else:
            if use_sample:
                user_story = st.text_area(
                    "Enter the user story to analyze:",
                    value=SAMPLE_USER_STORY,
                    height=300,
                    key="user_story"
                )
            else:
                user_story = st.text_area(
                    "Enter the user story to analyze:",
                    placeholder="As a [user], I want to [action] so that [benefit]...",
                    height=300,
                    key="user_story"
                )
        st.caption(f"Length: {len(user_story)} characters")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("🐛 Bug History")
        simple_bug_input_mode = st.checkbox("Use Simple Bug Input Mode", value=False, key="simple_bug_input_mode")

        generated_bug_history = st.session_state.get("generated_bug_history", "")

        if simple_bug_input_mode:
            raw_bug_default = (
                "Users reported issues with payment retries, login/session drops, and cart count mismatch"
                if use_sample else ""
            )
            raw_bug_input = st.text_area(
                "Describe historical issues in simple words:",
                value=raw_bug_default,
                placeholder="Example: payment retries failed, auth expired unexpectedly, API timeouts happened",
                height=130,
                key="raw_bug_input"
            )

            if st.button("✨ Generate Structured Bug History", use_container_width=True):
                if not raw_bug_input.strip():
                    st.warning("Please describe historical issues first.")
                else:
                    with st.spinner("Generating structured bug history..."):
                        st.session_state["generated_bug_history"] = generate_structured_bug_history(raw_bug_input)
                    generated_bug_history = st.session_state.get("generated_bug_history", "")

            if generated_bug_history:
                st.text_area(
                    "Generated Bug History (used for analysis):",
                    value=generated_bug_history,
                    height=220,
                    key="generated_bug_history_preview"
                )

            bug_history = generated_bug_history
        else:
            if use_sample:
                bug_history = st.text_area(
                    "Enter historical bug data:",
                    value=SAMPLE_BUG_HISTORY,
                    height=300,
                    key="bug_history"
                )
            else:
                bug_history = st.text_area(
                    "Enter historical bug data:",
                    placeholder="BUG-001: Description\n- Severity: High\n- Module: ...",
                    height=300,
                    key="bug_history"
                )
        st.caption(f"Length: {len(bug_history)} characters")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis button
    st.markdown("---")

    if ReleaseTestingCrew is None:
        st.error("CrewAI is not available in this Python environment.")
        st.info("Current environment is Python 3.14, but this project's CrewAI stack requires Python 3.11/3.12.")
        st.info("Create a 3.11/3.12 virtual environment, reinstall requirements, and restart Streamlit.")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        analyze_button = st.button(
            "🚀 Run AI Analysis",
            type="primary",
            use_container_width=True
        )
    
    # Run analysis
    if analyze_button:
        if ReleaseTestingCrew is None:
            st.error("Cannot run analysis because CrewAI dependencies are not compatible with Python 3.14 in this setup.")
            return

        if simple_input_mode and not user_story.strip():
            raw_input = st.session_state.get("raw_feature_input", "")
            if raw_input.strip():
                user_story = generate_structured_user_story(raw_input)
                st.session_state["generated_user_story"] = user_story
                st.info("Generated structured story from simple input.")

        if simple_bug_input_mode and not bug_history.strip():
            raw_bug_input = st.session_state.get("raw_bug_input", "")
            if raw_bug_input.strip():
                bug_history = generate_structured_bug_history(raw_bug_input)
                st.session_state["generated_bug_history"] = bug_history
                st.info("Generated structured bug history from simple input.")

        if not user_story.strip():
            st.error("Please enter a user story to analyze.")
            return
        
        if not check_api_key():
            st.error("Groq API Key not configured. Please add GROQ_API_KEY to your .env file.")
            return
        
        # Progress container
        with st.spinner("🤖 AI Agents are working... This may take 1-2 minutes."):
            try:
                # Status updates
                status_placeholder = st.empty()
                
                status_placeholder.info("Creating AI agents...")
                results = run_analysis(user_story, bug_history)
                status_placeholder.empty()
                
                # Success message
                st.success("✅ Analysis complete!")
                
                # Display results
                st.markdown("---")
                display_results(results)
                
                # Download button
                st.markdown("---")
                full_output = f"""# AI Release Testing Analysis Results

## User Story
{user_story}

## Bug History
{bug_history}

---

## Requirements Analysis
{results.get('requirements', 'N/A')}

---

## Risk Analysis
{results.get('risk_analysis', 'N/A')}

---

## Generated Test Cases
{results.get('test_cases', 'N/A')}

---

## Predicted Failures & Root Causes
{results.get('root_cause_predictions', 'N/A')}

---

## Release Decision
{results.get('release_decision', {}).get('decision', 'N/A')}

## AI Confidence
{results.get('confidence', {}).get('score', 'N/A')}%

## Risk Score
{results.get('risk_numeric_score', 'N/A')}/100
"""
                pdf_bytes = generate_pdf_report_bytes(user_story, bug_history, results)

                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    if pdf_bytes:
                        st.download_button(
                            label="📄 Download Full Report (PDF)",
                            data=pdf_bytes,
                            file_name="release_testing_report.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    else:
                        st.warning("PDF export dependency missing. Install 'reportlab' to enable PDF downloads.")

                with dl_col2:
                    st.download_button(
                        label="📝 Download Full Report (Markdown)",
                        data=full_output,
                        file_name="release_testing_report.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.info("Please check your API key and try again.")


if __name__ == "__main__":
    main()
