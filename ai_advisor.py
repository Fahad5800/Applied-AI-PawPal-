from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask_pet_advisor(question: str, pet_name: str, species: str, age: int) -> dict:
    """Ask the AI a pet care question and get an answer with confidence score."""

    prompt = f"""
You are a knowledgeable pet care advisor. A pet owner is asking about their pet.

Pet Info:
- Name: {pet_name}
- Species: {species}
- Age: {age} years old

Question: {question}

Respond in this exact format:
ANSWER: (your answer here, 2-3 sentences max)
CONFIDENCE: (a number between 0.0 and 1.0 based on how confident you are)
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()

        answer = ""
        confidence = 0.5

        for line in text.split("\n"):
            if line.startswith("ANSWER:"):
                answer = line.replace("ANSWER:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.replace("CONFIDENCE:", "").strip())
                except ValueError:
                    confidence = 0.5

        return {
            "answer": answer,
            "confidence": confidence,
            "success": True
        }

    except Exception as e:
        return {
            "answer": "Sorry, I couldn't process that question right now.",
            "confidence": 0.0,
            "success": False,
            "error": str(e)
        }


def suggest_tasks(pet_name: str, species: str, age: int) -> dict:
    """Ask the AI to suggest a starter task list for a pet."""

    prompt = f"""
You are a pet care expert. Suggest a daily care task list for this pet.

Pet Info:
- Name: {pet_name}
- Species: {species}
- Age: {age} years old

Return ONLY a JSON list like this, nothing else:
[
  {{"task": "Morning Walk", "duration_minutes": 30, "priority": 1, "frequency": "daily"}},
  {{"task": "Feed Breakfast", "duration_minutes": 10, "priority": 1, "frequency": "daily"}}
]

Rules:
- Suggest 4-6 tasks appropriate for this species and age
- Priority must be 1 (high), 2 (medium), or 3 (low)
- Frequency must be daily, weekly, or monthly
- Duration must be a realistic number in minutes
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        tasks = json.loads(text)

        return {
            "tasks": tasks,
            "success": True
        }

    except Exception as e:
        return {
            "tasks": [],
            "success": False,
            "error": str(e)
        }