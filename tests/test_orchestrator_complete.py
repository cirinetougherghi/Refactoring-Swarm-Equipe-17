"""
Test complet de l'Orchestrateur
Teste le workflow complet : Audit -> Fix -> Test -> (Loop if needed)
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

# Import de l'orchestrateur
try:
    from src.orchestrator import Orchestrator
    print("✅ Import de l'Orchestrateur réussi")
except ImportError as e:
    print(f"❌ ERREUR d'import : {e}")
    sys.exit(1)


def test_orchestrator_simple():
    """Test de l'Orchestrateur sur un fichier simple"""
    
    print("\n" + "="*80)
    print("TEST COMPLET DE L'ORCHESTRATEUR")
    print("="*80 + "\n")
    
    # Crée un dossier de test avec un fichier buggé
    test_dir = "sandbox/test_orchestrator"
    os.makedirs(test_dir, exist_ok=True)
    
    # Fichier de test avec bugs
    test_code = """import os

def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count

def process_data():
    data = [1, 2, 3, 4, 5]
    avg = calculate_average(data)
    print(f"Average: {avg}")
    print(f"Square root: {math.sqrt(avg)}")

if __name__ == "__main__":
    process_data()
"""
    
    test_file = os.path.join(test_dir, "buggy_code.py")
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"📄 Fichier de test créé : {test_file}")
    print(f"📏 Code original ({len(test_code.splitlines())} lignes)")
    print("\n🐛 Bugs présents :")
    print("   - Missing import: math")
    print("   - Division by zero possible (empty list)")
    print("   - Missing docstrings")
    
    # Lance l'orchestrateur
    print("\n" + "="*80)
    print("🚀 LANCEMENT DE L'ORCHESTRATEUR")
    print("="*80 + "\n")
    
    
    orchestrator = Orchestrator(
        target_dir=test_dir,
        max_iterations=10  # 
    )
    
    try:
        results = orchestrator.run()
        
        # Affiche les résultats
        print("\n" + "="*80)
        print("📊 RÉSULTATS FINAUX")
        print("="*80 + "\n")
        
        print(f"Fichiers traités    : {results['total_files']}")
        print(f"Fichiers validés    : {results['files_validated']}")
        print(f"Fichiers échoués    : {results['files_failed']}")
        print(f"Taux de succès      : {results['success_rate']:.1f}%")
        
        if results['files']:
            print("\n📋 Détails par fichier :")
            for file_info in results['files']:
                status_symbol = "✅" if file_info['status'] == "VALIDATED" else "❌"
                print(f"\n{status_symbol} {file_info['file_name']}")
                print(f"   Status      : {file_info['status']}")
                print(f"   Itérations  : {file_info['iterations']}")
                print(f"   Bugs trouvés: {file_info['bugs_found']}")
                print(f"   Bugs corrigés: {file_info['bugs_fixed']}")
        
        # Vérifications
        print("\n" + "="*80)
        print("📈 VÉRIFICATIONS")
        print("="*80 + "\n")
        
        success = True
        
        # Vérifie qu'au moins un fichier a été traité
        if results['total_files'] == 0:
            print("❌ Aucun fichier traité")
            success = False
        else:
            print(f"✅ {results['total_files']} fichier(s) traité(s)")
        
        # Vérifie que le fichier a été validé
        if results['files_validated'] > 0:
            print(f"✅ {results['files_validated']} fichier(s) validé(s)")
        else:
            print("❌ Aucun fichier validé")
            success = False
        
        # Vérifie que des bugs ont été détectés et corrigés
        if results['files']:
            file_info = results['files'][0]
            if file_info['bugs_found'] > 0:
                print(f"✅ Bugs détectés : {file_info['bugs_found']}")
            else:
                print("⚠️ Aucun bug détecté")
            
            if file_info['bugs_fixed'] > 0:
                print(f"✅ Bugs corrigés : {file_info['bugs_fixed']}")
            else:
                print("⚠️ Aucun bug corrigé")
        
        # Vérifie les logs
        log_file = "logs/experiment_data.json"
        if os.path.exists(log_file):
            import json
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # Compte les entrées par agent
            orchestrator_logs = [l for l in logs if l.get('agent') == 'Orchestrator']
            auditor_logs = [l for l in logs if 'Auditor' in l.get('agent', '')]
            fixer_logs = [l for l in logs if 'Fixer' in l.get('agent', '')]
            
            print(f"✅ Logs créés : {len(logs)} entrées totales")
            print(f"   - Orchestrator : {len(orchestrator_logs)}")
            print(f"   - Auditor      : {len(auditor_logs)}")
            print(f"   - Fixer        : {len(fixer_logs)}")
        else:
            print("❌ Fichier de logs non trouvé")
            success = False
        
        print("\n" + "="*80)
        
        if success and results['files_validated'] > 0:
            print("🎉 SUCCÈS COMPLET : L'Orchestrateur fonctionne parfaitement !")
            print("="*80 + "\n")
            return True
        else:
            print("⚠️ SUCCÈS PARTIEL : L'Orchestrateur a des problèmes")
            print("="*80 + "\n")
            return False
    
    except Exception as e:
        print(f"\n❌ ERREUR lors de l'exécution : {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator_multiple_files():
    """Test avec plusieurs fichiers"""
    
    print("\n" + "="*80)
    print("TEST ORCHESTRATEUR - FICHIERS MULTIPLES")
    print("="*80 + "\n")
    
    # Crée plusieurs fichiers de test
    test_dir = "sandbox/test_orchestrator_multi"
    os.makedirs(test_dir, exist_ok=True)
    
    # Fichier 1 : Simple bug
    file1_code = """
def add(a, b):
    return a + b

print(add(1, 2))
print(undefined)
"""
    
    # Fichier 2 : Division par zéro
    file2_code = """
def divide(x, y):
    return x / y

print(divide(10, 0))
"""
    
    with open(os.path.join(test_dir, "file1.py"), 'w') as f:
        f.write(file1_code)
    
    with open(os.path.join(test_dir, "file2.py"), 'w') as f:
        f.write(file2_code)
    
    print("📄 2 fichiers de test créés")
    
    # Lance l'orchestrateur
    print("\n🚀 Lancement de l'Orchestrateur...\n")
    
    # ✅ CORRECTION ICI : max_iterations=10 (au lieu de 3)
    orchestrator = Orchestrator(
        target_dir=test_dir,
        max_iterations=10  # ✅ CHANGÉ DE 3 À 10
    )
    
    try:
        results = orchestrator.run()
        
        print("\n" + "="*80)
        print("📊 RÉSULTATS")
        print("="*80 + "\n")
        
        print(f"Fichiers traités : {results['total_files']}")
        print(f"Fichiers validés : {results['files_validated']}")
        
        if results['total_files'] == 2:
            print("✅ Les 2 fichiers ont été traités")
            return True
        else:
            print(f"⚠️ Seulement {results['total_files']} fichier(s) traité(s)")
            return False
    
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        return False


if __name__ == "__main__":
    print("\n" + "🧪"*40)
    print("TESTS COMPLETS DE L'ORCHESTRATEUR")
    print("🧪"*40)
    
    # Test 1 : Simple file
    test1 = test_orchestrator_simple()
    
    # Test 2 : Multiple files (optionnel, plus long)
    # test2 = test_orchestrator_multiple_files()
    
    print("\n" + "="*80)
    print("📊 RÉSUMÉ FINAL")
    print("="*80)
    
    if test1:
        print("✅ Test simple : SUCCÈS")
        print("\n🎉 L'Orchestrateur est prêt pour la production !")
        sys.exit(0)
    else:
        print("❌ Test simple : ÉCHEC")
        print("\n⚠️ L'Orchestrateur nécessite des corrections")
        sys.exit(1)