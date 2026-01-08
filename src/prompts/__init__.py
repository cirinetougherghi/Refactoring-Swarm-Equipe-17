"""
Module des prompts pour les agents du Refactoring Swarm.

Ce module contient les prompts système pour :
- Agent Auditeur (analyse de code)
- Agent Correcteur (correction de bugs) - À venir
- Agent Testeur (validation par tests) - À venir

Auteur: Ingénieur Prompt
Date: 2026-01-08
Version: 1.0
"""

from .auditor_prompt import get_auditor_prompt, get_auditor_metadata

__version__ = "1.0.0"
__author__ = "Ingénieur Prompt"

__all__ = [
    "get_auditor_prompt",
    "get_auditor_metadata",
]