"""
Configuration Module
====================
This module handles environment configuration and LLM initialization.
It loads the Groq API key from environment variables and sets up
the language model instance for use across all agents.
"""

import os
from typing import Any
from dotenv import load_dotenv

try:
    from crewai import LLM
    CREWAI_IMPORT_ERROR = None
except Exception as exc:
    LLM = None
    CREWAI_IMPORT_ERROR = exc

# Load environment variables from .env file.
# override=True ensures current project .env values take precedence over stale shell variables.
load_dotenv(override=True)


def get_api_key() -> str:
    """
    Retrieve the Groq API key from environment variables.
    
    Returns:
        str: The Groq API key
        
    Raises:
        ValueError: If GROQ_API_KEY is not set in environment
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
    
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment variables. "
            "Please create a .env file with your API key: GROQ_API_KEY=your-key-here"
        )
    
    return api_key


def get_llm() -> Any:
    """
    Initialize and return the LLM instance configured for the project.
    
    Uses Groq's llama-3.3-70b-versatile model with temperature=0.3 for consistent,
    focused outputs suitable for test case generation and analysis.
    
    Returns:
        LLM: Configured CrewAI LLM instance
    """
    if LLM is None:
        raise ImportError(
            "CrewAI is not available in this Python environment. "
            "Use Python 3.11/3.12 and reinstall project dependencies to run agent analysis."
        ) from CREWAI_IMPORT_ERROR

    api_key = get_api_key()
    
    # CrewAI's LLM supports custom OpenAI-compatible APIs
    # Using Groq's OpenAI-compatible endpoint without the "openai/" prefix
    llm = LLM(
        model="llama-3.3-70b-versatile",  # Just the model name without provider prefix
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        temperature=0.3,
    )
    
    return llm


# Configuration constants
class Config:
    """
    Configuration class holding project-wide settings.
    """
    
    # Model settings
    MODEL_NAME = "groq/llama-3.3-70b-versatile"
    TEMPERATURE = 0.3
    
    # Agent settings
    VERBOSE = True  # Enable verbose output for debugging
    ALLOW_DELEGATION = False  # Disable delegation for focused task execution
    
    # Output settings
    MAX_ITERATIONS = 5  # Maximum iterations for agent task completion


# Create a singleton LLM instance
_llm_instance = None


def get_llm_instance() -> Any:
    """
    Get or create the singleton LLM instance.
    
    This ensures we reuse the same LLM instance across all agents,
    improving efficiency and consistency.
    
    Returns:
        LLM: The singleton LLM instance
    """
    global _llm_instance
    
    if _llm_instance is None:
        _llm_instance = get_llm()
    
    return _llm_instance
