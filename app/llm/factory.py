import os
from typing import Literal
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

Provider = Literal["groq", "gemini", "openai", "auto"]


def get_llm(
    provider: Provider = "auto",
    temperature: float = 0.7
):
    """
    Centralized LLM factory with env-based selection and safe fallback.
    Priority:
    1. Explicit provider argument
    2. LLM_PROVIDER from .env
    3. Auto-detect based on available keys
    """

    # 1️⃣ ENV override
    env_provider = os.getenv("LLM_PROVIDER")
    if provider == "auto" and env_provider:
        provider = env_provider.lower()

    # 2️⃣ Auto-detection fallback
    if provider == "auto":
        if os.getenv("GROQ_API_KEY"):
            provider = "groq"
        elif os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
            provider = "gemini"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        else:
            raise ValueError("No LLM API keys found")

    print(f"[LLM FACTORY] Using provider: {provider}")

    try:
        if provider == "groq":
            return ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=temperature,
                groq_api_key=os.getenv("GROQ_API_KEY"),
            )

        if provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=temperature,
                google_api_key=api_key,
            )

        if provider == "openai":
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=temperature,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
            )

    except Exception as e:
        print(f"[LLM FACTORY] Error with {provider}: {e}")

        # 🔁 Safe fallback
        if provider != "gemini" and (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
            print("[LLM FACTORY] Falling back to Gemini...")
            return get_llm(provider="gemini", temperature=temperature)

        raise

    raise ValueError(f"Unknown provider: {provider}")
