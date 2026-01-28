"""
Prompt System pour l'Agent Testeur (Judge)
Version: 1.0
Date: 2026-01-10
Auteur: Ingénieur Prompt

Description:
Ce module contient le prompt système pour l'agent Testeur.
Le Testeur analyse les résultats de pytest et décide de valider ou renvoyer au Correcteur.
"""


def get_judge_prompt(filename: str, pytest_output: str) -> str:
    """
    Génère le prompt pour l'Agent Testeur (Judge) - VERSION OPTIMISÉE v1.1.
    
    Args:
        filename (str): Nom du fichier testé
        pytest_output (str): Sortie console de pytest
    
    Returns:
        str: Prompt optimisé prêt à envoyer à Gemini
    
    Version: 1.1 (optimisée -14% tokens)
    """
    
    prompt = f"""Tu es un expert en tests Python. Analyse les résultats pytest et décide de la suite.

📋 FICHIER TESTÉ : {filename}

📊 SORTIE PYTEST :
```
{pytest_output}
```

🎯 TA MISSION :
Interpréter les résultats et prendre une décision.

✅ DÉCISION "VALIDATE" SI :
- Tous les tests passent (100%)
- Aucune erreur d'exécution

❌ DÉCISION "PASS_TO_FIXER" SI :
- Au moins 1 test échoue
- Erreur de collection
- Aucun test trouvé

📤 FORMAT DE SORTIE :
JSON UNIQUEMENT avec cette structure :

Succès :
{{"decision":"VALIDATE","tests_run":X,"tests_passed":X,"tests_failed":0,"errors":[],"message":"All tests passed"}}

Échec :
{{"decision":"PASS_TO_FIXER","tests_run":X,"tests_passed":Y,"tests_failed":Z,"errors":[{{"test_name":"...","error_type":"...","error_message":"...","location":"..."}}],"message":"Z tests failed"}}

Pas de texte avant/après le JSON.
"""
    
    return prompt


def get_judge_metadata() -> dict:
    """
    Retourne les métadonnées du prompt Testeur.
    
    Returns:
        dict: Informations sur le prompt (version, coût estimé, etc.)
    """
    return {
        "version": "1.0",
        "date": "2026-01-10",
        "model_recommended": "gemini-2.5-flash",
        "estimated_tokens_input": 2500,  # Prompt + pytest output
        "estimated_tokens_output": 300,  # JSON de décision
        "action_type": "DEBUG",
        "description": "Analyse de résultats pytest et décision de validation"
    }


# Exemple d'utilisation pour tester
if __name__ == "__main__":
    # Sortie pytest simulée - Tests réussis
    test_output_pass = """============================= test session starts ==============================
collected 3 items

test_code.py::test_calculate_average PASSED                           [ 33%]
test_code.py::test_process_data PASSED                                [ 66%]
test_code.py::test_multiply_by_two PASSED                             [100%]

============================== 3 passed in 0.05s ===============================
"""
    
    # Sortie pytest simulée - Un test échoue
    test_output_fail = """============================= test session starts ==============================
collected 3 items

test_code.py::test_calculate_average PASSED                           [ 33%]
test_code.py::test_process_data FAILED                                [ 66%]
test_code.py::test_multiply_by_two PASSED                             [100%]

=================================== FAILURES ===================================
__________________________ test_process_data ___________________________
    def test_process_data():
>       assert result == 3.0
E       AssertionError: assert 2.5 == 3.0

test_code.py:15: AssertionError
========================= 1 failed, 2 passed in 0.08s ==========================
"""
    
    print("=" * 80)
    print("PROMPT TESTEUR - CAS 1 : Tests réussis")
    print("=" * 80)
    prompt1 = get_judge_prompt("test.py", test_output_pass)
    print(prompt1[:500])
    print("...")
    print(f"\nLongueur : {len(prompt1)} caractères")
    print(f"Tokens estimés : ~{len(prompt1) // 4}")
    
    print("\n" + "=" * 80)
    print("PROMPT TESTEUR - CAS 2 : Un test échoue")
    print("=" * 80)
    prompt2 = get_judge_prompt("test.py", test_output_fail)
    print(f"Longueur : {len(prompt2)} caractères")
    print(f"Tokens estimés : ~{len(prompt2) // 4}")