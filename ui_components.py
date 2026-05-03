"""
UI Components — Vibrant, animated, production-grade Streamlit components.
Neon-dark aesthetic with glowing accents and smooth animations.
"""

import plotly.graph_objects as go
import streamlit as st


def safe_html(html_str: str):
    # Remove all leading whitespace from every line so Streamlit doesn't render it as a markdown code block
    cleaned = "\n".join(line.lstrip() for line in html_str.split("\n"))
    st.markdown(cleaned, unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────────────

def inject_global_styles():
    """Inject all global CSS — call once at the top of app.py."""
    safe_html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap');

    /* ── Root Variables ── */
    :root {
        --bg-primary:    #05060F;
        --bg-secondary:  #0D0F1E;
        --bg-card:       #111327;
        --bg-glass:      rgba(255,255,255,0.03);
        --border:        rgba(255,255,255,0.07);
        --accent-blue:   #4F8EF7;
        --accent-cyan:   #00E5FF;
        --accent-green:  #00FF88;
        --accent-orange: #FF9800;
        --accent-pink:   #FF4B7B;
        --accent-gold:   #FFD700;
        --text-primary:  #F0F2FF;
        --text-muted:    #8890B5;
        --radius-card:   18px;
        --radius-btn:    12px;
        --font-display:  'Syne', sans-serif;
        --font-mono:     'Space Mono', monospace;
    }

    /* ── Global Reset ── */
    html, body, .stApp {
        background: var(--bg-primary) !important;
        font-family: var(--font-display) !important;
        color: var(--text-primary) !important;
    }

    /* ── Hide Streamlit default chrome ── */
    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1200px !important; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] * { font-family: var(--font-display) !important; }

    /* ── Input fields ── */
    input, textarea, [data-baseweb="input"] input {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius-btn) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-mono) !important;
        transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
    }
    input:focus, textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 3px rgba(79,142,247,0.18) !important;
    }

    /* ── Select boxes ── */
    [data-baseweb="select"] > div {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius-btn) !important;
        color: var(--text-primary) !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-cyan) 100%) !important;
        color: #05060F !important;
        font-family: var(--font-display) !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.06em !important;
        border: none !important;
        border-radius: var(--radius-btn) !important;
        padding: 0.65rem 1.8rem !important;
        cursor: pointer !important;
        transition: transform 0.15s ease, box-shadow 0.2s ease !important;
        box-shadow: 0 4px 20px rgba(79,142,247,0.35) !important;
        text-transform: uppercase !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(79,142,247,0.55) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── File uploader ── */
    [data-testid="stFileUploadDropzone"] {
        background: var(--bg-card) !important;
        border: 2px dashed rgba(79,142,247,0.4) !important;
        border-radius: var(--radius-card) !important;
        transition: border-color 0.25s ease !important;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: var(--accent-cyan) !important;
        background: rgba(79,142,247,0.06) !important;
    }

    /* ── Progress bar ── */
    [data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)) !important;
        border-radius: 999px !important;
    }
    [data-testid="stProgressBar"] > div {
        background: var(--bg-card) !important;
        border-radius: 999px !important;
    }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-card) !important;
    }

    /* ── Success / Warning / Error boxes ── */
    [data-testid="stAlert"] {
        border-radius: var(--radius-card) !important;
        font-family: var(--font-display) !important;
        border-left-width: 4px !important;
    }

    /* ── Metric ── */
    [data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-card) !important;
        padding: 1.2rem 1.5rem !important;
    }
    [data-testid="metric-container"] label { color: var(--text-muted) !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        font-size: 2rem !important;
    }

    /* ── Divider ── */
    hr {
        border: none !important;
        border-top: 1px solid var(--border) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-secondary); }
    ::-webkit-scrollbar-thumb { background: rgba(79,142,247,0.4); border-radius: 999px; }

    /* ── Animations ── */
    @keyframes glow-pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.6; }
    }
    @keyframes slide-up {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes badge-pop {
        0%   { transform: scale(0.7); opacity: 0; }
        70%  { transform: scale(1.08); }
        100% { transform: scale(1); opacity: 1; }
    }
    @keyframes shimmer {
        0%   { background-position: -400px 0; }
        100% { background-position: 400px 0; }
    }
    </style>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────

def render_header(title: str, subtitle: str = ""):
    safe_html(f"""
<div style="
        animation: slide-up 0.5s ease forwards;
        margin-bottom: 2rem;
        padding: 2.5rem 2.5rem 2rem;
        background: linear-gradient(135deg, rgba(79,142,247,0.12) 0%, rgba(0,229,255,0.06) 100%);
        border: 1px solid rgba(79,142,247,0.2);
        border-radius: 24px;
        position: relative;
        overflow: hidden;
    ">
        <!-- Decorative blobs -->
        <div style="
            position:absolute; top:-40px; right:-40px;
            width:160px; height:160px;
            background: radial-gradient(circle, rgba(0,229,255,0.18) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        "></div>
        <div style="
            position:absolute; bottom:-30px; left:40px;
            width:120px; height:120px;
            background: radial-gradient(circle, rgba(79,142,247,0.14) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        "></div>

        <div style="position:relative; z-index:1;">
            <span style="
                font-family:'Space Mono',monospace;
                font-size:0.72rem;
                letter-spacing:0.2em;
                color:#4F8EF7;
                text-transform:uppercase;
                display:block;
                margin-bottom:0.5rem;
            ">AI · PAPER · CORRECTION · SYSTEM</span>
            <h1 style="
                font-family:'Syne',sans-serif;
                font-size:clamp(1.8rem, 4vw, 2.8rem);
                font-weight:800;
                margin:0 0 0.6rem;
                background: linear-gradient(90deg, #F0F2FF 0%, #4F8EF7 50%, #00E5FF 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                line-height: 1.15;
            ">{title}</h1>
            { f'<p style="color:#8890B5; font-size:1rem; margin:0; font-family:Syne,sans-serif;">{subtitle}</p>' if subtitle else '' }
        </div>
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION LABEL
# ─────────────────────────────────────────────────────────────────────────────

def section_label(text: str, accent: str = "#4F8EF7"):
    safe_html(f"""
<div style="
        display:flex; align-items:center; gap:0.75rem;
        margin-bottom:1rem; margin-top:0.5rem;
        animation: slide-up 0.4s ease forwards;
    ">
        <div style="width:4px; height:22px; background:{accent};
                    border-radius:999px; flex-shrink:0;"></div>
        <span style="
            font-family:'Syne',sans-serif;
            font-size:1.05rem; font-weight:700;
            color:#F0F2FF; letter-spacing:0.03em;
        ">{text}</span>
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# GLOWING CARD
# ─────────────────────────────────────────────────────────────────────────────

def glow_card(content_html: str, accent: str = "#4F8EF7", animate: bool = True):
    anim = "animation: slide-up 0.45s ease forwards;" if animate else ""
    safe_html(f"""
<div style="
        {anim}
        background: var(--bg-card, #111327);
        border: 1px solid rgba(79,142,247,0.15);
        border-radius: 18px;
        padding: 1.6rem 1.8rem;
        box-shadow: 0 0 30px rgba(79,142,247,0.07),
                    inset 0 1px 0 rgba(255,255,255,0.05);
        position: relative;
        overflow: hidden;
        margin-bottom: 1rem;
    ">
        <div style="
            position:absolute; top:0; left:0; right:0; height:3px;
            background: linear-gradient(90deg, transparent, {accent}, transparent);
            opacity: 0.7;
        "></div>
        {content_html}
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# RANK BADGE
# ─────────────────────────────────────────────────────────────────────────────

def render_rank_badge(rank: dict, score: float):
    color  = rank["color"]
    bg     = rank["bg"]
    glow   = rank["glow"]
    label  = rank["label"]
    emoji  = rank["emoji"]
    badge  = rank["badge"]
    msg    = rank["message"]

    safe_html(f"""
<div style="
        animation: slide-up 0.5s ease 0.1s both;
        background: {bg};
        border-radius: 22px;
        padding: 2.5rem 2rem;
        text-align: center;
        box-shadow: 0 0 60px {glow}, 0 8px 32px rgba(0,0,0,0.5);
        margin: 1.5rem 0;
        position: relative;
        overflow: hidden;
    ">
        <!-- Shimmer effect -->
        <div style="
            position:absolute; inset:0;
            background: linear-gradient(105deg, transparent 30%, rgba(255,255,255,0.12) 50%, transparent 70%);
            background-size: 400px 100%;
            animation: shimmer 2.5s infinite;
        "></div>

        <div style="position:relative; z-index:1;">
            <div style="font-size:3.5rem; margin-bottom:0.5rem;
                        animation: badge-pop 0.5s ease 0.3s both;">{emoji}</div>
            <div style="
                font-family:'Space Mono',monospace;
                font-size:0.7rem; letter-spacing:0.22em;
                color:rgba(5,6,15,0.75); text-transform:uppercase;
                margin-bottom:0.3rem;
            ">{badge}</div>
            <div style="
                font-family:'Syne',sans-serif;
                font-size:2rem; font-weight:800;
                color:#05060F; line-height:1.1;
                margin-bottom:0.8rem;
            ">{label}</div>
            <div style="
                font-family:'Space Mono',monospace;
                font-size:2.8rem; font-weight:700;
                color:rgba(5,6,15,0.85);
                margin-bottom:0.8rem;
            ">{score:.1f}<span style="font-size:1.2rem;">/100</span></div>
            <p style="
                font-family:'Syne',sans-serif;
                font-size:0.92rem; color:rgba(5,6,15,0.7);
                margin:0; max-width:340px; margin:0 auto;
            ">{msg}</p>
        </div>
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# SCORE CHART
# ─────────────────────────────────────────────────────────────────────────────

def score_chart(content: float, similarity: float, concept: float):
    """Animated neon bar chart with per-bar color coding."""

    bars = [
        {"label": "Content",    "val": content,    "color": "#4F8EF7"},
        {"label": "Similarity", "val": similarity, "color": "#00E5FF"},
        {"label": "Concept",    "val": concept,    "color": "#00FF88"},
    ]

    fig = go.Figure()

    for b in bars:
        fig.add_trace(go.Bar(
            x=[b["label"]],
            y=[b["val"]],
            name=b["label"],
            marker=dict(
                color=b["color"],
                line=dict(color="rgba(255,255,255,0.15)", width=1),
                opacity=0.92,
            ),
            text=[f"<b>{b['val']:.1f}</b>"],
            textposition="outside",
            textfont=dict(color=b["color"], size=14, family="Space Mono"),
            width=0.45,
        ))

    fig.update_layout(
        title=dict(
            text="📊  Score Breakdown",
            font=dict(family="Syne", size=18, color="#F0F2FF"),
            x=0.02,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,19,39,0.6)",
        showlegend=False,
        height=340,
        margin=dict(l=20, r=20, t=55, b=20),
        yaxis=dict(
            range=[0, 110],
            tickfont=dict(color="#8890B5", family="Space Mono", size=11),
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.08)",
        ),
        xaxis=dict(
            tickfont=dict(color="#F0F2FF", family="Syne", size=14),
            showgrid=False,
        ),
        bargap=0.3,
    )

    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# RADAR CHART (bonus component)
# ─────────────────────────────────────────────────────────────────────────────

def radar_chart(content: float, similarity: float, concept: float,
                accuracy: float = None, clarity: float = None):
    """Neon radar/spider chart for holistic score view."""
    categories = ["Content", "Similarity", "Concept"]
    values     = [content, similarity, concept]

    if accuracy is not None:
        categories.append("Accuracy")
        values.append(accuracy)
    if clarity is not None:
        categories.append("Clarity")
        values.append(clarity)

    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor="rgba(79,142,247,0.15)",
        line=dict(color="#4F8EF7", width=2.5),
        marker=dict(color="#00E5FF", size=8, symbol="circle"),
        name="Score",
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(17,19,39,0.7)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="rgba(255,255,255,0.08)",
                tickfont=dict(color="#8890B5", family="Space Mono", size=10),
                tickvals=[20, 40, 60, 80, 100],
            ),
            angularaxis=dict(
                tickfont=dict(color="#F0F2FF", family="Syne", size=13),
                gridcolor="rgba(255,255,255,0.07)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        height=320,
        margin=dict(l=30, r=30, t=40, b=30),
        title=dict(
            text="🎯  Holistic Score Radar",
            font=dict(family="Syne", size=18, color="#F0F2FF"),
            x=0.02,
        ),
    )

    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# STAT PILLS (mini metric row)
# ─────────────────────────────────────────────────────────────────────────────

def stat_pills(stats: list[dict]):
    """
    Render a horizontal row of glowing stat pills.
    Each dict: { "label": str, "value": str, "color": str }
    """
    pills_html = ""
    for s in stats:
        c = s.get("color", "#4F8EF7")
        pills_html += f"""
        <div style="
            flex:1; min-width:130px;
            background:rgba(17,19,39,0.9);
            border:1px solid {c}33;
            border-radius:14px;
            padding:1rem 1.2rem;
            text-align:center;
            box-shadow: 0 0 20px {c}1A;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        ">
            <div style="
                font-family:'Space Mono',monospace;
                font-size:1.6rem; font-weight:700;
                color:{c}; margin-bottom:0.25rem;
            ">{s['value']}</div>
            <div style="
                font-family:'Syne',sans-serif;
                font-size:0.78rem; color:#8890B5;
                letter-spacing:0.06em; text-transform:uppercase;
            ">{s['label']}</div>
        </div>
        """

    safe_html(f"""
<div style="
        display:flex; flex-wrap:wrap; gap:0.75rem;
        animation: slide-up 0.4s ease 0.15s both;
        margin-bottom:1rem;
    ">
        {pills_html}
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# QUESTION FEEDBACK CARD
# ─────────────────────────────────────────────────────────────────────────────

def question_card(q_num: any, marks_given: float, marks_max: float,
                  feedback: str, similarity: float, grading_confidence: int = 100, confidence_reason: str = "", delay: float = 0):
    pct = (marks_given / marks_max * 100) if marks_max > 0 else 0

    if pct >= 70:
        accent, icon = "#00FF88", "✅"
    elif pct >= 40:
        accent, icon = "#FF9800", "⚠️"
    else:
        accent, icon = "#FF4B7B", "❌"

    bar_w = int(pct)

    safe_html(f"""
<div style="
        animation: slide-up 0.45s ease {delay}s both;
        background:#111327;
        border:1px solid rgba(255,255,255,0.07);
        border-left: 4px solid {accent};
        border-radius:16px;
        padding:1.4rem 1.6rem;
        margin-bottom:0.9rem;
        box-shadow: 0 0 25px {accent}18;
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.85rem;">
            <div style="font-family:'Syne',sans-serif; font-weight:700; font-size:1rem; color:#F0F2FF;">
                {icon} Question {q_num}
            </div>
            <div style="
                font-family:'Space Mono',monospace; font-size:0.9rem;
                color:{accent}; background:{accent}18;
                padding:0.3rem 0.8rem; border-radius:999px;
                border:1px solid {accent}44;
            ">
                {marks_given}/{marks_max} marks
            </div>
        </div>

        <!-- Progress bar -->
        <div style="background:rgba(255,255,255,0.06); border-radius:999px;
                    height:7px; margin-bottom:1rem; overflow:hidden;">
            <div style="
                width:{bar_w}%;
                height:100%;
                background:linear-gradient(90deg, {accent}88, {accent});
                border-radius:999px;
                transition: width 0.8s ease;
            "></div>
        </div>

        <div style="display:flex; gap:1rem; align-items:flex-start; flex-wrap:wrap;">
            <div style="flex:1; min-width:200px;">
                <div style="font-family:'Space Mono',monospace; font-size:0.72rem;
                            color:#8890B5; letter-spacing:0.1em; margin-bottom:0.3rem;">
                    FEEDBACK
                </div>
                <p style="font-family:'Syne',sans-serif; font-size:0.88rem;
                          color:#D0D4F0; margin:0; line-height:1.55;">
                    {feedback}
                </p>
                {f'''<div style="margin-top:0.8rem; padding:0.6rem 0.8rem; background:rgba(255,75,123,0.1); border-left:3px solid #FF4B7B; border-radius:4px;">
                    <div style="font-family:'Space Mono',monospace; font-size:0.65rem; color:#FF4B7B; letter-spacing:0.1em; margin-bottom:0.2rem;">LOW CONFIDENCE REASON</div>
                    <div style="font-family:'Syne',sans-serif; font-size:0.82rem; color:#F0F2FF;">{confidence_reason}</div>
                </div>''' if grading_confidence < 96 and confidence_reason and "clear" not in confidence_reason.lower() else ''}
            </div>
            <div style="text-align:center; min-width:80px;">
                <div style="font-family:'Space Mono',monospace; font-size:0.72rem;
                            color:#8890B5; letter-spacing:0.1em; margin-bottom:0.3rem;">
                    SIMILARITY
                </div>
                <div style="font-family:'Space Mono',monospace; font-size:1.3rem;
                            font-weight:700; color:{accent};">
                    {similarity:.0%}
                </div>
            </div>
            <div style="text-align:center; min-width:80px; padding-left:1rem; border-left:1px solid rgba(255,255,255,0.1);">
                <div style="font-family:'Space Mono',monospace; font-size:0.72rem;
                            color:#8890B5; letter-spacing:0.1em; margin-bottom:0.3rem;">
                    CONFIDENCE
                </div>
                <div style="font-family:'Space Mono',monospace; font-size:1.3rem;
                            font-weight:700; color:{'#00FF88' if grading_confidence > 80 else '#FF9800' if grading_confidence > 50 else '#FF4B7B'};">
                    {grading_confidence}%
                </div>
            </div>
        </div>
    </div>
    """)
