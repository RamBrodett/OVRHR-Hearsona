"""
Hearsona API Application Package

A modular FastAPI application for AI-powered audio generation
with LLM integration and session management.
"""

__version__ = "1.0.0"
__title__ = "Hearsona API"
__description__ = "AI-powered audio generation API with conversational interface"
__author__ = "Hearsona Team"

# Main application factory
from .main import create_app

__all__ = ["create_app"]