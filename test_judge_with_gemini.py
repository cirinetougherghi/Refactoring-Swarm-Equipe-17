"""
Script de test pour l'Agent Testeur (Judge)
Test avec différentes sorties pytest simulées
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from src.prompts.judge_prompt import get_judge_prompt
# ✅ AJOUT DATA OFFICER : Import du système de logging
from src.utils.logger import log_experiment, ActionType

# Charge les variables d'environnement
load_dotenv()

# Configure l'API Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ ERREUR : Clé API non trouvée dans .env")
    exit(1)

genai.configure(api_key=api_key)


# ============================================================================
# SORTIES PYTEST SIMULÉES
# ============================================================================

PYTEST_ALL_PASS = """============================= test session starts ==============================
platform darwin -- Python 3.11.0, pytest-7.4.0
collected 5 items

test_code.py::test_calculate_average PASSED                           [ 20%]
test_code.py::test_calculate_average_empty PASSED                     [ 40%]
test_code.py::test_process_data PASSED                                [ 60%]
test_code.py::test_multiply_by_two PASSED                             [ 80%]
test_code.py::test_multiply_by_two_negative PASSED                    [100%]

============================== 5 passed in 0.12s ===============================
"""

PYTEST_SOME_FAIL = """============================= test session starts ==============================
platform darwin -- Python 3.11.0, pytest-7.4.0
collected 5 items

test_code.py::test_calculate_average PASSED                           [ 20%]
test_code.py::test_calculate_average_empty FAILED                     [ 40%]
test_code.py::test_process_data PASSED                                [ 60%]
test_code.py::test_multiply_by_two FAILED                             [ 80%]
test_code.py::test_multiply_by_two_negative PASSED                    [100%]

=================================== FAILURES ===================================
______________________ test_calculate_average_empty ________________________
    def test_calculate_average_empty():
        result = calculate_average([])
>       assert result == 0
E       assert None == 0

test_code.py:12: AssertionError
__________________________ test_multiply_by_two ____________________________
    def test_multiply_by_two():
        result = multiply_by_two(5)
>       assert result == 10
E       AssertionError: assert 11 == 10

test_code.py:25: AssertionError
========================= 2 failed, 3 passed in 0.15s ==========================
"""

PYTEST_EXECUTION_ERROR = """============================= test session starts ==============================
platform darwin -- Python 3.11.0, pytest-7.4.0
collected 0 items / 1 error

=================================== ERRORS =====================================
__________________ ERROR collecting test_code.py __________________
test_code.py:2: in <module>
    import math
E   ImportError: No module named 'math'
=========================== 1 error in 0.03s ====================================
"""

PYTEST_NO_TESTS = """============================= test session starts ==============================
platform darwin -- Python 3.11.0, pytest-7.4.0
collected 0 items

============================ no tests ran in 0.01s ==============================
"""

PYTEST_SYNTAX_ERROR = """============================= test session starts ==============================
platform darwin -- Python 3.11.0, pytest-7.4.0
collected 0 items / 1 error

=================================== ERRORS =====================================
__________________ ERROR collecting test_code.py __________________
test_code.py:10: in <module>
    def calculate_average(numbers)
