"""
Test d'Intégration Complet - Refactoring Swarm
Vérifie que tous les agents fonctionnent ensemble correctement
Version FINALE pour dossier tests/ - Détaillée et automatique

UTILISATION:
    python -m tests.test_integration_complete

Ce test simule le workflow complet :
1. Création d'un fichier avec bugs
2. Audit par l'Auditeur
3. Correction par le Fixer
4. Validation par le Judge
5. Vérification des logs
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Déterminer le dossier racine du projet (parent du dossier tests/)
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent  # Remonter d'un niveau depuis tests/
sys.path.insert(0, str(project_root))

print("🔧 Configuration de l'environnement...")
print(f"📁 Projet : {project_root}")
print(f"📁 Tests : {current_dir}")

# Vérifier que les variables d'environnement sont configurées
try:
    from dotenv import load_dotenv
    import google.generativeai as genai
    
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ ERREUR CRITIQUE : Clé API Google non trouvée dans .env")
        print("   Veuillez configurer GOOGLE_API_KEY dans le fichier .env")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    print("✅ Configuration API réussie")
    
except ImportError as e:
    print(f"❌ ERREUR : Bibliothèque manquante : {e}")
    print("   Veuillez installer les dépendances : pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERREUR : {e}")
    sys.exit(1)


def setup_test_environment():
    """Prépare l'environnement de test"""
    print("\n" + "="*80)
    print("PRÉPARATION DE L'ENVIRONNEMENT DE TEST")
    print("="*80)
    
    # Créer dossiers nécessaires
    test_dir = project_root / "sandbox" / "test_integration"
    
    # Nettoyer s'il existe déjà
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    test_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Dossier de test créé : {test_dir}")
    
    return test_dir


def create_buggy_test_file(test_dir):
    """Crée un fichier Python avec plusieurs types de bugs"""
    print("\n" + "="*80)
    print("CRÉATION DU FICHIER DE TEST AVEC BUGS")
    print("="*80)
    
    buggy_code = '''"""Module de calcul avec bugs intentionnels"""

def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    result = total / count
    return result

def process_data(data):
    result = []
    for item in data:
        processed = item * 2 + undefined_variable
        result.append(processed)
    return result

def divide_numbers(a, b):
    return a / b

if __name__ == "__main__":
    # Test 1 : Division par zéro
    print(divide_numbers(10, 0))
    
    # Test 2 : Variable non définie
    print(process_data([1, 2, 3]))
    
    # Test 3 : Liste vide
    print(calculate_average([]))
'''
    
    test_file = test_dir / "buggy_calculator.py"
    test_file.write_text(buggy_code, encoding='utf-8')
    
    print(f"✅ Fichier créé : {test_file}")
    print(f"📏 Taille : {len(buggy_code)} caractères")
    print(f"📄 Lignes : {len(buggy_code.splitlines())} lignes")
    print("\n🐛 Bugs intentionnels inclus :")
    print("   1. Division par zéro (ligne 17)")
    print("   2. Variable non définie 'undefined_variable' (ligne 10)")
    print("   3. Division par zéro potentielle dans calculate_average")
    print("   4. Docstrings manquantes pour certaines fonctions")
    
    return test_file


