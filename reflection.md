# Model Card — PawPal+ AI Advisor

## Model Details
- **Model used:** Google Gemini 2.5 Flash
- **Provider:** Google AI Studio (free tier)
- **Access method:** Gemini API via `google-genai` Python library
- **Integration file:** `ai_advisor.py`

---

## Intended Use
The AI Advisor in PawPal+ is designed to:
- Answer general pet care questions based on a pet's species and age
- Suggest a starter task list for a new pet profile
- Provide confidence scores so users know how reliable each response is

This tool is intended for **general pet care guidance only** and is not a replacement for professional veterinary advice.

---

## AI Collaboration
This project was built with AI assistance throughout the development process including:
- Debugging code errors and API integration issues
- Generating boilerplate code for the Gemini API connection
- Suggesting prompt structures for reliable JSON output from the AI
- Understanding the complexity of code and brainstorming ideas

All AI-generated code was reviewed, tested, and modified before being included in the final project.

---

## Limitations and Biases
- **Species bias:** The model performs better for common pets (dogs, cats) than exotic or uncommon species
- **Age generalization:** Advice may not account for breed-specific needs within a species
- **No memory:** The AI has no memory between questions — each request is independent
- **Hallucination risk:** The model may occasionally give confident but incorrect advice
- **Rate limits:** The free tier has usage limits that can cause temporary unavailability

---

## Guardrails and Safety
- All AI responses are wrapped in try/except blocks — the app never crashes due to AI failure
- When the AI is unavailable, a clear error message is shown to the user
- Confidence scores below 0.5 are labeled as "Low confidence" to warn users
- The system always reminds users that AI advice is not a substitute for a vet

---

## Testing Results
- 9/9 core scheduler tests passing
- AI advisor tested with 3+ different pet profiles and question types
- Confidence scores averaged 0.85 across test queries
- App remained functional when AI was rate-limited (graceful fallback confirmed)

---

## Ethical Considerations
- **Transparency:** Users can see the confidence score for every AI response
- **Human oversight:** Users manually review and approve AI-suggested tasks before they are added to the schedule
- **No personal data stored:** The app does not store or log any user inputs or pet data beyond the current session
- **Responsible defaults:** The app defaults to the human-designed scheduler even when AI suggestions are available

---

## Reflection Prompts

### What did you learn about AI from this project?
I learned that integrating AI into a real application requires just as much work on the *reliability* side as on the feature side. Handling rate limits, parsing structured outputs, and writing fallback logic took more time than writing the AI prompts themselves.

### What surprised you?
I was surprised by the AI integration code. Writing an AI advisor code is relatively very simple compared to what I thought before working on this project. The prompts written in the ai_advisor file clarified many AI integration concepts.

### What would you do differently?
I would set up a local Heuristic model earlier in the project so rate limit issues don't block development. I would also add more thorough input validation before sending requests to the API. 

### What are the risks of deploying this AI system?
This AI system is not perfect. Making a full AI system requires training, checking the rules, guardrails, and many other parameters. This model is just for concept practices. If this AI is deployed, then there is a risk that it will provide responses that can harm pets.