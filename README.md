# PawPal+ 🐾

> An AI-powered pet care scheduling system that helps owners stay consistent with daily pet care.

## Original Project
This project is an extension of **PawPal+** built during Module 3. The original system allowed pet owners to create pet profiles, add care tasks, and generate a priority-based daily schedule. It included conflict detection, recurring task management, and a Streamlit UI.

---

## What's New in the Final Version
- **AI Care Advisor** — Ask natural language pet care questions and get answers powered by Gemini AI with a confidence score
- **AI Task Suggester** — Automatically generate a starter task list based on your pet's species and age
- **Guardrails** — Error handling and fallback messaging when the AI is unavailable
- **Bug Fixes** — Updating and fixing bugs from previous PawPal+ system like deletion of tasks and updating PawPal+ UML diagram.

---

## System Architecture
![System Architecture](assets/System%20Architecture.png)

The system has four main layers:
1. **Streamlit UI** (`app.py`) — the user-facing interface
2. **Core Scheduler** (`pawpal_system.py`) — handles task management, priority sorting, and conflict detection
3. **AI Advisor** (`ai_advisor.py`) — connects to Gemini API for pet care advice and task suggestions
4. **Testing + Reliability** — pytest suite, conflict logging, and confidence scoring

---

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/Fahad5800/Applied-AI-PawPal-.git
cd Applied-AI-PawPal-
```

### 2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API key
Create a `.env` file in the project root:
GEMINI_API_KEY=your-key-here

### 5. Run the app
```bash
streamlit run app.py
```

---

## Sample Interactions

### Example 1 — Ask the AI Advisor
**Input:** "How often should I walk my dog?"
**Pet:** Buddy, Dog, Age 3
**Output:** "For an adult dog like 3-year-old Buddy, aim for at least two walks per day. These walks are crucial for his physical exercise, mental stimulation, and regular potty breaks."
**Confidence:** 100%

### Example 2 — AI Task Suggestions
**Input:** Click "Suggest Tasks with AI" for a 3-year-old dog
**Output:** Morning Walk (30 min, daily), Feed Breakfast (10 min, daily), Evening Play (20 min, daily), Grooming (15 min, weekly), Vet Checkup (60 min, monthly)

### Example 3 — Conflict Detection
**Input:** Two tasks scheduled at overlapping times
**Output:** Warning banner showing both task names and the exact overlapping time range

---

## Design Decisions
- **Gemini AI** was chosen for the free tier availability suitable for this project
- **Greedy scheduling algorithm** was kept from the original — it's simple, fast, and predictable
- **Confidence scoring** was added to help users understand when AI advice is reliable vs uncertain
- **Session state** in Streamlit was used to persist suggested tasks between button clicks, solving a common re-render issue

---

## Testing Summary
Run the full test suite with:
\```bash
python -m pytest
\```

**What worked:**
- All 9 core scheduler tests pass consistently
- Conflict detection correctly identifies overlapping time slots
- Recurring task rescheduling works across daily, weekly, and monthly frequencies
- AI advisor returns structured responses with confidence scores

**What didn't work:**
- Gemini API rate limits caused failures during rapid testing — solved by adding try/except with fallback messages
- JSON parsing from AI occasionally failed when the model added extra text — solved by stripping markdown code blocks before parsing

**What I learned:**
- Reliable AI integration requires as much error handling as feature code
- Prompt engineering matters — small changes in how you ask for JSON output significantly affect reliability

---

## Reflection
This project taught me how to integrate AI into a real working application. The biggest challenge was handling API rate limits and model availability gracefully — the app needed to keep working even when the AI was unavailable. I learned that guardrails and fallback messaging are just as important as the AI features themselves.

## Reflection
This project taught me that building with AI is really two jobs in one: building the feature, and building the safety net around it. The AI advisor only works well because of the guardrails around it — without error handling, rate limit fallbacks, and confidence scoring, it would feel unreliable to a real user.

I also learned that prompt design is a form of engineering. Getting the model to return clean, parseable JSON every time required careful iteration on the prompt format.

If I were to extend this further, I would add a local fallback model so the app works completely offline, and a more sophisticated RAG system that pulls from a real pet care knowledge base rather than relying solely on the model's training data.

---

## Demo
🎥 [Loom Walkthrough](your-loom-link-here) — *(add after recording)*