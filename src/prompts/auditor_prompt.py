"""
Prompt System pour l'Agent Auditeur
Version: 1.0
Date: 2026-01-08
Auteur: Ingénieur Prompt

Description:
Ce module contient le prompt système pour l'agent Auditeur.
L'Auditeur analyse du code Python et produit un rapport JSON des problèmes détectés.
"""


def get_auditor_prompt(filename: str, code_content: str) -> str:
    """
    Génère le prompt pour l'Agent Auditeur - VERSION OPTIMISÉE v1.1.
    
    Args:
        filename (str): Nom du fichier à analyser
        code_content (str): Contenu du code Python
    
    Returns:
        str: Prompt optimisé prêt à envoyer à Gemini
    
    Version: 1.1 (optimisée -4% tokens, qualité préservée)
    """
    
    prompt = f"""Tu es un expert Python et auditeur de code.

📋 FICHIER : {filename}

🎯 MISSION :
Analyse ce code et détecte TOUS les problèmes. Ne JAMAIS inventer de bugs inexistants.

🐛 TYPES DE PROBLÈMES À DÉTECTER :

CRITICAL :
- Variables non définies
- Imports manquants
- Syntaxe invalide

HIGH :
- Division par zéro
- Index hors limites
- Opérations sur None
- Clés dictionnaire inexistantes
- Fichiers inexistants

MEDIUM :
- Docstrings manquantes
- Pas de type hints
- Nommage non descriptif

LOW :
- Violations PEP8 (espaces, longueur ligne)
- Imports désordonnés

📝 CODE À ANALYSER :
```python
{code_content}
```

📤 FORMAT DE SORTIE :
JSON UNIQUEMENT avec cette structure exacte :

{{"file":"{filename}","total_issues":X,"issues":[{{"line":N,"type":"...","severity":"...","description":"...","suggestion":"..."}}]}}

Exemple :
{{"file":"test.py","total_issues":2,"issues":[{{"line":5,"type":"undefined_variable","severity":"HIGH","description":"Variable 'x' not defined","suggestion":"Define 'x' before use"}},{{"line":10,"type":"missing_docstring","severity":"MEDIUM","description":"Function lacks docstring","suggestion":"Add docstring with Args/Returns"}}]}}

Si aucun bug : {{"file":"{filename}","total_issues":0,"issues":[]}}

Pas de texte avant/après le JSON.
"""
    
    return prompt


def get_auditor_metadata() -> dict:
    """
    Retourne les métadonnées du prompt Auditeur.
    
    Returns:
        dict: Informations sur le prompt (version, coût estimé, etc.)
    """
    return {
        "version": "1.0",
        "date": "2026-01-08",
        "model_recommended": "gemini-2.5-flash",
        "estimated_tokens_input": 2000,  # Estimation moyenne
        "estimated_tokens_output": 1000,  # Estimation moyenne
        "action_type": "ANALYSIS",
        "description": "Analyse statique de code Python pour détecter bugs et problèmes de qualité"
    }


# Exemple d'utilisation pour tester
if __name__ == "__main__":
    # Code de test simple avec bugs
    test_code = """import os

def calculate(x, y):
    result = x / y
    return result

print(calculate(10, 0))
print(undefined_var)
"""
    
    prompt = get_auditor_prompt("test.py", test_code)
    print("=" * 80)
    print("PROMPT GÉNÉRÉ :")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    print(f"\nLongueur approximative : {len(prompt)} caractères")
    print(f"Tokens estimés : ~{len(prompt) // 4}")