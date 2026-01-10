"""
Module des prompts pour les agents du Refactoring Swarm.

Ce module contient les prompts système pour :
- Agent Auditeur (analyse de code)
- Agent Correcteur (correction de bugs)
- Agent Testeur (validation par tests)

Auteur: Ingénieur Prompt
Date: 2026-01-10
Version: 1.0
"""

from .auditor_prompt import get_auditor_prompt, get_auditor_metadata
from .fixer_prompt import get_fixer_prompt, get_fixer_metadata
from .judge_prompt import get_judge_prompt, get_judge_metadata

__version__ = "1.0.0"
__author__ = "Ingénieur Prompt"

__all__ = [
    "get_auditor_prompt",
    "get_auditor_metadata",
    "get_fixer_prompt",
    "get_fixer_metadata",
    "get_judge_prompt",
    "get_judge_metadata",
]