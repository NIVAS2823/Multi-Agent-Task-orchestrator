import os
from typing import Literal
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv()

def get_llm(
    provider: Literal["groq", "gemini", "openai", "auto"] = "auto",
    temperature: float = 0.7
):
    """
    Get LLM with automatic fallback if rate limited
    """
    # Auto-select based on available API keys
    if provider == "auto":
        if os.getenv("GROQ_API_KEY"):
            provider = "groq"
        elif os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
            provider = "gemini"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        else:
            raise ValueError("No API keys found. Set GROQ_API_KEY, GOOGLE_API_KEY, or OPENAI_API_KEY")
    
    print(f"[LLM FACTORY] Using provider: {provider}")
    
    try:
        if provider == "groq":
            return ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=temperature,
                groq_api_key=os.getenv("GROQ_API_KEY")
            )
        elif provider == "gemini":
            google_key = os.getenv("GOOGLE_API_KEY")
            gemini_key = os.getenv("GEMINI_API_KEY")
            
            if google_key and gemini_key:
                print("Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.")
                api_key = google_key
            else:
                api_key = google_key or gemini_key
            
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=temperature,
                google_api_key=api_key
            )
        elif provider == "openai":
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=temperature,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
    except Exception as e:
        print(f"[LLM FACTORY] Error with {provider}: {e}")
        # Fallback to gemini if groq fails
        if provider == "groq" and (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
            print("[LLM FACTORY] Falling back to Gemini...")
            return get_llm(provider="gemini", temperature=temperature)
        raise
    
    raise ValueError(f"Unknown provider: {provider}")