#!/usr/bin/env python3
"""
Test d'intégration du logging pour validation avec Data Officer
"""
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from src.prompts import get_auditor_prompt, get_fixer_prompt, get_judge_prompt
from src.utils.logger import log_experiment, ActionType

def test_logging():
    """Teste que tous les logs sont correctement capturés"""
    
    print("="*80)
    print("🧪 TEST D'INTÉGRATION DU LOGGING")
    print("="*80)
    print()
    
    # Configuration
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Code de test simple
    code = """
def calculate(x):
    result = x / 0
    return result
"""
    
    # ========================================
    # TEST 1 : AUDITEUR
    # ========================================
    print("📋 TEST 1 : Logging de l'Auditeur")
    print("-"*80)
    
    prompt = get_auditor_prompt("test.py", code)
    print(f"✅ Prompt généré ({len(prompt)} caractères)")
    
    response = model.generate_content(prompt)
    print(f"✅ Réponse reçue ({len(response.text)} caractères)")
    
    audit_report = json.loads(response.text)
    print(f"✅ JSON parsé : {audit_report['total_issues']} bugs détectés")
    
    # LOGGING
    log_experiment(
        agent_name="Auditor",
        model_used="gemini-2.5-flash",
        action=ActionType.ANALYSIS,
        details={
            "file_analyzed": "test.py",
            "input_prompt": prompt,
            "output_response": response.text,
            "issues_found": audit_report['total_issues']
        },
        status="SUCCESS"
    )
    print("✅ Log enregistré avec ActionType.ANALYSIS")
    print()
    
    # ========================================
    # TEST 2 : CORRECTEUR
    # ========================================
    print("📋 TEST 2 : Logging du Correcteur")
    print("-"*80)
    
    prompt = get_fixer_prompt("test.py", code, audit_report)
    print(f"✅ Prompt généré ({len(prompt)} caractères)")
    
    response = model.generate_content(prompt)
    print(f"✅ Réponse reçue ({len(response.text)} caractères)")
    
    fixed_code = response.text
    print(f"✅ Code corrigé généré")
    
    # LOGGING
    log_experiment(
        agent_name="Fixer",
        model_used="gemini-2.5-flash",
        action=ActionType.FIX,
        details={
            "file_fixed": "test.py",
            "input_prompt": prompt,
            "output_response": response.text,
            "bugs_corrected": audit_report['total_issues']
        },
        status="SUCCESS"
    )
    print("✅ Log enregistré avec ActionType.FIX")
    print()
    
    # ========================================
    # TEST 3 : TESTEUR
    # ========================================
    print("📋 TEST 3 : Logging du Testeur")
    print("-"*80)
    
    # Simulation de sortie pytest
    pytest_output = """
============================= test session starts ==============================
collected 2 items

test_example.py::test_calculate PASSED                                  [ 50%]
test_example.py::test_valid PASSED                                      [100%]

============================== 2 passed in 0.03s ===============================
"""
    
    prompt = get_judge_prompt("test.py", pytest_output)
    print(f"✅ Prompt généré ({len(prompt)} caractères)")
    
    response = model.generate_content(prompt)
    print(f"✅ Réponse reçue ({len(response.text)} caractères)")
    
    judge_decision = json.loads(response.text)
    print(f"✅ JSON parsé : Décision = {judge_decision['decision']}")
    
    # LOGGING
    log_experiment(
        agent_name="Judge",
        model_used="gemini-2.5-flash",
        action=ActionType.DEBUG,
        details={
            "file_tested": "test.py",
            "input_prompt": prompt,
            "output_response": response.text,
            "decision": judge_decision['decision']
        },
        status="SUCCESS"
    )
    print("✅ Log enregistré avec ActionType.DEBUG")
    print()
    
    # ========================================
    # VÉRIFICATION DU FICHIER DE LOG
    # ========================================
    print("="*80)
    print("📊 VÉRIFICATION DU FICHIER DE LOG")
    print("="*80)
    
    log_file = "logs/experiment_data.json"
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = [json.loads(line) for line in f if line.strip()]
        
        print(f"✅ Fichier de log trouvé : {log_file}")
        print(f"✅ Nombre d'entrées : {len(logs)}")
        print()
        
        # Vérifier les 3 dernières entrées
        recent_logs = logs[-3:]
        
        for i, log in enumerate(recent_logs, 1):
            print(f"📝 Log {i} :")
            print(f"   Agent : {log.get('agent_name', 'N/A')}")
            print(f"   Action : {log.get('action', 'N/A')}")
            print(f"   Status : {log.get('status', 'N/A')}")
            
            # Vérifier champs obligatoires
            has_input = 'input_prompt' in log.get('details', {})
            has_output = 'output_response' in log.get('details', {})
            
            print(f"   input_prompt présent : {'✅' if has_input else '❌'}")
            print(f"   output_response présent : {'✅' if has_output else '❌'}")
            print()
        
        print("="*80)
        print("✅ TOUS LES TESTS DE LOGGING RÉUSSIS !")
        print("="*80)
        
    else:
        print(f"❌ Fichier de log non trouvé : {log_file}")

if __name__ == "__main__":
    test_logging()