def test_auditor_agent(test_file):
    """Test de l'Agent Auditeur"""
    print("\n" + "="*80)
    print("TEST 1 : AGENT AUDITEUR")
    print("="*80)
    
    try:
        from src.agents.auditor_agent import AuditorAgent
        
        print("✅ Import de AuditorAgent réussi")
        
        # Créer et tester l'agent
        auditor = AuditorAgent()
        print("✅ AuditorAgent initialisé")
        
        # Analyser le fichier
        print(f"\n🔍 Analyse de {test_file.name}...")
        report = auditor.analyze_file(str(test_file))
        
        if report is None:
            print("❌ ÉCHEC : L'Auditeur n'a pas retourné de rapport")
            return None
        
        print("✅ Rapport d'audit reçu")
        
        # Vérifier le contenu du rapport
        bugs_found = report.get('total_issues', 0)
        print(f"\n📊 RÉSULTATS :")
        print(f"   Bugs détectés : {bugs_found}")
        
        if bugs_found == 0:
            print("⚠️  ATTENTION : Aucun bug détecté (attendu : au moins 3)")
            return report
        
        # Afficher les bugs trouvés
        issues = report.get('issues', [])
        print(f"\n📋 Détails des problèmes ({len(issues)}) :")
        for i, issue in enumerate(issues[:5], 1):  # Afficher max 5
            print(f"   [{i}] Ligne {issue.get('line', '?')}")
            print(f"       Type : {issue.get('type', 'N/A')}")
            print(f"       Sévérité : {issue.get('severity', 'N/A')}")
            print(f"       Description : {issue.get('description', 'N/A')[:60]}...")
        
        if len(issues) > 5:
            print(f"   ... et {len(issues) - 5} autre(s) problème(s)")
        
        print("\n✅ TEST AUDITEUR : RÉUSSI")
        return report
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du test de l'Auditeur : {e}")
        import traceback
        traceback.print_exc()
        return None


def test_fixer_agent(test_file, audit_report):
    """Test de l'Agent Correcteur"""
    print("\n" + "="*80)
    print("TEST 2 : AGENT CORRECTEUR")
    print("="*80)
    
    if audit_report is None:
        print("❌ SKIP : Pas de rapport d'audit disponible")
        return False
    
    try:
        from src.agents.fixer_agent import FixerAgent
        
        print("✅ Import de FixerAgent réussi")
        
        # Créer et tester l'agent
        fixer = FixerAgent()
        print("✅ FixerAgent initialisé")
        
        # Lire le code original
        original_code = test_file.read_text(encoding='utf-8')
        original_lines = len(original_code.splitlines())
        
        print(f"\n🔧 Correction de {test_file.name}...")
        bugs_to_fix = audit_report.get('total_issues', 0)
        print(f"   Problèmes à corriger : {bugs_to_fix}")
        
        # Corriger le fichier
        success = fixer.fix_file(str(test_file), audit_report)
        
        if not success:
            print("❌ ÉCHEC : La correction a échoué")
            return False
        
        print("✅ Correction terminée")
        
        # Vérifier le code corrigé
        fixed_code = test_file.read_text(encoding='utf-8')
        fixed_lines = len(fixed_code.splitlines())
        
        print(f"\n📊 RÉSULTATS :")
        print(f"   Lignes originales : {original_lines}")
        print(f"   Lignes corrigées : {fixed_lines}")
        print(f"   Différence : {fixed_lines - original_lines:+d} lignes")
        
        # Vérifier syntaxe
        try:
            compile(fixed_code, test_file.name, 'exec')
            print("✅ Code corrigé syntaxiquement VALIDE")
            syntax_ok = True
        except SyntaxError as e:
            print(f"❌ ERREUR DE SYNTAXE : {e}")
            syntax_ok = False
        
        # Vérifications supplémentaires
        print(f"\n🔍 VÉRIFICATIONS :")
        
        checks = {
            "Docstrings présentes": '"""' in fixed_code or "'''" in fixed_code,
            "Variable 'undefined_variable' corrigée": "undefined_variable" not in fixed_code,
            "Protection division par zéro": ("if" in fixed_code and "== 0" in fixed_code) or "!= 0" in fixed_code
        }
        
        for check_name, result in checks.items():
            status = "✅" if result else "⚠️"
            print(f"   {status} {check_name}")
        
        all_checks_ok = all(checks.values())
        
        if syntax_ok and all_checks_ok:
            print("\n✅ TEST FIXER : RÉUSSI")
            return True
        else:
            print("\n⚠️  TEST FIXER : PARTIEL (code valide mais corrections incomplètes)")
            return syntax_ok
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du test du Fixer : {e}")
        import traceback
        traceback.print_exc()
        return False


