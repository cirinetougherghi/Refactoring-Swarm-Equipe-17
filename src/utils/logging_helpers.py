"""
Logging Helpers pour The Refactoring Swarm
Créé par: Data Officer (Chahd)
Date: Janvier 2026

OPTIONNEL : Ces helpers simplifient l'usage de log_experiment().
Le Data Officer utilisera log_experiment() directement.
"""

from .logger import log_experiment, ActionType

# Note: Ces helpers sont fournis pour l'équipe mais le Data Officer
# utilisera log_experiment() directement pour garder le contrôle total.

def log_auditor(prompt: str, response: str, **kwargs):
    """Helper pour logger l'Auditeur"""
    details = {"input_prompt": prompt, "output_response": response}
    details.update(kwargs)
    log_experiment(
        agent_name=kwargs.get("agent_name", "Auditor"),
        model_used=kwargs.get("model", "gemini-2.0-flash-exp"),
        action=ActionType.ANALYSIS,
        details=details,
        status=kwargs.get("status", "SUCCESS")
    )

def log_fixer(prompt: str, response: str, **kwargs):
    """Helper pour logger le Correcteur"""
    details = {"input_prompt": prompt, "output_response": response}
    details.update(kwargs)
    log_experiment(
        agent_name=kwargs.get("agent_name", "Fixer"),
        model_used=kwargs.get("model", "gemini-2.0-flash-exp"),
        action=ActionType.FIX,
        details=details,
        status=kwargs.get("status", "SUCCESS")
    )

def log_tester(prompt: str = "Test execution", response: str = "", **kwargs):
    """Helper pour logger le Testeur"""
    details = {"input_prompt": prompt, "output_response": response}
    details.update(kwargs)
    log_experiment(
        agent_name=kwargs.get("agent_name", "Tester"),
        model_used=kwargs.get("model", "gemini-2.0-flash-exp"),
        action=ActionType.DEBUG,
        details=details,
        status=kwargs.get("status", "SUCCESS")
    )