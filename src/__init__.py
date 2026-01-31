"""
Refactoring Swarm - Système multi-agents de refactoring automatique

Auteur: Équipe Refactoring Swarm
Date: 2026-01-10
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Équipe Refactoring Swarm"

from src.agents import AuditorAgent, FixerAgent, JudgeAgent
from src.orchestrator import Orchestrator

__all__ = [
    "AuditorAgent",
    "FixerAgent", 
    "JudgeAgent",
    "Orchestrator",
]