def test_judge_agent(test_file, audit_report):
    """Test de l'Agent Testeur"""
    print("\n" + "="*80)
    print("TEST 3 : AGENT TESTEUR (JUDGE)")
    print("="*80)
    
    try:
        from src.agents.judge_agent import JudgeAgent
        
        print("✅ Import de JudgeAgent réussi")
        
        # Créer et tester l'agent
        judge = JudgeAgent()
        print("✅ JudgeAgent initialisé")
        
        print(f"\n⚖️  Test de {test_file.name}...")
        
        # Tester le fichier
        judge_report = judge.judge_file(str(test_file), audit_report)
        
        if judge_report is None:
            print("❌ ÉCHEC : Le Judge n'a pas retourné de rapport")
            return False
        
        print("✅ Rapport de test reçu")
        
        # Vérifier le contenu du rapport
        decision = judge_report.get('decision', 'UNKNOWN')
        passed = judge_report.get('passed', 0)
        failed = judge_report.get('failed', 0)
        message = judge_report.get('message', 'N/A')
        
        print(f"\n📊 RÉSULTATS :")
        print(f"   Décision : {decision}")
        print(f"   Tests passés : {passed}")
        print(f"   Tests échoués : {failed}")
        print(f"   Message : {message[:80]}...")
        
        success = decision == "VALIDATE"
        
        if success:
            print("\n✅ TEST JUDGE : RÉUSSI (Code validé)")
        else:
            print(f"\n⚠️  TEST JUDGE : Code non validé (décision: {decision})")
        
        return success
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du test du Judge : {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator(test_dir):
    """Test de l'Orchestrateur"""
    print("\n" + "="*80)
    print("TEST 4 : ORCHESTRATEUR")
    print("="*80)
    
    try:
        from src.orchestrator import Orchestrator
        
        print("✅ Import de Orchestrator réussi")
        
        # Créer l'orchestrateur avec le dossier de test
        orchestrator = Orchestrator(
            target_dir=str(test_dir),
            max_iterations=10
        )
        print("✅ Orchestrator initialisé")
        
        print(f"\n🎯 Lancement du workflow complet...")
        print(f"   Dossier cible : {test_dir}")
        print(f"   Max itérations : 10")
        
        # Exécuter le workflow
        summary = orchestrator.run()
        
        if summary is None:
            print("❌ ÉCHEC : L'Orchestrateur n'a pas retourné de résumé")
            return False
        
        print("✅ Workflow terminé")
        
        # Afficher le résumé
        print(f"\n📊 RÉSUMÉ :")
        print(f"   Fichiers traités : {summary.get('total_files', 0)}")
        print(f"   Validés : {summary.get('files_validated', 0)}")
        print(f"   Échoués : {summary.get('files_failed', 0)}")
        print(f"   Taux de succès : {summary.get('success_rate', 0):.1f}%")
        
        # Vérifier les détails des fichiers
        files = summary.get('files', [])
        if files:
            print(f"\n📋 Détails :")
            for file_info in files:
                status_symbol = "✅" if file_info['status'] == "VALIDATED" else "❌"
                print(f"   {status_symbol} {file_info['file_name']}")
                print(f"       Status: {file_info['status']}")
                print(f"       Itérations: {file_info['iterations']}")
                print(f"       Bugs trouvés: {file_info['bugs_found']}")
                print(f"       Bugs corrigés: {file_info['bugs_fixed']}")
        
        success = summary.get('files_validated', 0) > 0
        
        if success:
            print("\n✅ TEST ORCHESTRATOR : RÉUSSI")
        else:
            print("\n⚠️  TEST ORCHESTRATOR : Aucun fichier validé")
        
        return success
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du test de l'Orchestrateur : {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_logs():
    """Vérifie que les logs ont été créés correctement"""
    print("\n" + "="*80)
    print("TEST 5 : VÉRIFICATION DES LOGS")
    print("="*80)
    
    log_file = project_root / "logs" / "experiment_data.json"
    
    if not log_file.exists():
        print(f"❌ Fichier de logs introuvable : {log_file}")
        return False
    
    print(f"✅ Fichier de logs trouvé : {log_file}")
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        print(f"✅ Fichier JSON valide")
        print(f"\n📊 CONTENU :")
        print(f"   Entrées de log : {len(logs)}")
        
        if len(logs) == 0:
            print("⚠️  ATTENTION : Aucune entrée dans les logs")
            return False
        
        # Vérifier la structure des logs
        required_fields = ['timestamp', 'agent_name', 'model_used', 'action', 'details', 'status']
        
        sample_log = logs[0]
        missing_fields = [field for field in required_fields if field not in sample_log]
        
        if missing_fields:
            print(f"⚠️  Champs manquants dans les logs : {missing_fields}")
        else:
            print(f"✅ Structure des logs conforme")
        
        # Compter les agents
        agents = {}
        for log in logs:
            agent = log.get('agent_name', 'Unknown')
            agents[agent] = agents.get(agent, 0) + 1
        
        print(f"\n📋 Actions par agent :")
        for agent, count in agents.items():
            print(f"   {agent}: {count} action(s)")
        
        print("\n✅ TEST LOGS : RÉUSSI")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON : {e}")
        return False
    except Exception as e:
        print(f"❌ ERREUR : {e}")
        return False


def run_all_tests():
    """Exécute tous les tests d'intégration"""
    
    print("\n" + "🧪"*40)
    print("TEST D'INTÉGRATION COMPLET - REFACTORING SWARM")
    print("🧪"*40)
    
    # Préparer l'environnement
    test_dir = setup_test_environment()
    
    # Créer le fichier de test
    test_file = create_buggy_test_file(test_dir)
    
    # Résultats
    results = {}
    
    # Test 1 : Auditeur
    audit_report = test_auditor_agent(test_file)
    results['Auditeur'] = audit_report is not None
    
    # Test 2 : Fixer
    if audit_report:
        results['Fixer'] = test_fixer_agent(test_file, audit_report)
    else:
        print("\n⚠️  SKIP : Test Fixer (pas de rapport d'audit)")
        results['Fixer'] = False
    
    # Test 3 : Judge
    if audit_report:
        results['Judge'] = test_judge_agent(test_file, audit_report)
    else:
        print("\n⚠️  SKIP : Test Judge (pas de rapport d'audit)")
        results['Judge'] = False
    
    # Test 4 : Orchestrateur (re-créer le fichier pour un test propre)
    test_file = create_buggy_test_file(test_dir)
    results['Orchestrateur'] = test_orchestrator(test_dir)
    
    # Test 5 : Logs
    results['Logs'] = verify_logs()
    
    # Résumé final
    print("\n" + "="*80)
    print("📊 RÉSUMÉ FINAL DES TESTS")
    print("="*80)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    print("\n" + "="*80)
    print(f"RÉSULTAT : {passed}/{total} tests réussis ({passed/total*100:.0f}%)")
    print("="*80)
    
    if passed == total:
        print("\n🎉 SUCCÈS COMPLET !")
        print("✅ Tous les agents fonctionnent correctement ensemble")
        print("✅ Le système est prêt pour le rendu")
        return True
    elif passed >= total * 0.6:
        print(f"\n⚠️  SUCCÈS PARTIEL ({passed}/{total})")
        print("⚠️  Certains composants nécessitent des corrections")
        print("⚠️  Vérifiez les erreurs ci-dessus")
        return False
    else:
        print(f"\n❌ ÉCHEC ({passed}/{total})")
        print("❌ Le système nécessite des corrections importantes")
        print("❌ Vérifiez la configuration et les dépendances")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERREUR CRITIQUE : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)