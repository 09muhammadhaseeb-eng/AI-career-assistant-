"""
Chat interface component — message history + input box + file upload.
"""
from __future__ import annotations

import streamlit as st
import os


WELCOME = """👋 Hi! I'm your AI career assistant.

I can help you:
- **Find** jobs, internships, and scholarships matched to your background
- **Review** your resume or cover letter
- **Prepare** for interviews with practice questions and feedback
- **Plan** your career path with honest, actionable advice

Tell me what you're looking for, or use the quick-start buttons in the sidebar to get going.
"""


def _avatar(role: str) -> str:
    return "🎯" if role == "assistant" else "👤"


def render_chat(profile: dict, ai_fn) -> None:
    """
    Render full chat UI.

    Parameters
    ----------
    profile : dict
        User profile from sidebar.
    ai_fn : callable
        Function(messages, profile, file_text) -> str  that calls the LLM.
    """
    # ── Init session state ────────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "file_content" not in st.session_state:
        st.session_state["file_content"] = ""

    # ── Conversation history ──────────────────────────────────────────────
    # Welcome message when conversation is empty
    if not st.session_state["messages"]:
        with st.chat_message("assistant", avatar="🎯"):
            st.markdown(WELCOME)

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"], avatar=_avatar(msg["role"])):
            st.markdown(msg["content"])

    # ── File upload (collapsible) ─────────────────────────────────────────
    with st.expander("📎 Attach a file for review (resume, cover letter, etc.)", expanded=False):
        uploaded = st.file_uploader(
            "Upload a .txt or .pdf file",
            type=["txt", "pdf"],
            label_visibility="collapsed",
        )
        if uploaded:
            if uploaded.type == "application/pdf":
                try:
                    import pdfplumber
                    with pdfplumber.open(uploaded) as pdf:
                        text = "\n".join(p.extract_text() or "" for p in pdf.pages)
                    st.session_state["file_content"] = text
                    st.success(f"✅ Loaded {uploaded.name} ({len(text):,} characters)")
                except Exception as e:
                    st.error(f"Could not read PDF: {e}")
            else:
                text = uploaded.read().decode("utf-8", errors="ignore")
                st.session_state["file_content"] = text
                st.success(f"✅ Loaded {uploaded.name} ({len(text):,} characters)")

        if st.session_state["file_content"]:
            if st.button("🗑️ Remove file", key="remove_file"):
                st.session_state["file_content"] = ""
                st.rerun()

    # ── Quick-prompt injection ────────────────────────────────────────────
    if "quick_prompt" in st.session_state and st.session_state["quick_prompt"]:
        quick = st.session_state.pop("quick_prompt")
        _send_message(quick, profile, ai_fn)
        st.rerun()

    # ── Chat input ────────────────────────────────────────────────────────
    if user_input := st.chat_input("Ask about jobs, internships, scholarships, or career advice…"):
        _send_message(user_input, profile, ai_fn)


def _send_message(user_input: str, profile: dict, ai_fn) -> None:
    """Append user message, call AI, append assistant response."""
    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🎯"):
        with st.spinner("Thinking…"):
            # Check for API key
            api_key = st.session_state.get("api_key") or os.environ.get("ANTHROPIC_API_KEY", "")
            if not api_key:
                response = (
                    "⚠️ **No API key found.**\n\n"
                    "Please enter your Anthropic API key in **⚙️ Settings** in the sidebar, "
                    "or set the `ANTHROPIC_API_KEY` secret on Streamlit Cloud.\n\n"
                    "Get your key at [console.anthropic.com](https://console.anthropic.com)."
                )
            else:
                os.environ["ANTHROPIC_API_KEY"] = api_key
                try:
                    response = ai_fn(
                        messages=st.session_state["messages"],
                        profile=profile,
                        file_text=st.session_state.get("file_content", ""),
                    )
                except Exception as e:
                    err = str(e)
                    if "authentication" in err.lower() or "api_key" in err.lower() or "401" in err:
                        response = (
                            "⚠️ **Invalid API key.** Please check the key in Settings and try again."
                        )
                    elif "rate_limit" in err.lower() or "429" in err:
                        response = (
                            "⏳ **Rate limit hit.** Please wait a moment and try again."
                        )
                    else:
                        response = f"❌ Something went wrong: `{err}`"

        st.markdown(response)

    st.session_state["messages"].append({"role": "assistant", "content": response})
    # Clear file after it's been sent once so it's not re-appended
    if st.session_state.get("file_content"):
        st.session_state["file_content"] = ""
