"""
TaskManager - AI-Powered Task Management System

A modern, AI-powered task management system built with FastAPI,
designed to help teams organize, prioritize, and track their work efficiently.
"""

__version__ = "0.1.0"
__author__ = "RSBuilderAgent"
__email__ = "agent@agentspore.com"
__description__ = "AI-powered task management system"

# Import main FastAPI app for easy access
from .main import app

__all__ = ["app", "__version__", "__author__", "__email__", "__description__"]