"""
Upgraded Streamlit Web App
Automated Paper Correction System - Startup UI Version
"""

import streamlit as st
import os
import json
import hashlib
import nest_asyncio
from dotenv import load_dotenv

load_dotenv(override=True)

# Assuming these are available in your project directory
from pipeline import run_correction_pipeline
from utils import save_uploaded_file, ensure_directory_exists, verify_openrouter_api_key
import ui_components as ui

# --- MOCK USER DATABASE ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

MOCK_USERS = {
    "teacher_demo": {"password_hash": hash_password("teacher123"), "role": "Teacher"},
    "student_demo": {"password_hash": hash_password("student123"), "role": "Student"}
}

# Fix asyncio loop for pipeline compatibility
try:
    nest_asyncio.apply()
except:
    pass

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Paper Corrector Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global dark neon styling
ui.inject_global_styles()

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "results" not in st.session_state:
    st.session_state.results = None
if "role" not in st.session_state:
    st.session_state.role = None

# ---------------- LOGIN / LANDING PAGE ----------------
def login_page():
    # Render the gorgeous header from ui_components
    ui.render_header("AI Paper Corrector Pro", "Automated grading powered by Gemini Vision & LLMs")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Setup login card layout centered on the screen
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        login_html = """
        <div style='text-align: center; margin-bottom: 1.5rem;'>
            <h1 style='font-family: Syne, sans-serif; font-size: 2.2rem; font-weight: 800; color: #F0F2FF; margin-bottom: 0.5rem;'>🔐 Access Portal</h1>
            <p style='color: #8890B5; font-size: 1rem; font-family: Space Mono, monospace;'>Enter your credentials to continue</p>
        </div>
        """
        
        # We render the text above via our glow card, but we need Streamlit inputs for actual interaction
        ui.glow_card(login_html, animate=True)
        
        username = st.text_input("Username", placeholder="e.g. teacher_demo")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        st.markdown("<br>", unsafe_allow_html=True)
        login_btn = st.button("SIGN IN", use_container_width=True)

        with st.expander("ℹ️ Demo Credentials"):
            st.markdown("- **Teacher Profile**: `teacher_demo` / `teacher123`\n- **Student Profile**: `student_demo` / `student123`")

        if login_btn:
            if username in MOCK_USERS and MOCK_USERS[username]["password_hash"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.role = MOCK_USERS[username]["role"]
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password.")

# Stop execution here if not logged in
if not st.session_state.logged_in:
    login_page()
    st.stop()


# ---------------- MAIN DASHBOARD (LOGGED IN) ----------------

ui.render_header("AI Paper Corrector Pro", f"Welcome back, {st.session_state.username} ({st.session_state.role})")

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Configuration")

comparison_method = st.sidebar.selectbox(
    "Comparison Method",
    ["gemini", "sentence_transformers"]
)

use_ai_feedback = st.sidebar.checkbox("Use AI Feedback", value=True)

# Removed Total Marks input since it is now dynamically inferred by Gemini

st.sidebar.divider()

is_or_valid, or_msg = verify_openrouter_api_key()
if is_or_valid:
    st.sidebar.success("✅ OpenRouter API Ready")
else:
    st.sidebar.error("❌ OpenRouter Key Missing")


st.sidebar.divider()

if st.sidebar.button("🗑️ Clear All Caches", use_container_width=True, help="Force re-extraction and re-evaluation"):
    st.cache_data.clear()
    st.cache_resource.clear()
    import shutil
    import os
    if os.path.exists("temp_uploads"):
        shutil.rmtree("temp_uploads", ignore_errors=True)
    st.sidebar.success("✅ Caches cleared! Please run the process again.")

st.sidebar.divider()

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.results = None
    st.rerun()


# ---------------- FILE UPLOAD ----------------
st.markdown("### Upload Documents")
col1, col2, col3 = st.columns(3)

teacher_file = col1.file_uploader("📄 Teacher Key", type=['pdf','png','jpg'])
student_file = col2.file_uploader("📝 Student Script", type=['pdf','png','jpg'])
reference_file = col3.file_uploader("💡 Reference (Optional)", type=['pdf','png','jpg'])


# ---------------- PROCESS FUNCTION ----------------
def process_papers():
    if not is_or_valid:
        st.error("API Key Error: Please check your .env file for the OpenRouter key.")
        return None

    temp_dir = "temp_uploads"
    ensure_directory_exists(temp_dir)

    teacher_path = save_uploaded_file(teacher_file, temp_dir)
    student_path = save_uploaded_file(student_file, temp_dir)
    reference_path = save_uploaded_file(reference_file, temp_dir) if reference_file else None

    with st.spinner("Processing with Gemini AI..."):
        try:
            results = run_correction_pipeline(
                teacher_file_path=teacher_path,
                student_file_path=student_path,
                reference_file_path=reference_path,
                comparison_method=comparison_method,
                use_ai_feedback=use_ai_feedback,
                output_dir="results",
                save_results=False
            )
            return results
        except Exception as e:
            st.error(f"Pipeline failed: {e}")
            return None


# ---------------- EVALUATE BUTTON ----------------
if st.button("🚀 Process and Evaluate", use_container_width=True):
    if teacher_file and student_file:
        st.session_state.results = process_papers()
    else:
        st.warning("⚠️ Please upload both the Teacher Key and the Student Script.")


# ---------------- DISPLAY RESULTS ----------------
def get_rank_config(score: float):
    if score >= 90:
        return {"level": 1, "emoji": "👑", "badge": "ELITE TIER", "label": "Top Performer", "bg": "linear-gradient(135deg, rgba(255,215,0,0.1) 0%, rgba(255,152,0,0.1) 100%)", "color": "#FFD700", "glow": "rgba(255,215,0,0.15)", "message": "Exceptional work. Near perfect mastery of the content."}
    elif score >= 75:
        return {"level": 2, "emoji": "⚡", "badge": "ADVANCED TIER", "label": "Excellent", "bg": "linear-gradient(135deg, rgba(0,255,136,0.1) 0%, rgba(0,229,255,0.1) 100%)", "color": "#00FF88", "glow": "rgba(0,255,136,0.15)", "message": "Strong performance with solid understanding."}
    elif score >= 60:
        return {"level": 3, "emoji": "👍", "badge": "PROFICIENCY TIER", "label": "Good", "bg": "linear-gradient(135deg, rgba(79,142,247,0.1) 0%, rgba(139,92,246,0.1) 100%)", "color": "#4F8EF7", "glow": "rgba(79,142,247,0.15)", "message": "Good grasp of the fundamentals."}
    elif score >= 40:
        return {"level": 4, "emoji": "📚", "badge": "DEVELOPING TIER", "label": "Average", "bg": "linear-gradient(135deg, rgba(255,152,0,0.1) 0%, rgba(244,67,54,0.1) 100%)", "color": "#FF9800", "glow": "rgba(255,152,0,0.15)", "message": "Shows basic understanding but needs improvement."}
    else:
        return {"level": 5, "emoji": "⚠️", "badge": "FOUNDATION TIER", "label": "Needs Improvement", "bg": "linear-gradient(135deg, rgba(255,75,123,0.15) 0%, rgba(255,0,85,0.1) 100%)", "color": "#FF4B7B", "glow": "rgba(255,75,123,0.15)", "message": "Significant knowledge gaps detected."}

if st.session_state.results:
    results = st.session_state.results
    evaluation = results['evaluation_report']['evaluation']

    st.markdown("<br><br>", unsafe_allow_html=True)
    ui.section_label("EVALUATION SUMMARY", accent="#00E5FF")

    total_score = evaluation['total_score']
    max_score = evaluation['max_score']
    percentage = evaluation['percentage']
    grade = evaluation.get("grade", "N/A")

    stats = [
        {"label": "Total Score",  "value": f"{total_score}/{max_score}", "color": "#4F8EF7"},
        {"label": "Percentage",   "value": f"{percentage:.1f}%",         "color": "#00FF88"},
        {"label": "Letter Grade", "value": grade,                        "color": "#FF9800"},
    ]
    
    # Check if we have extraction confidence
    teacher_extracted = results.get("extracted_data", {}).get("teacher_key", {}).get("pages", [])
    student_extracted = results.get("extracted_data", {}).get("student_script", {}).get("pages", [])
    
    if teacher_extracted and student_extracted:
        t_conf = sum(p.get("confidence_score", 100) for p in teacher_extracted) / len(teacher_extracted)
        s_conf = sum(p.get("confidence_score", 100) for p in student_extracted) / len(student_extracted)
        avg_extract_conf = (t_conf + s_conf) / 2
        
        stats.append({"label": "Read Clarity", "value": f"{avg_extract_conf:.0f}%", "color": "#a855f7" if avg_extract_conf > 80 else "#ef4444"})
    
    ui.stat_pills(stats)

    # Display any low-confidence warnings
    low_confidence_reasons = []
    for page in teacher_extracted:
        if page.get("confidence_score", 100) < 96 and page.get("confidence_reason") and "Clear text" not in page.get("confidence_reason", ""):
            low_confidence_reasons.append(f"Teacher Key (Page {page.get('page_no')}): {page.get('confidence_reason')}")
            
    for page in student_extracted:
        if page.get("confidence_score", 100) < 96 and page.get("confidence_reason") and "Clear text" not in page.get("confidence_reason", ""):
            low_confidence_reasons.append(f"Student Script (Page {page.get('page_no')}): {page.get('confidence_reason')}")
            
    if low_confidence_reasons:
        warning_msg = "⚠️ **Some pages had low extraction clarity:**\n\n" + "\n".join(f"- {reason}" for reason in low_confidence_reasons)
        st.warning(warning_msg)

    st.markdown("<br>", unsafe_allow_html=True)
    rank_conf = get_rank_config(percentage)
    ui.render_rank_badge(rank_conf, percentage)

    st.markdown("<br>", unsafe_allow_html=True)
    ui.section_label("PERFORMANCE BREAKDOWN", accent="#FF4B7B")
    
    similarity_scores = [p['similarity_score'] for p in evaluation.get('item_scores', [])]
    avg_similarity = sum(similarity_scores)/len(similarity_scores) if similarity_scores else 0
    content_score = percentage
    concept_score = avg_similarity

    colA, colB = st.columns(2)
    with colA:
        ui.score_chart(content_score, avg_similarity, concept_score)
    with colB:
        ui.radar_chart(content_score, avg_similarity, concept_score, accuracy=percentage*0.9, clarity=avg_similarity*1.1)

    st.markdown("<br>", unsafe_allow_html=True)
    ui.section_label("QUESTION ANALYSIS", accent="#FFD700")

    for idx, item in enumerate(evaluation.get('item_scores', [])):
        ui.question_card(
            q_num=item['item_no'],
            marks_given=item['marks_awarded'],
            marks_max=item['max_marks'],
            feedback=item.get("analysis", "No specific feedback provided for this section."),
            similarity=item['similarity_score']/100,
            grading_confidence=item.get('grading_confidence', 100),
            confidence_reason=item.get('confidence_reason', ""),
            delay=0.1 * idx
        )

    st.markdown("<br>", unsafe_allow_html=True)
    ui.section_label("GLOBAL AI FEEDBACK", accent="#8B5CF6")
    feedback_html = f"<div style='color: #D0D4F0; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;'>{results['feedback']}</div>"
    ui.glow_card(feedback_html, accent="#8B5CF6")