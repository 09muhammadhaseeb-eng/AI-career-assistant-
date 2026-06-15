"""
Sidebar component — user profile + app controls.
"""
import streamlit as st


EDUCATION_OPTIONS = [
    "High School / GED",
    "Associate's Degree",
    "Bachelor's Degree",
    "Master's Degree",
    "PhD / Doctoral",
    "Professional Degree (JD, MD, etc.)",
    "Bootcamp / Self-taught",
    "Currently Enrolled",
]

FIELD_SUGGESTIONS = [
    "Computer Science",
    "Data Science / Analytics",
    "Software Engineering",
    "Mechanical Engineering",
    "Electrical Engineering",
    "Business / Management",
    "Finance / Economics",
    "Marketing / Communications",
    "Biology / Life Sciences",
    "Chemistry / Chemical Engineering",
    "Environmental Science",
    "Political Science / Public Policy",
    "Nursing / Healthcare",
    "Education",
    "Design / UX",
    "Psychology",
    "Other",
]


def render_sidebar() -> dict:
    """Render the sidebar and return the current user profile dict."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-header">
                <span class="sidebar-logo">🎯</span>
                <span class="sidebar-title">CareerPath AI</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("### Your Profile")
        st.caption("Personalize results by filling in your background.")

        field = st.selectbox(
            "Field of Study / Work",
            [""] + FIELD_SUGGESTIONS,
            index=0,
            help="Your academic or professional discipline",
        )
        if field == "Other":
            field = st.text_input("Enter your field")

        education = st.selectbox(
            "Education Level",
            [""] + EDUCATION_OPTIONS,
            index=0,
        )

        location = st.text_input(
            "Location",
            placeholder="City, State or Remote",
            help="Where you want to work (or 'Remote')",
        )

        goals = st.text_area(
            "Career Goals",
            placeholder="e.g. Land a data science role at a climate startup…",
            height=100,
            help="The more specific, the better the recommendations",
        )

        st.markdown("---")

        # Quick-start prompts
        st.markdown("### Quick Starts")
        prompts = [
            "🔍 Find me jobs in my field",
            "🎓 Show me internships",
            "🏆 What scholarships can I apply for?",
            "📄 Help me improve my resume",
            "🗣️ Prep me for a PM interview",
        ]
        for p in prompts:
            if st.button(p, use_container_width=True, key=f"quick_{p}"):
                st.session_state["quick_prompt"] = p.split(" ", 1)[1]  # strip emoji

        st.markdown("---")

        # API key input
        with st.expander("⚙️ Settings", expanded=False):
            api_key = st.text_input(
                "Anthropic API Key",
                type="password",
                placeholder="sk-ant-...",
                help="Get yours at console.anthropic.com",
                value=st.session_state.get("api_key", ""),
            )
            if api_key:
                st.session_state["api_key"] = api_key
                import os
                os.environ["ANTHROPIC_API_KEY"] = api_key

            st.caption(
                "Set via Streamlit Cloud secrets as `ANTHROPIC_API_KEY` "
                "to avoid entering it each session."
            )

            if st.button("🗑️ Clear Conversation", use_container_width=True):
                st.session_state["messages"] = []
                st.session_state["file_content"] = ""
                st.rerun()

        st.markdown("---")
        st.caption("Built with Claude · [Anthropic](https://anthropic.com)")

    return {
        "field": field,
        "education": education,
        "location": location,
        "goals": goals,
    }
