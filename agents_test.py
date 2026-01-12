"""
Script de test pour verifier que tous les agents fonctionnent
Responsable : Lead Dev (Orchestrateur)
Date : 2026-01-10

Usage:
    python test_agents.py
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai


def main():
    print("\n" + "="*80)
    print("TEST DU SYSTEME REFACTORING SWARM")
    print("="*80 + "\n")
    
    # Test 1: Imports
    print("Test 1: Verification des imports...")
    try:
        from src.agents import AuditorAgent, FixerAgent, JudgeAgent
        print("  [OK] Agents importes avec succes")
    except ImportError as e:
        print(f"  [ERREUR] Impossible d'importer les agents: {e}")
        sys.exit(1)
    
    # Test 2: Environment
    print("\nTest 2: Verification de l'environnement...")
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("  [ERREUR] Cle API non trouvee dans .env")
        print("  Ajoutez GOOGLE_API_KEY=votre_cle dans le fichier .env")
        sys.exit(1)
    
    print("  [OK] Cle API trouvee")
    
    try:
        genai.configure(api_key=api_key)
        print("  [OK] API Gemini configuree")
    except Exception as e:
        print(f"  [ERREUR] Configuration API echouee: {e}")
        sys.exit(1)
    
    # Test 3: Creation des agents
    print("\nTest 3: Creation des agents...")
    try:
        auditor = AuditorAgent()
        print("  [OK] AuditorAgent cree")
        
        fixer = FixerAgent()
        print("  [OK] FixerAgent cree")
        
        judge = JudgeAgent()
        print("  [OK] JudgeAgent cree")
    except Exception as e:
        print(f"  [ERREUR] Creation des agents echouee: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test 4: Test de l'Auditeur
    print("\nTest 4: Test de l'Auditeur sur un fichier simple...")
    
    # Cree le dossier sandbox s'il n'existe pas
    os.makedirs("sandbox", exist_ok=True)
    
    # Cree un fichier de test avec des bugs
    test_file = "sandbox/test_simple.py"
    test_code = """def calculate(x, y):
    result = x / y
    return result

print(calculate(10, 0))
print(undefined_variable)
"""
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        print(f"  [OK] Fichier de test cree: {test_file}")
    except Exception as e:
        print(f"  [ERREUR] Creation du fichier echouee: {e}")
        sys.exit(1)
    
    # Analyse avec l'auditeur
    print("\n  Analyse en cours...")
    try:
        report = auditor.analyze_file(test_file)
        
        if report:
            bugs = report.get('total_issues', 0)
            print(f"\n  [OK] Audit reussi!")
            print(f"  Bugs detectes: {bugs}")
            
            if bugs > 0:
                print("\n  Premiers problemes detectes:")
                for i, issue in enumerate(report.get('issues', [])[:3], 1):
                    print(f"    {i}. Ligne {issue.get('line')}: {issue.get('type')}")
                    print(f"       {issue.get('description')}")
        else:
            print("  [ERREUR] Audit echoue - Aucun rapport retourne")
            sys.exit(1)
            
    except Exception as e:
        print(f"  [ERREUR] Test de l'auditeur echoue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test 5: Verification des logs
    print("\nTest 5: Verification des logs...")
    log_file = "logs/experiment_data.json"
    
    if os.path.exists(log_file):
        print(f"  [OK] Fichier de logs cree: {log_file}")
        
        try:
            import json
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            print(f"  [OK] {len(logs)} entree(s) de log trouvee(s)")
            
            if len(logs) > 0:
                last_log = logs[-1]
                print(f"  Dernier log: Agent '{last_log.get('agent')}' - Status: {last_log.get('status')}")
        except Exception as e:
            print(f"  [ATTENTION] Logs non valides: {e}")
    else:
        print(f"  [ATTENTION] Fichier de logs non trouve (sera cree au premier usage)")
    
    # Test 6: Verification des outils
    print("\nTest 6: Verification des outils...")
    try:
        from src.tools.file_tools import read_file, write_file
        print("  [OK] Outils de fichiers importes")
        
        from src.tools.analysis_tools import run_pytest, run_pylint
        print("  [OK] Outils d'analyse importes")
    except ImportError as e:
        print(f"  [ERREUR] Import des outils echoue: {e}")
        sys.exit(1)
    
    # Fin des tests
    print("\n" + "="*80)
    print("TOUS LES TESTS SONT PASSES AVEC SUCCES!")
    print("="*80)
    print("\nLe systeme est pret a l'emploi.")
    print("\nPour lancer le systeme complet:")
    print("  python main.py --target_dir ./sandbox")
    print("\n")


if __name__ == "__main__":
    main()