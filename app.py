"""
CareerPath AI — Main Streamlit application.
Entry point: app.py (repo root)
"""
import os
import streamlit as st

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="CareerPath AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-username/ai-career-assistant",
        "Report a Bug": "https://github.com/your-username/ai-career-assistant/issues",
        "About": "CareerPath AI — Powered by Claude",
    },
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Fonts & base ───────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Hide default Streamlit chrome ──────────────────────────── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* ── Sidebar header ─────────────────────────────────────────── */
    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 4px 0 12px 0;
    }
    .sidebar-logo { font-size: 1.8rem; }
    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ── Page header ────────────────────────────────────────────── */
    .page-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.25rem;
    }
    .page-title {
        font-size: 1.75rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }
    .page-sub {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-bottom: 1rem;
    }

    /* ── Opportunity cards ──────────────────────────────────────── */
    .opp-card {
        background: #1a1a24;
        border: 1px solid #2d2d42;
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s ease, transform 0.15s ease;
    }
    .opp-card:hover {
        border-color: #6366f1;
        transform: translateY(-1px);
    }
    .opp-card-type {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .opp-card-title {
        font-size: 1rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.25rem;
        line-height: 1.3;
    }
    .opp-card-org {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 0.3rem;
    }
    .opp-card-meta {
        font-size: 0.78rem;
        color: #64748b;
        margin-bottom: 0.5rem;
    }
    .opp-card-summary {
        font-size: 0.85rem;
        color: #cbd5e1;
        line-height: 1.5;
        margin-bottom: 0.6rem;
    }
    .opp-card-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 0.75rem;
    }
    .tag {
        background: #2d2d42;
        color: #a78bfa;
        border-radius: 999px;
        padding: 2px 10px;
        font-size: 0.72rem;
        font-weight: 500;
    }
    .opp-card-link {
        display: inline-block;
        font-size: 0.82rem;
        font-weight: 600;
        color: #6366f1;
        text-decoration: none;
        border-bottom: 1px solid transparent;
        transition: border-color 0.15s;
    }
    .opp-card-link:hover { border-bottom-color: #6366f1; }

    /* ── Chat tweaks ────────────────────────────────────────────── */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }
    [data-testid="stChatInputContainer"] {
        border-top: 1px solid #2d2d42;
        padding-top: 0.75rem;
    }

    /* ── Stat strip ─────────────────────────────────────────────── */
    .stat-strip {
        display: flex;
        gap: 24px;
        background: #1a1a24;
        border: 1px solid #2d2d42;
        border-radius: 10px;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }
    .stat-item { display: flex; align-items: center; gap: 8px; }
    .stat-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #a78bfa;
    }
    .stat-label {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 400;
    }

    /* ── Tab styling ────────────────────────────────────────────── */
    [data-testid="stTabs"] [role="tablist"] {
        gap: 4px;
        border-bottom: 1px solid #2d2d42;
        margin-bottom: 1rem;
    }
    [data-testid="stTabs"] [role="tab"] {
        border-radius: 6px 6px 0 0;
        font-weight: 500;
        font-size: 0.9rem;
    }

    /* ── Mobile ─────────────────────────────────────────────────── */
    @media (max-width: 640px) {
        .stat-strip { gap: 14px; }
        .opp-card { padding: 0.9rem 1rem; }
        .page-title { font-size: 1.4rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Load secrets / env ───────────────────────────────────────────────────────
# Support Streamlit Cloud secrets
if "ANTHROPIC_API_KEY" in st.secrets:
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

# ── Imports (after path is known clean) ─────────────────────────────────────
from components.sidebar import render_sidebar
from components.chat import render_chat
from components.explorer import render_explorer
from utils.ai_client import stream_response
from utils.database import _load

# ── Render sidebar, get profile ───────────────────────────────────────────────
profile = render_sidebar()

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="page-header">
        <span style="font-size:2rem;">🎯</span>
        <h1 class="page-title">CareerPath AI</h1>
    </div>
    <p class="page-sub">Your AI mentor for jobs, internships, and scholarships — from search to offer.</p>
    """,
    unsafe_allow_html=True,
)

# ── Stats strip ───────────────────────────────────────────────────────────────
all_opps = _load()
n_jobs = sum(1 for o in all_opps if o["type"] == "job")
n_intern = sum(1 for o in all_opps if o["type"] == "internship")
n_scholar = sum(1 for o in all_opps if o["type"] == "scholarship")

st.markdown(
    f"""
    <div class="stat-strip">
        <div class="stat-item">
            <span class="stat-value">{len(all_opps)}</span>
            <span class="stat-label">Total Listings</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">{n_jobs}</span>
            <span class="stat-label">💼 Jobs</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">{n_intern}</span>
            <span class="stat-label">🎓 Internships</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">{n_scholar}</span>
            <span class="stat-label">🏆 Scholarships</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Main tabs ─────────────────────────────────────────────────────────────────
tab_chat, tab_explore = st.tabs(["💬 AI Assistant", "🔭 Browse Listings"])

with tab_chat:
    render_chat(profile=profile, ai_fn=stream_response)

with tab_explore:
    render_explorer()