E     File "test_code.py", line 10
E       def calculate_average(numbers)
E                                     ^
E   SyntaxError: invalid syntax
=========================== 1 error in 0.02s ====================================
"""


def test_judge_case(case_name: str, file_name: str, pytest_output: str):
    """
    Teste le Testeur sur un cas spécifique.
    
    Args:
        case_name (str): Nom du cas de test
        file_name (str): Nom du fichier testé
        pytest_output (str): Sortie pytest à analyser
    """
    print("=" * 80)
    print(f"🧪 TEST : {case_name}")
    print("=" * 80)
    
    # Génère le prompt
    print("⚙️  Génération du prompt...")
    prompt = get_judge_prompt(file_name, pytest_output)
    print(f"✅ Prompt généré ({len(prompt)} caractères, ~{len(prompt)//4} tokens)")
    
    # Envoie à Gemini
    print("🤖 Envoi à Gemini pour analyse...")
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        raw_response = response.text

        print(f"✅ Réponse reçue ({len(raw_response)} caractères)")
         # ✅ AJOUT DATA OFFICER : Log de l'interaction réussie
        log_experiment(
            agent_name="Judge_Agent",
            model_used="gemini-2.5-flash",
            action=ActionType.DEBUG,
            details={
                "test_case": case_name,
                "file_tested": file_name,
                "input_prompt": prompt,
                "output_response": raw_response,
                "prompt_length_chars": len(prompt),
                "response_length_chars": len(raw_response),
                "pytest_output_lines": len(pytest_output.splitlines())
            },
            status="SUCCESS"
        )
        
    except Exception as e:
        print(f"❌ Erreur lors de l'appel API : {e}")
         # ✅ AJOUT DATA OFFICER : Log de l'erreur API
        log_experiment(
            agent_name="Judge_Agent",
            model_used="gemini-2.5-flash",
            action=ActionType.DEBUG,
            details={
                "test_case": case_name,
                "file_tested": file_name,
                "input_prompt": prompt,
                "output_response": "",
                "error_type": type(e).__name__,
                "error_message": str(e)
            },
            status="ERROR"
        )
        return
    
    # Affiche la réponse brute
    print("\n" + "=" * 80)
    print("📨 RÉPONSE BRUTE DE GEMINI :")
    print("=" * 80)
    print(raw_response)
    print("=" * 80)
    
    # Parse le JSON
    try:
        # Nettoie la réponse
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        result = json.loads(cleaned)
        print("\n✅ JSON VALIDE !")
          # ✅ AJOUT DATA OFFICER : Log enrichi avec résultats du parsing
        log_experiment(
            agent_name="Judge_Agent",
            model_used="gemini-2.5-flash",
            action=ActionType.DEBUG,
            details={
                "test_case": case_name,
                "file_tested": file_name,
                "input_prompt": prompt,
                "output_response": raw_response,
                "parsing_status": "SUCCESS",
                "json_valid": True,
                "decision": result.get('decision', 'N/A'),
                "total_tests": result.get('total_tests', 0),
                "passed_tests": result.get('passed', 0),
                "failed_tests": result.get('failed', 0),
                "errors_count": len(result.get('errors', []))
            },
            status="SUCCESS"
        )
        
        # Affiche les résultats
        print(f"\n📊 RÉSULTAT DE L'ANALYSE :")
        print(f"   Fichier : {result.get('file', 'N/A')}")
        print(f"   Décision : {result.get('decision', 'N/A')}")
        print(f"   Tests totaux : {result.get('total_tests', 0)}")
        print(f"   Réussis : {result.get('passed', 0)}")
        print(f"   Échoués : {result.get('failed', 0)}")
        print(f"   Message : {result.get('message', 'N/A')}")
        
        # Affiche les erreurs
        errors = result.get('errors', [])
        if errors:
            print(f"\n❌ ERREURS DÉTECTÉES ({len(errors)}) :")
            for i, error in enumerate(errors, 1):
                print(f"   [{i}] Test : {error.get('test_name', 'N/A')}")
                print(f"       Type : {error.get('error_type', 'N/A')}")
                print(f"       Message : {error.get('message', 'N/A')}")
                print(f"       Location : {error.get('location', 'N/A')}")
        
        # Sauvegarde le résultat
        output_file = f"results_judge_{case_name.lower().replace(' ', '_')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Résultat sauvegardé dans : {output_file}")
        
    except json.JSONDecodeError as e:
        print(f"\n❌ ERREUR : JSON INVALIDE !")
        print(f"   Erreur : {e}")
                # ✅ AJOUT DATA OFFICER : Log de l'échec du parsing
        log_experiment(
            agent_name="Judge_Agent",
            model_used="gemini-2.5-flash",
            action=ActionType.DEBUG,
            details={
                "test_case": case_name,
                "file_tested": file_name,
                "input_prompt": prompt,
                "output_response": raw_response,
                "parsing_status": "FAILED",
                "json_valid": False,
                "parsing_error_type": type(e).__name__,
                "parsing_error_message": str(e)
            },
            status="PARTIAL"
        )

        
        # Sauvegarde la réponse brute
        error_file = f"debug_judge_{case_name.lower().replace(' ', '_')}.txt"
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(raw_response)
        print(f"\n💾 Réponse brute sauvegardée dans : {error_file}")
    
    print("\n" + "=" * 80)


def main():
    """Fonction principale - teste tous les cas"""
    
    print("\n" + "🧪" * 40)
    print("TEST DE L'AGENT TESTEUR AVEC GEMINI 2.5 FLASH")
    print("🧪" * 40 + "\n")
    
    # Liste des cas à tester
    test_cases = [
        ("Cas 1 - Tous les tests passent", "buggy_code_simple.py", PYTEST_ALL_PASS),
        ("Cas 2 - Quelques tests échouent", "buggy_code_simple.py", PYTEST_SOME_FAIL),
        ("Cas 3 - Erreur d'exécution", "buggy_code_simple.py", PYTEST_EXECUTION_ERROR),
        ("Cas 4 - Aucun test", "buggy_code_simple.py", PYTEST_NO_TESTS),
        ("Cas 5 - Erreur de syntaxe", "buggy_code_simple.py", PYTEST_SYNTAX_ERROR),
    ]
    
    for case_name, file_name, pytest_output in test_cases:
        test_judge_case(case_name, file_name, pytest_output)
        print("\n")
    
    print("✅ TOUS LES TESTS TERMINÉS !\n")
    print("\n📊 Les logs d'expérimentation ont été enregistrés dans logs/experiment_data.json")
    print("💡 Lancez 'python validate_logs.py' pour valider le format des logs\n")
    
    # Résumé
    print("=" * 80)
    print("📊 RÉSUMÉ DES CAS TESTÉS")
    print("=" * 80)
    print("✅ Cas 1 : Tous passent → Devrait retourner VALIDATE")
    print("✅ Cas 2 : Quelques échouent → Devrait retourner PASS_TO_FIXER")
    print("✅ Cas 3 : Erreur exécution → Devrait retourner PASS_TO_FIXER")
    print("✅ Cas 4 : Aucun test → Devrait retourner PASS_TO_FIXER")
    print("✅ Cas 5 : Erreur syntaxe → Devrait retourner PASS_TO_FIXER")
    print("=" * 80)


if __name__ == "__main__":
    main()