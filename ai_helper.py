import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


# Load OPENAI_API_KEY and optional OPENAI_MODEL from the local .env file.
load_dotenv()


def _build_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise RuntimeError("AI Assistant is not connected yet. Please set OPENAI_API_KEY.")
    return OpenAI(api_key=api_key)


def ask_ai(question):
    """Send a study question to OpenAI and return the response text."""
    client = _build_client()
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        instructions=(
            "You are the BMCC StudyTogether AI Study Assistant. Give concise, practical, "
            "student-friendly help. Always format your answer with exactly these markdown "
            "sections: Short Summary, Study Explanation, 3 Practice Questions, Study Tips. "
            "The 3 Practice Questions section must contain exactly three numbered questions."
        ),
        input=question,
        max_output_tokens=750,
    )
    answer = getattr(response, "output_text", "").strip()
    if not answer:
        raise RuntimeError("The AI response was empty. Please try asking again.")
    return answer


__all__ = ["OpenAIError", "ask_ai"]
