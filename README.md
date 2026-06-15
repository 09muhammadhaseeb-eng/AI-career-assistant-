# 🎯 CareerPath AI

An AI-powered career assistant that helps you discover jobs, internships, and scholarships — then guides you from search all the way to offer letter.

Built with **Claude (Anthropic)** + **Streamlit**. Deployable to Streamlit Cloud in under 5 minutes.

---

## ✨ Features

| Feature | Details |
|---|---|
| 💬 AI Chat | Powered by Claude with tool-calling — finds real listings from the DB |
| 🔭 Browse Listings | Filter 24+ curated opportunities by type, field & education |
| 📄 Resume Review | Upload .txt or .pdf files for AI feedback |
| 🎓 Interview Prep | Practice questions, answer frameworks, feedback |
| 🏆 Scholarship Finder | 7+ scholarships from Gates to NSF |
| 🌙 Dark UI | Polished dark theme, mobile-first layout |

---

## 🚀 Deploy to Streamlit Cloud (Recommended)

### Step 1 — Fork / Clone & Push to GitHub

```bash
# Clone this repo (or create a new one and copy the files in)
git clone https://github.com/your-username/ai-career-assistant.git
cd ai-career-assistant

# If starting fresh:
git init
git add .
git commit -m "Initial commit — CareerPath AI"

# Create a GitHub repo (via github.com or gh CLI), then:
git remote add origin https://github.com/YOUR_USERNAME/ai-career-assistant.git
git branch -M main
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub
2. Click **"New app"**
3. Select your repository, branch (`main`), and set **Main file path** to `app.py`
4. Click **"Deploy"**

### Step 3 — Add your API Key (Secrets)

In your Streamlit Cloud app dashboard:

1. Click **⋮ → Settings → Secrets**
2. Add the following:

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-..."
```

3. Click **Save** — the app will reboot automatically

> **Get your key**: [console.anthropic.com](https://console.anthropic.com) → API Keys → Create Key

---

## 💻 Run Locally

```bash
# 1. Clone
git clone https://github.com/your-username/ai-career-assistant.git
cd ai-career-assistant

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
export ANTHROPIC_API_KEY="sk-ant-api03-..."   # macOS/Linux
# set ANTHROPIC_API_KEY=sk-ant-api03-...      # Windows CMD

# 5. Run
streamlit run app.py
```

App opens at `http://localhost:8501`

> **No API key yet?** The app still works — the Browse tab shows all listings without any API calls. You'll need a key for the AI chat.

---

## 📁 Project Structure

```
ai-career-assistant/
├── app.py                    # Main entry point
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml           # Dark theme + server config
├── components/
│   ├── __init__.py
│   ├── sidebar.py            # User profile + quick-start prompts
│   ├── chat.py               # Chat interface + file upload
│   └── explorer.py           # Searchable card grid
├── utils/
│   ├── __init__.py
│   ├── ai_client.py          # Anthropic API + tool-call loop
│   └── database.py           # Local opportunity search
└── data/
    └── opportunities.json    # 24+ curated listings
```

---

## 🔧 Configuration

### Streamlit theme (`.streamlit/config.toml`)
Edit `primaryColor`, `backgroundColor`, or `font` to match your brand.

### Adding more opportunities (`data/opportunities.json`)
Each entry follows this schema:

```json
{
  "id": 25,
  "type": "job",                          // "job" | "internship" | "scholarship"
  "title": "Role Title",
  "organization": "Company Name",
  "location": "City, State (Remote OK)",
  "deadline": "December 1, 2025",
  "field": ["computer science", "tech"],  // keywords for matching
  "education_level": ["bachelor"],        // "associate"|"bachelor"|"master"|"phd"
  "experience_level": "entry",            // "intern"|"entry"|"mid"|"senior"|"graduate"
  "summary": "One-sentence pitch.",
  "link": "https://example.com/careers",
  "tags": ["python", "remote", "saas"]    // for card display + search
}
```

### Replacing mock web_search
In `utils/ai_client.py`, find the `web_search` tool handler and replace the stub with a real call to Brave Search, Serper, or Tavily:

```python
if tool_name == "web_search":
    # Example with Serper (https://serper.dev)
    import requests
    r = requests.post(
        "https://google.serper.dev/search",
        json={"q": tool_input["query"]},
        headers={"X-API-KEY": os.environ["SERPER_API_KEY"]},
    )
    results = r.json().get("organic", [])
    return "\n".join(f"{i['title']}: {i['link']}" for i in results[:5])
```

---

## 🛡️ Privacy

- No conversation data is stored between sessions (Streamlit's default stateless model)
- Uploaded files are processed in-memory and not written to disk
- API keys entered in the sidebar are stored only in `st.session_state` for the duration of the session

---

## 📝 License

MIT — use freely, attribution appreciated.
