"""
Test complet de l'Agent Auditeur
Vérifie que l'Auditeur détecte correctement tous les types de bugs
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Configuration
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ ERREUR : Clé API non trouvée")
    exit(1)

genai.configure(api_key=api_key)

# Import de l'agent
from src.agents.auditor_agent import AuditorAgent


def test_case_1_simple_bugs():
    """Test 1 : Code simple avec bugs évidents"""
    print("\n" + "="*80)
    print("TEST 1 : CODE SIMPLE AVEC BUGS ÉVIDENTS")
    print("="*80)
    
    # Crée un fichier de test temporaire
    test_code = """import os

def calculate(x, y):
    result = x / y
    return result

print(calculate(10, 0))
print(undefined_var)
"""
    
    test_file = "sandbox/test_audit_simple.py"
    os.makedirs("sandbox", exist_ok=True)
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    # Test l'auditeur
    auditor = AuditorAgent()
    report = auditor.analyze_file(test_file)
    
    # Vérifications
    print("\n📊 RÉSULTATS :")
    
    if report is None:
        print("❌ ÉCHEC : Aucun rapport retourné")
        return False
    
    bugs_found = report.get('total_issues', 0)
    print(f"   Bugs détectés : {bugs_found}")
    
    # Attendu : Au moins 3 bugs
    # 1. division_by_zero (ligne 7)
    # 2. undefined_variable (ligne 8)
    # 3. missing_docstring (fonction calculate)
    
    if bugs_found < 3:
        print(f"❌ ÉCHEC : Attendu au moins 3 bugs, trouvé {bugs_found}")
        return False
    
    print("✅ SUCCÈS : Nombre de bugs correct")
    
    # Vérifie que les bugs critiques sont détectés
    issues = report.get('issues', [])
    has_division = any('division' in i.get('description', '').lower() for i in issues)
    has_undefined = any('undefined' in i.get('description', '').lower() for i in issues)
    
    if not has_division:
        print("❌ ÉCHEC : Division par zéro non détectée")
        return False
    
    if not has_undefined:
        print("❌ ÉCHEC : Variable non définie non détectée")
        return False
    
    print("✅ SUCCÈS : Bugs critiques détectés")
    
    # Nettoyage
    os.remove(test_file)
    
    return True


def test_case_2_clean_code():
    """Test 2 : Code propre sans bugs"""
    print("\n" + "="*80)
    print("TEST 2 : CODE PROPRE (PAS DE FAUX POSITIFS)")
    print("="*80)
    
    test_code = '''"""Module de calcul."""

def add(a: int, b: int) -> int:
    """Additionne deux nombres.
    
    Args:
        a: Premier nombre
        b: Deuxième nombre
    
    Returns:
        La somme de a et b
    """
    return a + b


def multiply(x: int, y: int) -> int:
    """Multiplie deux nombres.
    
    Args:
        x: Premier nombre
        y: Deuxième nombre
    
    Returns:
        Le produit de x et y
    """
    return x * y
'''
    
    test_file = "sandbox/test_audit_clean.py"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    # Test l'auditeur
    auditor = AuditorAgent()
    report = auditor.analyze_file(test_file)
    
    # Vérifications
    print("\n📊 RÉSULTATS :")
    
    if report is None:
        print("❌ ÉCHEC : Aucun rapport retourné")
        return False
    
    bugs_found = report.get('total_issues', 0)
    print(f"   Bugs détectés : {bugs_found}")
    
    # Code propre = 0 bugs HIGH/CRITICAL
    issues = report.get('issues', [])
    critical_bugs = [i for i in issues if i.get('severity') in ['HIGH', 'CRITICAL']]
    
    if len(critical_bugs) > 0:
        print(f"❌ ÉCHEC : Faux positifs détectés ({len(critical_bugs)} bugs HIGH/CRITICAL)")
        for bug in critical_bugs:
            print(f"   - Ligne {bug.get('line')}: {bug.get('description')}")
        return False
    
    print("✅ SUCCÈS : Aucun faux positif")
    
    # Nettoyage
    os.remove(test_file)
    
    return True


def test_case_3_missing_import():
    """Test 3 : Import manquant"""
    print("\n" + "="*80)
    print("TEST 3 : IMPORT MANQUANT")
    print("="*80)
    
    test_code = """
def calculate_sqrt(x):
    return math.sqrt(x)

print(calculate_sqrt(16))
"""
    
    test_file = "sandbox/test_audit_import.py"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    # Test l'auditeur
    auditor = AuditorAgent()
    report = auditor.analyze_file(test_file)
    
    # Vérifications
    print("\n📊 RÉSULTATS :")
    
    if report is None:
        print("❌ ÉCHEC : Aucun rapport retourné")
        return False
    
    issues = report.get('issues', [])
    has_import_error = any(
        'import' in i.get('description', '').lower() or 
        'math' in i.get('description', '').lower()
        for i in issues
    )
    
    if not has_import_error:
        print("❌ ÉCHEC : Import manquant non détecté")
        return False
    
    print("✅ SUCCÈS : Import manquant détecté")
    
    # Nettoyage
    os.remove(test_file)
    
    return True


def test_case_4_json_validity():
    """Test 4 : JSON toujours valide"""
    print("\n" + "="*80)
    print("TEST 4 : VALIDITÉ DU JSON")
    print("="*80)
    
    # Test avec plusieurs types de code
    test_cases = [
        "print('hello')",
        "def f(): pass",
        "",  # Code vide
        "x = 1 / 0",
    ]
    
    auditor = AuditorAgent()
    
    for i, code in enumerate(test_cases, 1):
        test_file = f"sandbox/test_audit_json_{i}.py"
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        report = auditor.analyze_file(test_file)
        
        if report is None:
            print(f"❌ ÉCHEC : Rapport None pour cas {i}")
            return False
        
        # Vérifie structure minimale
        if 'total_issues' not in report:
            print(f"❌ ÉCHEC : Champ 'total_issues' manquant pour cas {i}")
            return False
        
        if 'issues' not in report:
            print(f"❌ ÉCHEC : Champ 'issues' manquant pour cas {i}")
            return False
        
        os.remove(test_file)
    
    print("✅ SUCCÈS : JSON toujours valide")
    return True


def run_all_tests():
    """Execute tous les tests"""
    
    print("\n" + "🧪"*40)
    print("TESTS COMPLETS DE L'AGENT AUDITEUR")
    print("🧪"*40)
    
    tests = [
        ("Bugs simples", test_case_1_simple_bugs),
        ("Code propre", test_case_2_clean_code),
        ("Import manquant", test_case_3_missing_import),
        ("Validité JSON", test_case_4_json_validity),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ ERREUR LORS DU TEST '{test_name}' : {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*80)
    print(f"RÉSULTAT FINAL : {passed}/{total} tests réussis ({passed/total*100:.0f}%)")
    print("="*80)
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
        print("✅ L'Auditeur fonctionne parfaitement")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) échoué(s)")
        print("❌ L'Auditeur nécessite des corrections")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)