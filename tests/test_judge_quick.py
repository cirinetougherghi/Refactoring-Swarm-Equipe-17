"""
Test rapide de l'Agent Testeur (Judge)
Teste la validation par pytest
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Configuration
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERREUR : Clé API non trouvée dans .env")
    sys.exit(1)

genai.configure(api_key=api_key)

# Import de l'agent
try:
    from src.agents.judge_agent import JudgeAgent
    print("✅ Import de l'Agent Testeur réussi")
except ImportError as e:
    print(f"❌ ERREUR d'import : {e}")
    sys.exit(1)


def test_judge_quick():
    """Test rapide du Testeur avec sortie pytest simulée"""
    
    print("\n" + "="*80)
    print("TEST RAPIDE DU TESTEUR (JUDGE)")
    print("="*80 + "\n")
    
    # Crée un fichier Python simple pour tester
    test_code = """
def add(a, b):
    return a + b

def multiply(x, y):
    return x * y
"""
    
    os.makedirs("sandbox", exist_ok=True)
    test_file = "sandbox/test_judge_quick.py"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"📄 Fichier de test créé : {test_file}")
    
    # TEST 1 : Simulation pytest - Tous les tests passent
    print("\n" + "="*80)
    print("TEST 1 : SORTIE PYTEST - TOUS LES TESTS PASSENT")
    print("="*80)
    
    pytest_success = """============================= test session starts ==============================
collected 3 items

test_code.py::test_add PASSED                                            [ 33%]
test_code.py::test_multiply PASSED                                       [ 66%]
test_code.py::test_combined PASSED                                       [100%]

============================== 3 passed in 0.05s ===============================
"""
    
    print("\n📊 Sortie pytest simulée :")
    print("-"*80)
    print(pytest_success)
    print("-"*80)
    
    # Utilise le Judge pour analyser
    judge = JudgeAgent()
    
    # Simule l'appel avec pytest_output directement
    # (Normalement pytest serait exécuté, mais ici on simule)
    from src.prompts import get_judge_prompt
    import json
    
    print("\n🤖 Analyse du Testeur...")
    
    prompt = get_judge_prompt(test_file, pytest_success)
    
    try:
        response = judge.model.generate_content(prompt)
        raw_response = response.text.strip()
        
        # Nettoie le JSON
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        judge_report = json.loads(cleaned)
        
        print("\n✅ Rapport JSON reçu")
        print(f"\n📊 RÉSULTATS :")
        print(f"   Décision     : {judge_report.get('decision', 'N/A')}")
        print(f"   Tests passés : {judge_report.get('passed', 0)}")
        print(f"   Tests échoués : {judge_report.get('failed', 0)}")
        print(f"   Message      : {judge_report.get('message', 'N/A')}")
        
        # Vérifications
        decision = judge_report.get('decision', '')
        
        print("\n📈 VÉRIFICATIONS :")
        
        if decision == "VALIDATE":
            print("   ✅ Décision correcte : VALIDATE (tous les tests passent)")
        else:
            print(f"   ❌ Décision incorrecte : {decision} (attendu: VALIDATE)")
        
        # TEST 2 : Simulation pytest - Quelques tests échouent
        print("\n" + "="*80)
        print("TEST 2 : SORTIE PYTEST - QUELQUES TESTS ÉCHOUENT")
        print("="*80)
        
        pytest_failure = """============================= test session starts ==============================
collected 3 items

test_code.py::test_add PASSED                                            [ 33%]
test_code.py::test_multiply FAILED                                       [ 66%]
test_code.py::test_combined PASSED                                       [100%]

=================================== FAILURES ===================================
__________________________ test_multiply ___________________________
    def test_multiply():
>       assert multiply(2, 3) == 6
E       AssertionError: assert 7 == 6

test_code.py:10: AssertionError
========================= 1 failed, 2 passed in 0.08s ==========================
"""
        
        print("\n📊 Sortie pytest simulée :")
        print("-"*80)
        print(pytest_failure)
        print("-"*80)
        
        print("\n🤖 Analyse du Testeur...")
        
        prompt2 = get_judge_prompt(test_file, pytest_failure)
        response2 = judge.model.generate_content(prompt2)
        raw_response2 = response2.text.strip()
        
        # Nettoie le JSON
        cleaned2 = raw_response2.strip()
        if cleaned2.startswith("```json"):
            cleaned2 = cleaned2[7:]
        if cleaned2.startswith("```"):
            cleaned2 = cleaned2[3:]
        if cleaned2.endswith("```"):
            cleaned2 = cleaned2[:-3]
        cleaned2 = cleaned2.strip()
        
        judge_report2 = json.loads(cleaned2)
        
        print("\n✅ Rapport JSON reçu")
        print(f"\n📊 RÉSULTATS :")
        print(f"   Décision     : {judge_report2.get('decision', 'N/A')}")
        print(f"   Tests passés : {judge_report2.get('passed', 0)}")
        print(f"   Tests échoués : {judge_report2.get('failed', 0)}")
        
        decision2 = judge_report2.get('decision', '')
        
        print("\n📈 VÉRIFICATIONS :")
        
        if decision2 == "PASS_TO_FIXER":
            print("   ✅ Décision correcte : PASS_TO_FIXER (des tests échouent)")
        else:
            print(f"   ❌ Décision incorrecte : {decision2} (attendu: PASS_TO_FIXER)")
        
        # Vérifie les logs
        log_file = "logs/experiment_data.json"
        if os.path.exists(log_file):
            print("   ✅ Fichier de logs créé")
        
        print("\n" + "="*80)
        
        # Résultat final
        test1_ok = decision == "VALIDATE"
        test2_ok = decision2 == "PASS_TO_FIXER"
        
        if test1_ok and test2_ok:
            print("🎉 SUCCÈS : Le Testeur fonctionne correctement !")
            print("="*80 + "\n")
            return True
        else:
            print("⚠️ PARTIEL : Le Testeur a des problèmes de décision")
            print("="*80 + "\n")
            return False
        
    except json.JSONDecodeError as e:
        print(f"\n❌ ERREUR : JSON invalide du Testeur")
        print(f"   {e}")
        return False
    
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = test_judge_quick()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)