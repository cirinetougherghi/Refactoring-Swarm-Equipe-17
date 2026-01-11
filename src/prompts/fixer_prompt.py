"""
Prompt System pour l'Agent Correcteur (Fixer)
Version: 1.0
Date: 2026-01-09
Auteur: Ingénieur Prompt

Description:
Ce module contient le prompt système pour l'agent Correcteur.
Le Correcteur lit le code buggé et le rapport de l'Auditeur, puis corrige tous les problèmes.
"""


def get_fixer_prompt(filename: str, buggy_code: str, audit_report: dict) -> str:
    """
    Génère le prompt pour l'Agent Correcteur (Fixer) - VERSION OPTIMISÉE v1.1.
    
    Args:
        filename (str): Nom du fichier à corriger
        buggy_code (str): Code Python avec bugs
        audit_report (dict): Rapport JSON de l'Auditeur
    
    Returns:
        str: Prompt optimisé prêt à envoyer à Gemini
    
    Version: 1.1 (optimisée -12% tokens)
    """
    
    # Convertit le rapport en JSON string
    import json
    audit_json = json.dumps(audit_report, indent=2, ensure_ascii=False)
    
    prompt = f"""Tu es un expert Python chargé de corriger les bugs détectés.

📋 FICHIER : {filename}

🐛 RAPPORT D'AUDIT :
{audit_json}

📝 CODE ORIGINAL :
```python
{buggy_code}
```

🎯 TA MISSION :
Corrige TOUS les bugs listés dans le rapport.

✅ RÈGLES :
- Conserve la structure et logique originale
- Ajoute docstrings Google format (Args, Returns)
- Gère les cas limites (division par zéro, listes vides, None)
- Respecte PEP8
- Ne réécris pas complètement le code

❌ INTERDICTIONS :
- Ajouter des fonctionnalités non demandées
- Changer la logique métier
- Inclure des explications ou commentaires (sauf docstrings)

📤 FORMAT DE SORTIE :
Code Python pur UNIQUEMENT. Pas de :
- Balises markdown (```python)
- Explications textuelles
- Commentaires de changements

Commence directement par le code corrigé.
"""
    
    return prompt


def get_fixer_metadata() -> dict:
    """
    Retourne les métadonnées du prompt Correcteur.
    
    Returns:
        dict: Informations sur le prompt (version, coût estimé, etc.)
    """
    return {
        "version": "1.0",
        "date": "2026-01-09",
        "model_recommended": "gemini-2.5-flash",
        "estimated_tokens_input": 3000,  # Code + rapport + prompt
        "estimated_tokens_output": 1500,  # Code corrigé
        "action_type": "FIX",
        "description": "Correction automatique de code Python basée sur rapport d'audit"
    }


# Exemple d'utilisation pour tester
if __name__ == "__main__":
    # Code de test buggé
    test_code = """import os

def calculate(x,y):
    result = x / y
    return result

print(calculate(10, 0))
print(undefined_var)
"""
    
    # Rapport d'audit simulé
    test_report = {
        "file": "test.py",
        "total_issues": 5,
        "issues": [
            {
                "line": 3,
                "type": "missing_docstring",
                "severity": "MEDIUM",
                "description": "Function 'calculate' has no docstring",
                "suggestion": "Add a docstring"
            },
            {
                "line": 3,
                "type": "pep8_spacing",
                "severity": "LOW",
                "description": "Missing space after comma in parameters",
                "suggestion": "Change (x,y) to (x, y)"
            },
            {
                "line": 4,
                "type": "division_by_zero",
                "severity": "HIGH",
                "description": "Division by y which can be zero",
                "suggestion": "Add check: if y == 0: raise ValueError"
            },
            {
                "line": 8,
                "type": "division_by_zero",
                "severity": "HIGH",
                "description": "Calling calculate with 0 as second argument",
                "suggestion": "Handle the zero case"
            },
            {
                "line": 9,
                "type": "undefined_variable",
                "severity": "CRITICAL",
                "description": "Variable 'undefined_var' is not defined",
                "suggestion": "Define the variable or remove the line"
            }
        ]
    }
    
    prompt = get_fixer_prompt("test.py", test_code, test_report)
    print("=" * 80)
    print("PROMPT CORRECTEUR GÉNÉRÉ :")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    print(f"\nLongueur approximative : {len(prompt)} caractères")
    print(f"Tokens estimés : ~{len(prompt) // 4}")