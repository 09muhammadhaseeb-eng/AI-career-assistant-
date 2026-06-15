"""
Opportunities explorer — searchable card grid for browsing the database directly.
"""
from __future__ import annotations

import streamlit as st
from utils.database import search_opportunities, _load


TYPE_ICONS = {"job": "💼", "internship": "🎓", "scholarship": "🏆"}
TYPE_COLORS = {
    "job": "#3b82f6",
    "internship": "#8b5cf6",
    "scholarship": "#f59e0b",
}


def render_explorer() -> None:
    """Render the searchable opportunity browser."""
    st.markdown("## 🔭 Browse Opportunities")
    st.caption("Search and filter all 24+ listings in our curated database.")

    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        query = st.text_input("Search", placeholder="e.g. data science, nursing, scholarship…", label_visibility="collapsed")
    with col2:
        opp_type = st.selectbox("Type", ["All", "Job", "Internship", "Scholarship"], label_visibility="collapsed")
    with col3:
        edu = st.selectbox(
            "Education",
            ["All", "High School", "Associate", "Bachelor", "Master", "PhD"],
            label_visibility="collapsed",
        )

    edu_map = {
        "All": None,
        "High School": "high school",
        "Associate": "associate",
        "Bachelor": "bachelor",
        "Master": "master",
        "PhD": "phd",
    }

    results = search_opportunities(
        query=query,
        opp_type=None if opp_type == "All" else opp_type.lower(),
        education_level=edu_map[edu],
        limit=30,
    )

    # If nothing searched, show everything
    if not query and opp_type == "All" and edu == "All":
        results = _load()

    st.markdown(f"**{len(results)} result{'s' if len(results) != 1 else ''}**")
    st.markdown("---")

    if not results:
        st.info("No matches found. Try broadening your search.")
        return

    # 2-column card grid
    cols = st.columns(2)
    for i, r in enumerate(results):
        icon = TYPE_ICONS.get(r["type"], "📌")
        color = TYPE_COLORS.get(r["type"], "#6b7280")
        with cols[i % 2]:
            st.markdown(
                f"""
                <div class="opp-card">
                    <div class="opp-card-type" style="color:{color};">
                        {icon} {r['type'].upper()}
                    </div>
                    <div class="opp-card-title">{r['title']}</div>
                    <div class="opp-card-org">🏢 {r['organization']}</div>
                    <div class="opp-card-meta">
                        📍 {r['location']}&nbsp;&nbsp;|&nbsp;&nbsp;⏰ {r['deadline']}
                    </div>
                    <div class="opp-card-summary">{r['summary']}</div>
                    <div class="opp-card-tags">
                        {"".join(f'<span class="tag">{t}</span>' for t in r["tags"][:4])}
                    </div>
                    <a class="opp-card-link" href="{r['link']}" target="_blank">Apply / Learn More →</a>
                </div>
                """,
                unsafe_allow_html=True,
            )
